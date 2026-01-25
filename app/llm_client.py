"""
LLM Client Module.
Provides unified interface for OpenAI, Google Gemini, and Groq.
Falls back gracefully between providers.
"""

import os
import json
import logging
from typing import Optional, Dict, Any
from abc import ABC, abstractmethod

from app.config import get_settings

logger = logging.getLogger(__name__)


class BaseLLMClient(ABC):
    """Abstract base class for LLM clients."""
    
    @abstractmethod
    async def generate(self, prompt: str, system_prompt: str = "", temperature: float = 0.7) -> str:
        """Generate a response from the LLM."""
        pass
    
    @abstractmethod
    def is_available(self) -> bool:
        """Check if the LLM provider is available."""
        pass


class OpenAIClient(BaseLLMClient):
    """OpenAI GPT client implementation."""
    
    def __init__(self, api_key: Optional[str] = None, model: str = "gpt-4o-mini"):
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.model = model
        self._client = None
        
        if self.api_key:
            try:
                from openai import AsyncOpenAI
                self._client = AsyncOpenAI(api_key=self.api_key)
            except ImportError:
                logger.warning("OpenAI package not installed")
    
    def is_available(self) -> bool:
        return self._client is not None and self.api_key is not None
    
    async def generate(self, prompt: str, system_prompt: str = "", temperature: float = 0.7) -> str:
        if not self.is_available():
            raise RuntimeError("OpenAI client not available")
        
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        
        response = await self._client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=temperature,
            max_tokens=500
        )
        
        return response.choices[0].message.content


class GeminiClient(BaseLLMClient):
    """Google Gemini client implementation."""
    
    def __init__(self, api_key: Optional[str] = None, model: str = "gemini-1.5-flash"):
        self.api_key = api_key or os.getenv("GOOGLE_API_KEY")
        self.model = model
        self._client = None
        
        if self.api_key:
            try:
                import google.generativeai as genai
                genai.configure(api_key=self.api_key)
                self._client = genai.GenerativeModel(self.model)
            except ImportError:
                logger.warning("Google Generative AI package not installed")
    
    def is_available(self) -> bool:
        return self._client is not None and self.api_key is not None
    
    async def generate(self, prompt: str, system_prompt: str = "", temperature: float = 0.7) -> str:
        if not self.is_available():
            raise RuntimeError("Gemini client not available")
        
        full_prompt = f"{system_prompt}\n\n{prompt}" if system_prompt else prompt
        
        # Gemini uses synchronous API, wrap for async
        import asyncio
        loop = asyncio.get_event_loop()
        response = await loop.run_in_executor(
            None,
            lambda: self._client.generate_content(
                full_prompt,
                generation_config={"temperature": temperature, "max_output_tokens": 500}
            )
        )
        
        return response.text


class GroqClient(BaseLLMClient):
    """Groq client implementation using gpt-oss-120b model."""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or get_settings().GROQ_API_KEY or os.getenv("GROQ_API_KEY")
        self.model = "openai/gpt-oss-120b"
        self._client = None
        
        if self.api_key:
            try:
                from groq import Groq
                self._client = Groq(api_key=self.api_key)
            except ImportError:
                logger.warning("Groq package not installed")
    
    def is_available(self) -> bool:
        return self._client is not None and self.api_key is not None
    
    async def generate(self, prompt: str, system_prompt: str = "", temperature: float = 0.7) -> str:
        """Generate response using Groq API."""
        if not self.is_available():
            raise RuntimeError("Groq client not available")
            
        import asyncio
        from functools import partial
        
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        
        try:
            # Using partial to pass arguments correctly to run_in_executor
            func = partial(
                self._client.chat.completions.create,
                model=self.model,
                messages=messages,
                temperature=temperature,
                max_completion_tokens=8192,
                top_p=1,
                reasoning_effort="medium"
            )
            
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(None, func)
            
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"Groq generation error: {e}")
            raise


