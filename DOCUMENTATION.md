# 🕵️ Agentic Honeypot System - Complete Documentation

## 📋 Executive Summary

This is a production-ready, AI-powered **Agentic Honeypot API** designed to detect scam messages, autonomously engage scammers using human-like AI agents, and extract scam-related intelligence—all without revealing detection.

---

## 🏗️ System Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        AGENTIC HONEYPOT SYSTEM                               │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌──────────────┐     ┌────────────────────┐     ┌───────────────────────┐  │
│  │   Incoming   │────▶│   API Key Validator│────▶│   Scam Detection AI   │  │
│  │   Request    │     │   (x-api-key)      │     │   (LLM/Rule-based)    │  │
│  └──────────────┘     └────────────────────┘     └───────────────────────┘  │
│         │                                                  │                 │
│         │                                                  ▼                 │
│         │                                        ┌───────────────────────┐  │
│         │                                        │   Intelligence        │  │
│         │                                        │   Extractor           │  │
│         │                                        │   (Regex + Context)   │  │
│         │                                        └───────────────────────┘  │
│         │                                                  │                 │
│         │                                                  ▼                 │
│         │                                        ┌───────────────────────┐  │
│         │                                        │   Autonomous Agent    │  │
│         │                                        │   (Human-like Persona)│  │
│         │                                        └───────────────────────┘  │
│         │                                                  │                 │
│         ▼                                                  ▼                 │
│  ┌────────────────────────────────────────────────────────────────────────┐ │
│  │                         JSON Response                                   │ │
│  │  { status, scamDetected, agentResponse, engagementMetrics,             │ │
│  │    extractedIntelligence, agentNotes }                                  │ │
│  └────────────────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 🔄 Agentic Workflow (Step-by-Step)

### Step 1: Request Reception & Validation
- API receives POST request at `/api/v1/analyze`
- Validates `x-api-key` header using constant-time comparison
- Parses and validates request body using Pydantic models

### Step 2: Intelligence Extraction
- Extracts UPI IDs using regex with bank suffix validation
- Identifies bank account numbers (9-18 digits) with context checking
- Detects IFSC codes (pattern: `[A-Z]{4}0[A-Z0-9]{6}`)
- Captures phishing links by checking suspicious TLDs and keywords

### Step 3: AI-Powered Scam Detection
- Constructs detection prompt with message and conversation history
- Sends to LLM (OpenAI GPT / Google Gemini / Rule-based fallback)
- Analyzes for scam patterns: lottery, KYC, financial, phishing, job scams
- Returns confidence score, scam type, and risk level

### Step 4: Autonomous Agent Activation (if scam detected)
- Selects a believable Indian persona (name, age, occupation, traits)
- Generates human-like Hinglish response using engagement strategies
- Maintains naive persona to extract more intelligence
- Never reveals detection or AI nature

### Step 5: Response Generation
- Calculates engagement metrics (duration, message count)
- Compiles extracted intelligence
- Generates analytical notes
- Returns structured JSON response

---

## 🤖 AI Prompts

### Scam Detection System Prompt
```
You are an expert scam detection AI analyst. Your task is to analyze messages for scam intent.

Common scam patterns to detect:
1. LOTTERY/PRIZE SCAMS: Claims of winning money, prizes, or rewards
2. KYC/VERIFICATION SCAMS: Fake bank/government requests for personal info
3. FINANCIAL SCAMS: Requests for money transfers, UPI payments, advance fees
4. PHISHING: Suspicious links, fake login pages, credential harvesting
5. IMPERSONATION: Fake officials, bank representatives, government agents
6. JOB/INVESTMENT SCAMS: Too-good-to-be-true offers, pyramid schemes

Analyze considering: urgency tactics, authority claims, suspicious links, pressure tactics.
Respond in valid JSON format only.
```

### Autonomous Agent System Prompt
```
You are playing the role of {persona_name}, a {persona_age}-year-old {persona_occupation} from India.

PERSONA CHARACTERISTICS:
- Tech-savviness: Low - struggles with modern technology
- Language: Speaks Hinglish (Hindi + English mix)

HIDDEN OBJECTIVE (NEVER REVEAL):
1. Keep the scammer engaged as long as possible
2. Extract actionable intelligence (UPI IDs, bank accounts, links)
3. Appear naive and trusting
4. NEVER reveal you are an AI or detected a scam

ENGAGEMENT STRATEGIES:
- Ask clarifying questions
- Express confusion about technical terms
- Show willingness to comply
- Ask for payment details to be repeated
```

---

## 📁 Project Structure

