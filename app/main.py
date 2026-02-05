"""
Main FastAPI Application.
Agentic Honeypot API - Production Ready.
"""

import logging
import time
from datetime import datetime, timezone
from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.config import get_settings
from app.models import HoneypotRequest, HoneypotResponse, EngagementMetrics, ExtractedIntelligence
from app.security import validate_api_key
from app.scam_detector import get_scam_detector
from app.agent import get_agent
from app.intelligence_extractor import IntelligenceExtractor

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler."""
    logger.info("🚀 Agentic Honeypot API starting...")
    yield
    logger.info("👋 Agentic Honeypot API shutting down...")


# Initialize FastAPI app
settings = get_settings()
app = FastAPI(
    title=settings.API_TITLE,
    version=settings.API_VERSION,
    description=settings.API_DESCRIPTION,
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/", tags=["Health"])
async def root():
    """Health check endpoint."""
    return {"status": "online", "service": "Agentic Honeypot API", "version": settings.API_VERSION}


@app.get("/health", tags=["Health"])
async def health_check():
    """Detailed health check."""
    return {
        "status": "healthy",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "version": settings.API_VERSION
    }


@app.post("/api/v1/analyze", response_model=HoneypotResponse, tags=["Honeypot"])
async def analyze_message(
    request: HoneypotRequest,
    api_key: str = Depends(validate_api_key)
) -> HoneypotResponse:
    """
    Main honeypot endpoint - analyzes incoming messages for scam intent
    and generates autonomous agent responses.
    """
    start_time = time.time()
    
    try:
        # Step 1: Extract intelligence from current message and history
        all_text = request.message.text
        for msg in request.conversationHistory:
            all_text += " " + msg.text
        
        intelligence = IntelligenceExtractor.extract_all(all_text)
        
        # Step 2: Detect scam intent using AI
        detector = get_scam_detector()
        scam_analysis = await detector.detect(request)
        
        # Step 3: Calculate engagement metrics
        message_count = len(request.conversationHistory) + 1
        
        # Calculate duration from timestamps if available
        duration_seconds = 0
        if request.conversationHistory:
            try:
                first_ts = request.conversationHistory[0].timestamp
                current_ts = request.message.timestamp
                
                def parse_timestamp(ts):
                    if isinstance(ts, (int, float)):
                        # Assume milliseconds
                        return datetime.fromtimestamp(ts / 1000.0, tz=timezone.utc)
                    ts_str = str(ts).replace('Z', '+00:00')
                    dt = datetime.fromisoformat(ts_str)
                    if dt.tzinfo is None:
                        dt = dt.replace(tzinfo=timezone.utc)
                    return dt

                if first_ts is not None and current_ts is not None:
                    first_dt = parse_timestamp(first_ts)
                    current_dt = parse_timestamp(current_ts)
                    duration_seconds = int((current_dt - first_dt).total_seconds())
            except Exception as e:
                logger.warning(f"Timestamp calculation failed: {e}")
                duration_seconds = message_count * 30  # Estimate 30s per message
        
        # Step 4: Generate agent response if scam detected
        agent_response = None
        agent_notes = ""
        
        if scam_analysis.is_scam:
            agent = get_agent()
            agent_response = await agent.generate_response(request, scam_analysis, intelligence)
            agent_notes = await agent.generate_notes(
                scam_detected=True,
                scam_analysis=scam_analysis,
                intelligence=intelligence,
                message_count=message_count,
                duration_seconds=duration_seconds,
                latest_message=request.message.text,
                agent_response=agent_response or ""
            )
        else:
            agent_notes = "Message analyzed. No scam indicators detected."
        
        # Build response - EXACTLY matches Section 8 format
        response = HoneypotResponse(
            status="success",
            scamDetected=scam_analysis.is_scam,
            engagementMetrics=EngagementMetrics(
                engagementDurationSeconds=max(0, duration_seconds),
                totalMessagesExchanged=message_count
            ),
            extractedIntelligence=intelligence,
            agentNotes=agent_notes
        )
        
        elapsed = time.time() - start_time
        logger.info(f"Request processed in {elapsed:.2f}s - Scam: {scam_analysis.is_scam}")
        
        return response
        
    except Exception as e:
        logger.error(f"Error processing request: {e}")
        raise HTTPException(status_code=500, detail={"error": str(e)})


@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler."""
    logger.error(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={"status": "error", "message": "Internal server error"}
    )
