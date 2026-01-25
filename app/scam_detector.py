"""
Scam Detection Module.
Uses AI to detect scam intent in messages.
"""

import json
import logging
from typing import Optional
from app.models import ScamAnalysis, HoneypotRequest
from app.llm_client import LLMClientFactory
from app.prompts import SCAM_DETECTION_SYSTEM_PROMPT, SCAM_DETECTION_USER_PROMPT

logger = logging.getLogger(__name__)


class ScamDetector:
    """
    AI-powered scam detection engine.
    Analyzes messages for scam intent using LLM.
    """
    
    def __init__(self):
        self.llm_client = LLMClientFactory.get_client()
    
    async def detect(self, request: HoneypotRequest) -> ScamAnalysis:
        """
        Detect scam intent in the incoming message.
        
        Args:
            request: The honeypot request containing message and history
            
        Returns:
            ScamAnalysis with detection results
        """
        try:
            # Format conversation history for the prompt
            history_text = self._format_conversation_history(request.conversationHistory)
            
            # Build the detection prompt
            prompt = SCAM_DETECTION_USER_PROMPT.format(
                message=request.message.text,
                sender=request.message.sender,
                channel=request.metadata.channel,
                timestamp=request.message.timestamp,
                conversation_history=history_text or "No previous conversation"
            )
            
            # Get AI analysis
            response = await self.llm_client.generate(
                prompt=prompt,
                system_prompt=SCAM_DETECTION_SYSTEM_PROMPT,
                temperature=0.3  # Lower temperature for more consistent detection
            )
            
            # Parse the response
            analysis = self._parse_response(response)
            
            logger.info(f"Scam detection result: is_scam={analysis.is_scam}, confidence={analysis.confidence}")
            
            return analysis
            
        except Exception as e:
            logger.error(f"Scam detection error: {e}")
            # Return a safe default on error
            return ScamAnalysis(
                is_scam=False,
                confidence=0.0,
                scam_type=None,
                reasoning=f"Detection error: {str(e)}",
                risk_level="low"
            )
    
    def _format_conversation_history(self, history: list) -> str:
        """Format conversation history for the prompt."""
        if not history:
            return ""
        
        formatted = []
        for msg in history[-10:]:  # Last 10 messages for context
            role = msg.sender.upper()
            text = msg.text
            formatted.append(f"{role}: {text}")
        
        return "\n".join(formatted)
    
    def _parse_response(self, response: str) -> ScamAnalysis:
        """Parse the LLM response into ScamAnalysis."""
        try:
            # Clean the response - remove markdown code blocks if present
            cleaned = response.strip()
            if cleaned.startswith("```"):
                # Remove markdown code block
                lines = cleaned.split("\n")
                # Remove first and last lines (```json and ```)
                lines = [l for l in lines if not l.strip().startswith("```")]
                cleaned = "\n".join(lines)
            
            # Parse JSON
            data = json.loads(cleaned)
            
            return ScamAnalysis(
                is_scam=data.get("is_scam", False),
                confidence=float(data.get("confidence", 0.0)),
                scam_type=data.get("scam_type"),
                reasoning=data.get("reasoning", "No reasoning provided"),
                risk_level=data.get("risk_level", "low")
            )
            
        except json.JSONDecodeError as e:
            logger.warning(f"Failed to parse scam detection response: {e}")
            
            # Fallback: try to extract boolean from text
            response_lower = response.lower()
            is_scam = "true" in response_lower and "is_scam" in response_lower
            
            return ScamAnalysis(
                is_scam=is_scam,
                confidence=0.5 if is_scam else 0.2,
                scam_type="unknown" if is_scam else None,
                reasoning="Parsed from unstructured response",
                risk_level="medium" if is_scam else "low"
            )


# Singleton instance
_detector: Optional[ScamDetector] = None


def get_scam_detector() -> ScamDetector:
    """Get or create the scam detector singleton."""
    global _detector
    if _detector is None:
        _detector = ScamDetector()
    return _detector
