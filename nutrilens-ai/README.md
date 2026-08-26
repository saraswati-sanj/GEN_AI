# 🥗 NutriLens AI — Generative AI Barcode Health & RAG Risk Assessment Engine

NutriLens AI is an end-to-end Healthcare AI and Nutritional Informatics platform that decodes food product barcodes, retrieves detailed nutritional facts from the global OpenFoodFacts database, executes semantic vector search over clinical and regulatory standards (FSSAI, ICMR 2024, WHO, USDA, PubMed), and generates personalized health risk assessments and scores (0–100) using Google Gemini LLM across **English, Hindi, Kannada, and Tamil**.

---

## 🏛️ Project Architecture

```
nutrilens-ai/
│
├── notebooks/
│   └── NutriLens_AI_Model.ipynb       ← 🧠 CORE AI/ML PIPELINE (Source of Truth)
│
├── backend/
│   ├── app/
│   │   ├── api/v1/endpoints/          ← REST Endpoints (users, scan, history)
│   │   ├── core/                      ← Config, Database (PostgreSQL/SQLite), Security (bcrypt, JWT)
│   │   ├── models/                    ← ORM & Pydantic Schemas
│   │   └── services/                  ← VectorStore, GeminiService, BarcodeDecoder
│   └── main.py                        ← FastAPI Application Entry Point
│
├── frontend/
│   ├── index.html                     ← Master Dashboard & Interactive Scanner
│   ├── login.html                     ← Dedicated Standalone Sign In Page
│   ├── register.html                  ← Dedicated Standalone Sign Up Page
│   ├── dashboard.html                 ← Application Dashboard
│   ├── css/                           ← Glassmorphism Responsive CSS Design System
│   └── js/                            ← Scanner & JWT Auth State Management
│
├── knowledge_base/                    ← 📚 Clinical & Regulatory Documents
│   ├── fssai/                         ← FSSAI Labelling & Additive Regulations (2020)
│   ├── icmr/                          ← ICMR-NIN Dietary Guidelines for Indians (2024)
│   ├── who/                           ← WHO Guidelines on Free Sugars & Trans Fats
│   ├── usda/                          ← USDA Macronutrient & Saturated Fat Limits
│   ├── pubmed/                        ← Peer-Reviewed Studies on Ultra-Processed Additives
│   └── openfoodfacts/                 ← Nutri-Score & NOVA Algorithmic Standards
│
├── models/                            ← Cached / Local Model Artifacts
├── data/                              ← Exported Scans & Evaluation Benchmarks
├── Dockerfile                         ← Container Build Specification for Render
├── render.yaml                        ← 1-Click Render Cloud Deployment Blueprint
├── RENDER_DEPLOY_GUIDE.md             ← Step-by-Step Render Deployment Manual
├── requirements.txt                   ← Python Dependencies
└── README.md                          ← Project Documentation
```

---

## 🧠 Core AI/ML Pipeline (`notebooks/NutriLens_AI_Model.ipynb`)

The primary AI/ML pipeline is fully implemented and demonstrated inside `notebooks/NutriLens_AI_Model.ipynb`:

