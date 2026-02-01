# Agentic Honey-Pot System

AI-powered scam detection and autonomous engagement API for the India AI Impact Buildathon.

## Quick Start

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure environment:**
   ```bash
   # Copy and edit .env file
   cp .env.example .env
   # Edit .env with your GEMINI_API_KEY and HONEYPOT_API_KEY
   ```

3. **Run the server:**
   ```bash
   python main.py
   # Or: uvicorn main:app --reload --port 8000
   ```

## API Endpoints

### POST /honeypot
Main endpoint for scam message processing.

**Headers:**
- `X-API-Key`: Your API key (required)

**Request:**
```json
{
  "conversation_id": "unique-id",
  "message": "Scammer's message here"
}
```

**Response:**
```json
{
  "conversation_id": "unique-id",
  "response_message": "Agent's response",
  "scam_detected": true,
  "confidence_score": 0.85,
  "extracted_intelligence": {
    "bank_accounts": [],
    "upi_ids": [],
    "phishing_urls": []
  },
  "engagement_metrics": {
    "turn_count": 1,
    "engagement_duration_seconds": 0
  }
}
```

## Submission Details

- **Deployed URL**: Your Railway/Render URL
- **API KEY**: Value of `HONEYPOT_API_KEY` in your .env file

## Deployment

### Railway.app
```bash
# Install Railway CLI
npm install -g @railway/cli

# Login and deploy
railway login
railway init
railway up
```

### Render.com
1. Connect GitHub repo
2. Set environment variables
3. Deploy as Python web service

## Testing

```bash
curl -X POST http://localhost:8000/honeypot \
  -H "Content-Type: application/json" \
  -H "X-API-Key: satark-honeypot-2026" \
  -d '{"conversation_id": "test-1", "message": "Congratulations! You won Rs. 50 lakhs!"}'
```
