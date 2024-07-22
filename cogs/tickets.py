import discord
from discord.ext import commands
import aiosqlite
from discord.ui import View, button
from discord.ext.commands import has_permissions
from asyncpg import Connection

class ticketuiQuit(View):
    def __init__(self, conn):
        super().__init__()
        self.conn: Connection = conn

    @button(label="Yes", emoji="✅")
    async def handler_yes(self, interaction, button):
        await interaction.channel.delete()
        await self.conn.execute('''
            DELETE FROM tickets WHERE user_id = $1
        ''', (interaction.user.id,))
        await self.conn.execute()
        await interaction.user.send("Closed ticked.")
        

    @button(label="No", emoji="❌")
    async def handler_no(self, interaction, button):
        await interaction.response.edit_message(content="Ticket closing stopped.", view=None)


class ticketui(View):
    def __init__(self):
        super().__init__(timeout=None)

    @button(label="Close", emoji="❌")
    async def handler(self, interaction, button):
        await interaction.response.send_message("Are you sure?", view=ticketuiQuit())

class tickets(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.conn: Connection = bot.ticketdb
        
    
    @commands.group(invoke_without_command=True)
    async def ticket(self, ctx):
        await ctx.send('Welcome to our bot ticket system! Use command "help ticket" for more info.')


    @ticket.command(name='create')
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def create_ticket(self, ctx):
        async with aiosqlite.connect('tickets.db') as conn:
            row = await self.conn.execute('SELECT allowed_role, moderation_role FROM settings WHERE guild_id = $1', (ctx.guild.id,))
            roles = await row.fetchone()
            if not roles:
                await ctx.send('Owner havent confiruget bot yet.')
                return
            found = False
            for role in ctx.author.roles:
                if role.id == roles[0]:
                    found = True
                    break
            if found == False:
                await ctx.send('You dont have permission to use this command.')
                return
        async with aiosqlite.connect('tickets.db') as conn:
            row = await conn.execute('SELECT user_id FROM tickets WHERE guild_id = $1 AND user_id = $1', (ctx.guild.id, ctx.author.id,))
            exists = await row.fetchone()
            if exists:
                print(exists)
                await ctx.send('You already have a ticket in this server.')
                return
            await ctx.send('Creating ticket...')
            await conn.execute('INSERT INTO tickets VALUES ($1,$2,$3)', (ctx.guild.id, ctx.channel.id, ctx.author.id))
            await conn.commit()
            channel = await ctx.guild.create_text_channel('ticket-'+ctx.author.name)
            for role in ctx.guild.roles:
                await channel.set_permissions(role, send_messages=False, read_messages=False)

            await channel.set_permissions(ctx.author, send_messages=True, read_messages=True)
            staff_role = ctx.guild.get_role(roles[1])
            await channel.set_permissions(staff_role, send_messages=True, read_messages=True)
            await channel.send(f"Hi {ctx.author.mention}! your ticked was created! Click button below to close it.", view=ticketui())
            await ctx.send('Created ticket.')

    @ticket.command(name='remove_cd', aliases=['rcd', 'remcd', 'removecd'])
    @has_permissions(administrator=True)
    async def remove_cooldown(self, ctx, member: discord.Member):
        if member == None:
            await ctx.reply('Please specify a member to remove the cooldown.')
            return
        if type(member) != discord.Member:
            print(type(member))
            await ctx.reply('Please specify valid member to remove the cooldown.')
            return
        async with aiosqlite.connect('tickets.db') as conn:
            row = await conn.execute('SELECT user_id FROM tickets WHERE guild_id = ?', (ctx.guild.id,))
            if not row:
                await ctx.send('User doesnt have cd.')
                return
            await conn.execute('DELETE FROM tickets WHERE user_id = ? AND guild_id = ?', (member.id, ctx.guild.id))
            await conn.commit()
            await ctx.send('Removed from db.')

        

    @ticket.command(name='confiruge', aliases=['cfg', 'config'])
    @has_permissions(administrator=True)
    async def confiruge_ticket(self, ctx, type: str, role: discord.Role):
        async with aiosqlite.connect('tickets.db') as conn:
            if type == 'allowed_role':
                await conn.execute('INSERT INTO settings(guild_id, allowed_role) VALUES (?,?) ON CONFLICT DO UPDATE SET allowed_role = ?', (ctx.guild.id, role.id, role.id))
            elif type == 'moderation_role':
                await conn.execute('INSERT INTO settings(guild_id, moderation_role) VALUES (?,?) ON CONFLICT DO UPDATE SET moderation_role = ?', (ctx.guild.id, role.id, role.id))
            else:
                await ctx.send('Invalid method, methods: allowed_role, moderation_role.')
                return
            await conn.commit()
            await ctx.send('Confirgured.')


    


            
async def setup(bot):
    await bot.add_cog(tickets(bot))