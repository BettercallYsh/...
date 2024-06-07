from aiohttp import web
from pyrogram import Client
from .route import routes
from config import API_HASH, APP_ID, LOGGER, TG_BOT_TOKEN, TG_BOT_WORKERS, PORT

async def web_server():
    # Initialize Pyrogram client
    bot = Client(
        name="Bot",
        api_hash=API_HASH,
        api_id=APP_ID,
        bot_token=TG_BOT_TOKEN,
        workers=TG_BOT_WORKERS
    )

    # Start Pyrogram client
    await bot.start()

    # Create aiohttp web application
    web_app = web.Application(client_max_size=30000000)
    web_app["bot"] = bot  # Store bot instance in app for later access
    web_app.add_routes(routes)

    return web_app
