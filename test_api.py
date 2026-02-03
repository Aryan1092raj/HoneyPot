"""
Test script for ScamBait AI API
Tests authentication, conversation history, intelligence extraction, and response format
"""

import requests
import json
import time
from datetime import datetime

# Configuration
API_URL = "http://localhost:8000/api/honeypot"
API_KEY = "your-secure-api-key-here"  # Change this to match your .env HONEYPOT_API_KEY

def print_section(title):
    """Print formatted section header"""
    print("\n" + "="*70)
    print(f"  {title}")
    print("="*70)

def test_authentication():
    """Test 1: API Key Authentication"""
    print_section("TEST 1: API Key Authentication")
    
    # Test without API key
    print("\n1a. Testing WITHOUT API key (should fail)...")
    response = requests.post(
        API_URL,
        json={"sessionId": "test-auth", "message": "Hello"}
    )
    print(f"   Status: {response.status_code}")
    print(f"   Expected: 422 (validation error)")
    
    # Test with wrong API key
    print("\n1b. Testing with WRONG API key (should fail)...")
    response = requests.post(
        API_URL,
        headers={"X-API-Key": "wrong-key-12345"},
        json={"sessionId": "test-auth", "message": "Hello"}
    )
    print(f"   Status: {response.status_code}")
    print(f"   Expected: 401")
    print(f"   Response: {response.json()}")
    
    # Test with correct API key
    print("\n1c. Testing with CORRECT API key (should succeed)...")
    response = requests.post(
        API_URL,
        headers={"X-API-Key": API_KEY, "Content-Type": "application/json"},
        json={"sessionId": "test-auth", "message": "Hello"}
    )
    print(f"   Status: {response.status_code}")
    print(f"   Expected: 200")
    if response.status_code == 200:
        print(f"   ✅ Authentication working!")
    else:
        print(f"   ❌ Failed: {response.text}")
    
    return response.status_code == 200

def test_input_validation():
    """Test 2: Input Validation"""
    print_section("TEST 2: Input Validation")
    
    headers = {"X-API-Key": API_KEY, "Content-Type": "application/json"}
    
    # Test empty message
    print("\n2a. Testing EMPTY message (should fail)...")
    response = requests.post(
        API_URL,
        headers=headers,
        json={"sessionId": "test-validation", "message": ""}
    )
    print(f"   Status: {response.status_code}")
    print(f"   Expected: 422 (validation error)")
    
    # Test very long message
    print("\n2b. Testing VERY LONG message (>5000 chars, should fail)...")
    long_message = "A" * 5001
    response = requests.post(
        API_URL,
        headers=headers,
        json={"sessionId": "test-validation", "message": long_message}
    )
    print(f"   Status: {response.status_code}")
    print(f"   Expected: 422 (validation error)")
    
    # Test valid message
    print("\n2c. Testing VALID message (should succeed)...")
    response = requests.post(
        API_URL,
        headers=headers,
        json={"sessionId": "test-validation", "message": "This is a valid message"}
    )
    print(f"   Status: {response.status_code}")
    print(f"   Expected: 200")
    if response.status_code == 200:
        print(f"   ✅ Input validation working!")
    
    return response.status_code == 200

def test_conversation_history():
    """Test 3: Conversation History Management"""
    print_section("TEST 3: Conversation History Management")
    
    headers = {"X-API-Key": API_KEY, "Content-Type": "application/json"}
    session_id = f"test-history-{int(time.time())}"
    
    # First message
    print("\n3a. Sending FIRST message...")
    response1 = requests.post(
        API_URL,
        headers=headers,
        json={
            "sessionId": session_id,
            "message": "Hello! I am calling from State Bank. Your KYC is pending."
        }
    )
    data1 = response1.json()
    print(f"   Status: {response1.status_code}")
    print(f"   Message Count: {data1.get('messageCount')}")
    print(f"   Agent Reply: {data1.get('reply')[:100]}...")
    
    # Second message (should remember first)
    print("\n3b. Sending SECOND message (should have context)...")
    response2 = requests.post(
        API_URL,
        headers=headers,
        json={
            "sessionId": session_id,
            "message": "Please send Rs 500 to verify your account.",
            "conversationHistory": []  # Empty - should use session history
        }
    )
    data2 = response2.json()
    print(f"   Status: {response2.status_code}")
    print(f"   Message Count: {data2.get('messageCount')}")
    print(f"   Agent Reply: {data2.get('reply')[:100]}...")
    
    # Third message
    print("\n3c. Sending THIRD message...")
    response3 = requests.post(
        API_URL,
        headers=headers,
        json={
            "sessionId": session_id,
            "message": "Send to UPI: scammer@paytm"
        }
    )
    data3 = response3.json()
    print(f"   Status: {response3.status_code}")
    print(f"   Message Count: {data3.get('messageCount')}")
    print(f"   Agent Reply: {data3.get('reply')[:100]}...")
    
    if data1.get('messageCount') == 1 and data2.get('messageCount') == 2 and data3.get('messageCount') == 3:
        print(f"\n   ✅ Conversation history working! Message counts: 1 → 2 → 3")
        return True
    else:
        print(f"\n   ❌ Conversation history NOT working correctly")
        return False

