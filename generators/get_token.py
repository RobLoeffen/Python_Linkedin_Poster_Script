import requests
from config import CLIENT_ID, CLIENT_SECRET

code = "AQQEOja-sTQ1O9tQkgwTdXLRRwQzIwoxtRAJxSQzUI53HS2TVjYaHI8mjCf6-t8pUZZN2m5ylp4coA5sH81ggBlCohqicRCFqRtvQ2bEMKRehPB0HkCjweAyNgeD04LRjWLSRrlYw4FEDyEmqxLvSzcPbapq9qBdAlWnv2vvpPK47DrTkd_bgXOMIOrLQVGumk2bFdi23gtlaUS0bjA"

url = "https://www.linkedin.com/oauth/v2/accessToken"

data = {
    "grant_type": "authorization_code",
    "code": code,
    "client_id": CLIENT_ID,
    "client_secret": CLIENT_SECRET,
    "redirect_uri": "http://localhost:8000/callback"
}

response = requests.post(url, data=data)

print(response.json())