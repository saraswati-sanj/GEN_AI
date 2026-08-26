# 🚀 Deploying NutriLens AI to Render (Step-by-Step Guide)

This guide walks you through deploying the **NutriLens AI** application to [Render](https://render.com) for 100% free cloud hosting.

---

## 📋 Prerequisites
1. A free account on [Render.com](https://render.com).
2. A free [Google AI Studio Gemini API Key](https://aistudio.google.com/app/apikey).
3. Your NutriLens AI repository pushed to GitHub.

---

## 🌟 Method 1: Deploy via Render Blueprint (`render.yaml`) — Recommended (1-Click)

The repository includes a pre-configured `render.yaml` Blueprint file that automates the entire service creation and container build.

### Steps:
1. **Push your latest code to GitHub**:
   ```bash
   git add .
   git commit -m "Add authentication system and Render deployment config"
   git push origin main
   ```
2. Open your [Render Dashboard](https://dashboard.render.com/).
3. Click the **"New +"** button in the top right and select **"Blueprint"**.
4. Connect your GitHub repository (`nutrilens-ai`).
5. Render will automatically detect `render.yaml` and parse the Web Service configuration.
6. In the environment variable prompt, enter your `GEMINI_API_KEY`:
   - `GEMINI_API_KEY`: `AIzaSy...` (your Google Gemini API Key)
7. Click **"Apply"**.
8. Render will build the Docker container and start your live instance at `https://nutrilens-ai-xxxx.onrender.com`.

---

## 🛠️ Method 2: Manual Web Service Setup (Docker)

If you prefer setting up the Web Service manually from the Render Dashboard:

### Steps:
1. Go to [Render Dashboard](https://dashboard.render.com/) -> Click **"New +"** -> **"Web Service"**.
2. Select **"Build and deploy from a Git repository"** and select your repository.
3. Configure the service settings:
   - **Name**: `nutrilens-ai`
   - **Language / Runtime**: `Docker`
   - **Branch**: `main` (or `master`)
   - **Dockerfile Path**: `./Dockerfile`
   - **Docker Build Context**: `.`
   - **Instance Type**: `Free`
4. Expand **"Advanced"** / **"Environment Variables"** and add:
   | Key | Value | Description |
   |-----|-------|-------------|
   | `GEMINI_API_KEY` | `AIzaSy...` | Your Gemini API Key (**Required**) |
   | `GEMINI_MODEL` | `gemini-1.5-flash` | Gemini model name |
   | `SECRET_KEY` | `your-secure-random-string-32-chars` | Key for JWT tokens |
   | `DATABASE_URL` | `sqlite+aiosqlite:///./nutrilens.db` | Local SQLite database |
   | `EMBEDDING_MODEL` | `BAAI/bge-small-en-v1.5` | Embedding model |
   | `CHROMA_PERSIST_DIR` | `./chroma_db` | Chroma vector database directory |
5. **Health Check Path**: `/api/v1/health`
6. Click **"Create Web Service"**.

---

## 🔍 Verification & Health Check

Once deployment finishes, Render will provide a public URL (e.g. `https://nutrilens-ai.onrender.com`).

1. **Verify Backend Health**:
   Visit `https://nutrilens-ai.onrender.com/api/v1/health` in your browser.
   You should see:
   ```json
   {
     "status": "healthy",
     "app": "NutriLens AI",
     "version": "1.0.0",
     "chroma_chunks": 16
   }
   ```

2. **Verify Interactive API Docs**:
   Visit `https://nutrilens-ai.onrender.com/docs` to test interactive Swagger API documentation.

3. **Verify Frontend UI**:
   Visit `https://nutrilens-ai.onrender.com/` to use the live NutriLens AI barcode scanner, sign in/sign up, and analyze food products in English, Hindi, Kannada, and Tamil!

---

## 💡 Troubleshooting
- **Free Tier Cold Starts**: Render's free tier spins down instances after 15 minutes of inactivity. The first request may take 30-50 seconds to boot up.
- **Missing Gemini Key**: If scans fail with an authentication error, verify `GEMINI_API_KEY` under the **Environment** tab in your Render service settings.
- **Port Binding**: The app automatically uses the dynamic `$PORT` variable provided by Render.
