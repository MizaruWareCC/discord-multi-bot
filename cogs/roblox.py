import discord
from .utils.robloxfinder import *
from discord.ext import commands
import datetime
import aiosqlite
from discord import ui
from .utils.utils import get_cookie
import traceback
from .utils.paginator import Paginator
from discord.utils import format_dt as timestamp


class cookiev(ui.View):
    def __init__(self, bot, idz: int):
        self.idz = idz
        self.bot = bot
        super().__init__(timeout=30)

    @ui.button(label='Continiue')
    async def handle(self, interaction, button):
        if interaction.user.id != self.idz:
            await interaction.response.send_message('This isnt for you!', ephemeral=True)
            return
        
        button.disabled = True
        await interaction.response.send_modal(cookie())

    async def on_timeout(self):
        for button in self.children:
            button.disabled = True



class cookie(ui.Modal, title='Paste here your roblox cookies'):
    cookie = ui.TextInput(label='Cookies', placeholder='Cookies here', required=True)

    async def on_submit(self, interaction):
        async with aiosqlite.connect('robloxcookies.db') as conn:
            await conn.execute('INSERT INTO cookies(discord_id, cookie) VALUES (?, ?) ON CONFLICT(discord_id) DO UPDATE SET cookie = ?', (interaction.user.id, '.ROBLOSECURITY='+self.cookie.value, self.cookie.value))
            await conn.commit()
            await interaction.response.send_message("Saved! Thanks.", ephemeral=True)

    async def on_error(self, interaction, error):
        await interaction.response.send_message('Oops! An error occurred, we apologize!', ephemeral=True)
        traceback.print_exc()
 


