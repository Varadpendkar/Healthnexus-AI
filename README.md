# Healthnexus AI

Healthnexus AI is an AI-assisted health insurance platform for:

- Plan recommendations
- Bill analysis (Bill Buster)
- Pre-authorization estimation
- Insurance guidance chatbot

## Verified Runtime Status (April 8, 2026)

The project was run and validated in this workspace.

- ✅ Backend started successfully on `http://localhost:5001`
- ✅ Frontend started successfully on `http://localhost:3000`
- ✅ Health endpoint responded: `GET /api/health`
- ⚠️ PMSBY live source currently falls back to internal plans in this environment (upstream API returns HTTP 400)

## Project Structure

- `backend/` — Flask API, ML ranking, chatbot, bill/pre-auth services
- `frontend/` — React + TypeScript UI
- `shared/` — shared models/data/uploads/index assets
- `outputs/` — generated reports/logs/results
- `.env` — root environment configuration

## Prerequisites

- Python 3.10+
- Node.js 18+ and npm

## Run the Project

### 1) Backend

#### Option A: Standard setup (recommended for new machines)

```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python app.py
```

Backend URL: `http://localhost:5001`

#### Option B: Workspace-verified interpreter

In this workspace, backend was successfully started using:

```bash
cd backend
'/Volumes/Sandisk 128/Work/Final Year Project /project/AImedenv/bin/python' app.py
```

### 2) Frontend

Open a second terminal:

```bash
cd frontend
npm install
npm start
```

Frontend URL: `http://localhost:3000`

## Quick Smoke Checks

### Backend health

```bash
curl http://127.0.0.1:5001/api/health
```

### PMSBY plans route

```bash
curl 'http://127.0.0.1:5001/api/platforms/plans?source=pmsby&limit=3'
```

Expected behavior in this environment right now:

- `fallback_used: true`
- `is_live: false`
- `source: internal`

This is graceful fallback behavior when upstream PMSBY API auth is unavailable.

## Environment Notes

Root `.env` includes PMSBY settings:

- `DATA_GOV_IN_BASE_URL`
- `PMSBY_RESOURCE_ID`
- `INSURANCE_CACHE_TTL_SECONDS`
- `INSURANCE_REQUEST_TIMEOUT_SECONDS`

Optional key field:

- `DATA_GOV_IN_API_KEY`

If PMSBY upstream authentication is not accepted, backend automatically serves internal plan data instead of failing the request.

## One-Command Startup (Optional)

From project root:

```bash
./start.sh
```

If needed:

```bash
chmod +x start.sh
./start.sh
```

> Note: backend currently runs on port `5001` (`backend/app.py`).

## Recent Functional Updates (April 2026)

- Recommendation flow is ML-first (single reliable path, optional Groq reranking when configured)
- Get Quote supports Patient Report Upload + Auto-Fill
- Missing profile fields are safely defaulted before ranking
- Chatbot short-query handling improved for insurance terms
- Bill Buster supports async upload/status/result workflow
- Smart Pre-Auth and resource search routes are available
