tkn = ""


import discord
from discord.ext import commands
import json
import aiohttp
pid = 15207127759
uid = 5242709924
WHITELIST_IDS = [826495966176739368]

class opencloud(commands.Cog):
    def __init__(self, bot):
        self.bot: commands.Bot = bot

    @commands.group(invoke_without_command=True)
    async def opcl(self, ctx, *, message: str):
        pass
    
    @opcl.command()
    async def broadcast(self, ctx, *, message: str):
        if ctx.author.id not in WHITELIST_IDS:
            return
        async with aiohttp.ClientSession() as session:
            async with session.post(f"https://apis.roblox.com/messaging-service/v1/universes/{uid}/topics/Announcement", headers={"Content-Type": "application/json", "x-api-key":tkn}, json={"message": message[:1024]}) as resp:
                if resp.status == 200:
                    await ctx.send('Sent announcement!')
                else:
                    await ctx.send(f"Something went wrong.. status: {resp.status}")
    
    @opcl.command()
    async def shutdown(self, ctx):
        if ctx.author.id not in WHITELIST_IDS:
            return
        
        async with aiohttp.ClientSession() as session:
            async with session.post(f"https://apis.roblox.com/messaging-service/v1/universes/{uid}/topics/shutdown", headers={"Content-Type": "application/json", "x-api-key":tkn}, json={"message": "Shutdown"}) as resp:
                if resp.status == 200:
                    await ctx.send('Shutdowned servers!')
                else:
                    await ctx.send(f"Something went wrong.. status: {resp.status}")

    @opcl.command()
    async def kick(self, ctx, name: str, *, reason: str = "Kicked by administrator"):
        if ctx.author.id not in WHITELIST_IDS:
            return
        
        async with aiohttp.ClientSession() as session:
            async with session.post(f"https://apis.roblox.com/messaging-service/v1/universes/{uid}/topics/kick", headers={"Content-Type": "application/json", "x-api-key":tkn}, json={"message": json.dumps({"name": name, "reason": reason})}) as resp:
                if resp.status == 200:
                    await ctx.send('Kicked player!')
                else:
                    await ctx.send(f"Something went wrong.. status: {resp.status}")
    
    @opcl.command()
    async def ban(self, ctx, id: str, *, reason: str = "Banned by administrator"):
        if ctx.author.id not in WHITELIST_IDS:
            return
        
        async with aiohttp.ClientSession() as session:
            async with session.post(f"https://apis.roblox.com/messaging-service/v1/universes/{uid}/topics/ban", headers={"Content-Type": "application/json", "x-api-key":tkn}, json={"message": json.dumps({"id": id, "reason": reason})}) as resp:
                if resp.status == 200:
                    await ctx.send('Banned player!')
                else:
                    await ctx.send(f"Something went wrong.. status: {resp.status}")

    @opcl.command()
    async def unban(self, ctx, id: str, *, reason: str = "Unbanned by administrator"):
        if ctx.author.id not in WHITELIST_IDS:
            return
        
        async with aiohttp.ClientSession() as session:
            async with session.post(f"https://apis.roblox.com/messaging-service/v1/universes/{uid}/topics/unban", headers={"Content-Type": "application/json", "x-api-key":tkn}, json={"message": json.dumps({"id": id, "reason": reason})}) as resp:
                if resp.status == 200:
                    await ctx.send('Unbanned player!')
                else:
                    await ctx.send(f"Something went wrong.. status: {resp.status}")

async def setup(bot: commands.Bot):
    await bot.add_cog(opencloud(bot))