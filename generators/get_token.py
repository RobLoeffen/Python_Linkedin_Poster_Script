import sys
from pathlib import Path
import urllib.parse

# Zorg dat de root directory in sys.path staat
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import requests
from config import CLIENT_ID, CLIENT_SECRET, DOUWE_CLIENT_ID, DOUWE_CLIENT_SECRET

REDIRECT_URI = "http://localhost:8000/callback"
SCOPES = "openid profile email w_member_social"
TOKEN_URL = "https://www.linkedin.com/oauth/v2/accessToken"

def get_auth_url(client_id):
    params = {
        "response_type": "code",
        "client_id": client_id,
        "redirect_uri": REDIRECT_URI,
        "scope": SCOPES,
    }
    return f"https://www.linkedin.com/oauth/v2/authorization?{urllib.parse.urlencode(params)}"

def extract_code(raw_input):
    raw_input = raw_input.strip()
    if "code=" in raw_input:
        # Gebruiker plakt de hele URL
        parsed = urllib.parse.urlparse(raw_input)
        query = urllib.parse.parse_qs(parsed.query)
        if "code" in query:
            return query["code"][0]
    return raw_input

def exchange_code_for_token(client_id, client_secret, code):
    data = {
        "grant_type": "authorization_code",
        "code": code,
        "client_id": client_id,
        "client_secret": client_secret,
        "redirect_uri": REDIRECT_URI,
    }
    response = requests.post(TOKEN_URL, data=data)
    return response.json()

def main():
    print("=" * 60)
    print("LinkedIn OAuth Token Generator")
    print("=" * 60)
    print("\nVoor welk account wil je een token genereren?")
    print("1) Hoofdaccount (LINKEDIN_ACCESS_TOKEN)")
    print("2) Douwe account (DOUWE_ACCESS_TOKEN)")
    keuze = input("\nKies 1 of 2: ").strip()

    if keuze == "1":
        account_name = "Hoofdaccount"
        client_id = CLIENT_ID
        client_secret = CLIENT_SECRET
        env_key = "LINKEDIN_ACCESS_TOKEN"
    elif keuze == "2":
        account_name = "Douwe account"
        client_id = DOUWE_CLIENT_ID
        client_secret = DOUWE_CLIENT_SECRET
        env_key = "DOUWE_ACCESS_TOKEN"
    else:
        print("Ongeldige keuze.")
        sys.exit(1)

    auth_url = get_auth_url(client_id)
    print(f"\n--- STAP 1: Open deze URL in je browser ({account_name}) ---")
    print(auth_url)
    print("\nLog in op LinkedIn en klik op 'Toestaan'.")
    print("Je wordt doorgestuurd naar een pagina (bijv. localhost:8000/callback?code=...).")
    print("Het maakt niet uit dat de pagina niet laadt/een fout geeft.")
    
    print(f"\n--- STAP 2: Plak de code of de volledige URL hieronder ---")
    user_input = input("Plak hier: ").strip()
    code = extract_code(user_input)

    if not code:
        print("Geen geldige code gevonden.")
        sys.exit(1)

    print("\nToken ophalen bij LinkedIn...")
    result = exchange_code_for_token(client_id, client_secret, code)

    if "access_token" in result:
        token = result["access_token"]
        expires_in = result.get("expires_in", "onbekend")
        print("\n" + "=" * 60)
        print("SUCCES! Token ontvangen:")
        print("=" * 60)
        print(f"Token: {token}")
        print(f"Geldigheid: {expires_in} seconden (~60 dagen)")

        # Optie om direct .env bij te werken
        update = input(f"\nWil je dit token direct opslaan in .env voor {env_key}? (j/n): ").strip().lower()
        if update in ["j", "ja", "y", "yes"]:
            env_path = PROJECT_ROOT / ".env"
            with open(env_path, "r", encoding="utf-8") as f:
                lines = f.readlines()
            
            updated = False
            new_lines = []
            for line in lines:
                if line.startswith(f"{env_key}=") or line.startswith(f"{env_key} ="):
                    new_lines.append(f"{env_key}={token}\n")
                    updated = True
                else:
                    new_lines.append(line)
            
            if not updated:
                new_lines.append(f"{env_key}={token}\n")
            
            with open(env_path, "w", encoding="utf-8") as f:
                f.writelines(new_lines)
            
            print(f"✔ .env succesvol bijgewerkt met nieuw {env_key}!")
            print(f"\nVergeet niet dit token ook bij te werken in GitHub Secrets als je de GitHub Action gebruikt!")
    else:
        print("\nFOUT bij het ophalen van token:")
        print(result)

if __name__ == "__main__":
    main()
