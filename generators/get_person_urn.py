import requests

from config import DOUWE_ACCESS_TOKEN

headers = {
    "Authorization": f"Bearer {DOUWE_ACCESS_TOKEN}"
}

response = requests.get(
    "https://api.linkedin.com/v2/userinfo",
    headers=headers
)

print(response.status_code)
print(response.json())