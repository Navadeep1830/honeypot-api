"""
Conversation Manager for the Agentic Honey-Pot System.
Handles multi-turn conversation state and history.
"""

from typing import Dict, List, Optional
from datetime import datetime
from models import ConversationMessage, EngagementMetrics


class Conversation:
    """Represents a single conversation with a scammer."""
    
    def __init__(self, conversation_id: str):
        self.conversation_id = conversation_id
        self.messages: List[Dict[str, str]] = []
        self.start_time: datetime = datetime.utcnow()
        self.last_activity: datetime = datetime.utcnow()
        self.scam_detected: bool = False
        self.agent_active: bool = False
        self.confidence_score: float = 0.0
    
    def add_message(self, role: str, content: str):
        """Add a message to the conversation history."""
        self.messages.append({
            "role": role,
            "content": content,
            "timestamp": datetime.utcnow().isoformat()
        })
        self.last_activity = datetime.utcnow()
    
    def get_turn_count(self) -> int:
        """Get number of conversation turns (pairs of messages)."""
        return len(self.messages) // 2 + len(self.messages) % 2
    
    def get_engagement_duration(self) -> float:
        """Get engagement duration in seconds."""
        return (self.last_activity - self.start_time).total_seconds()
    
    def get_metrics(self) -> EngagementMetrics:
        """Get engagement metrics for this conversation."""
        return EngagementMetrics(
            turn_count=self.get_turn_count(),
            engagement_duration_seconds=self.get_engagement_duration(),
            messages_exchanged=len(self.messages)
        )
    
    def get_history_for_agent(self, max_messages: int = 10) -> List[Dict[str, str]]:
        """Get conversation history formatted for the AI agent."""
        return self.messages[-max_messages:]


class ConversationManager:
    """Manages all active conversations."""
    
    def __init__(self):
        self.conversations: Dict[str, Conversation] = {}
    
    def get_or_create(self, conversation_id: str) -> Conversation:
        """Get existing conversation or create a new one."""
        if conversation_id not in self.conversations:
            self.conversations[conversation_id] = Conversation(conversation_id)
        return self.conversations[conversation_id]
    
    def get(self, conversation_id: str) -> Optional[Conversation]:
        """Get a conversation by ID."""
        return self.conversations.get(conversation_id)
    
    def add_scammer_message(self, conversation_id: str, message: str) -> Conversation:
        """Add a scammer message to the conversation."""
        conversation = self.get_or_create(conversation_id)
        conversation.add_message("scammer", message)
        return conversation
    
    def add_agent_response(self, conversation_id: str, response: str) -> Conversation:
        """Add an agent response to the conversation."""
        conversation = self.get_or_create(conversation_id)
        conversation.add_message("agent", response)
        return conversation
    
    def mark_scam_detected(self, conversation_id: str, confidence: float):
        """Mark a conversation as having detected scam."""
        conversation = self.get_or_create(conversation_id)
        conversation.scam_detected = True
        conversation.confidence_score = confidence
        conversation.agent_active = True
    
    def cleanup_old_conversations(self, max_age_hours: int = 24):
        """Remove conversations older than max_age_hours."""
        cutoff = datetime.utcnow()
        to_remove = []
        
        for conv_id, conv in self.conversations.items():
            age = (cutoff - conv.last_activity).total_seconds() / 3600
            if age > max_age_hours:
                to_remove.append(conv_id)
        
        for conv_id in to_remove:
            del self.conversations[conv_id]


# Singleton instance
conversation_manager = ConversationManager()
