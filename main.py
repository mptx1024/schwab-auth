import os
import webbrowser
import json
import datetime
import requests
import subprocess
from pathlib import Path
from dotenv import load_dotenv
from datetime import datetime, timezone

def _run(cmd: list[str], label: str) -> None:
        print(f"{label}: running -> {' '.join(cmd)}")
        result = subprocess.run(cmd, text=True, capture_output=True)
        if result.returncode == 0:
            print(f"[{label}: SUCCESS (exit={result.returncode})")
            if result.stdout:
                print(f"[{label}: stdout:\n{result.stdout.strip()}")
            if result.stderr:
                print(f"[{label}: stderr:\n{result.stderr.strip()}")
            return

        # Failure case
        print(f"[{label}: FAILED (exit={result.returncode})")
        if result.stdout:
            print(f"[{label}: stdout:\n{result.stdout.strip()}")
        if result.stderr:
            print(f"[{label}: stderr:\n{result.stderr.strip()}")
        raise subprocess.CalledProcessError(
            result.returncode,
            cmd,
            output=result.stdout,
            stderr=result.stderr,
        )


def push_tokens(new_tokens_path: str,local_dest_path: str, remote_dest_path: str=None, ) -> None:
    """Copy tokens.json to the remote server AND to a local project path."""

    # 1) Copy to local project directory
    _run(["scp", new_tokens_path, local_dest_path], "Copy tokens to local")
    # 2) Copy to remote server
    # remote like: "user@server:/opt/trading/secrets/tokens.json"
    if remote_dest_path is not None:
      _run(["scp", new_tokens_path, remote_dest_path], "Copy tokens to remote")

def main() -> None:
    # python-dotenv reads  .env file and injects those key/value pairs into os.environ
    dotenv_path = Path(__file__).with_name(".env")
    load_dotenv(dotenv_path=dotenv_path)

    schwab_app_key = os.environ["SCHWAB_APP_KEY"]
    schwab_secret = os.environ["SCHWAB_SECRET"]
    callback_url = os.environ["SCHWAB_CALLBACK_URL"]
    ——

    auth_url = (
        "https://api.schwabapi.com/v1/oauth/authorize"
        f"?client_id={schwab_app_key}&redirect_uri={callback_url}"
    )

    print(f"Open to authenticate: {auth_url}")
    try:
        webbrowser.open(auth_url)
    except Exception as e:
        print(f"Failed to open browser automatically: {e}")

    response_url = input("After authorizing, paste the address bar url here: ")
    code = f"{response_url[response_url.index('code=') + 5:response_url.index('%40')]}@"

    print(f"Authorization code obtained: {code}")
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
    push_tokens(
        new_tokens_path=str(tokens_path),
        remote_dest_path=os.environ["REMOTE_TOKEN_PATH"] if "REMOTE_TOKEN_PATH" in os.environ else None,
        local_dest_path=os.environ["LOCAL_TOKEN_PATH"],
    )

if __name__ == "__main__":
    main()