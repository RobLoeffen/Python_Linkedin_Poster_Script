import sys
from pathlib import Path

# Zorg dat de root directory in sys.path staat
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

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
