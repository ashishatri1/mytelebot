import os
import importlib
import asyncio
import logging
import sys
from telethon import events, Button
from telethon import TelegramClient
from telethon.tl.types import PeerChannel
from logging.handlers import RotatingFileHandler
from config import API_ID, API_HASH, TOKENS

from bot import app


logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s - %(levelname)s] - %(name)s - %(message)s",
    datefmt="%d-%b-%y %H:%M:%S",
    handlers=[
        RotatingFileHandler("log.txt", maxBytes=5000000, backupCount=10),
        logging.StreamHandler(),
    ],
)

log = logging.getLogger("Bot")

if __name__ == "__main__":
    if not API_ID or not API_HASH or not TOKENS or not isinstance(TOKENS, list) or len(TOKENS) == 0:
        log.error("❌ Invalid configuration! Please ensure 'API_ID', 'API_HASH', and 'TOKENS' are correctly set in 'config.py'.")
        sys.exit(1)

    for root, _, files in os.walk("plugins"):
        for file in files:
            if file.endswith(".py") and not file.startswith("__"):
                module_path = os.path.join(root, file).replace(os.sep, ".").removesuffix(".py")
                importlib.import_module(module_path)


    loop = asyncio.get_event_loop()
    loop.run_until_complete(app.start())
