"""
NutriLens AI — Food Barcode Scan & AI Analysis API Endpoints
"""
from datetime import datetime, timezone
from typing import Optional, List, Dict, Any

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.scan_history import ScanHistory
from app.models.schemas import ManualScanRequest, ScanResponse, ProductData
from app.models.user import User
from app.api.v1.endpoints.users import get_current_user_optional
from app.services.barcode_decoder import decode_barcode_from_image
from app.services.openfoodfacts_service import fetch_product_by_barcode, SAMPLE_PRODUCTS
from app.services.gemini_service import analyze_product_with_gemini

router = APIRouter(prefix="/scan", tags=["Barcode & AI Analysis"])


async def execute_full_scan_pipeline(
    barcode: str,
    language: str,
    override_profile: Optional[Dict[str, Any]],
    current_user: Optional[User],
    db: AsyncSession
) -> ScanResponse:
    """Core scanning pipeline: fetch product -> run RAG Gemini -> persist to history."""
    
    # 1. Build effective user profile context
    user_profile = {}
    if current_user:
        user_profile = {
            "age": current_user.age,
            "health_conditions": current_user.health_conditions,
            "allergies": current_user.allergies,
            "preferred_language": current_user.preferred_language,
        }
    if override_profile:
        user_profile.update(override_profile)

    # 2. Fetch product data from OpenFoodFacts (or sample dictionary)
    product_data: ProductData = await fetch_product_by_barcode(barcode)

    # 3. Perform RAG Vector Search & Gemini LLM Multilingual Analysis
    target_lang = language or (current_user.preferred_language if current_user else "en")
    analysis_result = await analyze_product_with_gemini(product_data, user_profile, target_lang)

    # 4. Save scan to ScanHistory DB table if user authenticated or session active
    scan_id = None
    try:
        db_scan = ScanHistory(
            user_id=current_user.id if current_user else None,
            barcode=product_data.barcode,
            product_name=product_data.product_name,
            brand=product_data.brand,
            product_image_url=product_data.image_url,
            scan_result={
                "product": product_data.model_dump(),
                "analysis": analysis_result.model_dump(),
            },
            overall_health_score=analysis_result.overall_health_score,
            language=target_lang,
        )
        db.add(db_scan)
        await db.commit()
        await db.refresh(db_scan)
        scan_id = db_scan.id
    except Exception as err:
        # Don't fail the scan request if database saving encounters an issue
        pass

    return ScanResponse(
        scan_id=scan_id,
        product=product_data,
        analysis=analysis_result,
        scanned_at=datetime.now(timezone.utc)
    )


@router.post("/manual", response_model=ScanResponse)
async def scan_manual_barcode(
    scan_in: ManualScanRequest,
    current_user: Optional[User] = Depends(get_current_user_optional),
    db: AsyncSession = Depends(get_db),
):
    """
    Process a product scan by entering or reading a raw barcode number.
    """
    return await execute_full_scan_pipeline(
        barcode=scan_in.barcode,
        language=scan_in.language,
        override_profile=scan_in.user_profile,
        current_user=current_user,
        db=db,
    )


@router.post("/image", response_model=ScanResponse)
async def scan_barcode_image(
    file: UploadFile = File(...),
    language: str = Form("en"),
    current_user: Optional[User] = Depends(get_current_user_optional),
    db: AsyncSession = Depends(get_db),
):
    """
    Upload an image containing a product barcode (PNG/JPG/WebP).
    Decodes the barcode using pyzbar/OpenCV and executes the RAG analysis pipeline.
    """
    image_bytes = await file.read()
    if not image_bytes:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Uploaded file is empty.",
        )

    barcode = decode_barcode_from_image(image_bytes)
    if not barcode:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Could not detect or decode a valid barcode in the uploaded image. Please try a clearer picture or enter the barcode manually.",
        )

    return await execute_full_scan_pipeline(
        barcode=barcode,
        language=language,
        override_profile=None,
        current_user=current_user,
        db=db,
    )


@router.get("/samples")
async def get_sample_barcodes() -> List[Dict[str, Any]]:
    """
    Return pre-seeded sample food product barcodes for 1-click testing.
    """
    samples = []
    for code, p in SAMPLE_PRODUCTS.items():
        samples.append({
            "barcode": code,
            "product_name": p["product_name"],
            "brand": p["brand"],
            "category": p["categories"].split(",")[0],
            "nutri_score": p["nutri_score"],
            "image_url": p["image_url"],
        })
    return samples
