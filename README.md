# Healthnexus AI - Smart Health Insurance Recommendation System

**An AI-powered web application that helps users find the perfect health insurance plan based on their personal profile, health conditions, and budget.**

---

## 🚀 Quick Start

### Starting the Servers

The easiest way to start both servers is:

```bash
cd "Healthnexus AI"
./start_server.sh
```

This will automatically start:

- **Backend server** on http://localhost:5001
- **Frontend server** on http://localhost:3000

Then open your browser and go to: **http://localhost:3000**

---

## 📋 Prerequisites

Before running the application, make sure you have:

1. **Python 3.8 or higher**
   - Check: `python3 --version`
2. **Node.js 16 or higher**
   - Check: `node --version`
3. **npm (comes with Node.js)**
   - Check: `npm --version`

---

## 🔧 Installation

### Step 1: Install Backend Dependencies

```bash
# Navigate to the project directory
cd "Healthnexus AI"

# Create a Python virtual environment
python3 -m venv AImedenv

# Activate the virtual environment
source AImedenv/bin/activate

# Install Python packages
pip install -r requirements.txt
```

### Step 2: Install Frontend Dependencies

```bash
# Navigate to the frontend folder
cd frontend

# Install Node.js packages
npm install

# Go back to the main directory
cd ..
```

---

## 🏃 Running the Application

### Option 1: Using the Start Script (Recommended)

```bash
./start_server.sh
```

This script will:

- Start the Flask backend server on port 5001
- Start the React frontend server on port 3000
- Run both in the background

### Option 2: Manual Start (Two Separate Terminals)

**Terminal 1 - Backend:**

```bash
cd "Healthnexus AI"
source AImedenv/bin/activate
python backend/app/main.py
```

**Terminal 2 - Frontend:**

```bash
cd "Healthnexus AI/frontend"
npm start
```

### Stopping the Servers

If you used the start script:

```bash
# Find the process IDs
lsof -i :5001  # Backend
lsof -i :3000  # Frontend

# Kill the processes
kill <PID>
```

Or press `Ctrl+C` in each terminal if started manually.

---

## 📁 Project Structure

```
Healthnexus AI/
│
├── backend/                          # Flask backend application
│   ├── app/
│   │   ├── __init__.py              # App initialization
│   │   ├── main.py                  # Main Flask application entry point
│   │   ├── api/                     # API route handlers
│   │   │   ├── auth.py              # Login/Signup endpoints
│   │   │   ├── insurance.py         # Insurance recommendation endpoints
│   │   │   └── health.py            # Health check endpoint
│   │   ├── core/                    # Core business logic
│   │   │   ├── recommender.py       # ML recommendation engine
│   │   │   └── plan_ranker.py       # Plan ranking algorithm
│   │   ├── models/                  # Database models
│   │   │   ├── user.py              # User model
│   │   │   └── insurance.py         # Insurance plan model
│   │   ├── services/                # Business services
│   │   │   ├── auth_service.py      # Authentication logic
│   │   │   └── ml_service.py        # Machine learning service
│   │   ├── utils/                   # Utility functions
│   │   │   ├── validators.py        # Input validation
│   │   │   └── helpers.py           # Helper functions
│   │   └── static/                  # Static files (if any)
│   │
│   └── data/                        # Data files
│       ├── hospitals_large.csv      # Hospital network data
│       ├── hospitals_real.csv       # Real hospital information
│       └── mock_platforms.json      # Insurance platform data
│
├── frontend/                        # React frontend application
│   ├── public/                      # Public static files
│   │   ├── index.html               # Main HTML file
│   │   └── favicon.ico              # Website icon
│   │
│   ├── src/                         # Source code
│   │   ├── App.tsx                  # Main React component with routes
│   │   ├── index.tsx                # React entry point
│   │   │
│   │   ├── components/              # Reusable components
│   │   │   ├── Navigation.tsx       # Header navigation bar
│   │   │   ├── PlanCard.tsx         # Insurance plan card display
│   │   │   └── GetQuote/            # Quote form components
│   │   │       ├── PersonalInfoStep.tsx   # Step 1: Personal info
│   │   │       ├── PreferencesStep.tsx    # Step 2: Preferences
│   │   │       └── HealthStep.tsx         # Step 3: Health details
│   │   │
│   │   ├── pages/                   # Page components
│   │   │   ├── HomePage.tsx         # Landing page
│   │   │   ├── GetQuotePage.tsx     # Multi-step quote form
│   │   │   ├── RecommendationsPage.tsx # AI recommendations display
│   │   │   ├── LoginPage.tsx        # User login
│   │   │   ├── SignupPage.tsx       # User registration
│   │   │   ├── ResourcesPage.tsx    # Educational resources hub
│   │   │   └── resources/           # Resource detail pages
│   │   │       ├── GlossaryPage.tsx           # Insurance terms glossary
│   │   │       ├── ChooseHealthInsurancePage.tsx  # Buying guide
│   │   │       ├── Top5MistakesPage.tsx       # Common mistakes
│   │   │       ├── DeductiblesPage.tsx        # Deductibles explained
│   │   │       ├── ClaimsGuidePage.tsx        # Claims process guide
│   │   │       └── TermVsWholeLifePage.tsx    # Life insurance comparison
│   │   │
│   │   ├── services/                # API communication
│   │   │   └── api.ts               # Axios API calls to backend
│   │   │
│   │   └── types/                   # TypeScript type definitions
│   │       └── insurance.ts         # Insurance-related types
│   │
│   ├── package.json                 # Node.js dependencies
│   └── tsconfig.json                # TypeScript configuration
│
├── models/                          # Machine learning models
│   └── llm/                         # Language models (if used)
│
├── AImedenv/                        # Python virtual environment
│   ├── bin/                         # Executables
│   ├── lib/                         # Python libraries
│   └── pyvenv.cfg                   # Virtual environment config
│
├── requirements.txt                 # Python dependencies
├── start_server.sh                  # Server startup script
├── SETUP_GUIDE.md                   # Detailed setup instructions
└── README.md                        # This file
```

