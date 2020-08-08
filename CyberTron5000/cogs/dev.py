import ast
import asyncio
import subprocess
import sys

import aiohttp
import discord
from discord.ext import commands

from CyberTron5000.utils import checks
from CyberTron5000.utils import cyberformat

tick = "<:tickgreen:732660186560462958>"
null = '<:ticknull:732660186057015317>'
redx = "<:redx:732660210132451369>"
reload = '<:reload:732674920873459712>'


class Developer(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.tick = ":tickgreen:732660186560462958"
        self._ = None
        
    async def cog_check(self, ctx):
        return ctx.author.id == 350349365937700864
    
    @commands.group(aliases=["e", "evaluate"], name='eval', invoke_without_command=True, help="Evaluates a function.")
    async def eval_fn(self, ctx, *, cmd):
        global result
        try:
            fn_name = "_eval_expr"
            cmd = cyberformat.codeblock(cmd)
            cmd = cmd.strip("` ")
            cmd = "\n".join(f"    {i}" for i in cmd.splitlines())
            body = f"async def {fn_name}():\n{cmd}"
            parsed = ast.parse(body)
            body = parsed.body[0].body
            checks.insert_returns(body)
            env = {
                'me': ctx.guild.me,
                'bot': ctx.bot,
                'discord': discord,
                'commands': commands,
                'get': discord.utils.get,
                'ctx': ctx,
                'asyncio': asyncio,
                '__import__': __import__,
                'author': ctx.author,
                'guild': ctx.guild,
                'channel': ctx.channel,
                '_': self._,
            }
            try:
                exec(compile(parsed, filename="<eval>", mode="exec"), env)
                result = (await eval(f"{fn_name}()", env))
            except Exception as error:
                return await ctx.send(embed=discord.Embed(color=self.client.colour,
                                                          description=f"{error.__class__.__name__}```py\n{error}\n```"))
        except Exception as error:
            return await ctx.send(embed=discord.Embed(color=self.client.colour,
                                                      description=f"{error.__class__.__name__}```py\n{error}\n```"))
        
        embed = discord.Embed(color=self.client.colour)
        embed.description = f"```py\n{result}\n```"
        await ctx.message.add_reaction(emoji=self.tick)
        await ctx.send(embed=embed)
        self._ = result
        
    @commands.command()
    async def repl(self, ctx):
        """Starts a REPL session"""
        global result
        await ctx.send(embed=discord.Embed(description="```Starting REPL Session```", colour=self.client.colour))
        while True:
            ms = await self.client.wait_for('message', check=lambda m: m.author == ctx.author)
            if ms.content.lower().startswith(f"{ctx.prefix}exit"):
                return await ctx.send(
                    embed=discord.Embed(description="```Exiting REPL Session```", color=self.client.colour))
            try:
                fn_name = "_eval_expr"
                cmd = cyberformat.codeblock(ms.content)
                cmd = cmd.strip("` ")
                cmd = "\n".join(f"    {i}" for i in cmd.splitlines())
                body = f"async def {fn_name}():\n{cmd}"
                parsed = ast.parse(body)
                body = parsed.body[0].body
                checks.insert_returns(body)
                env = {
                    'me': ctx.guild.me,
                    'bot': ctx.bot,
                    'discord': discord,
                    'commands': commands,
                    'get': discord.utils.get,
                    'ctx': ctx,
                    'asyncio': asyncio,
                    'session': aiohttp.ClientSession(),
                    '__import__': __import__,
                    'author': ctx.author,
                    'guild': ctx.guild,
                    'channel': ctx.channel,
                    '_': self._,
                }
                try:
                    exec(compile(parsed, filename="<ast>", mode="exec"), env)
                    result = (await eval(f"{fn_name}()", env))
                except Exception as error:
                    await ctx.send(embed=discord.Embed(color=self.client.colour,
                                                       description=f"{error.__class__.__name__}```py\n{error}\n```"))
                    continue
            except Exception as error:
                await ctx.send(embed=discord.Embed(color=self.client.colour,
                                                   description=f"{error.__class__.__name__}```py\n{error}\n```"))
                continue
            await ctx.send(f'{result}')
            self._ = result

    @commands.command(help="Loads Cogs", aliases=['l'])
    async def load(self, ctx, *extension):
        if not extension:
            for file in self.client.ext:
                try:
                    self.client.load_extension(file)
                except:
                    continue
            embed = discord.Embed(
                description="\n".join([f"{tick} `cogs.{f[19:]}`" for f in self.client.ext]),
                colour=self.client.colour)
            await ctx.send(embed=embed)
            await ctx.message.add_reaction(emoji=":tickgreen:732660186560462958")

        else:
            cogs = [c[19:] for c in self.client.ext]
            for i in extension:
                if i not in cogs:
                    return await ctx.send(f"**{i}** is not a valid cog!")

            for f in extension:
                self.client.load_extension(f'CyberTron5000.cogs.{f}')
            a = []
            for x in cogs:
                if x in extension:
                    a.append(f"{tick} `cogs.{x}`")
                else:
                    a.append(f"{null} `cogs.{x}`")

            await ctx.message.add_reaction(emoji=":tickgreen:732660186560462958")
            await ctx.send(embed=discord.Embed(description="\n".join(a), colour=self.client.colour))
    
    @commands.command(help="Unloads Cogs", aliases=['ul'])
    async def unload(self, ctx, *extension):
        if not extension:
            for file in self.client.ext:
                try:
                    self.client.unload_extension(file)
                except:
                    continue
            embed = discord.Embed(
                description="\n".join([f"{redx} `cogs.{f[19:]}`" for f in self.client.ext]),
                colour=self.client.colour)
            await ctx.send(embed=embed)
            await ctx.message.add_reaction(emoji=":tickgreen:732660186560462958")
        
        else:
            cogs = [c[19:] for c in self.client.ext]
            for i in extension:
                if i not in cogs:
                    return await ctx.send(f"**{i}** is not a valid cog!")
            
            for f in extension:
                self.client.unload_extension(f'CyberTron5000.cogs.{f}')
            a = []
            for x in cogs:
                if x in extension:
                    a.append(f"{redx} `cogs.{x}`")
                else:
                    a.append(f"{null} `cogs.{x}`")
            
            await ctx.message.add_reaction(emoji=":tickgreen:732660186560462958")
            await ctx.send(embed=discord.Embed(description="\n".join(a), colour=self.client.colour))
    
    @commands.command(help="Reloads Cogs", aliases=['rl'])
    async def reload(self, ctx, *extension):
        if not extension:
            for file in self.client.ext:
                try:
                    self.client.reload_extension(file)
                except:
                    continue
            embed = discord.Embed(
                description="\n".join([f"{reload} `cogs.{f[19:]}`" for f in self.client.ext]),
                colour=self.client.colour)
            await ctx.send(embed=embed)
            await ctx.message.add_reaction(emoji=":tickgreen:732660186560462958")

        else:
            cogs = [c[19:] for c in self.client.ext]
            print(cogs)
            for i in extension:
                if i not in cogs:
                    return await ctx.send(f"**{i}** is not a valid cog!")

            for f in extension:
                self.client.reload_extension(f'CyberTron5000.cogs.{f}')
            a = []
            for x in cogs:
                if x in extension:
                    a.append(f"{reload} `cogs.{x}`")
                else:
                    a.append(f"{null} `cogs.{x}`")

            await ctx.message.add_reaction(emoji=":tickgreen:732660186560462958")
            await ctx.send(embed=discord.Embed(description="\n".join(a), colour=self.client.colour))
    
    @commands.command(help="Logs CyberTron5000 out.")
    async def logout(self, ctx):
        await ctx.send(
            embed=discord.Embed(title=f"{self.client.user.name} logging out. Goodbye World! 🌍",
                                color=self.client.colour))
        await self.client.logout()
    
    @commands.command()
    async def restart(self, ctx):
        await ctx.message.add_reaction(emoji=self.tick)
        await self.client.logout()
        subprocess.call([sys.executable, "main.py"])
    
    @commands.command(aliases=['nu', 'update'])
    async def news_update(self, ctx, *, message):
        """Update the current news."""
        number = await self.client.pg_con.fetch("SELECT number FROM news")
        number = number[0][0] or 0
        number += 1
        await self.client.pg_con.execute("UPDATE news SET message = $1, number = $2", message, number)
        await ctx.send(f"News updated to: ```{message}```")

    @commands.command()
    async def sql(self, ctx, *, statement):
        statement = cyberformat.codeblock(statement, lang='sql')
        res = await self.client.pg_con.fetch(statement)
        await ctx.send(res)

    
def setup(client):
    client.add_cog(Developer(client))