class FallbackLLMClient(BaseLLMClient):
    """
    Rule-based fallback when no LLM API is available.
    Provides basic scam detection and response generation.
    """
    
    SCAM_KEYWORDS = [
        'prize', 'winner', 'lottery', 'won', 'congratulations', 'claim',
        'urgent', 'immediately', 'verify', 'kyc', 'suspend', 'blocked',
        'account', 'update', 'otp', 'password', 'pin', 'cvv',
        'bank', 'transfer', 'payment', 'upi', 'send money',
        'reward', 'bonus', 'offer', 'free', 'gift',
        'click here', 'link', 'verify now', 'act now',
        'limited time', 'expire', 'deadline',
        'government', 'rbi', 'income tax', 'refund',
        'loan', 'credit', 'approved', 'eligible',
        'job', 'work from home', 'earn money', 'investment'
    ]
    
    ENGAGEMENT_RESPONSES = [
        "Ji ji, main samajh raha hoon. Kripya thoda aur batayein.",
        "Acha ji? Ye toh bahut acchi baat hai! Mujhe kya karna hoga?",
        "Main thoda confused hoon, aap zaroor genuine honge. Batayein kaise aage badhein?",
        "Shukriya ji aapka. Mujhe trust hai aap par. Details share karein please.",
        "Haan ji bilkul. Main ready hoon. Aap batayein kya karna hai.",
        "Ye account number ya UPI ID bata dijiye jahan payment karni hai.",
        "Main abhi kar deta hoon. Bas confirmation ke liye ek baar repeat kar dijiye.",
        "Ji haan, main senior citizen hoon. Technology mein thoda weak hoon. Help kar dijiye.",
    ]
    
    def is_available(self) -> bool:
        """Always available as fallback."""
        return True
    
    async def generate(self, prompt: str, system_prompt: str = "", temperature: float = 0.7) -> str:
        """Generate response based on rules when no LLM is available."""
        import random
        
        # Check if this is a scam detection request
        if "analyze" in prompt.lower() and "scam" in prompt.lower():
            return self._detect_scam(prompt)
        
        # Otherwise, generate engagement response
        return random.choice(self.ENGAGEMENT_RESPONSES)
    
    def _detect_scam(self, text: str) -> str:
        """Rule-based scam detection - analyzes message and conversation history."""
        # Extract MESSAGE content
        message_text = ""
        if "MESSAGE:" in text:
            try:
                start = text.find("MESSAGE:") + len("MESSAGE:")
                end_markers = ["SENDER:", "CHANNEL:", "TIMESTAMP:", "CONVERSATION"]
                end = len(text)
                for marker in end_markers:
                    pos = text.find(marker, start)
                    if pos != -1 and pos < end:
                        end = pos
                message_text = text[start:end].strip()
            except:
                pass
        
        # Extract CONVERSATION HISTORY - but stop at prompt instructions
        conv_text = ""
        if "CONVERSATION HISTORY:" in text:
            try:
                start = text.find("CONVERSATION HISTORY:") + len("CONVERSATION HISTORY:")
                # Stop at prompt instructions
                end_markers = ["Respond with", "Remember:", "{", "JSON"]
                end = len(text)
                for marker in end_markers:
                    pos = text.find(marker, start)
                    if pos != -1 and pos < end:
                        end = pos
                conv_text = text[start:end].strip()
            except:
                pass
        
        # Combine message and conversation for analysis
        full_context = (message_text + " " + conv_text).lower()
        
        # High-confidence scam keywords (strong indicators)
        high_confidence_keywords = [
            'lottery', 'won prize', 'claim prize', 'congratulations you won',
            'send money', 'pay fee', 'processing fee', 'advance payment',
            'kyc blocked', 'account suspended', 'account suspension', 'verify immediately',
            'click here to claim', 'limited time offer', 'will be blocked',
            'share your upi', 'share upi', 'avoid suspension', 'blocked today',
            'verify now', 'account will be', 'bank account blocked'
        ]
        
        # Count high-confidence matches
        high_matches = sum(1 for keyword in high_confidence_keywords if keyword in full_context)
        
        # Count regular scam indicators
        regular_matches = sum(1 for keyword in self.SCAM_KEYWORDS if keyword in full_context)
        if high_matches >= 1:
            confidence = min(0.95, 0.5 + high_matches * 0.2)
            is_scam = True
        else:
            confidence = min(0.95, regular_matches * 0.1)
            is_scam = regular_matches >= 3 and confidence > 0.25
        
        # Determine scam type
        scam_type = None
        if is_scam:
            if any(kw in full_context for kw in ['prize', 'lottery', 'winner', 'won']):
                scam_type = "lottery_scam"
            elif any(kw in full_context for kw in ['kyc', 'verify', 'blocked', 'suspended']):
                scam_type = "kyc_scam"
            elif any(kw in full_context for kw in ['bank', 'transfer', 'upi', 'payment']):
                scam_type = "financial_scam"
            elif any(kw in full_context for kw in ['job', 'work from home', 'investment']):
                scam_type = "job_investment_scam"
            else:
                scam_type = "unknown"
        
        result = {
            "is_scam": is_scam,
            "confidence": confidence,
            "scam_type": scam_type,
            "reasoning": f"Detected {high_matches} high-confidence and {regular_matches} regular scam indicators",
            "risk_level": "high" if confidence > 0.7 else ("medium" if confidence > 0.4 else "low")
        }
        
        return json.dumps(result)


class LLMClientFactory:
    """Factory for creating LLM clients with fallback logic."""
    
    _instance: Optional[BaseLLMClient] = None
    
    @classmethod
    def get_client(cls) -> BaseLLMClient:
        """Get the best available LLM client."""
        if cls._instance is not None:
            return cls._instance
        
        # Try Groq first (Preferred)
        groq_client = GroqClient()
        if groq_client.is_available():
            logger.info("Using Groq LLM client")
            cls._instance = groq_client
            return cls._instance

        # Try OpenAI next
        openai_client = OpenAIClient()
        if openai_client.is_available():
            logger.info("Using OpenAI GPT client")
            cls._instance = openai_client
            return cls._instance
        
        # Try Gemini next
        gemini_client = GeminiClient()
        if gemini_client.is_available():
            logger.info("Using Google Gemini client")
            cls._instance = gemini_client
            return cls._instance
        
        # Fall back to rule-based system
        logger.warning("No LLM API available, using rule-based fallback")
        cls._instance = FallbackLLMClient()
        return cls._instance
    
    @classmethod
    def reset(cls):
        """Reset the cached client instance."""
        cls._instance = None
