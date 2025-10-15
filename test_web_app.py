"""
Test Script for Spam Detector Web Application
Tests the prediction API endpoint
"""

import requests
import json

# API endpoint
url = "http://127.0.0.1:5000/predict"

# Test messages
test_messages = [
    {
        "name": "Obvious Spam",
        "message": "CONGRATULATIONS! You've won a $1000 gift card! Click here to claim: http://bit.ly/free-gift",
        "expected": "Spam"
    },
    {
        "name": "Legitimate Message",
        "message": "Hi John, just wanted to remind you about our meeting tomorrow at 3 PM. See you there!",
        "expected": "Legitimate"
    },
    {
        "name": "Urgent Spam",
        "message": "URGENT: Your account will be closed! Call this number immediately: 1-800-FAKE-NUM",
        "expected": "Spam"
    },
    {
        "name": "Normal Text",
        "message": "Thanks for the dinner last night, it was great catching up with you!",
        "expected": "Legitimate"
    },
    {
        "name": "Prize Spam",
        "message": "You are a winner! Claim your prize now by clicking this link before it expires!",
        "expected": "Spam"
    }
]

print("=" * 70)
print("🧪 SPAM DETECTOR API TEST")
print("=" * 70)
print(f"\n🔗 Testing API at: {url}\n")

# Test each message
for i, test in enumerate(test_messages, 1):
    print(f"\n{'─' * 70}")
    print(f"Test {i}: {test['name']}")
    print(f"{'─' * 70}")
    print(f"📨 Message: {test['message'][:60]}...")
    print(f"🎯 Expected: {test['expected']}")
    
    try:
        # Send request
        response = requests.post(
            url,
            json={"message": test['message']},
            timeout=10
        )
        
        # Parse response
        data = response.json()
        
        if data.get('error'):
            print(f"❌ Error: {data.get('message')}")
        else:
            prediction = data.get('prediction')
            confidence = data.get('confidence')
            is_spam = data.get('is_spam')
            
            # Check if prediction matches expected
            is_correct = prediction == test['expected']
            status_icon = "✅" if is_correct else "❓"
            
            print(f"\n{status_icon} Prediction: {prediction}")
            print(f"📊 Confidence: {confidence}%")
            print(f"🔍 Status: {'CORRECT' if is_correct else 'UNEXPECTED'}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Error: Cannot connect to server. Is Flask app running?")
        print("   Start the server with: python app.py")
        break
    except Exception as e:
        print(f"❌ Error: {str(e)}")

print(f"\n{'=' * 70}")
print("✅ Testing Complete!")
print("=" * 70)
print("\n💡 Tip: Open http://127.0.0.1:5000 in your browser for the full UI")
