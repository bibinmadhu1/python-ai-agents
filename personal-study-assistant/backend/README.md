cd personal-study-assistant
cd backend
cp .env.example .env
# edit .env, set OPENAI_API_KEY or GOOGLE_APPLICATION_CREDENTIALS
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

===============================================

Deploy to Google Cloud (simple Cloud Run flow)
Prereqs: gcloud CLI, billing enabled, project selected.
Backend (Cloud Run)
Build and push Docker image to Artifact Registry or Container Registry.
cd backend
gcloud builds submit --tag gcr.io/PROJECT_ID/personal-study-backend:latest
gcloud run deploy personal-study-backend
--image gcr.io/PROJECT_ID/personal-study-backend:latest
--region=us-central1 --platform=managed --allow-unauthenticated
--set-env-vars AI_PROVIDER=openai,OPENAI_API_KEY=YOUR_KEY