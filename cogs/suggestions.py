import discord
from discord.ext import commands
from discord import app_commands
from typing import Optional
from discord import ui
import traceback
import aiosqlite
import datetime
from .utils.paginator import Paginator


class Modal(ui.Modal, title='Suggestion'):
    suggestion = ui.TextInput(label='Suggestion', placeholder='What do you wanna see in this bot?')

    async def on_submit(self, interaction: discord.Interaction) -> None:
        await interaction.response.send_message('Thanks for your suggestion!', ephemeral=True)
        async with aiosqlite.connect('suggestions.db') as conn:
            await conn.execute('INSERT INTO suggestions(user_id, suggestion, status) VALUES (?,?,?)', (interaction.user.id, self.suggestion.value, 'unsolved'))
            await conn.commit()

class send(ui.View):
    def __init__(self, id: int):
        self.user = id
        super().__init__(timeout=20)
    
    @ui.button(label='Suggestion', style=discord.ButtonStyle.green)
    async def suggestion(self, interaction, button):
        if interaction.user.id != self.user:
            await interaction.response.send_message('You cant do that!', ephemeral=True)
            return
        
        await interaction.response.send_modal(Modal())
    
    async def on_timeout(self):
        self.stop()

        

WHITELIST_IDS = [826495966176739368]



