# ITM Gwalior — Intelligent College Enquiry Chatbot 🎓🤖

[![Python](https://img.shields.io/badge/Python-3.9%2B-blue.svg)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Flask-3.0.0-lightgrey.svg)](https://flask.palletsprojects.com/)
[![NLTK](https://img.shields.io/badge/NLTK-3.9.3-green.svg)](https://www.nltk.org/)
[![Deploy on Railway](https://railway.app/button.svg)](https://railway.app/)

A production-ready, intelligent NLP-powered chatbot designed specifically for **Institute of Technology & Management (ITM), Gwalior**. It seamlessly handles student queries regarding courses, fees, scholarships, and facilitates automated campus visit appointments.

---

## 🏗️ Architecture & Flow Diagram

The application follows a robust modular architecture separating the frontend, web server, NLP engine, and data storage.

![Architecture Diagram](./architecture.png)

*(The diagram illustrates the flow from the browser to the Flask server, passing through the NLP pipeline (Intent Classification → Entity Extraction → Context Management) and finally generating a response using JSON knowledge bases and SQLite).*

---

## ✨ Core Features

- **Hybrid NLP Engine:** Uses Exact Match, Keyword Boost, and TF-IDF Cosine Similarity for highly accurate intent classification.
- **Context Awareness:** Maintains up to 10 conversational turns, allowing users to use pronouns (e.g., "uska fee kitna hai").
- **Smart Entity Extraction:** Automatically detects phone numbers, emails, courses, dates, and times from raw user input.
- **Interactive Slot Booking:** An automated 8-state machine that handles lead generation and appointment booking step-by-step.
- **Admin Dashboard:** Secure, password-protected panel (`/admin`) to view analytics, manage appointments, and export data.
- **Hinglish Support:** Trained to understand mixed-language queries typical of Indian students (e.g., "admission process kya hai?").

---

## 📂 Project Structure

```text
college_chatbot/
├── app.py                     # Main Flask Application
├── Procfile                   # Railway Deployment config (gunicorn)
├── requirements.txt           # Project dependencies
├── setup.py                   # Setup script (Downloads NLTK data, inits DB)
│
├── chatbot/                   # 🧠 NLP Pipeline
│   ├── nlp_engine.py          # TF-IDF vectorization & similarity engine
│   ├── intent_classifier.py   # Intent prediction logic
│   ├── entity_extractor.py    # Regex & NLP based entity extraction
│   ├── slot_manager.py        # Booking state machine
│   ├── context_manager.py     # Session history management
│   └── response_generator.py  # Dynamic response builder
│
├── data/                      # 🗄️ JSON Knowledge Bases
│   ├── intents.json           # NLP training patterns (500+ patterns)
│   ├── knowledge_base.json    # Real college data (Fees, Courses, Contacts)
│   └── faqs.json              # Direct Q&A pairs
│
├── database/                  # 💾 Storage
│   ├── college.db             # SQLite3 database (Appointments, Leads, Logs)
│   └── db_manager.py          # CRUD operations
│
├── tests/                     # 🧪 Testing Suite
│   ├── e2e_tests.py           # End-to-End user flow simulations
│   ├── run_smoke_tests.py     # Quick API endpoint health checks
│   ├── stress_tests.py        # Load testing for concurrent users
│   └── test_nlp_and_response.py # NLP accuracy & intent validation
│
└── templates/ & static/       # 🎨 Frontend UI (HTML, CSS, Vanilla JS)
```

---

## 🧪 Testing Suite

We have included a comprehensive testing suite inside the `tests/` directory to ensure reliability before deployment:

1. **Smoke Tests (`run_smoke_tests.py`):** Ensures all critical endpoints (`/chat`, `/health`, `/admin`) are up and responding correctly.
2. **NLP Validation (`test_nlp_and_response.py`):** Feeds various phrasing variations to the NLP engine to ensure the TF-IDF model correctly predicts intents.
3. **End-to-End Tests (`e2e_tests.py`):** Simulates a complete user conversation, including the multi-step slot booking process.
4. **Stress Testing (`stress_tests.py`):** Tests the Flask server under concurrent load to ensure it doesn't crash during traffic spikes.

**To run tests locally:**
```bash
python tests/test_nlp_and_response.py
```

---

## 🚀 Deployment (Railway)

This application is configured for instant deployment on Linux containers like [Railway.app](https://railway.app).

1. **Connect GitHub:** Create a New Project on Railway and select this repository.
2. **Root Directory:** In Railway Settings, set the Root Directory to `college_chatbot`.
3. **Environment Variables:**
   - `FLASK_SECRET_KEY`: Set a secure random string.
   - `ADMIN_USERNAME`: Your desired admin username (default: `admin`).
   - `ADMIN_PASSWORD`: Your secure admin password.
4. Railway will automatically detect the `Procfile`, install `requirements.txt`, run the NLTK downloader inside `app.py`, and launch via `gunicorn`.

---

## 🛠️ Local Setup

If you want to run or modify the bot on your local Windows/Mac machine:

```bash
# 1. Navigate to project folder
cd college_chatbot

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run setup (Initializes database & downloads NLTK resources)
python setup.py

# 4. Start the development server
python app.py
```
*Visit `http://localhost:5000` to interact with the bot.*

---

## 🔮 Future Improvements / Roadmap

To take this chatbot to the next level, the following features can be implemented in the future:

1. **Advanced LLM Fallback (AI Integration):** Integrate OpenAI (ChatGPT) or Google Gemini API to handle complex, out-of-scope questions dynamically when the local NLP model fails to find an intent.
2. **WhatsApp / Telegram Integration:** Connect the Flask backend to WhatsApp Business API (Twilio/Meta) so students can chat directly from their phones.
3. **Voice Input/Output:** Add Web Speech API in the frontend to allow students to speak their queries and listen to the responses.
4. **Multilingual Translation:** Integrate Google Translate API to dynamically translate Hindi/Marathi/Gujarati queries to English before processing, and translate the response back to the user's native language.
5. **Live ERP/CRM Sync:** Automatically push "Leads" and "Appointments" directly into the college's official CRM software via REST APIs instead of just SQLite.
6. **Live Agent Handoff:** A feature where the bot transfers the chat to a real human counsellor if the user gets frustrated or types "talk to human".

---
*Built for Institute of Technology & Management, Gwalior.*
