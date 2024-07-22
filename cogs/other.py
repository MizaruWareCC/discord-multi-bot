import discord
from discord.ext import commands


class ReactButton(discord.ui.View):
    def __init__(self, ctx):
        super().__init__(timeout=None)
        for item in self.children:
            print(f"{item.disabled}")
        
        self.ctx = ctx

    async def interaction_check(self, interaction) -> bool:
        return interaction.user.id == self.ctx.author.id

    @discord.ui.button(emoji="📜", label="Role", style=discord.ButtonStyle.success,
                       custom_id='persistent_verify:react_button')
    async def react_click(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer(ephemeral=False)
        await interaction.followup.send("Hi buddy!")

class other(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.command()
    async def view(self, ctx):
        await ctx.send(view=ReactButton(ctx))



async def setup(bot):
    await bot.add_cog(other(bot))