```
 [Product Barcode / Image]                 [Domain Knowledge Base]
            │                                         │
            ▼ (pyzbar / OpenFoodFacts)                ▼ (FSSAI, ICMR, WHO, USDA, PubMed)
  ┌───────────────────┐                     ┌───────────────────┐
  │   Product Data    │                     │  Markdown Corpus  │
  │ (Ingredients,     │                     └─────────┬─────────┘
  │  Nutrients, NOVA) │                               │ (Text Preprocessing & Overlapping Chunking)
  └─────────┬─────────┘                               ▼
            │                               ┌───────────────────┐
            │                               │ Document Chunks   │
            │                               └─────────┬─────────┘
            │                                         │ (BAAI/bge-small-en-v1.5)
            │                                         ▼
            │                               ┌───────────────────┐
            │                               │ Vector Database   │
            │                               │    (ChromaDB)     │
            │                               └─────────┬─────────┘
            ▼                                         │
  ┌───────────────────┐                               │
  │   User Profile    │                               │
  │ (Conditions,      │                               │
  │  Allergies, Age)  │                               │
  └─────────┬─────────┘                               │
            │                                         │
            ▼ (Dynamic Query Construction)            │
  ┌───────────────────┐                               │
  │ Contextual Query  │───────────────────────────────┤ (HNSW Cosine Vector Search)
  └───────────────────┘                               │
                                                      ▼
                                            ┌───────────────────┐
                                            │ Top-K RAG Context │
                                            └─────────┬─────────┘
                                                      │
                                                      ▼
                                   ┌─────────────────────────────────────┐
                                   │     Gemini Clinical RAG Prompt      │
                                   │ (Product + User Profile + Evidence) │
                                   └──────────────────┬──────────────────┘
                                                      │
                                                      ▼ (google.genai / Gemini 1.5 Flash)
                                   ┌─────────────────────────────────────┐
                                   │ Structured Output (Pydantic Schema) │
                                   │ (Risk Breakdown, Scores, Advice)    │
                                   └──────────────────┬──────────────────┘
                                                      │ (If API failure / offline)
                                                      ▼
                                   ┌─────────────────────────────────────┐
                                   │    Deterministic Fallback Rules     │
                                   └─────────────────────────────────────┘
```

---

## 🌟 Key Features

1. **Standalone Authentication & Personalization**:
   - Dedicated `login.html` and `register.html` pages with direct `bcrypt` password hashing and signed JWT tokens.
   - User profile customization: Age, Diabetes Mellitus, Hypertension, Chronic Kidney Disease (CKD), Pregnancy, Heart Disease, Celiac Disease, and Food Allergies.
   - Persistent scan history synchronized across devices.

2. **Computer Vision Barcode Scanner**:
   - Real-time browser camera stream using ZXing.
   - Uploaded barcode image decoding using `pyzbar` and OpenCV preprocessing.
   - Pre-seeded test sample barcodes (Maggi Noodles, Coca-Cola, Kurkure, Amul Butter, etc.).

3. **OpenFoodFacts Real-Time Integration**:
   - Extracts product names, brands, categories, raw ingredient declarations, energy/sugars/sodium/saturated fats per 100g, Nutri-Score (A–E), and NOVA groups (1–4).

4. **Dense Vector Search (BAAI/bge-small-en-v1.5 & ChromaDB)**:
   - Encodes regulatory documents into 384-dimensional continuous semantic vector representations.
   - Retrieves top-$k$ clinical evidence passages using HNSW cosine similarity.

5. **Clinical Generative AI Evaluation (Google Gemini)**:
   - Produces structured JSON output strictly validated via Pydantic schemas.
   - Computes objective Health Scores (0–100), personalized condition risks, additive warnings, and healthy alternatives in **English, Hindi, Kannada, and Tamil**.

6. **Deterministic Fallback Engine**:
   - Zero-dependency rule-based heuristics based on FSSAI/ICMR thresholds when offline.

---

## 🚀 Quick Start Guide

### 1. Launch Jupyter Notebook (AI/ML Pipeline)
```bash
# Start Jupyter Notebook
jupyter notebook notebooks/NutriLens_AI_Model.ipynb
```

### 2. Launch FastAPI Full-Stack Web Application
```bash
# Navigate to backend directory
cd backend

# Install dependencies
pip install -r requirements.txt

# Start FastAPI server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```
Open your browser at **`http://localhost:8000`** (or `http://localhost:8000/login.html`).

---

## ☁️ Deployment on Render (1-Click)

NutriLens AI is pre-configured for deployment on [Render](https://render.com) using the included `render.yaml` blueprint or Docker container:

1. Push your repository to GitHub.
2. Go to **[Render Dashboard](https://dashboard.render.com)** -> **New +** -> **Blueprint**.
3. Connect your repo, enter your `GEMINI_API_KEY`, and click **Apply**.
4. Full instructions are available in [RENDER_DEPLOY_GUIDE.md](file:///e:/GEN_AI/nutrilens-ai/RENDER_DEPLOY_GUIDE.md).

---

## 📚 Academic Viva Preparation
A 20-question comprehensive academic viva guide covering RAG, BGE embeddings, ChromaDB, inference vs training, and anti-hallucination guardrails is included in **Section 23** of `notebooks/NutriLens_AI_Model.ipynb`.
