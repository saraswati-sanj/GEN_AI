"""
NutriLens AI — Barcode Image Decoding Service
Decodes standard EAN/UPC/Code128 barcodes from uploaded images using pyzbar & OpenCV/PIL.
"""
import io
import logging
from typing import Optional

from PIL import Image, ImageEnhance, ImageFilter

logger = logging.getLogger("nutrilens.barcode")

try:
    from pyzbar.pyzbar import decode as pyzbar_decode
    PYZBAR_AVAILABLE = True
except Exception as e:
    logger.warning(f"pyzbar decoding library not fully loaded: {e}. Standard pyzbar fallback active.")
    PYZBAR_AVAILABLE = False


def decode_barcode_from_image(image_bytes: bytes) -> Optional[str]:
    """
    Extract barcode number string from raw image bytes.
    Applies image preprocessing (grayscale, contrast enhancement, sharpening)
    if initial decode fails.
    """
    try:
        pil_image = Image.open(io.BytesIO(image_bytes))
    except Exception as e:
        logger.error(f"Failed to open image file: {e}")
        return None

    # Step 1: Try direct pyzbar decode on original image
    if PYZBAR_AVAILABLE:
        try:
            decoded_objects = pyzbar_decode(pil_image)
            for obj in decoded_objects:
                barcode_str = obj.data.decode("utf-8").strip()
                if barcode_str and len(barcode_str) >= 8:
                    logger.info(f"Successfully decoded barcode '{barcode_str}' (type: {obj.type})")
                    return barcode_str
        except Exception as err:
            logger.debug(f"Direct pyzbar decode attempt failed: {err}")

    # Step 2: Preprocess image (Grayscale + High Contrast) and try again
    try:
        gray_img = pil_image.convert("L")
        enhancer = ImageEnhance.Contrast(gray_img)
        contrast_img = enhancer.enhance(2.0)

        if PYZBAR_AVAILABLE:
            decoded_objects = pyzbar_decode(contrast_img)
            for obj in decoded_objects:
                barcode_str = obj.data.decode("utf-8").strip()
                if barcode_str and len(barcode_str) >= 8:
                    logger.info(f"Successfully decoded preprocessed barcode '{barcode_str}'")
                    return barcode_str
    except Exception as err:
        logger.debug(f"Preprocessed pyzbar decode failed: {err}")

    # Step 3: Try OpenCV fallback decoding if available
    try:
        import cv2
        import numpy as np

        np_arr = np.frombuffer(image_bytes, np.uint8)
        cv_img = cv2.imdecode(np_arr, cv2.IMREAD_GRAYSCALE)
        if cv_img is not None:
            barcode_detector = cv2.BarcodeDetector()
            retval, decoded_info, decoded_type, _ = barcode_detector.detectAndDecode(cv_img)
            if retval and decoded_info:
                code = decoded_info[0] if isinstance(decoded_info, (list, tuple)) else decoded_info
                if code and len(code) >= 8:
                    logger.info(f"OpenCV barcode detector found code '{code}'")
                    return str(code).strip()
    except Exception as cv_err:
        logger.debug(f"OpenCV barcode decode attempt failed: {cv_err}")

    logger.warning("No valid barcode found in uploaded image.")
    return None
