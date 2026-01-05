
import requests
import os
from dotenv import load_dotenv

load_dotenv()

def test_coords():
    # Coordinates for New York City (approx)
    lat = "40.7128"
    lng = "-74.0060"
    
    url = f"https://api.collectapi.com/gasPrice/fromCoordinates?lat={lat}&lng={lng}"
    headers = {
        "authorization": os.getenv("COLLECT_API_KEY"),
        "content-type": "application/json"
    }

    try:
        response = requests.get(url, headers=headers)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_coords()
