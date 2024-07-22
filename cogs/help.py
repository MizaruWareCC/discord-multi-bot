import discord
from discord.ext import commands

class help(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.group(name='help', invoke_without_command=True)
    async def help(self, ctx):
        await ctx.send('Please select from categories: economy, ticket, moderation, tag.')

    # @help.command(name='economy', aliases=['eco'])
    # async def economy_help(self, ctx):
    #     embed = discord.Embed(title='Economy Commands', color=discord.Color.blue())
    #     embed.add_field(name='work', value='Work to earn money.', inline=False)
    #     embed.add_field(name='transfer (or tr) [user] [amount]', value='Transfer money to another user.', inline=False)
    #     embed.add_field(name='remove_cooldown (or rcd or removecd) [user]', value='Remove work cooldown for a user.', inline=False)
    #     embed.add_field(name='rob [user]', value='Rob person with 1/5 chance.', inline=False)
    #     embed.add_field(name='set_balance (or sb, or setb) [user] [amount]', value='Set money for user.', inline=False)
    #     embed.add_field(name='balance (or bal or money) [user]', value='Check user balance.', inline=False)
    #     embed.add_field(name='allornothing (or 50/50)', value='Youll triple your balance or lose all, 50/50 chance.', inline=False)
    #     embed.add_field(name='bet [amount]', value='2/3 chance to win your amount, or lose.', inline=False)
    #     await ctx.send(embed=embed)


    @help.command(name='ticket')
    async def ticket_help(self, ctx):
        embed = discord.Embed(title='Ticket Commands', color=discord.Color.green())
        embed.add_field(name='create', value='Create a new ticket.', inline=False)
        embed.add_field(name='remove_cd (or rcd or remcd or removecd) [user]', value='Remove cooldown for creating tickets.', inline=False)
        embed.add_field(name='confiruge (or cfg or config)', value='Configure ticket settings.', inline=False)
        await ctx.send(embed=embed)

    @help.command(name='moderation', aliases=['mod'])
    async def moderation_help(self, ctx):
        embed = discord.Embed(title='Moderation Commands', color=discord.Color.red())
        embed.add_field(name='kick [user] reason', value='Kick a member from the server.', inline=False)
        embed.add_field(name='ban [user] reason', value='Ban a member from the server.', inline=False)
        embed.add_field(name='mute [user] reason', value='Mute a member for a specified duration.', inline=False)
        embed.add_field(name='unmute [user]', value='Unmute a muted member.', inline=False)
        await ctx.send(embed=embed)
    
    @help.command(name='tag', aliases=['tags'])
    async def tag_help(self, ctx):
        embed = discord.Embed(title='Tag commands', color=discord.Color.magenta())
        embed.add_field(name='tag create [name]', value='Creates a tag.', inline=False)
        embed.add_field(name='tag update [name] [text]', value='Update tag text.', inline=False)
        embed.add_field(name='get_owner (or gw) [tag]', value='Get a user that created tag.', inline=False)
        embed.add_field(name='delete [tag]', value='Deletes your tag.', inline=False)

        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(help(bot))