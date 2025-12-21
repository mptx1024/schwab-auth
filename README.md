### Environment Configuration

This project requires a `.env` file in the project root.

You must define `LOCAL_TOKEN_DIR`, which specifies the **local destination path for `tokens.json`**, including the filename.  
It is used by the script to copy the refreshed `tokens.json` to the desired local directory.

**Example:**
```env
LOCAL_TOKEN_DIR=/home/frank/src/trading/tokens.json
```
**How to use**
1. run `uv run -m main`
2. login and copy paste the Schwab's authenticated URL in termial
3. Done. the generated tokens.json file is pasted & updated to the designated location
 
