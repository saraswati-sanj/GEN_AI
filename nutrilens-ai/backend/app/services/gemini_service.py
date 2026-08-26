"""
NutriLens AI — Gemini Generative AI RAG Analysis Service
Combines product details, user health profiles, and ChromaDB scientific evidence
to generate personalized food health evaluations in JSON format across 4 languages.
"""
import json
import logging
from typing import Dict, Any, List, Optional

import google.generativeai as genai

from app.core.config import settings
from app.models.schemas import ProductData, GeminiAnalysis
from app.services.vector_store import vector_store

logger = logging.getLogger("nutrilens.gemini")

LANGUAGE_NAMES = {
    "en": "English",
    "hi": "Hindi (हिंदी)",
    "kn": "Kannada (ಕನ್ನಡ)",
    "ta": "Tamil (தமிழ்)"
}


def construct_prompt(
    product: ProductData,
    user_profile: Dict[str, Any],
    retrieved_docs: List[Dict[str, Any]],
    language: str = "en"
) -> str:
    """Build a detailed system and context prompt for Gemini."""
    
    lang_name = LANGUAGE_NAMES.get(language, "English")

    docs_text = "\n\n".join([
        f"--- SCIENTIFIC REFERENCE [{doc['metadata'].get('category', 'REGULATION').upper()}] ---\n{doc['content']}"
        for doc in retrieved_docs
    ]) if retrieved_docs else "No specific regulatory documents found."

    prompt = f"""
You are NutriLens AI, an expert clinical nutritionist, food regulatory auditor, and biochemical safety researcher.
Evaluate the following packaged food product using trusted scientific guidelines (FSSAI, WHO, ICMR 2024, USDA, PubMed).

================================================================================
PRODUCT INFORMATION
================================================================================
Product Name: {product.product_name}
Brand: {product.brand}
Category: {product.categories or 'Packaged Food'}
Ingredients List: {product.ingredients_text or 'Not specified'}
Nutri-Score: {product.nutri_score or 'Unrated'}
NOVA Group: {product.nova_group or 'Unclassified'} (1: Minimally Processed, 4: Ultra-Processed)

NUTRITIONAL FACTS (per 100g / 100ml):
- Energy: {product.nutriments.energy_kcal_100g or 'N/A'} kcal
- Fat: {product.nutriments.fat_100g or 'N/A'} g (Saturated Fat: {product.nutriments.saturated_fat_100g or 'N/A'} g)
- Carbohydrates: {product.nutriments.carbohydrates_100g or 'N/A'} g (Sugars: {product.nutriments.sugars_100g or 'N/A'} g)
- Dietary Fiber: {product.nutriments.fiber_100g or 'N/A'} g
- Proteins: {product.nutriments.proteins_100g or 'N/A'} g
- Salt: {product.nutriments.salt_100g or 'N/A'} g
- Sodium: {product.nutriments.sodium_100g or 'N/A'} g

Declared Allergens: {', '.join(product.allergens) if product.allergens else 'None declared'}
INS Additive Codes: {', '.join(product.additives) if product.additives else 'None listed'}

================================================================================
USER HEALTH PROFILE
================================================================================
Age: {user_profile.get('age', 'Not specified')}
Health Conditions:
- Diabetes: {user_profile.get('health_conditions', {}).get('diabetes', False)}
- Hypertension (High BP): {user_profile.get('health_conditions', {}).get('hypertension', False)}
- Chronic Kidney Disease (CKD): {user_profile.get('health_conditions', {}).get('kidney_disease', False)}
- Pregnancy: {user_profile.get('health_conditions', {}).get('pregnancy', False)}
- Heart Disease: {user_profile.get('health_conditions', {}).get('heart_disease', False)}
- Obesity: {user_profile.get('health_conditions', {}).get('obesity', False)}
- Celiac Disease: {user_profile.get('health_conditions', {}).get('celiac_disease', False)}
Allergies: {', '.join(user_profile.get('allergies', [])) if user_profile.get('allergies') else 'None'}

================================================================================
RETRIEVED REGULATORY & SCIENTIFIC EVIDENCE (RAG CONTEXT)
================================================================================
{docs_text}

================================================================================
INSTRUCTIONS & OUTPUT SPECIFICATION
================================================================================
1. Respond in **{lang_name}** language. Ensure technical clarity, accuracy, and natural tone.
2. Return ONLY a single, valid JSON object strictly matching this structure without markdown backticks:

{{
  "product_summary": {{
    "title": "Product Title",
    "verdict": "High Risk | Moderate Risk | Healthy Choice",
    "brief": "Concise summary of product profile"
  }},
  "ingredient_explanations": [
    {{
      "name": "Ingredient Name",
      "purpose": "Purpose in product (e.g. preservative, sweetener, binder)",
      "safety_level": "safe | moderate_concern | high_concern",
      "notes": "Health effect details"
    }}
  ],
  "nutrition_summary": {{
    "calories_per_100g": {product.nutriments.energy_kcal_100g or 0},
    "macros_summary": "High in carbohydrates, high in saturated fats",
    "sugar_level": "low | moderate | high",
    "sodium_level": "low | moderate | high",
    "fat_level": "low | moderate | high",
    "fiber_adequacy": "poor | moderate | good",
    "overall_nutrition_rating": "Poor | Fair | Excellent"
  }},
  "health_risk_assessment": [
    {{
      "condition": "Diabetes / BP / Kidney / Pregnancy / General",
      "risk_level": "low | moderate | high",
      "explanation": "Specific physiological risk based on user profile and product contents"
    }}
  ],
  "harmful_ingredients": [
    {{
      "ingredient": "Name of harmful ingredient",
      "reason_for_harm": "Why it is detrimental to health"
    }}
  ],
  "additive_explanations": [
    {{
      "ins_code": "INS XXX or E-Number",
      "name": "Additive Name",
      "function": "Emulsifier / Preservative / Color",
      "safety_status": "Safe | Restricted | Flagged",
      "daily_limit": "ADI limit if applicable",
      "concerns": "Health concern"
    }}
  ],
  "fssai_guideline_summary": "Summary of compliance with FSSAI HFSS limits and labelling norms.",
  "personalized_recommendations": [
    "Actionable personal advice based on user health conditions"
  ],
  "better_alternatives": [
    {{
      "name": "Healthier product alternative",
      "reason": "Why it is better",
      "healthier_aspects": ["Lower sugar", "No artificial colors"]
    }}
  ],
  "overall_health_score": 42,  // Int between 0 (Unhealthy) and 100 (Optimal)
  "daily_consumption_advice": "Avoid completely | Limit to once a month | Occasional snack (<1x/week) | Safe for daily intake",
  "language": "{language}"
}}
"""
    return prompt


