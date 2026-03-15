"""
Complete Telegram authentication locally using partial session data.

This script simulates the second step of Telegram session generation
that would normally happen in GitHub Actions, but runs locally using
credentials from .env file.

Steps:
1. Run 'generate_session.py' to get 'partial_session' and 'phone_code_hash'.
2. Enter the code received in Telegram.
3. Run this script.
4. Provide the required data when prompted or set them in .env.
5. Copy the resulting TELEGRAM_SESSION_STR.

Prerequisites:
- pip install telethon python-dotenv
- A .env file with TELEGRAM_API_ID, TELEGRAM_API_HASH, TELEGRAM_PHONE
  (or set them as environment variables).
- The 'partial_session' and 'phone_code_hash' from Step 1.
"""

import asyncio
import os
from dotenv import load_dotenv
from telethon import TelegramClient
from telethon.sessions import StringSession
from telethon.errors import SessionPasswordNeededError

# Load environment variables from .env file
load_dotenv()

# --- Get credentials from environment or .env ---
API_ID = int(os.environ.get("TELEGRAM_API_ID"))
API_HASH = os.environ.get("TELEGRAM_API_HASH")
PHONE = os.environ.get("TELEGRAM_PHONE")

if not all([API_ID, API_HASH, PHONE]):
    print("Error: TELEGRAM_API_ID, TELEGRAM_API_HASH, or TELEGRAM_PHONE not found in environment or .env file.")
    exit(1)

# --- Get data from user input or environment ---
PARTIAL_SESSION = os.environ.get("STEP2_PARTIAL_SESSION") or input("Enter PARTIAL_SESSION from Step 1: ").strip()
PHONE_CODE_HASH = os.environ.get("STEP2_PHONE_CODE_HASH") or input("Enter PHONE_CODE_HASH from Step 1: ").strip()
CODE = os.environ.get("STEP2_CODE") or input("Enter the code received in Telegram: ").strip()
# Optional: 2FA password
PASSWORD = os.environ.get("STEP2_PASSWORD") or input("Enter 2FA password (if applicable, otherwise press Enter): ").strip()
if not PASSWORD:
    PASSWORD = None # Ensure it's None, not an empty string, for the script logic


async def main():
    print(f"\nCompleting authentication for phone: {PHONE}")
    print("Using API ID, Hash, and Phone from .env or environment variables.\n")

    client = TelegramClient(
        StringSession(PARTIAL_SESSION),
        API_ID,
        API_HASH,
    )
    await client.connect()

    try:
        await client.sign_in(
            PHONE,
            CODE,
            phone_code_hash=PHONE_CODE_HASH,
        )
    except SessionPasswordNeededError:
        if PASSWORD is None:
            print("ERROR: 2FA password is required but not provided.")
            print("Set STEP2_PASSWORD in your .env file or provide it when prompted.")
            await client.disconnect()
            return
        print("2FA password required, signing in...")
        await client.sign_in(password=PASSWORD)

    me = await client.get_me()
    session = client.session.save()
    await client.disconnect()

    print("\n" + "=" * 60)
    print("SUCCESS! Your session string (add as GitHub Secret):")
    print("=" * 60)
    print(session)
    print("=" * 60)
    print("\nSecret name: TELEGRAM_SESSION_STR")
    print("Go to: GitHub repo → Settings → Secrets and variables → Actions → New repository secret")


if __name__ == "__main__":
    asyncio.run(main())
