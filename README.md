# 🕵️ Agentic Honeypot API

**AI-powered scam detection and autonomous engagement system for Hackathon 2026**

Matches **Problem Statement 2** specifications exactly.

---

## 🚀 Quick Start

```bash
# Install dependencies
cd /home/bishnups/Agentic_honeypot
source venv/bin/activate
python run.py
```

Server runs at `http://localhost:8000`

---

## 📡 API Endpoint

```
POST /api/v1/analyze
```

### Headers (Section 4)
```
x-api-key: hp-secret-key-2026
Content-Type: application/json
```

---

## 📥 Request Format (Section 6)

### First Message (6.1)
```json
{
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

### Follow-up Message (6.2)
```json
{
  "message": {
    "sender": "scammer",
    "text": "Share your UPI ID to avoid account suspension.",
    "timestamp": "2026-01-21T10:17:10Z"
  },
  "conversationHistory": [
    {
      "sender": "scammer",
      "text": "Your bank account will be blocked today.",
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

---

## 📤 Response Format (Section 8)

```json
{
  "status": "success",
  "scamDetected": true,
  "agentResponse": "Acha ji? Ye toh bahut acchi baat hai!",
  "engagementMetrics": {
    "engagementDurationSeconds": 420,
    "totalMessagesExchanged": 18
  },
  "extractedIntelligence": {
    "bankAccounts": ["12345678901234", "IFSC: HDFC0001234"],
    "upiIds": ["scammer@upi"],
    "phishingLinks": ["http://malicious-link.example"]
  },
  "agentNotes": "Scammer used urgency tactics and payment redirection"
}
```

---

## ✅ Test Results

```
🧪 AGENTIC HONEYPOT API TEST SUITE

✅ Health Check - PASSED
✅ API Key Validation (Section 4) - PASSED
✅ First Message (Section 6.1) - PASSED
✅ Second Message with History (Section 6.2) - PASSED  
✅ Intelligence Extraction - PASSED
✅ Safe Message (Non-Scam) - PASSED
✅ Response Format Validation (Section 8) - PASSED

🎉 ALL TESTS PASSED!
```

---

## 🏗️ Architecture

```
Request → API Key Validator → Scam Detector → Agent → Intelligence Extractor → Response
```

- **Scam Detection**: AI-powered with rule-based fallback
- **Agent**: Human-like Hinglish persona
- **Intelligence Extraction**: Regex + contextual validation

---

## 📁 Project Structure

```
├── app/
│   ├── main.py          # FastAPI application
│   ├── models.py        # Pydantic models (matches PS exactly)
│   ├── scam_detector.py # AI scam detection
│   ├── agent.py         # Autonomous engagement agent
│   ├── intelligence_extractor.py
│   ├── llm_client.py    # LLM providers + fallback
│   └── prompts.py       # AI prompts
├── test_api.py          # Test suite
├── run.py               # Entry point
└── requirements.txt
```

---

## 🔧 Configuration

```bash
# For production - add LLM API key:
OPENAI_API_KEY=sk-xxx  # or
GOOGLE_API_KEY=xxx
```

---

**Built for Problem Statement 2 - Agentic Honey-Pot** 🏆
