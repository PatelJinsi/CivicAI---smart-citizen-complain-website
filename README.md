# 🏛️ CivicAI — Smart Citizen Complaint Management System

> AI-powered government complaint portal built with Python Django + NLP.
> Final Year Project | Django 4.2 + scikit-learn + VADER Sentiment

---

## 🚀 Features

| Feature | Description |
|---|---|
| 🤖 **AI Category Prediction** | NLP classifier (TF-IDF + Logistic Regression) auto-detects Road / Water / Garbage / Electricity |
| 🚨 **Urgency Detection** | Scores each complaint 0–100 using keyword analysis and severity signals |
| 💬 **Sentiment Analysis** | VADER NLP detects Positive / Negative / Frustrated / Neutral tone |
| 🏛️ **Auto Department Routing** | Complaint auto-assigned to correct government department |
| 📊 **Admin Dashboard** | Real-time analytics, Chart.js bar chart, filters, quick status update |
| 🔐 **Authentication** | Django auth with role-based access (Citizen vs Admin) |
| 📍 **Complaint Tracking** | Citizens track status: New → In Progress → Resolved |
| 📱 **Responsive UI** | Bootstrap 5, dark government theme, mobile-friendly |

---

## 🛠️ Tech Stack

```
Backend:    Python 3.11 · Django 4.2 · SQLite
AI/NLP:     scikit-learn · NLTK · vaderSentiment · joblib
Frontend:   Bootstrap 5 · Chart.js · DM Sans font
Deployment: Gunicorn · WhiteNoise · Render.com / Railway
```

---

## ⚡ Quick Start (5 minutes)

### 1. Clone & Setup Virtual Environment
```bash
git clone https://github.com/yourusername/smart-complaint-system.git
cd smart-complaint-system

python -m venv venv

# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Create .env file
```bash
cp .env.example .env
# Edit .env and set your SECRET_KEY
```

### 4. Run Migrations
```bash
python manage.py migrate
```

### 5. One-Command Setup (AI + Users + Sample Data)
```bash
python manage.py setup_project
```

This single command:
- ✅ Trains and saves the NLP classifier
- ✅ Creates 5 government departments
- ✅ Creates admin user (admin / Admin@123)
- ✅ Creates demo citizen (citizen1 / Citizen@123)
- ✅ Seeds 12 sample complaints with AI analysis

### 6. Run the Server
```bash
python manage.py runserver
```

Open → **http://127.0.0.1:8000**

---

## 🔑 Login Credentials

| Role | Username | Password |
|---|---|---|
| 🛡️ Admin | `admin` | `Admin@123` |
| 👤 Citizen | `citizen1` | `Citizen@123` |

> **Admin Dashboard** → http://127.0.0.1:8000/dashboard/
> **Django Admin** → http://127.0.0.1:8000/admin/

---

## 📁 Project Structure

```
smart_complaint_system/
│
├── manage.py                   # Django entry point
├── requirements.txt            # All dependencies
├── Procfile                    # Deployment config
├── .env.example                # Environment variables template
│
├── core/                       # Django project settings
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
│
├── complaints/                 # Main app
│   ├── models.py               # Complaint + Department models
│   ├── views.py                # All views (home, submit, dashboard)
│   ├── urls.py                 # URL routing
│   ├── forms.py                # Django forms
│   ├── admin.py                # Admin panel config
│   ├── ai_engine.py            # 🤖 ALL AI/NLP logic
│   ├── complaint_model.pkl     # Trained classifier (auto-generated)
│   └── management/
│       └── commands/
│           └── setup_project.py   # One-command project setup
│
├── templates/
│   ├── base.html               # Master layout
│   ├── home.html               # Public landing page
│   ├── auth/
│   │   ├── login.html
│   │   └── register.html
│   └── complaints/
│       ├── submit.html         # Complaint submission form
│       ├── my_complaints.html  # Citizen tracking view
│       ├── complaint_detail.html  # Full complaint + AI result
│       └── dashboard.html      # Admin dashboard
│
├── static/
│   ├── css/style.css           # Custom styles
│   └── js/main.js              # Frontend JavaScript
│
├── fixtures/
│   └── initial_data.json       # Department seed data
│
└── media/                      # Uploaded complaint images
```

---

## 🤖 AI Engine — How It Works

### File: `complaints/ai_engine.py`

#### 1. Category Prediction
```python
from complaints.ai_engine import predict_category
result = predict_category("The road has huge potholes near school")
# → {'category': 'road', 'confidence': 94.2, 'department': 'Public Works Department'}
```
- **Algorithm:** TF-IDF Vectorizer + Logistic Regression Pipeline
- **Training data:** 75 labeled complaint texts (15 per category)
- **Categories:** road, water, garbage, electricity, other
- **Accuracy:** ~95% on training data

#### 2. Urgency Detection
```python
from complaints.ai_engine import detect_urgency
score = detect_urgency("Dangerous sparking wire! Child almost electrocuted!")
# → 95 (Critical)
```
- Keyword scoring across 4 urgency levels (critical/high/medium/low)
- Boosts for: time duration, exclamation marks, text length
- Score range: 0–100

#### 3. Sentiment Analysis
```python
from complaints.ai_engine import analyze_sentiment
sentiment = analyze_sentiment("This has been happening for months! Nobody cares!")
# → 'frustrated'
```
- Uses **VADER** (Valence Aware Dictionary and sEntiment Reasoner)
- Returns: positive / neutral / negative / frustrated

---

## 🌐 Deployment on Render.com (Free)

1. Push code to GitHub
2. Go to [render.com](https://render.com) → New Web Service
3. Connect your GitHub repo
4. Set these:
   - **Build Command:** `pip install -r requirements.txt && python manage.py migrate && python manage.py setup_project`
   - **Start Command:** `gunicorn core.wsgi:application`
5. Add Environment Variable: `SECRET_KEY` = (any random 50-char string)
6. Deploy!

---

## 📊 URL Routes

| URL | View | Access |
|---|---|---|
| `/` | Home page | Public |
| `/register/` | Register | Public |
| `/login/` | Login | Public |
| `/submit/` | Submit complaint | Citizen |
| `/my-complaints/` | Track complaints | Citizen |
| `/complaint/<id>/` | Complaint detail | Citizen/Admin |
| `/dashboard/` | Admin dashboard | Admin only |
| `/admin/` | Django admin | Admin only |

---

## 👨‍💻 Author

Built as a Final Year Project demonstrating Django + AI/NLP integration for civic technology.

**Stack:** Python · Django · scikit-learn · VADER · Bootstrap 5