---

## 🎯 How It Works

### User Flow

1. **Landing Page** (`HomePage.tsx`)
   - User sees the main features and benefits
   - Clicks "Get Quote" to start

2. **Quote Form** (`GetQuotePage.tsx`)
   - **Step 1**: Enter personal information (age, gender, income, location)
   - **Step 2**: Set preferences (plan type, coverage amount, budget)
   - **Step 3**: Provide health details (pre-existing conditions)

3. **AI Processing** (Backend)
   - LightGBM machine learning model analyzes user profile
   - Evaluates 125+ health insurance plans
   - Ranks plans based on suitability, coverage, and affordability

4. **Recommendations** (`RecommendationsPage.tsx`)
   - Top 5 personalized plan recommendations
   - Detailed information: premium, coverage, deductibles, hospitals
   - Compare up to 3 plans side-by-side

5. **Education** (`ResourcesPage.tsx`)
   - Access 6+ educational guides
   - Learn insurance terminology
   - Understand how to choose and use insurance

---

## 🧠 Technology Stack

### Backend

- **Flask 3.1.2** - Web framework
- **LightGBM 4.6.0** - Machine learning model for plan ranking
- **Pandas 3.0.0** - Data manipulation
- **SQLAlchemy 2.0.36** - Database ORM
- **Flask-JWT-Extended 4.7.1** - Authentication
- **Flask-CORS 5.0.0** - Cross-origin requests

### Frontend

- **React 18.2.0** - UI framework
- **TypeScript 4.9.5** - Type-safe JavaScript
- **Material-UI 5.14.20** - Component library
- **React Router 6.20.1** - Navigation
- **Axios 1.6.2** - HTTP client

### Machine Learning

- **LightGBM Model** - Trained on user interactions and plan features
- **125+ Insurance Plans** - Real health insurance data
- **30+ Hospitals** - Network hospital information

---

## 🌟 Features

### 1. AI-Powered Recommendations

- Machine learning model analyzes your profile
- Considers 15+ factors including age, health, budget, location
- Ranks plans by suitability score

### 2. Smart Health Condition Handling

- Accurately handles pre-existing conditions:
  - Diabetes
  - Hypertension
  - Heart disease
  - Asthma
  - Obesity
  - Thyroid disorders
- Adjusts premium calculations accordingly

### 3. Comprehensive Plan Information

- Premium breakdowns (base + conditions)
- Coverage amounts and deductibles
- Co-payment percentages
- Network hospitals
- Claim settlement ratios
- Customer ratings

### 4. Educational Resources

- **Insurance Glossary** - 18 key terms explained
- **Buying Guides** - Step-by-step instructions
- **Common Mistakes** - What to avoid
- **Deductibles Guide** - Understanding costs
- **Claims Process** - How to file claims
- **Life Insurance Comparison** - Term vs Whole Life

### 5. User Authentication

- Secure login/signup system
- JWT-based authentication
- Password encryption with bcrypt

### 6. Responsive Design

- Works on desktop, tablet, and mobile
- Modern, clean Material-UI interface
- Smooth animations and transitions

---

## 🔍 API Endpoints

### Backend API (http://localhost:5001)

#### Health Check

```
GET /api/health
Returns: Server status and ML model status
```

#### Get Recommendations

```
POST /api/insurance/recommend
Body: User profile (age, gender, health conditions, preferences)
Returns: Top 5 personalized plan recommendations
```

#### Authentication

```
POST /api/auth/register
Body: {name, email, password}
Returns: JWT access token

POST /api/auth/login
Body: {email, password}
Returns: JWT access token
```

