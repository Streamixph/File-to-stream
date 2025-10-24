import asyncio
import uvicorn
from bot import bot, initialize_clients
from webserver import app

async def main():
    # Pehle saare clients (main bot + extra bots) ko start karo
    print("Starting bot and initializing all clients...")
    await bot.start()
    await initialize_clients(bot)
    print("Bot services are ready!")

    # Ab web server ko start karo
    # Uvicorn ko is tarah se chalane se yeh background mein chalta rahega
    # aur bot bhi chalta rahega.
    config = uvicorn.Config(
        app,
        host="0.0.0.0",
        port=8000, # Render by default port 8000 expect karta hai
        log_level="info"
    )
    server = uvicorn.Server(config)
    
    # Dono ko ek saath run karo
    await asyncio.gather(
        server.serve(),
        bot.idle() # Yeh bot ko chalu rakhta hai
    )

if __name__ == "__main__":
    print("Starting application...")
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nShutting down...")
    finally:
        # Jab application band ho, toh bot ko aache se stop karo
        if bot.is_initialized:
            asyncio.run(bot.stop())
            print("Bot stopped.")