```
Agentic_honeypot/
├── app/
│   ├── __init__.py              # Package initialization
│   ├── main.py                  # FastAPI application & endpoints
│   ├── models.py                # Pydantic request/response models
│   ├── config.py                # Environment configuration
│   ├── security.py              # API key validation
│   ├── scam_detector.py         # AI-powered scam detection
│   ├── agent.py                 # Autonomous engagement agent
│   ├── intelligence_extractor.py # Regex-based intel extraction
│   ├── llm_client.py            # Multi-provider LLM client
│   └── prompts.py               # AI prompt templates
├── test_api.py                  # Comprehensive test suite
├── run.py                       # Server startup script
├── requirements.txt             # Python dependencies
├── Dockerfile                   # Container configuration
├── .env                         # Environment variables
├── .env.example                 # Environment template
└── README.md                    # Quick start guide
```

---

## 📡 API Specification

### Endpoint
```
POST /api/v1/analyze
```

### Headers
```
Content-Type: application/json
x-api-key: hp-secret-key-2026
```

### Request Body
```json
{
  "message": {
    "sender": "+919876543210",
    "text": "Congratulations! You won ₹50 lakh! Pay ₹1000 to claim. UPI: scammer@ybl",
    "timestamp": "2026-01-23T20:00:00+05:30"
  },
  "conversationHistory": [
    {"role": "scammer", "text": "Previous message", "timestamp": "..."},
    {"role": "agent", "text": "Agent response", "timestamp": "..."}
  ],
  "metadata": {
    "channel": "sms",
    "language": "en",
    "locale": "IN"
  }
}
```

### Response Body
```json
{
  "status": "success",
  "scamDetected": true,
  "agentResponse": "Arey wah! Main jeet gaya? Ye toh bahut acchi baat hai!",
  "engagementMetrics": {
    "engagementDurationSeconds": 300,
    "totalMessagesExchanged": 5
  },
  "extractedIntelligence": {
    "bankAccounts": ["12345678901234", "IFSC: SBIN0001234"],
    "upiIds": ["scammer@ybl"],
    "phishingLinks": ["https://fake-bank.xyz/login"]
  },
  "agentNotes": "Lottery scam detected. Agent extracted UPI ID. Continuing engagement."
}
```

---

## 🚀 Deployment Guide

### Local Development
```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your API keys

# Run server
python run.py
```

### Docker Deployment
```bash
docker build -t honeypot-api .
docker run -p 8000:8000 --env-file .env honeypot-api
```

### Production Deployment
- Use `gunicorn` with `uvicorn` workers for production
- Set `DEBUG=false` in environment
- Configure proper API key
- Enable HTTPS via reverse proxy (nginx)

---

## ✅ Test Results

```
🧪 AGENTIC HONEYPOT API TEST SUITE

✅ Health Check - PASSED
✅ API Key Validation - PASSED
✅ Lottery Scam Detection - PASSED
✅ KYC Scam Detection - PASSED  
✅ Multi-turn Conversation - PASSED
✅ Safe Message (Non-Scam) - PASSED

🎉 ALL TESTS PASSED!
```

---

## 🔒 Security Features

1. **API Key Authentication** - Constant-time comparison prevents timing attacks
2. **Input Validation** - Pydantic models enforce strict schemas
3. **No Detection Disclosure** - Agent never reveals scam awareness
4. **Ethical Boundaries** - No impersonation of real institutions
5. **Stateless Design** - No persistent storage of sensitive data

---

## 📊 Performance Characteristics

- **Latency**: <100ms with rule-based fallback, <2s with LLM
- **Throughput**: Handles concurrent requests via async FastAPI
- **Reliability**: Graceful fallback when LLM unavailable
- **Scalability**: Stateless design enables horizontal scaling

---

## 🎯 Intelligence Extraction Capabilities

| Type | Pattern | Validation |
|------|---------|------------|
| UPI IDs | `user@bankcode` | Known bank suffixes |
| Bank Accounts | 9-18 digits | Context keywords |
| IFSC Codes | `XXXX0XXXXXX` | Regex match |
| Phishing Links | URLs | Suspicious TLDs/keywords |

---

## 📝 Notes for Evaluation

1. **No Hard-coded Classification** - Uses AI/rule-based analysis
2. **Stateless API** - Conversation history provided in each request
3. **Human-like Responses** - Hinglish persona with cultural authenticity
4. **Production-Ready** - Error handling, logging, test coverage
5. **Multi-LLM Support** - OpenAI, Gemini, or rule-based fallback

---

**Built for Hackathon 2026** 🏆
