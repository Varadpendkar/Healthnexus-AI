# Healthnexus AI - Backend

Flask backend API for insurance plan recommendations powered by LightGBM ML model.

## Features

- ✅ ML-powered plan recommendations
- ✅ User authentication (JWT)
- ✅ CORS-enabled for React frontend
- ✅ RESTful API endpoints
- ✅ SQLite database

## Installation

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

## Running the Server

```bash
python app.py
```

Server will start at `http://localhost:5000`

## API Endpoints

### Health Check

```
GET /api/health
```

### Authentication

```
POST /api/auth/register
POST /api/auth/login
```

### Recommendations

```
POST /api/recommendations
GET /api/plans/<plan_id>
POST /api/plans/save (requires auth)
GET /api/plans/saved (requires auth)
```

## Example Request

```bash
curl -X POST http://localhost:5000/api/recommendations \
  -H "Content-Type: application/json" \
  -d '{
    "age": 30,
    "annual_income": 800000,
    "has_diabetes": true,
    "coverage_amount": 500000,
    "limit": 8
  }'
```
