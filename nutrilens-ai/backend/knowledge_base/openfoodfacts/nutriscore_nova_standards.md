# OpenFoodFacts Nutri-Score V2 and NOVA Food Classification Framework

## 1. Nutri-Score V2 Calculation Algorithm
Nutri-Score is a 5-color logo (A, B, C, D, E) that rates the nutritional quality of food products from A (dark green - highest nutritional quality) to E (dark orange - lowest nutritional quality).

### Positive Points (N Points - Negative Nutrients to minimize):
Evaluates content per 100g/100ml:
1. **Energy**: Points 0 to 10 (higher energy = more points).
2. **Sugars**: Points 0 to 15 (higher sugars = more points).
3. **Saturated Fatty Acids**: Points 0 to 10.
4. **Sodium**: Points 0 to 20 (higher sodium = more points).

### Negative Points (P Points - Positive Nutrients to encourage):
Evaluates content per 100g/100ml:
1. **Fruits, Vegetables, Legumes, Nuts, Olive/Rapeseed oils**: Points 0 to 5.
2. **Fibers**: Points 0 to 5.
3. **Proteins**: Points 0 to 7.

### Final Score Calculation:
- **Final Score = N Points - P Points** (for standard solid foods).
- Lower final scores represent healthier products.
  - **Class A**: Score ≤ -1 (Dark Green - Excellent profile)
  - **Class B**: Score 0 to 2 (Light Green - Good profile)
  - **Class C**: Score 3 to 10 (Yellow - Moderate profile)
  - **Class D**: Score 11 to 18 (Orange - Poor profile)
  - **Class E**: Score ≥ 19 (Dark Orange - Very poor profile)

---

## 2. NOVA Ultra-Processed Food Classification System
Developed by researchers at the University of São Paulo, NOVA groups foods according to the extent and purpose of industrial processing:

### NOVA Group 1 — Unprocessed or Minimally Processed Foods
- Fresh fruits, vegetables, grains, legumes, meat, poultry, milk, eggs, natural spices.
- Processes include washing, grinding, chilling, pasteurization, freezing without added ingredients.

### NOVA Group 2 — Processed Culinary Ingredients
- Direct extractions: Oils, butter, sugar, salt, vinegar.
- Used in kitchens to season and prepare Group 1 foods.

### NOVA Group 3 — Processed Foods
- Simple products made by adding Group 2 ingredients (salt, oil, sugar) to Group 1 foods.
- Examples: Canned vegetables, salted nuts, artisanal cheeses, freshly baked breads.

### NOVA Group 4 — Ultra-Processed Foods (UPF)
- Formulations of substances derived from foods plus cosmetic additives (emulsifiers, colorants, artificial flavors, high fructose corn syrup, hydrogenated oils).
- Examples: Carbonated soft drinks, packaged instant noodles, potato chips, mass-produced packaged snacks, confectioneries, nuggets, energy drinks.
- Health Risk: UPFs are linked to metabolic syndrome, obesity, gut dysbiosis, cardiovascular mortality, and hyper-palatability leading to overconsumption.