def generate_heuristic_fallback_analysis(
    product: ProductData,
    user_profile: Dict[str, Any],
    language: str = "en"
) -> GeminiAnalysis:
    """Generate structured rule-based health analysis if Gemini API is unconfigured."""
    
    sugars = product.nutriments.sugars_100g or 0.0
    sodium = product.nutriments.sodium_100g or ((product.nutriments.salt_100g or 0) / 2.5)
    sat_fat = product.nutriments.saturated_fat_100g or 0.0
    nova = product.nova_group or 3

    # Calculate overall score baseline
    score = 100
    if sugars > 10.0: score -= 25
    if sodium > 0.4: score -= 25
    if sat_fat > 5.0: score -= 20
    if nova == 4: score -= 15
    if len(product.additives) > 3: score -= 10
    score = max(5, min(95, score))

    is_diabetic = user_profile.get("health_conditions", {}).get("diabetes", False)
    is_hypertensive = user_profile.get("health_conditions", {}).get("hypertension", False)

    risks = []
    if is_diabetic and sugars > 5.0:
        risks.append({
            "condition": "Diabetes Mellitus",
            "risk_level": "high",
            "explanation": f"Contains {sugars}g sugar per 100g, which can cause rapid postprandial blood glucose spikes."
        })
    if is_hypertensive and sodium > 0.35:
        risks.append({
            "condition": "Hypertension",
            "risk_level": "high",
            "explanation": f"Contains high sodium level ({round(sodium*1000, 1)} mg/100g), exceeding FSSAI recommended single-serving thresholds."
        })
    if not risks:
        risks.append({
            "condition": "General Population",
            "risk_level": "moderate" if score < 60 else "low",
            "explanation": "Processed food product. Consume in moderation in accordance with ICMR dietary guidelines."
        })

    harmful = []
    if sugars > 15.0:
        harmful.append({"ingredient": "High Added Sugar", "reason_for_harm": "Elevated risk of insulin resistance, dental caries, and fatty liver disease."})
    if "INS 621" in product.additives or "MSG" in (product.ingredients_text or ""):
        harmful.append({"ingredient": "Monosodium Glutamate (INS 621)", "reason_for_harm": "Flavor enhancer associated with dietary overconsumption and sensitive neuro-flushing."})
    if "INS 150d" in product.additives:
        harmful.append({"ingredient": "Caramel IV (INS 150d)", "reason_for_harm": "Synthetic caramel color containing 4-MEI process contaminants."})

    return GeminiAnalysis(
        product_summary={
            "title": product.product_name,
            "verdict": "High Risk" if score < 45 else ("Moderate Concern" if score < 75 else "Healthy Choice"),
            "brief": f"{product.brand} {product.product_name} evaluated against FSSAI & ICMR dietary guidelines."
        },
        ingredient_explanations=[
            {
                "name": "Main Ingredients",
                "purpose": "Primary food matrix",
                "safety_level": "safe" if score > 70 else "moderate_concern",
                "notes": product.ingredients_text[:200] if product.ingredients_text else "Ingredients evaluated."
            }
        ],
        nutrition_summary={
            "calories_per_100g": product.nutriments.energy_kcal_100g or 0.0,
            "macros_summary": f"Carbs: {product.nutriments.carbohydrates_100g or 0}g, Fat: {product.nutriments.fat_100g or 0}g, Protein: {product.nutriments.proteins_100g or 0}g",
            "sugar_level": "high" if sugars > 10 else ("moderate" if sugars > 4 else "low"),
            "sodium_level": "high" if sodium > 0.4 else ("moderate" if sodium > 0.15 else "low"),
            "fat_level": "high" if sat_fat > 5 else "low",
            "fiber_adequacy": "good" if (product.nutriments.fiber_100g or 0) > 4 else "poor",
            "overall_nutrition_rating": "Poor" if score < 50 else ("Fair" if score < 75 else "Good")
        },
        health_risk_assessment=risks,
        harmful_ingredients=harmful if harmful else [{"ingredient": "Ultra-Processed Matrix", "reason_for_harm": "Industrial processing reduces natural micronutrient bioavailability."}],
        additive_explanations=[
            {
                "ins_code": add,
                "name": f"Additive {add}",
                "function": "Preservative / Texture / Color",
                "safety_status": "Restricted" if "150d" in add or "621" in add else "Permitted",
                "daily_limit": "FSSAI Permitted limit",
                "concerns": "Monitor cumulative daily intake."
            }
            for add in product.additives[:4]
        ],
        fssai_guideline_summary=f"FSSAI HFSS Evaluation: Saturated fat {sat_fat}g/100g, Sugars {sugars}g/100g, Sodium {round(sodium*1000, 1)}mg/100g.",
        personalized_recommendations=[
            "Check total daily sodium and added sugar intake across all meals.",
            "Combine with fiber-rich fresh salads or vegetables to lower glycemic response."
        ],
        better_alternatives=[
            {
                "name": "Whole food / Minimally processed alternative",
                "reason": "Provides unrefined nutrients without synthetic INS food additives.",
                "healthier_aspects": ["Zero added sugars", "Higher dietary fiber", "No synthetic colors"]
            }
        ],
        overall_health_score=score,
        daily_consumption_advice="Avoid completely" if score < 30 else ("Occasional snack (<1x/week)" if score < 60 else "Safe for regular intake"),
        language=language
    )


