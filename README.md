### Environment Configuration

#### Required in `.env`

-   `SCHWAB_APP_KEY`
-   `SCHWAB_SECRET`
-   `CALLBACK_URL`
-   `LOCAL_TOKEN_PATH`
    **destination paths** for where the generated `tokens.json` should be copied after authentication. **file path** (including filename). Example: `/home/yourname/src/trading/tokens.json`

#### Optional

-   `REMOTE_TOKEN_PATH`  
    Remote **file path** (including filename) in `scp` format where `tokens.json` should be copied, e.g. `user@host:/path/to/tokens.json`.  
    If not set, the remote copy step is skipped.

### Usage

```bash
uv run -m main
```

Follow the prompt to paste the authenticated redirect URL. Once complete, `tokens.json` will be updated and pushed to the configured destinations.

### How It Works

1. Launches a browser to complete Schwab OAuth authentication.
2. Exchanges the authorization code for access + refresh tokens.
3. Writes a fresh `tokens.json` in the project directory.
4. Copies `tokens.json` to the configured local path.
5. Optionally copies `tokens.json` to the configured remote path via `scp`.
