import discord
from discord.ext import commands
from discord.ext.commands import has_permissions
import datetime
import aiosqlite

class moderation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def gwarn(self, user_id, guild_id, reason, moder_id):
        async with aiosqlite.connect('punishments.db') as conn:
            await conn.execute('INSERT INTO warnings(user_id, guild_id, reason, moder_id) VALUES (?,?,?,?)', (user_id, guild_id, reason, moder_id))
    
    def compare_roles(self, target, member):
        if target.top_role.position <= member.top_role.position:
            return False
        return True


    @commands.command()
    @has_permissions(kick_members=True)
    async def kick(self, ctx, member: discord.Member, *, reason='No reason was provided.'):
        if self.compare_roles(ctx.auhor.id, member) == False:
            await ctx.send('You cannot do this to someone with a higher/same role than you.')
            return
        if self.compare_roles(ctx.guild.me, member) == False:
            await ctx.send('Bot have lower role than person you are trying to moderate.')
            return
        if member.id == ctx.author.id:
            await ctx.send('You cannot kick yourself.')
            return
        await member.kick(reason=reason)
        await ctx.send(f'{member.mention} has been kicked.')

    @commands.command()
    @has_permissions(ban_members=True)
    async def ban(self, ctx, member: discord.Member, *, reason='No reason was provided'):
        if ctx.author.top_role.position <= member.top_role.position:
            await ctx.send('You cannot do this to someone with a higher/same role than you.')
            return
        if self.compare_roles(ctx.guild.me, member) == False:
            await ctx.send('Bot have lower role than person you are trying to moderate.')
            return
        if member.id == ctx.author.id:
            await ctx.send('You cannot ban yourself.')
            return
        await member.ban(reason=reason, delete_message_days=0)
        await ctx.send(f'{member.mention} has been banned.')

    @commands.command()
    @has_permissions(mute_members=True)
    async def mute(self, ctx, member: discord.Member, time: str, *, reason='No reason was provided'):
        if ctx.author.top_role.position <= member.top_role.position:
            await ctx.send('You cannot do this to someone with a higher/same role than you.')
            return
        if self.compare_roles(ctx.guild.me, member) == False:
            await ctx.send('Bot have lower role than person you are trying to moderate.')
            return
        if member.id == ctx.author.id:
            await ctx.send('You cannot mute yourself.')
        try:
            if 's' in time:
                time = time.replace('s', '')
                await member.timeout(datetime.timedelta(seconds=int(time)), reason=reason)
                await ctx.send(f'{member.mention} has been muted for {time} seconds.')
            elif 'm' in time:
                time = time.replace('m', '')
                await member.timeout(datetime.timedelta(minutes=int(time)), reason=reason)
                await ctx.send(f'{member.mention} has been muted for {time} minutes.')
            elif 'h' in time:
                time = time.replace('h', '')
                await member.timeout(datetime.timedelta(hours=int(time)), reason=reason)
                await ctx.send(f'{member.mention} has been muted for {time} hours.')
            elif 'd' in time:
                time = time.replace('d', '')
                await member.timeout(datetime.timedelta(days=int(time)), reason=reason)
                await ctx.send(f'{member.mention} has been muted for {time} days.')
            elif 'w' in time:
                time = time.replace('w', '')
                await member.timeout(datetime.timedelta(weeks=int(time)), reason=reason)
                await ctx.send(f'{member.mention} has been muted for {time} weeks')
            else:
                await ctx.send(f"Invalid time format! {time}. We only support: s, m, h, d, w.")
                return
        except Exception as e:
            await ctx.send(f"Invalid time!")

    @commands.command()
    @has_permissions(mute_members=True)
    async def unmute(self, ctx, member: discord.Member):
        await member.timeout(datetime.timedelta(seconds=0))
        await ctx.send(f'{member.mention} has been unmuted.')

    @commands.command()
    @has_permissions(manage_messages=True)
    async def clear(self, ctx, amount: int):
        if amount > 500:
            await ctx.send('Max amount is 500!')
            return
        await ctx.channel.purge(limit=amount)
        await ctx.send('Done!')

    @commands.group(name='warnings', aliases=['warn'], invoke_withour_command=True)
    @has_permissions(administrator=True)
    async def warn(self, ctx, member: discord.Member=None, *reason: str):
        if not member:
            await ctx.send('Warning system for this bot! Please use help warnings for more')
            return
        await self.gwarn(member.id, ctx.guild.id, reason, ctx.author.id)
        warn_embed = discord.Embed(title='Warnings')
        warn_embed.add_field(name='Reason', value=reason)
        warn_embed.add_field(name='Moderator', value=ctx.author.mention)

        await ctx.send(embed=warn_embed)

        


async def setup(bot):
    await bot.add_cog(moderation(bot))