"""tweet_poster.py

CLI script to generate and publish tweets for multiple Twitter
accounts using Google Gemini (Generative AI).

1. Put all Twitter API credentials in a file called `accounts.txt` in the
   same folder. Each line must contain four comma-separated values:

   consumer_key, consumer_secret, access_token, access_token_secret

   Lines starting with # or empty lines are ignored.

2. Add your topic or reference text in `text.txt` (UTF-8 encoded).

3. Ensure you have a Google-Gemini API key in either:
     • Environment variable `GEMINI_API_KEY` (recommended) or
     • Hard-coded below by editing the `GEMINI_API_KEY` constant.

4. Install dependencies:
       pip install -r requirements.txt

5. Run the script:
       python post_tweets.py

The script will sequentially:
   • Generate a 240-character tweet (one sentence + 3 hashtags) about the
     text in `text.txt` via Gemini-Pro.
   • Publish it to each Twitter account listed in `accounts.txt`.

Note: Twitter/X may enforce rate limits and stricter rules depending on
      your API tier. Handle responsibly.
"""

from __future__ import annotations

import csv
import os
import sys
import textwrap
from typing import Dict, List

import google.generativeai as genai
import tweepy

# ---------------------------- Configuration -----------------------------
# Replace the placeholder if you prefer hard-coding your key. Otherwise,
# export GEMINI_API_KEY in your shell environment.
GEMINI_API_KEY: str | None = os.getenv("GEMINI_API_KEY", "AIzaSyCagfz85pH3s3vaZlgXYmH-2pD5C99Z7ss")

ACCOUNTS_FILE = "accounts.txt"
TEXT_FILE = "text.txt"

# ---------------------------- Helpers -----------------------------------

def die(message: str, *, code: int = 1) -> None:
    """Print *message* and abort the script."""
    print(f"[ERROR] {message}", file=sys.stderr)
    sys.exit(code)


def load_accounts(path: str = ACCOUNTS_FILE) -> List[Dict[str, str]]:
    """Read API credentials from *path* and return list of dicts."""
    if not os.path.exists(path):
        die(f"Accounts file '{path}' not found.")

    accounts: List[Dict[str, str]] = []
    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.reader(f)
        for ln, row in enumerate(reader, 1):
            # Skip comments / blank lines
            if not row or (row[0].strip().startswith("#")):
                continue
            if len(row) < 4:
                die(f"Line {ln} in '{path}' has fewer than 4 comma-separated fields.")
            ck, cs, at, ats = (cell.strip() for cell in row[:4])
            accounts.append(
                {
                    "consumer_key": ck,
                    "consumer_secret": cs,
                    "access_token": at,
                    "access_token_secret": ats,
                }
            )
    if not accounts:
        die("No valid accounts found in accounts.txt.")
    return accounts


def load_base_text(path: str = TEXT_FILE) -> str:
    if not os.path.exists(path):
        die(f"Base text file '{path}' not found.")
    with open(path, "r", encoding="utf-8") as f:
        content = f.read().strip()
    if not content:
        die("text.txt is empty.")
    return content


def setup_gemini(api_key: str) -> genai.GenerativeModel:
    """Initialise Gemini model and return it."""
    genai.configure(api_key=api_key)
    try:
        # استفاده مستقیم از مدل پیشنهادی gemini-1.5-flash
        model_name = "gemini-1.5-flash"
        print(f"Using model: {model_name}")
        model = genai.GenerativeModel(model_name)
    except Exception as exc:  # pragma: no cover
        die(f"Failed to initialise Gemini API: {exc}")
    return model


def generate_tweet(model: genai.GenerativeModel, prompt_subject: str) -> str:
    """Generate a tweet max 240 chars incl. 3 hashtags using Gemini."""
    prompt = textwrap.dedent(
        f"""
        متن زیر را در نظر بگیر:
        ---
        {prompt_subject}
        ---
        بر اساس این متن، یک جمله حداکثر 240 کاراکتری بساز که
        دقیقا سه هشتگ مرتبط به انتهای آن اضافه شده باشد.
        از نقل قول و مارک‌داون استفاده نکن. فقط یک جمله بده.
        خروجی باید قابل انتشار در توییتر باشد (۲۴۰ نویه حداکثر).
        """
    ).strip()

    try:
        response = model.generate_content(prompt)
    except Exception as exc:  # pragma: no cover
        die(f"Gemini API error: {exc}")

    tweet = response.text.strip()
    # Clean markdown formatting that Gemini might still add.
    if tweet.startswith("```") and tweet.endswith("```"):
        tweet = tweet.strip("`\n")
    tweet = tweet.replace("\n", " ").strip()

    # Enforce length <= 240; if longer, truncate with ellipsis.
    if len(tweet) > 240:
        tweet = tweet[:237] + "…"
    return tweet


def post_to_twitter(account: Dict[str, str], text: str) -> None:
    """Publish *text* using Tweepy under *account* credentials."""
    auth = tweepy.OAuth1UserHandler(
        account["consumer_key"],
        account["consumer_secret"],
        account["access_token"],
        account["access_token_secret"],
    )
    api = tweepy.API(auth)
    try:
        api.update_status(status=text)
    except Exception as exc:  # pragma: no cover
        print(f"[WARNING] Failed to tweet for account {account['consumer_key'][:4]}…: {exc}")
        return
    print(f"[OK] Tweet posted for account {account['consumer_key'][:4]}…")


# ---------------------------- Main flow ---------------------------------

def main() -> None:  # pragma: no cover
    # تنظیم کدگذاری کنسول ویندوز برای پشتیبانی بهتر از یونیکد
    import io
    import sys
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='backslashreplace')
    
    if not GEMINI_API_KEY:
        die("GEMINI_API_KEY is not set. Set environment variable or modify the script.")

    accounts = load_accounts()
    base_text = load_base_text()
    model = setup_gemini(GEMINI_API_KEY)

    print(f"Loaded {len(accounts)} accounts. Generating tweets…")
    for idx, account in enumerate(accounts, 1):
        print(f"\n[{idx}/{len(accounts)}] Generating tweet …", end=" ", flush=True)
        tweet_text = generate_tweet(model, base_text)
        print("done.")
        try:
            print(f"Tweet preview: {tweet_text}\nLength: {len(tweet_text)}")
        except UnicodeEncodeError:
            print(f"Tweet preview: [contains special characters]\nLength: {len(tweet_text)}")
        post_to_twitter(account, tweet_text)

    print("\nAll done.")


if __name__ == "__main__":
    main()
