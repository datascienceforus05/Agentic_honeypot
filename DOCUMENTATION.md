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
│  │   Request    │     │   (x-api-key)      │     │   (LLM/Groq/Rules)    │  │
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
│  │  { status, scamDetected, engagementMetrics,                            │ │
│  │    extractedIntelligence, agentNotes }                                  │ │
│  └────────────────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────────────────┘
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

### Request Body (Input)
Each API request represents one incoming message in a conversation.

#### 6.1 First Message
```json
{
  "sessionId": "wertyu-dfghj-ertyui",
  "message": {
    "sender": "scammer",
    "text": "Your bank account will be blocked today. Verify immediately.",
    "timestamp": "2026-01-21T10:15:30Z"
  },
  "conversationHistory": [],
  "metadata": {
    "channel": "SMS",
    "language": "English",
    "locale": "IN"
  }
}
```

#### 6.2 Second Message (Follow-up)
```json
{
  "sessionId": "wertyu-dfghj-ertyui",
  "message": {
    "sender": "scammer",
    "text": "Share your UPI ID to avoid account suspension.",
    "timestamp": "2026-01-21T10:17:10Z"
  },
  "conversationHistory": [
    {
      "sender": "scammer",
      "text": "Your bank account will be blocked today. Verify immediately.",
      "timestamp": "2026-01-21T10:15:30Z"
    },
    {
      "sender": "user",
      "text": "Why will my account be blocked?",
      "timestamp": "2026-01-21T10:16:10Z"
    }
  ],
  "metadata": {
    "channel": "SMS",
    "language": "English",
    "locale": "IN"
  }
}
```

### Response Body (Output)
Strictly matches Problem Statement Section 8.

```json
{
  "status": "success",
  "scamDetected": true,
  "engagementMetrics": {
    "engagementDurationSeconds": 420,
    "totalMessagesExchanged": 18
  },
  "extractedIntelligence": {
    "bankAccounts": ["XXXX-XXXX-XXXX"],
    "upiIds": ["scammer@upi"],
    "phishingLinks": ["http://malicious-link.example"]
  },
  "agentNotes": "Scammer used urgency tactics and payment redirection"
}
```

---

## 🔄 Agentic Workflow

### Step 1: Request Reception
- API receives POST request
- Validates `x-api-key`
- Parses `sessionId`, `message`, and `conversationHistory`

### Step 2: Intelligence Extraction
- Extracts UPI IDs, Bank Accounts, and Phishing Links using Regex + Context analysis

### Step 3: Scam Detection
- Uses Groq (Llama 3 70B via `openai/gpt-oss-120b`) for high-speed analysis
- Fallback to Rule-based detection if API unavailable
- Detects intent: Lottery, KYC, Financial, Phishing

### Step 4: Autonomous Agent
- Activates if `scamDetected: true`
- Adopts human-like persona (e.g., "Ramesh Kumar", elderly, tech-naive)
- Engages scammer to extract more details (Account Numbers, UPI)
- **Note:** Agent response is generated internally and stored in notes/logs, but not returned in the API response field as per Section 8 requirements.

---

## 📁 Project Structure

```
Agentic_honeypot/
├── app/
│   ├── main.py                  # FastAPI application
│   ├── models.py                # Pydantic models (Input/Output Specs)
│   ├── llm_client.py            # Groq / OpenAI / Gemini Client
│   ├── ...
├── requirements.txt
├── Dockerfile
└── README.md
```

---

## 🚀 Deployment

### Local Run
```bash
source venv/bin/activate
pip install -r requirements.txt
python run.py
```
Server runs at `http://0.0.0.0:8000`

### Render / Cloud Deployment
1. Push to GitHub
2. Connect to Render Web Service
3. Environment Variables:
   - `GROQ_API_KEY`: `your_key_here`
   - `HONEYPOT_API_KEY`: `hp-secret-key-2026`

---

**Built for Problem Statement 2** 🏆
