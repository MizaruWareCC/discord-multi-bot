import discord
from discord.ext import commands
import os
from dotenv import load_dotenv
import aiosqlite
import asyncpg

load_dotenv()

async def tickets_prepare():
    async with aiosqlite.connect('economy.db') as conn:
        await conn.execute('CREATE TABLE IF NOT EXISTS economy(user_id PRIMARY KEY, money)')
        await conn.execute('CREATE TABLE IF NOT EXISTS bank(user_id PRIMARY KEY, balance, time)')
        await conn.commit()
    async with aiosqlite.connect('tags.db') as conn:
        await conn.execute('CREATE TABLE IF NOT EXISTS tags(user_id, name UNIQUE, guild_id, text)')
        await conn.commit()
    async with aiosqlite.connect('punishments.db') as conn:
        await conn.execute('create table if not exists warnings(waring_id INTEGER PRIMARY KEY AUTOINCREMENT, user_id, guild_id, reason, moder_id)')
        await conn.commit()
    async with aiosqlite.connect('robloxcookies.db') as conn:
        await conn.execute('CREATE TABLE IF NOT EXISTS cookies(discord_id INTEGER PRIMARY KEY, cookie)')
        await conn.commit()
    async with aiosqlite.connect('roblox_users_saved.db') as conn:
        await conn.execute('CREATE TABLE IF NOT EXISTS users(discord_id, name, reason)')
        await conn.commit()
    async with aiosqlite.connect('suggestions.db') as conn:
        await conn.execute('CREATE TABLE IF NOT EXISTS suggestions(id INTEGER PRIMARY KEY AUTOINCREMENT, user_id, suggestion, status)')
        await conn.execute('CREATE TABLE IF NOT EXISTS bans(id INTEGER PRIMARY KEY AUTOINCREMENT, user_id UNIQUE, reason)')
        await conn.commit()

async def load_cogs():
    for filename in os.listdir('./cogs'):
        if filename.endswith('.py'):
            await bot.load_extension(f'cogs.{filename[:-3]}')
    await bot.load_extension('jishaku')

class bot_(commands.Bot):   
    async def setup_hook(self):
        self.pool = {}
        self.ticketdb: asyncpg.Connection = await asyncpg.connect('postgresql://dbot@localhost/tickets')
        await self.ticketdb.execute('CREATE TABLE IF NOT EXISTS tickets(guild_id BIGINT, channel_id BIGINT, user_id BIGINT)')
        await self.ticketdb.execute('CREATE TABLE IF NOT EXISTS settings(guild_id BIGINT PRIMARY KEY, moderation_role BIGINT, allowed_role BIGINT)')
        self.remove_command('help')
        await load_cogs()
        await tickets_prepare()


intents = discord.Intents.all()
intents.members = True
intents.messages = True

PREFIX_LIST = ['>', '?']

bot = bot_(command_prefix=PREFIX_LIST, intents=intents)
bot.strip_after_prefix = True

@bot.tree.context_menu(name='Report message')
async def message_report(interaction: discord.Integration, message: discord.Message):
    embed = discord.Embed(title='Report submitted', description='We recived you report!')
    embed.add_field(name='Message content', value=message.content[:1000]+'...')
    await interaction.response.send_message(embed=embed, ephemeral=True)



bot.run(os.getenv('TOKEN'))