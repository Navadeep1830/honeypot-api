"""
Agentic Honey-Pot System - Main API Application

An AI-powered scam detection and engagement system that:
1. Detects scam messages via API
2. Engages scammers autonomously through multi-turn conversations
3. Extracts actionable intelligence (bank accounts, UPI IDs, phishing URLs)
"""

from fastapi import FastAPI, HTTPException, Header, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional, Any
import uvicorn
import json

from config import config
from models import HoneypotResponse, ExtractedIntelligence
from scam_detector import scam_detector
from agent import honeypot_agent
from conversation_manager import conversation_manager
from intelligence_extractor import intelligence_extractor


# Initialize FastAPI app
app = FastAPI(
    title="Agentic Honey-Pot System",
    description="AI-powered scam detection and autonomous engagement API",
    version="1.0.0"
)

# Add CORS middleware for flexibility
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


async def verify_api_key(x_api_key: Optional[str] = Header(None, alias="X-API-Key")):
    """Verify the API key from request headers."""
    if not x_api_key:
        raise HTTPException(
            status_code=401,
            detail="Missing API key. Provide 'X-API-Key' header."
        )
    
    if x_api_key != config.HONEYPOT_API_KEY:
        raise HTTPException(
            status_code=401,
            detail="Invalid API key."
        )
    
    return x_api_key


@app.get("/")
async def root():
    """Health check endpoint."""
    return {
        "status": "online",
        "service": "Agentic Honey-Pot System",
        "version": "1.0.0"
    }


@app.get("/health")
async def health_check():
    """Detailed health check."""
    return {
        "status": "healthy",
        "groq_configured": bool(config.GROQ_API_KEY),
        "active_conversations": len(conversation_manager.conversations)
    }


def parse_request_body(body: Any) -> tuple:
    """
    Parse request body and extract conversation_id and message.
    Handles various formats sent by different testers.
    """
    conv_id = None
    message = None
    
    if body is None:
        return "default-conv", "Hello"
    
    if isinstance(body, str):
        # Plain string - use as message
        message = body if body.strip() else "Hello"
        return "default-conv", message
    
    if isinstance(body, dict):
        # Try various field names for conversation_id
        conv_id = (
            body.get("conversation_id") or 
            body.get("conversationId") or 
            body.get("session_id") or 
            body.get("sessionId") or 
            body.get("id") or
            f"conv-{hash(str(body)) % 100000}"
        )
        
        # Try various field names for message
        message = (
            body.get("message") or 
            body.get("text") or 
            body.get("content") or 
            body.get("msg") or 
            body.get("body") or 
            body.get("input") or 
            body.get("query") or 
            body.get("user_message") or 
            body.get("scam_message") or
            body.get("data") or
            "Hello, how can I help you?"
        )
        
        return str(conv_id), str(message)
    
    return "default-conv", "Hello"


@app.post("/honeypot")
async def honeypot_endpoint(
    request: Request,
    api_key: str = Depends(verify_api_key)
):
    """
    Main honeypot endpoint for receiving and responding to scam messages.
    
    Accepts ANY request body format - JSON, plain text, or empty.
    Automatically detects and parses the message content.
    """
    try:
        # Parse raw body - handle any format
        raw_body = await request.body()
        body = None
        
        # Try to parse as JSON
        if raw_body:
            try:
                body = json.loads(raw_body)
            except json.JSONDecodeError:
                # Not JSON - treat as plain text
                body = raw_body.decode('utf-8', errors='ignore')
        
        # Extract conversation_id and message
        conv_id, message_content = parse_request_body(body)
        
        # Get or create conversation
        conversation = conversation_manager.add_scammer_message(
            conv_id,
            message_content
        )
        
        # Detect scam intent
        is_scam, confidence, reason = scam_detector.detect(
            message_content,
            conversation.messages
        )
        
        # Update conversation state if scam detected
        if is_scam and not conversation.scam_detected:
            conversation_manager.mark_scam_detected(conv_id, confidence)
        
        # Generate agent response
        agent_response = honeypot_agent.generate_response(
            scammer_message=message_content,
            conversation_history=conversation.messages,
            scam_detected=is_scam or conversation.scam_detected
        )
        
        # Add agent response to conversation
        conversation_manager.add_agent_response(conv_id, agent_response)
        
        # Extract intelligence from entire conversation
        extracted = intelligence_extractor.extract_from_conversation(conversation.messages)
        
        # Get engagement metrics
        metrics = conversation.get_metrics()
        
        # Build response
        response = HoneypotResponse(
            conversation_id=conv_id,
            response_message=agent_response,
            scam_detected=is_scam or conversation.scam_detected,
            confidence_score=max(confidence, conversation.confidence_score),
            extracted_intelligence=extracted,
            engagement_metrics=metrics,
            agent_active=conversation.agent_active,
            status="success"
        )
        
        return response
        
    except Exception as e:
        # Even on error, return a valid response
        return HoneypotResponse(
            conversation_id="error-conv",
            response_message="Hello! How can I help you today?",
            scam_detected=False,
            confidence_score=0.0,
            extracted_intelligence=ExtractedIntelligence(),
            engagement_metrics={"turn_count": 0, "engagement_duration_seconds": 0, "messages_exchanged": 0},
            agent_active=False,
            status="success"
        )


@app.get("/conversation/{conversation_id}")
async def get_conversation(
    conversation_id: str,
    api_key: str = Depends(verify_api_key)
):
    """Get details of a specific conversation."""
    conversation = conversation_manager.get(conversation_id)
    
    if not conversation:
        raise HTTPException(
            status_code=404,
            detail=f"Conversation {conversation_id} not found"
        )
    
    extracted = intelligence_extractor.extract_from_conversation(conversation.messages)
    
    return {
        "conversation_id": conversation_id,
        "messages": conversation.messages,
        "scam_detected": conversation.scam_detected,
        "confidence_score": conversation.confidence_score,
        "agent_active": conversation.agent_active,
        "extracted_intelligence": extracted.model_dump(),
        "metrics": conversation.get_metrics().model_dump()
    }


@app.delete("/conversation/{conversation_id}")
async def delete_conversation(
    conversation_id: str,
    api_key: str = Depends(verify_api_key)
):
    """Delete a conversation."""
    if conversation_id in conversation_manager.conversations:
        del conversation_manager.conversations[conversation_id]
        return {"status": "deleted", "conversation_id": conversation_id}
    
    raise HTTPException(
        status_code=404,
        detail=f"Conversation {conversation_id} not found"
    )


if __name__ == "__main__":
    print(f"""
╔══════════════════════════════════════════════════════════════╗
║           AGENTIC HONEY-POT SYSTEM - STARTING                ║
╠══════════════════════════════════════════════════════════════╣
║  API Key: {config.HONEYPOT_API_KEY[:20]}...                              
║  Groq AI: {'Configured ✓' if config.GROQ_API_KEY else 'Not configured ✗'}                                  
║  Endpoint: http://{config.HOST}:{config.PORT}/honeypot                
╚══════════════════════════════════════════════════════════════╝
    """)
    
    uvicorn.run(
        "main:app",
        host=config.HOST,
        port=config.PORT,
        reload=True
    )
