import discord
import os
import aiohttp
import aiosqlite
from typing import Iterable, Optional


WHITELISTED_IDS = [757963924363542638, 826495966176739368]

JEYY_TOKEN = os.getenv('JEYY_TOKEN')
JEYY_URL = "https://api.jeyy.xyz/v2/"


async def message_from_reference(bot, reference: discord.MessageReference):
    try:
        msg = await bot.fetch_channel(reference.channel_id)
        msg = await msg.fetch_message(reference.message_id)
    except AttributeError:
        msg = None
    finally:
        return msg

async def jeyy(image_url: str, endpoint: str):
    async with aiohttp.ClientSession() as session:
        async with session.get(JEYY_URL+f'image/{endpoint}', headers={'Authorization': 'Bearer '+JEYY_TOKEN}, params={'image_url': image_url}) as response:
            return await response.read()

async def get_cookie(discord_id: int):
    try:
        async with aiosqlite.connect('robloxcookies.db') as conn:
            row = await conn.execute('SELECT cookie FROM cookies WHERE discord_id = ?', (discord_id,))
            cookie = await row.fetchone()
        if cookie is not None:
            return cookie[0]
        else: 
            return None
    except Exception as e:
        print("Error in get_cookie function:", e)
        raise e