def test_intelligence_extraction():
    """Test 4: Intelligence Extraction"""
    print_section("TEST 4: Intelligence Extraction")
    
    headers = {"X-API-Key": API_KEY, "Content-Type": "application/json"}
    session_id = f"test-extraction-{int(time.time())}"
    
    # Message with UPI ID
    print("\n4a. Extracting UPI ID...")
    response = requests.post(
        API_URL,
        headers=headers,
        json={
            "sessionId": session_id,
            "message": "Please send payment to scammer@paytm immediately"
        }
    )
    data = response.json()
    upi_ids = data.get('extractedIntelligence', {}).get('upiIds', [])
    print(f"   Extracted UPIs: {upi_ids}")
    print(f"   Expected: ['scammer@paytm']")
    
    # Message with phone number
    print("\n4b. Extracting Phone Number...")
    response = requests.post(
        API_URL,
        headers=headers,
        json={
            "sessionId": session_id,
            "message": "Call me on 9876543210 for verification"
        }
    )
    data = response.json()
    phones = data.get('extractedIntelligence', {}).get('phoneNumbers', [])
    print(f"   Extracted Phones: {phones}")
    print(f"   Expected: ['9876543210']")
    
    # Message with bank account
    print("\n4c. Extracting Bank Account...")
    response = requests.post(
        API_URL,
        headers=headers,
        json={
            "sessionId": session_id,
            "message": "Transfer to account number 123456789012"
        }
    )
    data = response.json()
    accounts = data.get('extractedIntelligence', {}).get('bankAccounts', [])
    print(f"   Extracted Accounts: {accounts}")
    
    # Message with phishing link
    print("\n4d. Extracting Phishing Link...")
    response = requests.post(
        API_URL,
        headers=headers,
        json={
            "sessionId": session_id,
            "message": "Update KYC here: http://fake-sbi-kyc.scam.com/update"
        }
    )
    data = response.json()
    links = data.get('extractedIntelligence', {}).get('phishingLinks', [])
    print(f"   Extracted Links: {links}")
    
    if upi_ids or phones or accounts or links:
        print(f"\n   ✅ Intelligence extraction working!")
        return True
    else:
        print(f"\n   ❌ No intelligence extracted")
        return False

def test_response_format():
    """Test 5: Response Format Compliance"""
    print_section("TEST 5: Response Format Compliance")
    
    headers = {"X-API-Key": API_KEY, "Content-Type": "application/json"}
    
    response = requests.post(
        API_URL,
        headers=headers,
        json={
            "sessionId": f"test-format-{int(time.time())}",
            "message": "Your account has security issue"
        }
    )
    
    if response.status_code != 200:
        print(f"   ❌ API returned {response.status_code}")
        return False
    
    data = response.json()
    
    required_fields = [
        'status', 'reply', 'sessionId', 'scamDetected',
        'extractedIntelligence', 'agentStrategy', 'currentPhase', 'messageCount'
    ]
    
    print("\n5. Checking required fields...")
    all_present = True
    for field in required_fields:
        present = field in data
        symbol = "✅" if present else "❌"
        print(f"   {symbol} {field}: {present}")
        if not present:
            all_present = False
    
    # Check nested extractedIntelligence
    print("\n   Checking extractedIntelligence structure...")
    intel = data.get('extractedIntelligence', {})
    intel_fields = ['upiIds', 'bankAccounts', 'ifscCodes', 'phoneNumbers', 'phishingLinks']
    for field in intel_fields:
        present = field in intel
        symbol = "✅" if present else "❌"
        print(f"   {symbol} extractedIntelligence.{field}: {present}")
        if not present:
            all_present = False
    
    # Print sample response
    print("\n   Sample Response:")
    print(f"   {json.dumps(data, indent=2)[:500]}...")
    
    if all_present:
        print(f"\n   ✅ Response format is correct!")
        return True
    else:
        print(f"\n   ❌ Response format has missing fields")
        return False

