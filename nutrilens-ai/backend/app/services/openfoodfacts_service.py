"""
NutriLens AI — OpenFoodFacts API Integration Service
Retrieves comprehensive nutritional data, ingredients, allergens, and INS additives by barcode.
"""
import logging
from typing import Optional, Dict, Any

import httpx

from app.core.config import settings
from app.models.schemas import ProductData, NutrimentValues

logger = logging.getLogger("nutrilens.openfoodfacts")

# Fallback rich sample database for common product barcodes (instant response guarantee)
SAMPLE_PRODUCTS: Dict[str, Dict[str, Any]] = {
    "8901058852309": {
        "barcode": "8901058852309",
        "product_name": "Maggi 2-Minute Masala Noodles",
        "brand": "Nestlé",
        "categories": "Noodles, Instant Noodles, Wheat Noodles",
        "ingredients_text": "Refined wheat flour (Maida), Palm oil, Salt, Wheat gluten, Mineral (Calcium carbonate), Thickeners (INS 508, INS 412), Acidity regulators (INS 501(i), INS 500(i), INS 330). Noodle Powder/Masala Mix: Hydrolysed groundnut protein, Mixed spices (Dehydrated onion, Coriander powder, Chili powder, Turmeric powder, Cumin powder, Aniseed, Black pepper, Fenugreek, Ginger, Nutmeg, Clove), Sugar, Noodle powder, Edible starch, Salt, Palm oil, Flavor enhancer (INS 635), Acidity regulator (INS 330), Color (INS 150d).",
        "nutriments": {
            "energy_kcal_100g": 427.0,
            "fat_100g": 15.7,
            "saturated_fat_100g": 6.8,
            "carbohydrates_100g": 63.5,
            "sugars_100g": 2.2,
            "fiber_100g": 3.6,
            "proteins_100g": 8.0,
            "salt_100g": 2.9,
            "sodium_100g": 1.16,
        },
        "allergens": ["Gluten", "Peanuts (Groundnut)"],
        "traces": ["Soy", "Milk"],
        "additives": ["INS 508", "INS 412", "INS 501(i)", "INS 500(i)", "INS 330", "INS 635", "INS 150d"],
        "nutri_score": "D",
        "nova_group": 4,
        "image_url": "https://images.openfoodfacts.org/images/products/890/105/885/2309/front_en.11.400.jpg",
        "found": True,
    },
    "5449000000996": {
        "barcode": "5449000000996",
        "product_name": "Coca-Cola Original Taste",
        "brand": "The Coca-Cola Company",
        "categories": "Beverages, Carbonated Drinks, Soft Drinks, Colas",
        "ingredients_text": "Carbonated water, Sugar (High Fructose Corn Syrup / Sucrose), Color (Caramel E150d / INS 150d), Acidulant (Phosphoric acid INS 338), Natural flavors, Caffeine.",
        "nutriments": {
            "energy_kcal_100g": 42.0,
            "fat_100g": 0.0,
            "saturated_fat_100g": 0.0,
            "carbohydrates_100g": 10.6,
            "sugars_100g": 10.6,
            "fiber_100g": 0.0,
            "proteins_100g": 0.0,
            "salt_100g": 0.01,
            "sodium_100g": 0.004,
        },
        "allergens": [],
        "traces": [],
        "additives": ["INS 150d", "INS 338", "Caffeine"],
        "nutri_score": "E",
        "nova_group": 4,
        "image_url": "https://images.openfoodfacts.org/images/products/544/900/000/0996/front_en.693.400.jpg",
        "found": True,
    },
    "8901491101837": {
        "barcode": "8901491101837",
        "product_name": "Kurkure Masala Munch",
        "brand": "PepsiCo India",
        "categories": "Snacks, Salty Snacks, Corn Snacks, Extruded Crisps",
        "ingredients_text": "Rice meal (42.8%), Edible vegetable oil (Palmolein), Corn meal (19.8%), Gram meal (3.3%), Spices and Condiments (Onion powder, Chili powder, Amchur, Coriander powder, Garlic powder, Ginger powder, Black pepper powder, Turmeric powder, Cumin), Salt, Sugar, Black salt, Acidity regulators (INS 330, INS 296), Flavor enhancers (INS 627, INS 631).",
        "nutriments": {
            "energy_kcal_100g": 558.0,
            "fat_100g": 34.5,
            "saturated_fat_100g": 15.6,
            "carbohydrates_100g": 54.2,
            "sugars_100g": 2.5,
            "fiber_100g": 1.8,
            "proteins_100g": 5.8,
            "salt_100g": 2.1,
            "sodium_100g": 0.84,
        },
        "allergens": [],
        "traces": ["Wheat", "Soy", "Milk"],
        "additives": ["INS 330", "INS 296", "INS 627", "INS 631"],
        "nutri_score": "E",
        "nova_group": 4,
        "image_url": "https://images.openfoodfacts.org/images/products/890/149/110/1837/front_en.12.400.jpg",
        "found": True,
    },
    "8901262010054": {
        "barcode": "8901262010054",
        "product_name": "Amul Pasteurised Butter",
        "brand": "Amul (GCMMF)",
        "categories": "Dairies, Fats, Spreads, Butter, Salted Butter",
        "ingredients_text": "Butter (made from Cow/Buffalo milk fat), Common salt (2.5%), Annatto color (INS 160b).",
        "nutriments": {
            "energy_kcal_100g": 722.0,
            "fat_100g": 80.0,
            "saturated_fat_100g": 51.0,
            "carbohydrates_100g": 0.0,
            "sugars_100g": 0.0,
            "fiber_100g": 0.0,
            "proteins_100g": 0.6,
            "salt_100g": 2.5,
            "sodium_100g": 1.0,
        },
        "allergens": ["Milk"],
        "traces": [],
        "additives": ["INS 160b"],
        "nutri_score": "E",
        "nova_group": 3,
        "image_url": "https://images.openfoodfacts.org/images/products/890/126/201/0054/front_en.16.400.jpg",
        "found": True,
    },
    "3017620422003": {
        "barcode": "3017620422003",
        "product_name": "Nutella Hazelnut Spread with Cocoa",
        "brand": "Ferrero",
        "categories": "Sweet Spreads, Chocolate Spreads, Hazelnut Spreads",
        "ingredients_text": "Sugar, Palm oil, Hazelnuts (13%), Skimmed milk powder (8.7%), Fat-reduced cocoa powder (7.4%), Emulsifier: Lecithins (Soy) (INS 322i), Vanillin (artificial flavor).",
        "nutriments": {
            "energy_kcal_100g": 539.0,
            "fat_100g": 30.9,
            "saturated_fat_100g": 10.6,
            "carbohydrates_100g": 57.5,
            "sugars_100g": 56.3,
            "fiber_100g": 3.0,
            "proteins_100g": 6.3,
            "salt_100g": 0.107,
            "sodium_100g": 0.043,
        },
        "allergens": ["Tree Nuts (Hazelnuts)", "Milk", "Soy"],
        "traces": [],
        "additives": ["INS 322i"],
        "nutri_score": "E",
        "nova_group": 4,
        "image_url": "https://images.openfoodfacts.org/images/products/301/762/042/2003/front_en.547.400.jpg",
        "found": True,
    },
    "8901607000184": {
        "barcode": "8901607000184",
        "product_name": "Quaker Oats Rolled Wholegrain",
        "brand": "Quaker (PepsiCo)",
        "categories": "Cereals, Breakfast Cereals, Rolled Oats, Wholegrain Cereals",
        "ingredients_text": "100% Whole grain rolled oats.",
        "nutriments": {
            "energy_kcal_100g": 407.0,
            "fat_100g": 8.0,
            "saturated_fat_100g": 1.6,
            "carbohydrates_100g": 67.0,
            "sugars_100g": 0.5,
            "fiber_100g": 10.2,
            "proteins_100g": 11.8,
            "salt_100g": 0.01,
            "sodium_100g": 0.004,
        },
        "allergens": ["Oats"],
        "traces": ["Wheat", "Barley"],
        "additives": [],
        "nutri_score": "A",
        "nova_group": 1,
        "image_url": "https://images.openfoodfacts.org/images/products/890/160/700/0184/front_en.6.400.jpg",
        "found": True,
    }
}


