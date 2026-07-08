import requests
import json

URL = "http://localhost:8000/agent"

# Test Case 1: Standard Business Request
standard_request = {
    "request": "Write a meeting agenda for a weekly sync of the Marketing team."
}

# Test Case 2: Complex Ambiguous Request
complex_request = {
    "request": "Plan a product launch for a mind-reading device. Make your own assumptions about budget, timeline, and risks."
}

def test_agent(payload, test_name):
    print(f"\n--- Running {test_name} ---")
    print(f"Sending request: '{payload['request']}'")
    print("Agent is thinking and executing... Please wait 15-30 seconds...")
    
    try:
        response = requests.post(URL, json=payload)
        if response.status_code == 200:
            print("\n SUCCESS!")
            print(json.dumps(response.json(), indent=4))
        else:
            print(f"\n ERROR {response.status_code}:")
            print(response.text)
    except Exception as e:
        print(f"\n FAILED TO CONNECT: {e}")

if __name__ == "__main__":
    test_agent(standard_request, "Test 1: Standard Request")