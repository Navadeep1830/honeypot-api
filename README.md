# 🛡️ Satark AI - Agentic Honey-Pot System

AI-powered scam detection and autonomous engagement API for the India AI Impact Buildathon.

---

## 📋 Submission Details

| Field | Value |
|-------|-------|
| **x-api-key** | `satark-honeypot-2026` |
| **Honeypot API Endpoint URL** | *(Get after deploying - see Step 3)* |

---

## 🚀 Quick Start (3 Steps)

### Step 1: Test Locally (Optional)

```powershell
# Navigate to project folder
cd c:\Users\sunko\OneDrive\Desktop\Coding\sn4

# Install dependencies
pip install -r requirements.txt

# Run the server
python main.py

# Open test interface in browser
start test.html
```

**Test with cURL:**
```powershell
curl -X POST http://localhost:8000/honeypot `
  -H "Content-Type: application/json" `
  -H "X-API-Key: satark-honeypot-2026" `
  -d '{"conversation_id": "test-1", "message": "You won lottery! Send bank account 1234567890123 to scammer@paytm"}'
```

---

### Step 2: Push to GitHub

1. **Create a new repository** at [github.com/new](https://github.com/new)
   - Name: `honeypot-api`
   - Keep it Public
   - Don't initialize with README

2. **Push your code:**
```powershell
cd c:\Users\sunko\OneDrive\Desktop\Coding\sn4
git remote add origin https://github.com/YOUR_USERNAME/honeypot-api.git
git branch -M main
git push -u origin main
```

---

### Step 3: Deploy to Render.com (FREE)

1. **Go to [render.com](https://render.com)** and sign up/login with GitHub

2. **Click "New +" → "Web Service"**

3. **Connect your `honeypot-api` repository**

4. **Configure the service:**

   | Setting | Value |
   |---------|-------|
   | Name | `satark-honeypot` |
   | Region | Singapore (closest to India) |
   | Branch | `main` |
   | Runtime | Python 3 |
   | Build Command | `pip install -r requirements.txt` |
   | Start Command | `uvicorn main:app --host 0.0.0.0 --port $PORT` |

5. **Add Environment Variables** (click "Advanced"):

   | Key | Value |
   |-----|-------|
   | `GROQ_API_KEY` | `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` |
   | `HONEYPOT_API_KEY` | `satark-honeypot-2026` |

6. **Click "Create Web Service"** and wait for deployment (~2-3 minutes)

7. **Copy your URL** (e.g., `https://satark-honeypot.onrender.com`)

---

### Step 4: Submit to Hackathon

Fill in the submission form:

| Field | Value |
|-------|-------|
| **x-api-key** | `satark-honeypot-2026` |
| **Honeypot API Endpoint URL** | `https://YOUR-APP-NAME.onrender.com/honeypot` |

---

## 🔌 API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/honeypot` | POST | Main endpoint - receives scam messages |
| `/health` | GET | Health check |
| `/docs` | GET | Interactive API documentation |
| `/conversation/{id}` | GET | View conversation history |

### Request Format

```json
POST /honeypot
Headers: {
  "Content-Type": "application/json",
  "X-API-Key": "satark-honeypot-2026"
}
Body: {
  "conversation_id": "unique-id",
  "message": "Scammer's message here"
}
```

### Response Format

```json
{
  "conversation_id": "unique-id",
  "response_message": "AI agent's response",
  "scam_detected": true,
  "confidence_score": 0.92,
  "extracted_intelligence": {
    "bank_accounts": ["1234567890123"],
    "upi_ids": ["scammer@paytm"],
    "phishing_urls": ["http://scam.com"],
    "ifsc_codes": ["SBIN0012345"],
    "phone_numbers": ["9876543210"]
  },
  "engagement_metrics": {
    "turn_count": 3,
    "engagement_duration_seconds": 45.2,
    "messages_exchanged": 6
  },
  "agent_active": true,
  "status": "success"
}
```

---

## 📁 Project Structure

```
sn4/
├── main.py                    # FastAPI application
├── agent.py                   # AI agent with persona
├── scam_detector.py           # Scam detection logic
├── intelligence_extractor.py  # Extract bank/UPI/URLs
├── conversation_manager.py    # Multi-turn conversation
├── models.py                  # Pydantic models
├── config.py                  # Configuration
├── requirements.txt           # Dependencies
├── Procfile                   # For deployment
├── test.html                  # Test interface
└── .env                       # Environment variables (local only)
```

---

## 🎯 Features

- ✅ **Scam Detection**: Multi-layer analysis (keywords + Groq AI)
- ✅ **Autonomous Agent**: Believable human persona to engage scammers
- ✅ **Intelligence Extraction**: Bank accounts, UPI IDs, URLs, IFSC, phone numbers
- ✅ **Multi-turn Conversations**: Context-aware responses
- ✅ **API Authentication**: Secure with X-API-Key header

---

## 🔧 Troubleshooting

**Server won't start?**
```powershell
pip install --upgrade fastapi uvicorn groq pydantic python-dotenv
```

**Deployment fails on Render?**
- Check that all environment variables are set
- Verify `requirements.txt` has no version conflicts
- Check Render logs for specific errors

**Intelligence not extracting?**
- Extraction only works on scammer messages (not agent responses)
- Bank accounts must be 9-18 digits
- UPI must have valid suffix (@paytm, @ybl, @upi, etc.)

---

## 📞 Support

Built for India AI Impact Buildathon - Problem 2: Agentic Honey-Pot
