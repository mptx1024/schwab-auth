1. run `uv run -m main`
2. login and copy paste the URL in termial
3. update the tokens.json file in remote trading bot server:`scp tokens.json frank@192.168.1.174:/home/frank/src/trading/tokens.json` update to both prod and local dev env: 
`scp tokens.json frank@192.168.1.174:/home/frank/src/trading/tokens.json && \
scp tokens.json /Users/frankjia/Documents/src/trading/tokens.json`