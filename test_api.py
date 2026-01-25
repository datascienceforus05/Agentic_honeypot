#!/usr/bin/env python3
"""
Test script for the Agentic Honeypot API.
Tests match EXACTLY the Problem Statement format.
"""

import requests
import json
from datetime import datetime

API_URL = "http://localhost:8000"
API_KEY = "hp-secret-key-2026"

HEADERS = {
    "Content-Type": "application/json",
    "x-api-key": API_KEY
}


def test_health():
    """Test health endpoint."""
    print("=" * 60)
    print("TEST: Health Check")
    print("=" * 60)
    
    response = requests.get(f"{API_URL}/health")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    assert response.status_code == 200
    print("✅ PASSED\n")


def test_first_message():
    """
    Test first message (start of conversation) - Problem Statement 6.1
    """
    print("=" * 60)
    print("TEST: First Message (Section 6.1)")
    print("=" * 60)
    
    # Exact format from Problem Statement 6.1
    payload = {
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
    
    response = requests.post(f"{API_URL}/api/v1/analyze", headers=HEADERS, json=payload)
    data = response.json()
    
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(data, indent=2)}")
    
    assert response.status_code == 200
    assert data["status"] == "success"
    assert data["scamDetected"] == True
    assert "engagementMetrics" in data
    assert "extractedIntelligence" in data
    assert "agentNotes" in data
    print("✅ PASSED\n")
    
    return data


def test_second_message():
    """
    Test second message (follow-up) - Problem Statement 6.2
    """
    print("=" * 60)
    print("TEST: Second Message with History (Section 6.2)")
    print("=" * 60)
    
    # Exact format from Problem Statement 6.2
    payload = {
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
    
    response = requests.post(f"{API_URL}/api/v1/analyze", headers=HEADERS, json=payload)
    data = response.json()
    
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(data, indent=2)}")
    
    assert response.status_code == 200
    assert data["status"] == "success"
    assert data["scamDetected"] == True
    assert data["engagementMetrics"]["totalMessagesExchanged"] == 3
    print("✅ PASSED\n")
    
    return data


def test_intelligence_extraction():
    """Test extraction of bank accounts, UPI IDs, and phishing links."""
    print("=" * 60)
    print("TEST: Intelligence Extraction")
    print("=" * 60)
    
    payload = {
        "message": {
            "sender": "scammer",
            "text": "Send ₹5000 to UPI: fraud@ybl or account 12345678901234 IFSC HDFC0001234. Click http://fake-bank.xyz/verify",
            "timestamp": "2026-01-21T10:20:00Z"
        },
        "conversationHistory": [],
        "metadata": {
            "channel": "WhatsApp",
            "language": "English",
            "locale": "IN"
        }
    }
    
    response = requests.post(f"{API_URL}/api/v1/analyze", headers=HEADERS, json=payload)
    data = response.json()
    
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(data, indent=2)}")
    
    assert response.status_code == 200
    assert "fraud@ybl" in data["extractedIntelligence"]["upiIds"]
    assert "12345678901234" in data["extractedIntelligence"]["bankAccounts"]
    assert len(data["extractedIntelligence"]["phishingLinks"]) > 0
    print("✅ PASSED\n")


def test_safe_message():
    """Test non-scam message - should return scamDetected: false."""
    print("=" * 60)
    print("TEST: Safe Message (Non-Scam)")
    print("=" * 60)
    
    payload = {
        "message": {
            "sender": "user",
            "text": "Hello, I wanted to check if my order has been shipped.",
            "timestamp": "2026-01-21T10:25:00Z"
        },
        "conversationHistory": [],
        "metadata": {
            "channel": "Chat",
            "language": "English",
            "locale": "IN"
        }
    }
    
    response = requests.post(f"{API_URL}/api/v1/analyze", headers=HEADERS, json=payload)
    data = response.json()
    
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(data, indent=2)}")
    
    assert response.status_code == 200
    assert data["scamDetected"] == False
    print("✅ PASSED\n")


def test_api_key_validation():
    """Test API authentication - Section 4."""
    print("=" * 60)
    print("TEST: API Key Validation (Section 4)")
    print("=" * 60)
    
    # Test missing API key
    response = requests.post(f"{API_URL}/api/v1/analyze", json={})
    print(f"Missing key - Status: {response.status_code}")
    assert response.status_code == 401
    
    # Test invalid API key
    bad_headers = {"Content-Type": "application/json", "x-api-key": "invalid-key"}
    response = requests.post(f"{API_URL}/api/v1/analyze", headers=bad_headers, json={})
    print(f"Invalid key - Status: {response.status_code}")
    assert response.status_code == 403
    
    print("✅ PASSED\n")


def test_response_format():
    """Verify response matches Section 8 format exactly."""
    print("=" * 60)
    print("TEST: Response Format Validation (Section 8)")
    print("=" * 60)
    
    payload = {
        "message": {
            "sender": "scammer",
            "text": "Congratulations! You won lottery. Pay processing fee.",
            "timestamp": "2026-01-21T10:30:00Z"
        },
        "conversationHistory": [],
        "metadata": {"channel": "SMS", "language": "English", "locale": "IN"}
    }
    
    response = requests.post(f"{API_URL}/api/v1/analyze", headers=HEADERS, json=payload)
    data = response.json()
    
    print(f"Response: {json.dumps(data, indent=2)}")
    
    # Verify all required fields from Section 8
    required_fields = ["status", "scamDetected", "engagementMetrics", "extractedIntelligence", "agentNotes"]
    for field in required_fields:
        assert field in data, f"Missing required field: {field}"
    
    # Verify engagementMetrics structure
    assert "engagementDurationSeconds" in data["engagementMetrics"]
    assert "totalMessagesExchanged" in data["engagementMetrics"]
    
    # Verify extractedIntelligence structure
    assert "bankAccounts" in data["extractedIntelligence"]
    assert "upiIds" in data["extractedIntelligence"]
    assert "phishingLinks" in data["extractedIntelligence"]
    
    print("✅ PASSED - Response matches Section 8 format\n")


def main():
    """Run all tests."""
    print("\n" + "=" * 60)
    print("🧪 AGENTIC HONEYPOT API TEST SUITE")
    print("    Matching Problem Statement 2 Format")
    print("=" * 60 + "\n")
    
    try:
        test_health()
        test_api_key_validation()
        test_first_message()
        test_second_message()
        test_intelligence_extraction()
        test_safe_message()
        test_response_format()
        
        print("=" * 60)
        print("🎉 ALL TESTS PASSED!")
        print("=" * 60)
        
    except AssertionError as e:
        print(f"❌ TEST FAILED: {e}")
        return 1
    except requests.exceptions.ConnectionError:
        print("❌ ERROR: Could not connect to API. Is the server running?")
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())