---

## 🛠️ Development

### Backend Development

```bash
# Activate virtual environment
source AImedenv/bin/activate

# Run Flask in development mode
cd backend
export FLASK_ENV=development
python app/main.py
```

The backend will automatically reload when you make changes.

### Frontend Development

```bash
cd frontend
npm start
```

The frontend will automatically reload when you make changes.

### Adding New Dependencies

**Backend:**

```bash
pip install <package-name>
pip freeze > requirements.txt
```

**Frontend:**

```bash
npm install <package-name>
# package.json is automatically updated
```

---

## 🧪 Testing

### Backend Testing

```bash
# Run tests (if test files exist)
python -m pytest tests/
```

### Frontend Testing

```bash
cd frontend
npm test
```

---

## 📊 Data Files Explained

### `data/hospitals_large.csv`

Contains 30+ hospitals across major Indian cities:

- Hospital name and location
- Network participation
- Specialties and ratings

### `data/hospitals_real.csv`

Real hospital data including:

- Apollo, Fortis, Max, AIIMS, Manipal
- City-wise distribution
- Cashless facility availability

### `data/mock_platforms.json`

Insurance platform information:

- Platform names
- Available plans
- Contact information

---

## 🐛 Troubleshooting

### Backend won't start

**Problem:** `ModuleNotFoundError: No module named 'flask'`

**Solution:**

```bash
source AImedenv/bin/activate
pip install -r requirements.txt
```

### Frontend won't start

**Problem:** `npm: command not found`

**Solution:** Install Node.js from https://nodejs.org/

**Problem:** `Port 3000 already in use`

**Solution:**

```bash
# Find and kill the process
lsof -i :3000
kill -9 <PID>
```

### ML Model not loading

**Problem:** Model file missing or corrupted

**Solution:** The model is loaded from the backend. Check `backend/models/` directory for model files.

### CORS errors in browser

**Problem:** Frontend can't connect to backend

**Solution:** Make sure:

1. Backend is running on port 5001
2. Frontend is running on port 3000
3. Flask-CORS is properly configured in `backend/app/main.py`

### Database errors

**Problem:** SQLite database issues

**Solution:**

```bash
# Delete the database and restart
rm backend/app.db
python backend/app/main.py
```

---

## 📝 Environment Variables (Optional)

You can create a `.env` file in the backend directory:

```
FLASK_ENV=development
SECRET_KEY=your-secret-key-here
DATABASE_URL=sqlite:///app.db
JWT_SECRET_KEY=your-jwt-secret-key
```

---

## 🚀 Deployment

### Backend Deployment (Production)

```bash
# Use a production WSGI server like Gunicorn
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5001 backend.app.main:app
```

### Frontend Deployment

```bash
cd frontend
npm run build
# Deploy the 'build' folder to your hosting service
```

---

## 📚 Additional Documentation

- **SETUP_GUIDE.md** - Comprehensive setup instructions with troubleshooting
- **DATASET_DOCUMENTATION.md** - Detailed information about data sources
- **HOSPITAL_INTEGRATION_IMPLEMENTATION.md** - Hospital network integration details

---

## 🤝 Contributing

To contribute to this project:

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Make your changes
4. Test thoroughly
5. Commit: `git commit -m "Add feature"`
6. Push: `git push origin feature-name`
7. Create a Pull Request

---

## 📞 Support

If you encounter any issues:

1. Check the **Troubleshooting** section above
2. Review **SETUP_GUIDE.md** for detailed setup help
3. Check that all dependencies are installed
4. Ensure both servers are running
5. Verify ports 3000 and 5001 are available

---

## ⚖️ License

This project is created for educational purposes as part of a Final Year Project.

---

## 🎓 Project Information

**Project Name:** Healthnexus AI - Smart Health Insurance Recommendation System

**Description:** An AI-powered web application that helps users find the perfect health insurance plan based on their personal profile, health conditions, and budget using machine learning.

**Key Features:**

- LightGBM-based recommendation engine
- Real-time plan ranking and comparison
- Pre-existing condition support
- Educational resource center
- Responsive Material-UI design

**Tech Stack:** React + TypeScript + Material-UI + Flask + LightGBM + SQLAlchemy

---

## 📈 Future Enhancements

Potential features for future development:

- [ ] Bill Scanner - Extract information from medical bills
- [ ] Pre-Authorization Assistant - Help with hospital pre-auth
- [ ] Claim Tracker - Track claim status in real-time
- [ ] Chatbot Integration - AI assistant for insurance queries
- [ ] Mobile App - React Native version
- [ ] Multi-language Support - Hindi, regional languages
- [ ] Family Plan Manager - Manage insurance for entire family
- [ ] Renewal Reminders - Email/SMS notifications

---

**Made with ❤️ for helping people find the right health insurance**
