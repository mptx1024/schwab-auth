import os
import webbrowser
import json
import datetime
import requests
import subprocess
from pathlib import Path
from dotenv import load_dotenv
from datetime import datetime, timezone


def push_tokens(local_path: str, remote: str, local_copy_path: str) -> None:
    """Copy tokens.json to the remote server AND to a local project path."""

    # 1) Copy to remote server
    # remote like: "user@server:/opt/trading/secrets/tokens.json"
    subprocess.run(["scp", local_path, remote], check=True)

    # 2) Copy to local project directory (scp works for local file copies too)
    subprocess.run(["scp", local_path, local_copy_path], check=True)

def main() -> None:
    # python-dotenv reads  .env file and injects those key/value pairs into os.environ
    dotenv_path = Path(__file__).with_name(".env")
    load_dotenv(dotenv_path=dotenv_path)

    schwab_app_key = os.environ["SCHWAB_APP_KEY"]
    schwab_secret = os.environ["SCHWAB_SECRET"]
    callback_url = os.environ["CALLBACK_URL"]
    

    auth_url = (
        "https://api.schwabapi.com/v1/oauth/authorize"
        f"?client_id={schwab_app_key}&redirect_uri={callback_url}"
    )

    print(f"[Schwabdev] Open to authenticate: {auth_url}")
    try:
        webbrowser.open(auth_url)
    except Exception as e:
        print(f"[Schwabdev] Failed to open browser automatically: {e}")

    response_url = input("[Schwabdev] After authorizing, paste the address bar url here: ")
    code = f"{response_url[response_url.index('code=') + 5:response_url.index('%40')]}@"

    print(f"[Schwabdev] Authorization code obtained: {code}")
    # headers = {'Authorization': f'Basic {base64.b64encode(bytes(f"{schwab_app_key}:{schwab_secret}", "utf-8")).decode("utf-8")}','Content-Type': 'application/x-www-form-urlencoded'}
    data = {'grant_type': 'authorization_code','code': code,'redirect_uri': callback_url}

    response = requests.post('https://api.schwabapi.com/v1/oauth/token', headers={'Content-Type': 'application/x-www-form-urlencoded'}, data=data, auth=(schwab_app_key, schwab_secret))
    token_dictionary = response.json()
    # access_token = token_dictionary['access_token']
    # refresh_token = token_dictionary['refresh_token']
    # print(f"[Schwabdev] Token response: {token_dictionary}")
    # print(f"[Schwabdev] Access Token: {access_token} \nRefresh Token: {refresh_token}")

    #--- Save tokens to tokens.json ---
    tokens_path = Path(__file__).with_name("tokens.json")
    now_utc = datetime.now(timezone.utc).isoformat()
    tokens = {
    "access_token_issued": now_utc,
    "refresh_token_issued": now_utc, 
    "token_dictionary": token_dictionary,    # full Schwab response including both tokens
    }
    with open(tokens_path, "w") as f:
        json.dump(tokens, f, indent=4)

    # --- Push tokens.json after update ---
    # You’ll want SSH keys set up so this doesn’t prompt for a password each time.
    # Toggle by setting PUSH_TOKENS=1 in your environment or .env.
    # if os.environ.get("PUSH_TOKENS") == "1":
    push_tokens(
        local_path=str(tokens_path),
        remote=os.environ["REMOTE_TOKEN_DIR"],
        local_copy_path=os.environ["LOCAL_TOKEN_DIR"],
    )

if __name__ == "__main__":
    main()