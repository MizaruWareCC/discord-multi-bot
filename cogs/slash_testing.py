import discord
from discord.ext import commands
from discord import app_commands

class slash_testing(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    



async def setup(bot: commands.Bot):
    await bot.add_cog(slash_testing(bot))