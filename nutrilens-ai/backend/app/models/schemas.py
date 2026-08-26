"""
NutriLens AI — Pydantic Schemas
Request/Response models for all API endpoints.
"""
from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, EmailStr, Field, field_validator


# ═══════════════════════════════════════════════════════════════════════════════
#  USER SCHEMAS
# ═══════════════════════════════════════════════════════════════════════════════

class HealthConditions(BaseModel):
    diabetes: bool = False
    hypertension: bool = False
    kidney_disease: bool = False
    pregnancy: bool = False
    heart_disease: bool = False
    obesity: bool = False
    celiac_disease: bool = False


class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=100)
    full_name: Optional[str] = None
    age: Optional[int] = Field(None, ge=1, le=120)
    health_conditions: HealthConditions = Field(default_factory=HealthConditions)
    allergies: List[str] = []
    preferred_language: str = "en"

    @field_validator("preferred_language")
    @classmethod
    def validate_language(cls, v: str) -> str:
        allowed = {"en", "hi", "kn", "ta"}
        if v not in allowed:
            raise ValueError(f"Language must be one of: {allowed}")
        return v


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    age: Optional[int] = Field(None, ge=1, le=120)
    health_conditions: Optional[HealthConditions] = None
    allergies: Optional[List[str]] = None
    preferred_language: Optional[str] = None

    @field_validator("preferred_language")
    @classmethod
    def validate_language(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            allowed = {"en", "hi", "kn", "ta"}
            if v not in allowed:
                raise ValueError(f"Language must be one of: {allowed}")
        return v


class UserResponse(BaseModel):
    id: uuid.UUID
    email: str
    full_name: Optional[str]
    age: Optional[int]
    health_conditions: Dict[str, Any]
    allergies: List[str]
    preferred_language: str
    created_at: datetime

    model_config = {"from_attributes": True}


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse


# ═══════════════════════════════════════════════════════════════════════════════
#  SCAN REQUEST SCHEMAS
# ═══════════════════════════════════════════════════════════════════════════════

class ManualScanRequest(BaseModel):
    barcode: str = Field(..., min_length=8, max_length=20, description="EAN/UPC barcode number")
    language: str = Field("en", description="Response language: en | hi | kn | ta")
    user_profile: Optional[Dict[str, Any]] = None  # override profile for guest users


# ═══════════════════════════════════════════════════════════════════════════════
#  PRODUCT DATA SCHEMAS
# ═══════════════════════════════════════════════════════════════════════════════

class NutrimentValues(BaseModel):
    energy_kcal_100g: Optional[float] = None
    fat_100g: Optional[float] = None
    saturated_fat_100g: Optional[float] = None
    carbohydrates_100g: Optional[float] = None
    sugars_100g: Optional[float] = None
    fiber_100g: Optional[float] = None
    proteins_100g: Optional[float] = None
    salt_100g: Optional[float] = None
    sodium_100g: Optional[float] = None


class ProductData(BaseModel):
    barcode: str
    product_name: Optional[str] = None
    brand: Optional[str] = None
    categories: Optional[str] = None
    ingredients_text: Optional[str] = None
    nutriments: NutrimentValues = Field(default_factory=NutrimentValues)
    allergens: List[str] = []
    traces: List[str] = []
    additives: List[str] = []
    nutri_score: Optional[str] = None
    nova_group: Optional[int] = None
    image_url: Optional[str] = None
    found: bool = False


# ═══════════════════════════════════════════════════════════════════════════════
#  GEMINI ANALYSIS SCHEMAS
# ═══════════════════════════════════════════════════════════════════════════════

class IngredientExplanation(BaseModel):
    name: str
    purpose: str
    safety_level: str  # "safe" | "moderate_concern" | "high_concern"
    notes: str


class NutritionSummary(BaseModel):
    calories_per_100g: Optional[float] = None
    macros_summary: str
    sugar_level: str  # "low" | "moderate" | "high"
    sodium_level: str
    fat_level: str
    fiber_adequacy: str
    overall_nutrition_rating: str


class HealthRisk(BaseModel):
    condition: str
    risk_level: str  # "low" | "moderate" | "high"
    explanation: str


class AdditiveExplanation(BaseModel):
    ins_code: str
    name: str
    function: str
    safety_status: str
    daily_limit: Optional[str] = None
    concerns: str


class AlternativeProduct(BaseModel):
    name: str
    reason: str
    healthier_aspects: List[str]


class GeminiAnalysis(BaseModel):
    product_summary: Dict[str, Any]
    ingredient_explanations: List[IngredientExplanation]
    nutrition_summary: NutritionSummary
    health_risk_assessment: List[HealthRisk]
    harmful_ingredients: List[Dict[str, str]]
    additive_explanations: List[AdditiveExplanation]
    fssai_guideline_summary: str
    personalized_recommendations: List[str]
    better_alternatives: List[AlternativeProduct]
    overall_health_score: int = Field(..., ge=0, le=100)
    daily_consumption_advice: str
    language: str


# ═══════════════════════════════════════════════════════════════════════════════
#  SCAN RESPONSE SCHEMA
# ═══════════════════════════════════════════════════════════════════════════════

class ScanResponse(BaseModel):
    scan_id: Optional[uuid.UUID] = None
    product: ProductData
    analysis: GeminiAnalysis
    scanned_at: datetime


# ═══════════════════════════════════════════════════════════════════════════════
#  HISTORY SCHEMAS
# ═══════════════════════════════════════════════════════════════════════════════

class ScanHistoryItem(BaseModel):
    id: uuid.UUID
    barcode: str
    product_name: Optional[str]
    brand: Optional[str]
    product_image_url: Optional[str]
    overall_health_score: Optional[float]
    language: str
    scanned_at: datetime

    model_config = {"from_attributes": True}


class ScanHistoryDetail(ScanHistoryItem):
    scan_result: Dict[str, Any]


class PaginatedHistory(BaseModel):
    items: List[ScanHistoryItem]
    total: int
    page: int
    page_size: int
    total_pages: int