class suggestions(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot


    sub = app_commands.Group(name='suggestion', description='Suggestion system for bot.')
    @sub.command()
    async def create(self, interaction, suggestion: str):
        async with aiosqlite.connect('suggestions.db') as conn:
            row = await conn.execute('SELECT reason FROM bans WHERE user_id = ?', (interaction.user.id,))
            result = await row.fetchone()
            if result:
                await interaction.response.send_message(f'You are banned from suggestions, reason: {result[0]}', ephemeral=True)
                return
            if not suggestion:
                await interaction.response.send_message(view=send(interaction.user.id))
            else:
                await conn.execute('INSERT INTO suggestions(user_id, suggestion, status) VALUES (?,?,?)', (interaction.user.id, suggestion, 'unsolved'))
                await conn.commit()
                
                await interaction.response.send_message('Thanks for your suggestion!', ephemeral=True)
    
    
    
    @sub.command(name='list')
    async def list(self, interaction, user_id: Optional[int]=None):
        async with aiosqlite.connect('suggestions.db') as conn:
            if user_id:
                rows = await conn.execute('SELECT id, suggestion, status FROM suggestions WHERE user_id = ?', (user_id,))
            else:
                rows = await conn.execute('SELECT id, suggestion, status FROM suggestions WHERE user_id = ?', (interaction.user.id,))
            
            result = await rows.fetchall()
        
        if not result:
            await interaction.response.send_message('You/user dont have suggestions', ephemeral=True)
            return
        
        embeds = list()
        for tuple in result:
            embed = discord.Embed(title=f'Suggestion №{tuple[0]}', description=tuple[1])
            embed.add_field(name='Status', value=tuple[2], inline=False)
            embeds.append(embed)

        ctx = await self.bot.get_context(interaction)
        paginator = Paginator(ctx)
        await paginator.send(embeds)
        
 
    
    @sub.command(name='review')
    async def review(self, interaction, id: int, status: Optional[str]='solved'):
        if interaction.user.id not in WHITELIST_IDS:
            return
        
        async with aiosqlite.connect('suggestions.db') as conn:
            row = await conn.execute('SELECT status FROM suggestions WHERE id = ?', (id,))
            result = await row.fetchone()
        
            if not result:
                await interaction.response.send_message('No such suggestion found', ephemeral=True)
                return
            
            await conn.execute('UPDATE suggestions SET status = ? WHERE id = ?', (status, id))
            await conn.commit()
            await interaction.response.send_message('Updated suggestion', ephemeral=True)
    
    @review.autocomplete('id')
    async def autoid(self, interaction: discord.Interaction, curret: str):
        async with aiosqlite.connect('suggestions.db') as conn:
            row = await conn.execute('SELECT id FROM suggestions')
            result = await row.fetchall()
              
        
        
        return [app_commands.Choice(name=str(tuple[0]), value=tuple[0]) for tuple in result][:25] if len(result) != 0 else [ ]
    @review.autocomplete('status')
    async def autostatus(self, interaction: discord.Interaction, curret: str):
        return [
            app_commands.Choice(name="Solved", value="solved"),
            app_commands.Choice(name="Unsolved", value="unsolved"),
            app_commands.Choice(name="In process", value="in process"),
            app_commands.Choice(name="Declined", value="declined")
        ]

    
    @sub.command(name='delete')
    async def delete(self, interaction, id: int):
        if interaction.user.id not in WHITELIST_IDS:
            return

        async with aiosqlite.connect('suggestions.db') as conn:
            row = await conn.execute('SELECT id FROM suggestions WHERE id = ?', (id,))
            result = await row.fetchone()
        
            if not result:
                await interaction.response.send_message('No such suggestion found', ephemeral=True)
                return
            
            await conn.execute('DELETE FROM suggestions WHERE id = ?', (id,))
            await conn.commit()
        
        await interaction.response.send_message('Deleted suggestion', ephemeral=True)

    @delete.autocomplete('id')
    async def autodeleteid(self, interaction: discord.Interaction, curret: str):
        async with aiosqlite.connect('suggestions.db') as conn:
            row = await conn.execute('SELECT id FROM suggestions')
            result = await row.fetchall()
              
        
        
        return [app_commands.Choice(name=str(tuple[0]), value=tuple[0]) for tuple in result][:25] if len(result) != 0 else [ ]

    @sub.command(name='all')
    async def all(self, interaction, status: Optional[str]='any'):
        if interaction.user.id not in WHITELIST_IDS:
            return
        async with aiosqlite.connect('suggestions.db') as conn:
            if status == 'any':
                rows = await conn.execute('SELECT id, suggestion, status, user_id FROM suggestions')
            else:
                rows = await conn.execute('SELECT id, suggestion, status, user_id FROM suggestions WHERE status=?', (status,))
            
            result = await rows.fetchall()
        
        if not result:
            await interaction.response.send_message('Cant find any suggestions!', ephemeral=True)
            return
        
        embeds = list()
        for tuple in result:
            embed = discord.Embed(title=f'Suggestion №{tuple[0]}', description=tuple[1])
            embed.add_field(name='Status', value=tuple[2], inline=False)
            embed.add_field(name='By', value=f"{tuple[3]} or <@{tuple[3]}>", inline=False)
            embeds.append(embed)

        ctx = await self.bot.get_context(interaction)
        paginator = Paginator(ctx)
        await paginator.send(embeds)
    
    @all.autocomplete('status')
    async def autoallstatus(self, interaction: discord.Interaction, curret: str):
        return [
            app_commands.Choice(name="Solved", value="solved"),
            app_commands.Choice(name="Unsolved", value="unsolved"),
            app_commands.Choice(name="In process", value="in process"),
            app_commands.Choice(name="Declined", value="declined")
        ]
        
 
    
    @sub.command(name='owner')
    async def owner(self, interaction, id: int):
        async with aiosqlite.connect('suggestions.db') as conn:
            row = await conn.execute('SELECT user_id FROM suggestions WHERE id = ?', (id,))
            result = await row.fetchone()
        
            if not result:
                await interaction.response.send_message('No such suggestion found', ephemeral=True)
                return
            
        await interaction.response.send_message(f'Id: {result[0]}, <@{result[0]}>')
    
    @owner.autocomplete('id')
    async def autoownerid(self, interaction: discord.Interaction, curret: str):
        async with aiosqlite.connect('suggestions.db') as conn:
            row = await conn.execute('SELECT id FROM suggestions')
            result = await row.fetchall()

        return [app_commands.Choice(name=str(tuple[0]), value=tuple[0]) for tuple in result][:25] if len(result) != 0 else []
              
    
    @sub.command(name='ban')
    async def ban(self, interaction, user_id: str, reason: Optional[str]='None'):
        if interaction.user.id not in WHITELIST_IDS:
            return
        
        
        async with aiosqlite.connect('suggestions.db') as conn:
            row = await conn.execute('SELECT reason FROM bans WHERE user_id = ?', (user_id,))
            result = await row.fetchone()
            if result:
                await interaction.response.send_message(f'User already banned, reason: {result[0]}', ephemeral=True)
                return
            
            await conn.execute('INSERT INTO bans(user_id, reason) VALUES (?, ?)', (user_id, reason))
            await conn.commit()
            await interaction.response.send_message('Banned user.', ephemeral=True)
    
        
    
    @sub.command(name='unban')
    async def unban(self, interaction, user_id: str):
        if interaction.user.id not in WHITELIST_IDS:
            return
        
        
        async with aiosqlite.connect('suggestions.db') as conn:
            row = await conn.execute('SELECT reason FROM bans WHERE user_id = ?', (user_id,))
            result = await row.fetchone()
            if not result:
                await interaction.response.send_message(f'User isnt banned.', ephemeral=True)
                return
            
            await conn.execute('DELETE FROM bans WHERE user_id = ?', (user_id, ))
            await conn.commit()
            await interaction.response.send_message('Unbanned user.', ephemeral=True)
    




        




async def setup(bot):
    await bot.add_cog(suggestions(bot))