async def analyze_product_with_gemini(
    product: ProductData,
    user_profile: Dict[str, Any],
    language: str = "en"
) -> GeminiAnalysis:
    """
    Perform RAG retrieval from ChromaDB and generate structured health analysis using Gemini LLM.
    """
    # 1. Retrieve scientific RAG context from ChromaDB
    query_terms = f"{product.product_name} {product.categories} {product.ingredients_text} {' '.join(product.additives)}"
    retrieved_docs = []
    try:
        retrieved_docs = vector_store.search(query_terms, top_k=4)
        logger.info(f"Retrieved {len(retrieved_docs)} vector context documents from ChromaDB.")
    except Exception as err:
        logger.warning(f"ChromaDB search failed: {err}")

    # 2. Check Gemini API key availability
    api_key = settings.GEMINI_API_KEY
    if not api_key or api_key.startswith("your_"):
        logger.warning("No valid GEMINI_API_KEY set. Falling back to heuristic rule-based AI engine.")
        return generate_heuristic_fallback_analysis(product, user_profile, language)

    # 3. Call Gemini LLM API
    try:
        genai.configure(api_key=api_key)
        model_name = settings.GEMINI_MODEL or "gemini-1.5-flash"
        model = genai.GenerativeModel(model_name)

        prompt = construct_prompt(product, user_profile, retrieved_docs, language)
        
        response = model.generate_content(
            prompt,
            generation_config={"response_mime_type": "application/json", "temperature": 0.2}
        )

        raw_text = response.text.strip()
        # Clean markdown wrappers if present
        if raw_text.startswith("```json"):
            raw_text = raw_text[7:]
        if raw_text.startswith("```"):
            raw_text = raw_text[3:]
        if raw_text.endswith("```"):
            raw_text = raw_text[:-3]

        parsed = json.loads(raw_text.strip())
        return GeminiAnalysis(**parsed)

    except Exception as e:
        logger.error(f"Gemini API invocation error: {e}. Utilizing fallback engine.")
        return generate_heuristic_fallback_analysis(product, user_profile, language)
