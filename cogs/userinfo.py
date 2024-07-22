import discord
from discord.ext import commands

class UserInfo:
    @classmethod
    async def convert(cls, ctx, argument):
        member = await commands.MemberConverter().convert(ctx, argument)
        return cls(member, ctx.author, ctx)
    
    def __init__(self, user: discord.Member, sender: discord.Member, ctx: commands.Context):
        self.user: discord.Member = user
        self.sender: discord.Member = sender
        self.ctx: commands.Context = ctx
    
    async def embeds(self):
        embed1 = discord.Embed(title=self.user.display_name)
        embed1.set_author(name=self.sender.display_name)
        embed1.set_image(url=self.user.avatar.url)
        embed2 = discord.Embed(title='Roles')
        rl = [role.name for role in self.user.roles]
        rl.reverse()
        roles = '\n'.join(rl)
        embed2.add_field(name="Roles", value=roles[:1024])
        return [embed1, embed2]

class info(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def info(self, ctx, user: UserInfo):
        await ctx.send(embeds=await user.embeds())


async def setup(bot):
    await bot.add_cog(info(bot))