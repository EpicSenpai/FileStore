import asyncio
import logging
import os
import aiohttp
from bot import Bot, web_app
from pyrogram import compose
from config import *

logger = logging.getLogger(__name__)

# HF Space ka public URL (agar env var SPACE_URL set hai to wo use hoga)
PING_URL = os.environ.get("SPACE_URL", "https://epicsenpai-rezefilesbot-v3.hf.space")
PING_INTERVAL = 20 * 60  # 20 minute


async def main():
    app = []

    # Create bot instance using config.py values
    app.append(
        Bot(
            SESSION,
            WORKERS,
            DB_CHANNEL,
            FSUBS,
            TOKEN,
            ADMINS,
            MESSAGES,
            AUTO_DEL,
            DB_URI,
            DB_NAME,
            API_ID,
            API_HASH,
            PROTECT,
            DISABLE_BTN
        )
    )

    await compose(app)


async def self_ping_loop():
    """Bot ko sleep hone se bachane ke liye khud ko ping karta rehta hai."""
    await asyncio.sleep(30)  # startup ke thodi der baad shuru, taaki server ready ho jaaye
    async with aiohttp.ClientSession() as session:
        while True:
            try:
                async with session.get(PING_URL, timeout=aiohttp.ClientTimeout(total=10)) as resp:
                    logger.info(f"Self-ping OK, status: {resp.status}")
            except Exception as e:
                logger.warning(f"Self-ping failed: {e}")
            await asyncio.sleep(PING_INTERVAL)


async def runner():
    await asyncio.gather(
        main(),
        web_app(),
        self_ping_loop()
    )

asyncio.run(runner())
