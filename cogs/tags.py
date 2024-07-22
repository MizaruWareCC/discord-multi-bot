import random
import string
import discord
from discord.ext import commands
from discord.ext.commands import BadArgument
import aiosqlite
from discord.ui import Modal
from discord import ui
from discord.ui import TextInput
from typing import Optional
from .utils.paginator import Paginator

class Tag:
    def __init__(self, name, user_id, guild_id, text):
        self.name = name
        self.user_id = user_id
        self.guild_id = guild_id
        self.text = text
    
    @classmethod
    async def convert(cls, ctx, argument):
        try:
            async with aiosqlite.connect('tags.db') as conn:
                cursor = await conn.execute('SELECT * FROM tags WHERE name = ?', (argument,))
                row = await cursor.fetchone()
                if row:
                    return cls(row[1], row[0], row[2], row[3])
                raise BadArgument('Invalid tag')
        except:
            pass

class TagManager:
    def __init__(self, db_file='tags.db'):
        self.db_file = db_file

    async def tag_exists(self, tag: Tag):
        async with aiosqlite.connect(self.db_file) as conn:
            cursor = await conn.execute('SELECT * FROM tags WHERE name = ? AND guild_id = ?', (tag.name, tag.guild_id))
            row = await cursor.fetchone()
            if not row:
                return False
            return True

    async def get_owner(self, tag: Tag):
        async with aiosqlite.connect(self.db_file) as conn:
            cursor = await conn.execute('SELECT user_id FROM tags WHERE name = ? AND guild_id = ?', (tag.name, tag.guild_id))
            row = await cursor.fetchone()
            if not row:
                return None
            return row[0]

    async def create_tag(self, tag: Tag):
        async with aiosqlite.connect(self.db_file) as conn:
            await conn.execute('INSERT INTO tags VALUES (?,?,?,?) ON CONFLICT DO NOTHING',
                               (tag.user_id, tag.name, tag.guild_id, tag.text))
            await conn.commit()

    async def update_tag(self, old_tag: Tag, new_tag: Tag):
        async with aiosqlite.connect(self.db_file) as conn:
            await conn.execute('UPDATE tags SET name = ?, text = ? WHERE name = ? AND guild_id = ?', (new_tag.name, new_tag.text, old_tag.name, old_tag.guild_id))
            await conn.commit()

    async def delete_tag(self, tag: Tag):
        async with aiosqlite.connect(self.db_file) as conn:
            await conn.execute('DELETE FROM tags WHERE name = ? AND guild_id = ?', (tag.name, tag.guild_id))
            await conn.commit()
 


class create_tag_modal(Modal, title='Tag creation'):
    tag_manager = TagManager()
    tag_name = TextInput(label='Name', max_length=20)
    text = TextInput(label='Text', max_length=2000)
    blacklist_words_name = ['create', 'update', 'get_owner', 'gw', 'delete']

    async def on_submit(self, interaction):
        for word in self.blacklist_words_name:
            if word in self.tag_name.value.lower():
                await interaction.response.send_message('Tag name cannot be: create, delete, get_owner, gw, update.')
                return
        
        if await self.tag_manager.tag_exists(self.tag_name) == True:
            await interaction.response.send_message('Tag name already exists')
            return
        
        await self.tag_manager.create_tag(interaction.user.id, self.tag_name.value, interaction.guild.id, self.text.value)
        await interaction.response.send_message('Done!')

class create_tag_view(ui.View):
    def __init__(self, id):
        super().__init__()
        self.id = id

    @ui.button(label='Continiue')
    async def handler(self, interaction, button):
        if interaction.user.id != self.id:
            await interaction.response.send_message('Not your interaction!', ephemeral=True)
            return
        button.disabled = True
        await interaction.response.send_modal(create_tag_modal())
        await interaction.edit_original_response(view=self)


