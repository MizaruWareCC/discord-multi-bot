from discord.ext import commands
import traceback
import asyncio
from discord import Embed
import discord

class listener(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener('on_command_error')
    async def on_command_error(self, ctx, error):
        if isinstance(error, commands.CommandOnCooldown):
            embed = Embed(title='Cooldown', description='Command is in cooldown', color=discord.Color.dark_gold())
            retry_after_seconds = error.retry_after

            weeks, remainder = divmod(int(retry_after_seconds), 604800)
            days, remainder = divmod(remainder, 86400)
            hours, remainder = divmod(remainder, 3600)
            minutes, seconds = divmod(remainder, 60)

            cooldown_message = ""

            if weeks > 0:
                cooldown_message += f"{weeks} week{'s' if weeks > 1 else ''} "
            if days > 0:
                cooldown_message += f"{days} day{'s' if days > 1 else ''} "
            if hours > 0:
                cooldown_message += f"{hours} hour{'s' if hours > 1 else ''} "
            if minutes > 0:
                cooldown_message += f"{minutes} minute{'s' if minutes > 1 else ''} "
            if seconds >= 0:
                cooldown_message += f"{seconds} second{'s' if seconds > 1 else ''}"

            embed.add_field(name='Expires', value=cooldown_message)

            msg = await ctx.send(embed=embed)
            if retry_after_seconds > 20:
                return
            
            await asyncio.sleep(retry_after_seconds)
            await msg.delete()
            
            
        
        elif isinstance(error, commands.MissingRequiredArgument):
            await ctx.send(f'Missing required arguments.')
        elif isinstance(error, commands.BadArgument):
            await ctx.send(f'Bad argument! Please provide valid argument for command.')
        elif isinstance(error, commands.CommandNotFound):
            pass
        elif isinstance(error, commands.MissingPermissions):
            await ctx.send(f'You dont have permission to use this command.')
        elif isinstance(error, commands.BotMissingPermissions):
            await ctx.send(f'Bot dont have permission to do this.')
        else:
            traceback.print_exception(error)

async def setup(bot):
    await bot.add_cog(listener(bot))