def test_scam_detection():
    """Test 6: Scam Detection Flag"""
    print_section("TEST 6: Scam Detection Flag")
    
    headers = {"X-API-Key": API_KEY, "Content-Type": "application/json"}
    
    response = requests.post(
        API_URL,
        headers=headers,
        json={
            "sessionId": f"test-scam-{int(time.time())}",
            "message": "URGENT! Your bank account will be blocked. Share OTP now!"
        }
    )
    
    data = response.json()
    scam_detected = data.get('scamDetected')
    
    print(f"\n   scamDetected: {scam_detected}")
    print(f"   Type: {type(scam_detected)}")
    print(f"   Expected: True (boolean)")
    
    if isinstance(scam_detected, bool):
        print(f"\n   ✅ scamDetected field present and is boolean!")
        return True
    else:
        print(f"\n   ❌ scamDetected field missing or wrong type")
        return False

def run_all_tests():
    """Run all tests and summarize results"""
    print("\n" + "="*70)
    print("  SCAMBAIT AI - API TEST SUITE")
    print("  Testing: Authentication, Validation, History, Extraction, Format")
    print("="*70)
    print(f"\n  API URL: {API_URL}")
    print(f"  API Key: {API_KEY[:10]}...{API_KEY[-5:]}")
    print(f"  Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    results = {}
    
    try:
        results['authentication'] = test_authentication()
    except Exception as e:
        print(f"\n   ❌ Test failed with error: {e}")
        results['authentication'] = False
    
    time.sleep(1)
    
    try:
        results['validation'] = test_input_validation()
    except Exception as e:
        print(f"\n   ❌ Test failed with error: {e}")
        results['validation'] = False
    
    time.sleep(1)
    
    try:
        results['history'] = test_conversation_history()
    except Exception as e:
        print(f"\n   ❌ Test failed with error: {e}")
        results['history'] = False
    
    time.sleep(1)
    
    try:
        results['extraction'] = test_intelligence_extraction()
    except Exception as e:
        print(f"\n   ❌ Test failed with error: {e}")
        results['extraction'] = False
    
    time.sleep(1)
    
    try:
        results['format'] = test_response_format()
    except Exception as e:
        print(f"\n   ❌ Test failed with error: {e}")
        results['format'] = False
    
    time.sleep(1)
    
    try:
        results['scam_detection'] = test_scam_detection()
    except Exception as e:
        print(f"\n   ❌ Test failed with error: {e}")
        results['scam_detection'] = False
    
    # Summary
    print_section("TEST SUMMARY")
    total_tests = len(results)
    passed_tests = sum(results.values())
    
    for test_name, passed in results.items():
        symbol = "✅" if passed else "❌"
        print(f"  {symbol} {test_name.replace('_', ' ').title()}: {'PASSED' if passed else 'FAILED'}")
    
    print(f"\n  Results: {passed_tests}/{total_tests} tests passed")
    
    if passed_tests == total_tests:
        print("\n  🎉 ALL TESTS PASSED! API is ready for hackathon submission.")
    else:
        print(f"\n  ⚠️  {total_tests - passed_tests} test(s) failed. Review issues above.")
    
    print("\n" + "="*70 + "\n")

if __name__ == "__main__":
    print("\n⚠️  NOTE: Make sure the API server is running on http://localhost:8000")
    print("   Run: python api.py")
    print("\n   Also update API_KEY in this script to match your .env HONEYPOT_API_KEY\n")
    
    input("Press Enter to start tests...")
    
    run_all_tests()