class tags(commands.Cog):
    def __init__(self, bot):
        self.tag_manager = TagManager()
        self.bot = bot
        self.blacklist_words_name = ['create', 'update', 'get_owner', 'gw', 'delete', 'list']

    @commands.group(name='tag', invoke_without_command=True)
    async def tag(self, ctx, tag: Tag = None):
        if tag is None:
            await ctx.send('Hi! This is tag system. For more use help command.')
            return

        if ctx.invoked_subcommand is None:
            await ctx.send(f'{tag.text}')
        
        

    @tag.command(name='create')
    async def create(self, ctx, tag_name, *, text):
        for word in self.blacklist_words_name:
            if word in tag_name.lower():
                await ctx.send('Tag name cannot be: '+', '.join(self.blacklist_words_name))
                return
        
        try:
            if await self.tag_manager.tag_exists(await Tag.convert(ctx, tag_name)) == True:
                await ctx.send('Tag name already exists')
                return
        except:
            pass
        
        await self.tag_manager.create_tag(Tag(tag_name, ctx.author.id, ctx.guild.id, text))
        await ctx.send('Done!')

    @tag.command(name='get_owner')
    async def get_owner_cmd(self, ctx, tag: Tag):
        if await self.tag_manager.tag_exists(tag) == False:
            await ctx.send('Tag doesnt exists!')
            return
        owner = await self.tag_manager.get_owner(tag)
        member = await ctx.guild.get_member(owner)
        if not member:
            await ctx.send('Owner is not in this guild...')
            return
        await ctx.send(f'Owner is {member.mention}')

    @tag.command(name='delete')
    async def delete(self, ctx, tag: Tag):
        if await self.tag_manager.tag_exists(tag) == False:
            await ctx.send('Tag doesnt exists!')
            return
        
        if ctx.author.id != 826495966176739368:

            if await self.tag_manager.get_owner(tag) != ctx.author.id:
                await ctx.send('You arent owner of the tag!')
                return
        
            
        await self.delete_tag(tag)
        await ctx.send('Done!')

    @tag.command(name='update')
    async def update(self, ctx, tag: Tag, *, text):
        text = ' '.join(text)
        if ctx.author.id != 826495966176739368:
            if await self.tag_manager.get_owner(tag) != ctx.author.id:
                await ctx.send('You arent owner of the tag!')
                return
        for word in self.blacklist_words:
            if word in tag.name.lower():
                await ctx.send('Dont use bad words!')
                return
        
        

        
        await self.tag_manager.update_tag_text(tag, text)
        await ctx.send('Done!')
    
    @tag.command(name='list')
    async def list_tags(self, ctx, user: Optional[int | discord.Member] = None):
        if isinstance(user, discord.Member):
            user = user.id

        valid = True
        if user:
            member = ctx.guild.get_member(user)
            valid = member is not None
        if not valid:
            await ctx.send('Invalid user ID or member mention.')
            return

        async with aiosqlite.connect('tags.db') as conn:
            if user:
                row = await conn.execute('SELECT * FROM tags WHERE user_id = ? AND guild_id = ?', (user, ctx.guild.id))
                result = await row.fetchall()
            else:
                row = await conn.execute('SELECT * FROM tags WHERE guild_id = ?', (ctx.guild.id,))
                result = await row.fetchall()

        if not result:
            await ctx.send('No tags found.')
            return

        
        embeds = list()
        tags_added = 0
        embed = discord.Embed(title="List of Tags", color=0x00ff00)
        for tag_info in result:
            
            if tags_added < 10:
                made_by = ctx.guild.get_member(tag_info[0])
                if made_by:
                    embed.add_field(name=tag_info[1], value=f"Made by {made_by.display_name}", inline=False)
                else:
                    embed.add_field(name=tag_info[1], value=f"Made by Unknown Member", inline=False)
                tags_added += 1            
            else:
                embeds.append(embed)
                embed = discord.Embed(title="List of Tags", color=0x00ff00)
                tags_added = 0
            
            if tags_added == len(result):
                embeds.append(embed)
        

        paginator = Paginator(ctx)
        await paginator.send(embeds)

    @tag.command(name="purge")
    async def purge(self, ctx, amount: Optional[int] = 100, user: Optional[int] = None):
        if ctx.author.id != 826495966176739368:
            return
        
        async with aiosqlite.connect('tags.db') as conn:
            if user:
                await conn.execute('DELETE FROM tags WHERE user_id = ? AND rowid IN (SELECT rowid FROM tags WHERE user_id = ? LIMIT ?)', (user, user, amount,))
                await conn.commit()
            else:
                await conn.execute('DELETE FROM tags WHERE rowid IN (SELECT rowid FROM tags LIMIT ?)', (amount,))
                await conn.commit()
        
        await ctx.send('Purged tags.')

    
    @tag.command(name='spamtags')
    async def spamtags(self, ctx, amount: int):
        for i in range(amount):
            name = ''.join(random.SystemRandom().choice(string.ascii_uppercase + string.digits) for _ in range(12))
            text = ''.join(random.SystemRandom().choice(string.ascii_uppercase + string.digits) for _ in range(100))
            await self.tag_manager.create_tag(Tag(name, ctx.author.id, ctx.guild.id, text))
        await ctx.send('Done!')


            







async def setup(bot):
    await bot.add_cog(tags(bot))