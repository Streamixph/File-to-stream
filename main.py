import asyncio
import os
from pyrogram import idle
from traceback import format_exc

# Apne project ke components ko import karo
from bot import bot, initialize_clients
from database import db
from webserver import app # webserver.py se FastAPI app ko import karo
import uvicorn

# Uvicorn server ko configure karo
PORT = int(os.environ.get("PORT", 8000))
config = uvicorn.Config(app=app, host='0.0.0.0', port=PORT)
server = uvicorn.Server(config)


async def start_services():
    """Poore application ko start karne wala main function."""
    print("--- Starting All Services ---")
    try:
        # Step 1: Database se connect karo
        await db.connect()

        # Step 2: Main Pyrogram bot ko start karo
        print("Starting main bot instance...")
        await bot.start()
        print("Main bot started successfully.")

        # Step 3: Storage channel ko cache karo (sabse zaroori fix)
        from config import Config
        try:
            print(f"Attempting to get info for STORAGE_CHANNEL ({Config.STORAGE_CHANNEL}) to cache it...")
            await bot.get_chat(Config.STORAGE_CHANNEL)
            print("✅ Channel info cached successfully. Bot is ready.")
        except Exception as e:
            print(f"!!! FATAL STARTUP ERROR: Could not get channel info. Error: {e}")
            print("!!! TROUBLESHOOTING: Make sure BOT_TOKEN and STORAGE_CHANNEL are correct, and the bot is an ADMIN in the channel.")
            return # Agar yeh fail ho toh aage mat badho

        # Step 4: Baaki multi-client bots ko start karo
        print("Initializing multi-clients...")
        await initialize_clients(bot)

        # Step 5: Web server ko background me chalao
        print(f"Starting web server on port {PORT}...")
        asyncio.create_task(server.serve())

        # Step 6: Bot ko chalta rakho
        print("✅ All services started successfully! Bot is now idle and waiting for tasks.")
        await idle()

    except Exception:
        print(f"An error occurred during startup: {format_exc()}")

async def stop_services():
    """Application ko aaram se band karne wala function."""
    print("--- Stopping All Services ---")
    try:
        if bot.is_initialized:
            await bot.stop()
        await db.disconnect()
        print("✅ Services stopped gracefully.")
    except Exception:
        print(f"An error occurred during shutdown: {format_exc()}")


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(start_services())
    except KeyboardInterrupt:
        print("Service stopping due to KeyboardInterrupt...")
    finally:
        loop.run_until_complete(stop_services())
