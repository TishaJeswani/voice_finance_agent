import requests

url = "http://localhost:8000/whatsapp"
data = {
    "From": "whatsapp:+1234567890",
    "Body": "Hello, how much did I spend on food?",
    "MessageSid": "SM1234567890"
}

try:
    response = requests.post(url, data=data)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.text}")
except Exception as e:
    print(f"Error: {e}")