class roblox(commands.Cog):
    def __init__(self, bot) -> None:
        self.bot = bot
        self.ids = [826495966176739368]

    @commands.command()
    async def roblox(self, ctx, player_name: str, place_id: Optional[int]=None):
        if ctx.author.id not in self.ids:
            await ctx.send('No perm')
            return
        server = RobloxPlayerFinder(ctx.author.id, place_id=place_id, limit=10000)

        

        msg = await ctx.send('Processing...')

        start = discord.utils.utcnow()

        @server.add_listener()
        async def on_find_start(name):
            await msg.edit(content=f'Searching... Elapsed: {timestamp(start, style="R")}')

        @server.add_listener()
        async def on_server_change(server, server_index):
            if server_index%30 == 0:
                await msg.edit(content=f'Searching... Curret server: {server_index}, Elapsed: {timestamp(start, style="R")}')

        @server.add_listener()
        async def on_player_find(server, server_index, id):
            await msg.edit(content=f'Found requested player, server job id: {id}. Server index: {server_index}. Click [here](https://roblox.com/games/{place_id}?serverJobid={id}) to join if you have [extension](https://chromewebstore.google.com/detail/roblox-jobid-join/pdeebkpgdaflejgihpbniammmelkdnac) for joining via jobid')

        @server.add_listener()
        async def on_find_failure(name):
            await msg.edit(content='Failed to find player, check if he is in provided game.')
        
        @server.add_listener()
        async def on_error(error):
            if error=='invaliduser':
                await msg.edit(content='Invalid user.')
            elif error=='invalidplace':
                await msg.edit(content='Invalid place.')
            elif error=='notonline':
                await msg.edit(content='User isnt online.')
            elif error=='notfriends':
                await msg.edit(content='Provide place id, user isnt your friend.')
            
            return
        
        try:
            await server.find_player(player_name)
        except Exception as e:
            traceback.print_exc()
        finally:
            pass

    @commands.command()
    async def getcookie(self, ctx):
        await ctx.send('https://chromewebstore.google.com/detail/cookie-tab-viewer/fdlghnedhhdgjjfgdpgpaaiddipafhgk - download, for roblox find .ROBLOSECURITY and copy it.')
    
    @commands.command()
    async def robloxlisten(self, ctx, player_name: str):
        if ctx.author.id not in self.ids:
            await ctx.send_message('No perm')
            return
        if await is_valid(player_name) == False:
            await ctx.send('Cant find that player')
            return
        
        await ctx.send('Listening...')
        
        await listen(player_name)

        await ctx.send(f'Wooo! Your player joined game {ctx.author.mention}')

    @commands.command()
    async def rid(self, ctx, name):
        await ctx.send(await get_user_id(name) or 'Lil niga no such user')

    @commands.command()
    async def rvalid(self, ctx, name):
        await ctx.send(await is_valid(name))
    
    @commands.command()
    async def rdata(self, ctx, name: str):
        if await is_valid(name) == False:
            await ctx.send('Invalid user nigga')
            return
        
        name = await get_user_id(name)
        
        data = await player_data(id)
        description = data['description']
        created = data['created']
        banned = data['isBanned']
        id = data['id']
        display_name = data['displayName']
        image_url = await player_avatar(id)

        status = await player_status(id)
        game = await player_game(id, ctx.author.id)
        
        embed = discord.Embed(title=name)
        embed.add_field(name='Display name', value=display_name, inline=False)
        embed.add_field(name='Description', value=description, inline=False)
        embed.add_field(name='Id', value=str(id), inline=False)
        embed.add_field(name='Created at', value=datetime.datetime.fromisoformat(created).strftime('%a %d %b %Y, %I:%M%p'), inline=False)
        embed.add_field(name='Banned', value=str(banned))
        if status == 2:
            st = 'In game.'
            embed.add_field(name='Status', value=st, inline=False)
        elif status == 1:
            st = 'Online.'
            embed.add_field(name='Status', value=st, inline=False)
        else:
            st = 'Offline.'
            embed.add_field(name='Status', value=st, inline=False)
        
        if 'gameId' in game and 'placeId' in game:
            embed.add_field(name='Place id', value=game['placeId'], inline=False)
            embed.add_field(name='Job id', value=game['gameId'], inline=False)


        
        
        
        embed.set_thumbnail(url=image_url)
        await ctx.send(embed=embed)
        
    
    @commands.command()
    async def status(self, ctx, name):
        if await is_valid(name) == False:
            await ctx.send('Invalid user nigga')
            return
        status = await player_status(name)
        if status == 2:
            st = 'in game.'
        elif status == 1:
            st = 'online.'
        elif status == 0:
            st = 'offline.'
        await ctx.send(f'User is {st}')
    
    @commands.group(name='cookie', invoke_without_command=True)
    async def cookie(self, ctx):
        id = ctx.author.id
        await ctx.send('READ THIS! You CAN provide your roblox cookies BUT you ARENT REQUIRED and you cookies are only used for roblox API endpoints like >rdata to get their place and job id or >roblox so we dont need to search him because it will give you result if you are friends and he is playing game.\nYou\'r cookies isnt shared to any third-part services and i do not look at them myself.\n\nTo delete your cookies: >cookie delete\n\n\nAny questions about bot: zrxw', view=cookiev(self.bot, id))


    @cookie.command(name='delete')
    async def delete(self, ctx):
        cookie = await get_cookie(ctx.author.id)
        if not cookie:
            await ctx.send("You've got no cookies.")
            return
        
        async with aiosqlite.connect('robloxcookies.db') as conn:
            await conn.execute('DELETE FROM cookies WHERE discord_id = ?', (ctx.author.id,))
            await conn.commit()

        await ctx.send('Done!')

    @commands.command()
    async def friends(self, ctx, name: str):
        if await is_valid(name) == False:
            await ctx.send('Invalid user')
            return
        
        id = await get_user_id(name)

        await ctx.send('This will take a while... We will show only 10 users due to alot of time request on 1 user.')

        limit = 10
        curret = 0
        
        async with aiohttp.ClientSession() as session:
            async with session.get(f'https://friends.roblox.com/v1/users/{id}/friends') as response:
                
                
                js = await response.json()
                js = js['data']

                embeds: list[discord.Embed] = []

                for user in js:
                    curret += 1
                    if limit < curret:
                        break
                    embed = discord.Embed(title=user['name'])
                    data = user
                    description = data['description']
                    created = data['created']
                    banned = data['isBanned']
                    id = data['id']
                    display_name = data['displayName']
                    image_url = await player_avatar(id)


                    embed.set_image(url=image_url)

                    status = await player_status(id)
                    game = await player_game(id, ctx.author.id)
                    
                    embed.add_field(name='Display name', value=display_name, inline=False)
                    embed.add_field(name='Description', value=description, inline=False)
                    embed.add_field(name='Id', value=str(id), inline=False)
                    embed.add_field(name='Created at', value=f"{timestamp(datetime.datetime.fromisoformat(created), style="F")} ({timestamp(datetime.datetime.fromisoformat(created), style="R")})", inline=False)
                    embed.add_field(name='Banned', value=str(banned))
                    if status == 2:
                        st = 'In game.'
                        embed.add_field(name='Status', value=st, inline=False)
                    elif status == 1:
                        st = 'Online.'
                        embed.add_field(name='Status', value=st, inline=False)
                    else:
                        st = 'Offline.'
                        embed.add_field(name='Status', value=st, inline=False)
                    
                    if 'gameId' in game and 'placeId' in game:
                        embed.add_field(name='Place id', value=game['placeId'], inline=False)
                        embed.add_field(name='Job id', value=game['gameId'], inline=False)


                    embeds.append(embed)
        pages = Paginator(ctx)
        await pages.send(embeds)

    @commands.command()
    async def savename(self, ctx, name: str, *, reason: Optional[str]='No reason was provided.'):
        async with aiosqlite.connect('roblox_users_saved.db') as conn:
            await conn.execute('INSERT INTO users VALUES (?, ?, ?)', (ctx.author.id, name, reason))
            await conn.commit()
        
        await ctx.send('Done!')
    
    @commands.command()
    async def loadnames(self, ctx, name: Optional[str]=None):
        if name:
            async with aiosqlite.connect('roblox_users_saved.db') as conn:
                row = await conn.execute('SELECT name, reason FROM users WHERE discord_id = ? AND name=?', (ctx.author.id, name))
                result = await row.fetchone()
            if not result:
                await ctx.send('Cant find that name!')
                return
            
            reason = result[1]
            await ctx.send(f'{name}: {reason}   ')
        else:
            async with aiosqlite.connect('roblox_users_saved.db') as conn:
                row = await conn.execute('SELECT name, reason FROM users WHERE discord_id = ?', (ctx.author.id,))
                result = await row.fetchall()

            if not result:
                await ctx.send('You have 0 saved users.')
                return
            
            embeds = list()
            embed = discord.Embed(title='Names')
            total = 0
            for tuple in result:
                if total < 10:
                    embed.add_field(name=tuple[0], value=tuple[1], inline=False)
                    total += 1
                else:
                    embeds.append(embed)
                    embed = discord.Embed(title='Names')
                    total = 0
                
                if total == len(result):
                    embeds.append(embed)

                

            
            paginator = Paginator(embeds, per_page=5)
            await paginator.start(ctx)
    
    @commands.command()
    async def deletename(self, ctx, name: str):
        async with aiosqlite.connect('roblox_users_saved.db') as conn:
            await conn.execute('DELETE FROM users WHERE name=? AND discord_id=?', (name,ctx.author.id))
            await conn.commit()
        
        await ctx.send('Done!')
    
    @commands.command()
    async def deletenames(self, ctx):
        async with aiosqlite.connect('roblox_users_saved.db') as conn:
            await conn.execute('DELETE FROM users WHERE discord_id=?', (ctx.author.id,))
            await conn.commit()
        
        await ctx.send('Done!')
                











async def setup(bot):
    await bot.add_cog(roblox(bot))