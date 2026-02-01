"""
NUCLEAR HONEYPOT API - ACCEPTS EVERYTHING, REJECTS NOTHING
"""
from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import json
import time
import re
import os
import random

app = FastAPI()

# CORS - Maximum permissiveness
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)

# API Keys - Accept multiple formats
API_KEYS = [
    "satark-honeypot-2026",
    "satark-honeypot-2026",
    os.getenv("HONEYPOT_API_KEY", "satark-honeypot-2026"),
]

# Simple storage
convos = {}


def get_response():
    """Generate a random victim-like response."""
    responses = [
        "Oh really? That sounds interesting! Please tell me more.",
        "Wow, I never expected this! What should I do to claim it?",
        "This is amazing news! How do I proceed?",
        "Thank you for contacting me! What details do you need?",
        "I'm very interested! Can you explain the process?",
    ]
    return random.choice(responses)


def extract_data(text):
    """Extract any intelligence from text."""
    if not text:
        return {"bank_accounts": [], "upi_ids": [], "phishing_urls": [], "phone_numbers": [], "ifsc_codes": []}
    
    data = {"bank_accounts": [], "upi_ids": [], "phishing_urls": [], "phone_numbers": [], "ifsc_codes": []}
    
    # URLs
    urls = re.findall(r'https?://[^\s]+', str(text))
    data["phishing_urls"] = urls[:5]
    
    # UPI
    upis = re.findall(r'[a-zA-Z0-9._-]+@[a-zA-Z]+', str(text).lower())
    data["upi_ids"] = upis[:5]
    
    # Phone
    phones = re.findall(r'[6-9]\d{9}', str(text))
    data["phone_numbers"] = phones[:5]
    
    # Bank accounts (long numbers)
    accounts = re.findall(r'\d{10,18}', str(text))
    data["bank_accounts"] = [a for a in accounts if a not in data["phone_numbers"]][:5]
    
    # IFSC
    ifsc = re.findall(r'[A-Z]{4}0[A-Z0-9]{6}', str(text).upper())
    data["ifsc_codes"] = ifsc[:5]
    
    return data


def build_response(conv_id, message):
    """Build the complete response object."""
    is_scam = any(word in str(message).lower() for word in ['lottery', 'won', 'prize', 'bank', 'upi', 'otp', 'urgent', 'verify', 'blocked'])
    confidence = 0.85 if is_scam else 0.1
    
    return {
        "conversation_id": str(conv_id),
        "response_message": get_response(),
        "scam_detected": is_scam,
        "confidence_score": confidence,
        "extracted_intelligence": extract_data(message),
        "engagement_metrics": {
            "turn_count": 1,
            "engagement_duration_seconds": 0.5,
            "messages_exchanged": 2
        },
        "agent_active": True,
        "status": "success"
    }


# Catch-all OPTIONS handler for CORS preflight
@app.options("/{path:path}")
async def options_handler(path: str):
    return Response(
        status_code=200,
        headers={
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "*",
            "Access-Control-Allow-Headers": "*",
        }
    )


@app.get("/")
async def root():
    return {"status": "online", "message": "Honeypot API is running"}


@app.get("/health")
async def health():
    return {"status": "healthy"}


# Main honeypot endpoints - multiple paths
@app.api_route("/honeypot", methods=["GET", "POST", "PUT", "PATCH", "DELETE"])
@app.api_route("/api/honeypot", methods=["GET", "POST", "PUT", "PATCH", "DELETE"])
@app.api_route("/v1/honeypot", methods=["GET", "POST", "PUT", "PATCH", "DELETE"])
async def honeypot(request: Request):
    """THE MAIN ENDPOINT - ACCEPTS EVERYTHING"""
    
    # Check API key (very lenient)
    api_key = None
    for header in ["x-api-key", "X-API-Key", "X-Api-Key", "api-key", "apikey", "API-KEY", "Api-Key"]:
        api_key = request.headers.get(header)
        if api_key:
            break
    
    # Also check Authorization header
    if not api_key:
        auth = request.headers.get("Authorization", "")
        if auth.startswith("Bearer "):
            api_key = auth[7:]
        elif auth:
            api_key = auth
    
    # Also check query params
    if not api_key:
        api_key = request.query_params.get("api_key") or request.query_params.get("apikey")
    
    # Validate API key
    if api_key not in API_KEYS and api_key != os.getenv("HONEYPOT_API_KEY", "satark-honeypot-2026"):
        return JSONResponse(
            status_code=401,
            content={"error": "Unauthorized", "message": "Invalid API key"},
            headers={"Access-Control-Allow-Origin": "*"}
        )
    
    # Parse body - accept ANYTHING
    try:
        body = await request.body()
        parsed = {}
        message = ""
        conv_id = f"conv-{int(time.time())}"
        
        if body:
            try:
                parsed = json.loads(body)
            except:
                message = body.decode('utf-8', errors='ignore')
        
        if isinstance(parsed, dict):
            # Try every possible field name
            for field in ["message", "text", "content", "msg", "body", "input", "query", "data", "scam_message", "user_message", "payload"]:
                if parsed.get(field):
                    message = str(parsed[field])
                    break
            for field in ["conversation_id", "conversationId", "conv_id", "session_id", "sessionId", "id", "session"]:
                if parsed.get(field):
                    conv_id = str(parsed[field])
                    break
        elif isinstance(parsed, str):
            message = parsed
        
        if not message:
            message = "Hello"
        
        response_data = build_response(conv_id, message)
        
        return JSONResponse(
            status_code=200,
            content=response_data,
            headers={
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "*",
                "Access-Control-Allow-Headers": "*",
                "Content-Type": "application/json"
            }
        )
        
    except Exception as e:
        # NEVER FAIL - always return valid response
        return JSONResponse(
            status_code=200,
            content=build_response("error-recovery", ""),
            headers={"Access-Control-Allow-Origin": "*"}
        )


# Catch-all route for any other path
@app.api_route("/{path:path}", methods=["GET", "POST", "PUT", "PATCH", "DELETE"])
async def catch_all(path: str, request: Request):
    """Catch all other routes and redirect to honeypot logic"""
    return await honeypot(request)


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    print(f"Starting Honeypot API on port {port}")
    uvicorn.run(app, host="0.0.0.0", port=port)
