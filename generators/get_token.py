import requests
from config import CLIENT_ID, CLIENT_SECRET, DOUWE_CLIENT_ID, DOUWE_CLIENT_SECRET

url = "https://www.linkedin.com/oauth/v2/accessToken"

data = {
    "grant_type": "authorization_code",
    "code": 'code',
    "client_id": DOUWE_CLIENT_ID,
    "client_secret": DOUWE_CLIENT_SECRET,
    "redirect_uri": "http://localhost:8000/callback"
}

response = requests.post(url, data=data)

print(response.json())