import os

API_HASH = os.getenv("API_HASH", "your_api_hash_here")
APP_ID = int(os.getenv("APP_ID", "your_app_id_here"))
TG_BOT_TOKEN = os.getenv("TG_BOT_TOKEN", "your_bot_token_here")
TG_BOT_WORKERS = int(os.getenv("TG_BOT_WORKERS", 4))
FORCE_SUB_CHANNEL = os.getenv("FORCE_SUB_CHANNEL", None)
CHANNEL_ID = int(os.getenv("CHANNEL_ID", "your_channel_id_here"))
PORT = int(os.getenv("PORT", 8080))
MONGO_URI = os.getenv("MONGO_URI", "your_mongo_uri_here")
DATABASE_NAME = os.getenv("DATABASE_NAME", "telegram_bot")

def LOGGER(name):
    import logging
    logging.basicConfig(level=logging.INFO)
    return logging.getLogger(name)