async def fetch_product_by_barcode(barcode: str) -> ProductData:
    """
    Fetch product details from OpenFoodFacts REST API.
    Falls back to pre-seeded sample product dictionary if API is unreachable or barcode matches sample.
    """
    clean_barcode = str(barcode).strip()

    # Check local sample lookup first for speed and offline testing
    if clean_barcode in SAMPLE_PRODUCTS:
        logger.info(f"Retrieved sample product for barcode '{clean_barcode}'")
        raw = SAMPLE_PRODUCTS[clean_barcode]
        return ProductData(
            barcode=raw["barcode"],
            product_name=raw["product_name"],
            brand=raw["brand"],
            categories=raw["categories"],
            ingredients_text=raw["ingredients_text"],
            nutriments=NutrimentValues(**raw["nutriments"]),
            allergens=raw["allergens"],
            traces=raw["traces"],
            additives=raw["additives"],
            nutri_score=raw["nutri_score"],
            nova_group=raw["nova_group"],
            image_url=raw["image_url"],
            found=True,
        )

    # Call OpenFoodFacts API
    url = f"{settings.OFF_BASE_URL}/{clean_barcode}.json"
    headers = {"User-Agent": settings.OFF_USER_AGENT}

    try:
        async with httpx.AsyncClient(timeout=10.0, follow_redirects=True) as client:
            resp = await client.get(url, headers=headers)
            if resp.status_code == 200:
                data = resp.json()
                if data.get("status") == 1 and "product" in data:
                    p = data["product"]
                    
                    # Extract nutriments
                    n_raw = p.get("nutriments", {})
                    nutriments = NutrimentValues(
                        energy_kcal_100g=n_raw.get("energy-kcal_100g") or n_raw.get("energy_100g"),
                        fat_100g=n_raw.get("fat_100g"),
                        saturated_fat_100g=n_raw.get("saturated-fat_100g"),
                        carbohydrates_100g=n_raw.get("carbohydrates_100g"),
                        sugars_100g=n_raw.get("sugars_100g"),
                        fiber_100g=n_raw.get("fiber_100g"),
                        proteins_100g=n_raw.get("proteins_100g"),
                        salt_100g=n_raw.get("salt_100g"),
                        sodium_100g=n_raw.get("sodium_100g"),
                    )

                    # Extract allergens & additives
                    allergens_raw = p.get("allergens_tags", []) or p.get("allergens", "")
                    allergens = [a.replace("en:", "").replace("hi:", "").title() for a in (allergens_raw if isinstance(allergens_raw, list) else allergens_raw.split(",")) if a]
                    
                    additives_raw = p.get("additives_tags", [])
                    additives = [ad.replace("en:", "").upper() for ad in additives_raw if ad]

                    # Extract images
                    img = p.get("image_front_url") or p.get("image_url") or p.get("image_small_url")

                    return ProductData(
                        barcode=clean_barcode,
                        product_name=p.get("product_name") or p.get("product_name_en") or p.get("product_name_hi") or "Unknown Product",
                        brand=p.get("brands") or "Unknown Brand",
                        categories=p.get("categories") or p.get("main_category"),
                        ingredients_text=p.get("ingredients_text") or p.get("ingredients_text_en") or "Ingredients unavailable",
                        nutriments=nutriments,
                        allergens=allergens,
                        traces=[],
                        additives=additives,
                        nutri_score=(p.get("nutriscore_grade") or "").upper() or None,
                        nova_group=p.get("nova_group"),
                        image_url=img,
                        found=True,
                    )

    except Exception as e:
        logger.error(f"Error querying OpenFoodFacts API for barcode {clean_barcode}: {e}")

    # If product not found in OFF API, return basic metadata shell
    return ProductData(
        barcode=clean_barcode,
        product_name=f"Food Product #{clean_barcode}",
        brand="Unknown",
        categories="Packaged Food",
        ingredients_text="Ingredients not listed in OpenFoodFacts database.",
        nutriments=NutrimentValues(),
        allergens=[],
        traces=[],
        additives=[],
        nutri_score=None,
        nova_group=None,
        image_url=None,
        found=False,
    )
