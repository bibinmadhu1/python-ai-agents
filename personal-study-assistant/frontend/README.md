Run locally
cd personal-study-assistant
cd frontend
npm install
npm run dev -- --host


===============================================
Frontend (static) — option A: Cloud Run
Build frontend static files
cd frontend
npm install
npm run build
Serve with a small static server container or host on Firebase Hosting / Cloud Storage. Easiest for
demos: use Firebase Hosting.
Frontend (Firebase Hosting) — option B (recommended for static websites)
Install Firebase CLI and initialize hosting in the frontend/dist folder.
firebase deploy --project PROJECT_ID

8
Environment & Secrets
For Cloud Run set environment variables (OPENAI_API_KEY) via --set-env-vars or use Secret
Manager.
For Google Gemini use a service account and set GOOGLE_APPLICATION_CREDENTIALS in Cloud
Run or configure the library accordingly.
