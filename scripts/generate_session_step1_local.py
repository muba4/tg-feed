"""
Run this script ONCE locally to initiate Telegram authentication
and obtain partial session data and phone code hash.

This corresponds to the first part of the session generation process.
Use the generated values in 'generate_session_step2_local.py'.

Steps:
  1. Get API credentials: https://my.telegram.org   → Apps → create app
  2. (Optional) Create .env file based on .env.example with your credentials
  3. Run: pip install telethon python-dotenv
  4. Run: python scripts/generate_session_step1_local.py
  5. Enter your phone number when prompted (or set TELEGRAM_PHONE in .env)
  6. Check Telegram for the login code
  7. Copy the generated .env entries for STEP2
  8. Run 'python scripts/generate_session_step2_local.py' and follow its prompts.

Note: The account must be a member of the comments group (loaderfromSVOchat)
to be able to read comments later.
"""

import asyncio
import os
from dotenv import load_dotenv
from telethon import TelegramClient
from telethon.sessions import StringSession

# Загружаем переменные из .env файла (если он существует)
load_dotenv()

# Получаем API ID и HASH из переменных окружения или .env
# Если они не установлены, запрашиваем у пользователя
api_id_input = os.environ.get("TELEGRAM_API_ID") or input("Enter API_ID (or set TELEGRAM_API_ID in .env): ")
try:
    API_ID = int(api_id_input)
except ValueError:
    print("Invalid API_ID provided. Please enter a valid number.")
    exit(1)

API_HASH = os.environ.get("TELEGRAM_API_HASH") or input("Enter API_HASH (or set TELEGRAM_API_HASH in .env): ")

# Получаем номер телефона из переменной окружения или .env
# Если не установлен, запрашиваем у пользователя
PHONE = os.environ.get("TELEGRAM_PHONE") or input("Enter your phone number (or set TELEGRAM_PHONE in .env): ")


async def main():
    print("\nInitiating connection with user account using API ID:", API_ID)
    print("Sending code request to Telegram...\n")

    client = TelegramClient(StringSession(), API_ID, API_HASH)
    await client.connect()

    # Проверяем, нужна ли авторизация
    if not await client.is_user_authorized():
        # Отправляем код на указанный номер и сохраняем результат
        sent_response = await client.send_code_request(PHONE)
        print(f"Code sent to {PHONE}. Please check your Telegram app for the 5-6 digit code.\n")

        # Выводим partial_session и phone_code_hash в формате .env
        partial_session = client.session.save()
        phone_code_hash = sent_response.phone_code_hash

        print("--- COPY THE FOLLOWING LINES TO YOUR .env FILE ---")
        print("# Data for Step 2 script (generate_session_step2_local.py)")
        # Выводим без repr() и без кавычек, чтобы можно было напрямую скопировать
        print(f"STEP2_PARTIAL_SESSION={partial_session}")
        print(f"STEP2_PHONE_CODE_HASH={phone_code_hash}")
        print("# Now run 'python scripts/generate_session_step2_local.py'")
        print("# It will ask for the code received in Telegram.")
        print("--- END OF LINES TO COPY ---\n")

        print("IMPORTANT: After copying, paste these lines into your .env file.")
        print("Then, run 'python scripts/generate_session_step2_local.py'.")
        print("That script will read the values from .env and prompt for the Telegram code.")
        print("After completion, it will print the final TELEGRAM_SESSION_STR.")
    else:
        print("Client is already authorized. No need to send code.")
        # Если уже авторизован, можно получить строку сессии, но это не часть Step 1 для нового входа
        session_string = client.session.save()
        print("Current session string (not needed for new login):")
        print(session_string)

    await client.disconnect()
    print("\nStep 1 completed. Remember to run Step 2 script.")


asyncio.run(main())
