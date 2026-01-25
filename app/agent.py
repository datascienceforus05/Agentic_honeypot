"""
Autonomous AI Agent Module.
Generates human-like responses to engage scammers.
"""

import logging
import random
from typing import Optional
from app.models import (
    HoneypotRequest, 
    ScamAnalysis, 
    AgentContext, 
    ExtractedIntelligence
)
from app.llm_client import LLMClientFactory
from app.prompts import (
    AGENT_SYSTEM_PROMPT, 
    AGENT_USER_PROMPT,
    AGENT_NOTES_SYSTEM_PROMPT,
    AGENT_NOTES_USER_PROMPT
)

logger = logging.getLogger(__name__)


class AutonomousAgent:
    """
    Autonomous AI agent that engages scammers with human-like responses.
    Maintains a consistent persona while extracting intelligence.
    """
    
    # Predefined personas for variety
    PERSONAS = [
        AgentContext(
            persona_name="Ramesh Kumar",
            persona_age=58,
            persona_occupation="Retired government employee",
            persona_traits=["trusting", "confused with technology", "polite", "eager to help"]
        ),
        AgentContext(
            persona_name="Sunita Devi",
            persona_age=62,
            persona_occupation="Retired school teacher",
            persona_traits=["caring", "naive about online scams", "talkative", "religious"]
        ),
        AgentContext(
            persona_name="Mohan Lal",
            persona_age=55,
            persona_occupation="Small shop owner",
            persona_traits=["busy", "impatient", "slightly greedy", "easily impressed"]
        ),
        AgentContext(
            persona_name="Kamla Sharma",
            persona_age=65,
            persona_occupation="Housewife",
            persona_traits=["lonely", "trusting of strangers", "talkative", "slow with technology"]
        ),
    ]
    
    # Fallback responses when LLM is unavailable
    FALLBACK_RESPONSES = {
        "lottery_scam": [
            "Arey wah! Main jeet gaya? Ye toh bahut acchi baat hai! Kaise claim karun ye prize?",
            "Sach mein? Itne paise? Main toh believe nahi kar sakta. Kya karna hoga mujhe?",
            "Ji ji, main bahut khush hoon. Batayein kahan payment receive karun?",
        ],
        "kyc_scam": [
            "Haan ji, mera account block ho gaya? Oh no! Kya karna padega verification ke liye?",
            "Ji main kar deta hoon KYC. Kaunse documents chahiye aapko?",
            "Accha accha, main samajh gaya. Aap bata dijiye kahan details bhejni hain.",
        ],
        "financial_scam": [
            "Theek hai ji, main payment kar deta hoon. UPI ID bata dijiye please.",
            "Haan ji, kitna bhejना है? Account number ya UPI ID dijiye.",
            "Main abhi transfer kar deta hoon. Confirm kar lijiye details ek baar.",
        ],
        "phishing": [
            "Ye link khol loon? Ek minute, main try karta hoon.",
            "Ji haan, main click kar raha hoon. Kya fill karna hai isme?",
            "Arey ye page khul nahi raha. Koi aur link hai kya aapke paas?",
        ],
        "default": [
            "Ji ji, main sun raha hoon. Aage batayein please.",
            "Accha ji? Thoda aur explain karenge please?",
            "Haan bilkul, main ready hoon. Kya karna hai mujhe?",
            "Theek hai ji, main aapki baat maan leta hoon. Details dijiye.",
        ]
    }
    
    def __init__(self, persona: Optional[AgentContext] = None):
        self.llm_client = LLMClientFactory.get_client()
        self.persona = persona or random.choice(self.PERSONAS)
    
    async def generate_response(
        self,
        request: HoneypotRequest,
        scam_analysis: ScamAnalysis,
        intelligence: ExtractedIntelligence
    ) -> str:
        """
        Generate a human-like response to engage the scammer.
        
        Args:
            request: The original honeypot request
            scam_analysis: Results from scam detection
            intelligence: Already extracted intelligence
            
        Returns:
            Human-like response message
        """
        try:
            # Format conversation history
            history_text = self._format_conversation_history(request.conversationHistory)
            
            # Build the agent prompt
            system_prompt = AGENT_SYSTEM_PROMPT.format(
                persona_name=self.persona.persona_name,
                persona_age=self.persona.persona_age,
                persona_occupation=self.persona.persona_occupation,
                persona_traits=", ".join(self.persona.persona_traits)
            )
            
            user_prompt = AGENT_USER_PROMPT.format(
                persona_name=self.persona.persona_name,
                scam_type=scam_analysis.scam_type or "unknown",
                risk_level=scam_analysis.risk_level,
                current_message=request.message.text,
                conversation_history=history_text or "No previous messages",
                bank_accounts=", ".join(intelligence.bankAccounts) or "None found yet",
                upi_ids=", ".join(intelligence.upiIds) or "None found yet",
                phishing_links=", ".join(intelligence.phishingLinks) or "None found yet"
            )
            
            # Generate response
            response = await self.llm_client.generate(
                prompt=user_prompt,
                system_prompt=system_prompt,
                temperature=0.8  # Higher temperature for more natural responses
            )
            
            # Clean up the response
            response = self._clean_response(response)
            
            logger.info(f"Agent generated response: {response[:100]}...")
            
            return response
            
        except Exception as e:
            logger.error(f"Agent response generation error: {e}")
            return self._get_fallback_response(scam_analysis.scam_type)
    
    async def generate_notes(
        self,
        scam_detected: bool,
        scam_analysis: ScamAnalysis,
        intelligence: ExtractedIntelligence,
        message_count: int,
        duration_seconds: int,
        latest_message: str,
        agent_response: str
    ) -> str:
        """
        Generate analytical notes about the interaction.
        
        Args:
            scam_detected: Whether scam was detected
            scam_analysis: Scam analysis results
            intelligence: Extracted intelligence
            message_count: Total messages exchanged
            duration_seconds: Engagement duration
            latest_message: Latest scammer message
            agent_response: Agent's response
            
        Returns:
            Brief analytical note
        """
        try:
            prompt = AGENT_NOTES_USER_PROMPT.format(
                scam_detected=scam_detected,
                scam_type=scam_analysis.scam_type or "unknown",
                risk_level=scam_analysis.risk_level,
                message_count=message_count,
                duration_seconds=duration_seconds,
                bank_accounts=", ".join(intelligence.bankAccounts) or "None",
                upi_ids=", ".join(intelligence.upiIds) or "None",
                phishing_links=", ".join(intelligence.phishingLinks) or "None",
                latest_message=latest_message,
                agent_response=agent_response
            )
            
            notes = await self.llm_client.generate(
                prompt=prompt,
                system_prompt=AGENT_NOTES_SYSTEM_PROMPT,
                temperature=0.5
            )
            
            # Truncate if too long
            return notes[:500] if len(notes) > 500 else notes
            
        except Exception as e:
            logger.error(f"Notes generation error: {e}")
            return self._generate_fallback_notes(
                scam_detected, scam_analysis, intelligence, message_count
            )
    
    def _format_conversation_history(self, history: list) -> str:
        """Format conversation history for the prompt."""
        if not history:
            return ""
        
        formatted = []
        for msg in history[-10:]:  # Last 10 messages
            role = "SCAMMER" if msg.sender.lower() == "scammer" else "ME"
            formatted.append(f"{role}: {msg.text}")
        
        return "\n".join(formatted)
    
    def _clean_response(self, response: str) -> str:
        """Clean and validate the agent response."""
        # Remove any meta-commentary or explanations
        response = response.strip()
        
        # Remove common LLM artifacts
        artifacts = [
            "Here's my response:",
            "As " + self.persona.persona_name + ":",
            "Response:",
            "*",
            "[",
            "("
        ]
        
        for artifact in artifacts:
            if response.startswith(artifact):
                response = response[len(artifact):].strip()
        
        # Ensure response isn't too long
        if len(response) > 300:
            # Find a natural break point
            sentences = response.split('.')
            response = '.'.join(sentences[:2]) + '.'
        
        return response
    
    def _get_fallback_response(self, scam_type: Optional[str]) -> str:
        """Get a fallback response when LLM fails."""
        responses = self.FALLBACK_RESPONSES.get(
            scam_type, 
            self.FALLBACK_RESPONSES["default"]
        )
        return random.choice(responses)
    
    def _generate_fallback_notes(
        self,
        scam_detected: bool,
        scam_analysis: ScamAnalysis,
        intelligence: ExtractedIntelligence,
        message_count: int
    ) -> str:
        """Generate basic notes without LLM."""
        if not scam_detected:
            return "No scam indicators detected in this interaction."
        
        intel_count = (
            len(intelligence.bankAccounts) + 
            len(intelligence.upiIds) + 
            len(intelligence.phishingLinks)
        )
        
        if intel_count > 0:
            return (
                f"{scam_analysis.scam_type or 'Scam'} detected with {scam_analysis.risk_level} risk. "
                f"Extracted {intel_count} intelligence items across {message_count} messages. "
                f"Agent successfully maintaining engagement."
            )
        else:
            return (
                f"{scam_analysis.scam_type or 'Potential scam'} detected. "
                f"Continuing engagement to extract actionable intelligence."
            )


# Singleton instance
_agent: Optional[AutonomousAgent] = None


def get_agent() -> AutonomousAgent:
    """Get or create the autonomous agent singleton."""
    global _agent
    if _agent is None:
        _agent = AutonomousAgent()
    return _agent
