from discord.ext import commands
from discord import *
from subprocess import run, PIPE
import aiofiles
import importlib as imp, traceback
class OwnerCog:

    def __init__(self, bot):
        self.bot = bot
        self.channel = self.bot.get_channel(485446051298541568)

    
    # Hidden means it won't show up on the default help.
    @commands.command(name='load', hidden=True)
    @commands.is_owner()
    async def cog_load(self, ctx, *cogs):
        """Command which Loads a Module.
        Remember to use dot path. e.g: cogs.owner"""
        for cog in cogs:
            try:
                self.bot.load_extension(cog)
            except Exception as e:
                embed = Embed(colour=Colour(0xff0000))
                embed.set_author(name="ERROR")
                embed.add_field(name=type(e).__name__,value=e)
                await ctx.send(embed=embed)
            else:
                embed = Embed(colour=Colour(0x00ff00))
                embed.set_author(name="SUCCESS")
                embed.add_field(name="Successfully loaded",value=cog)
                await ctx.send(embed=embed)

    @commands.command(name='unload', hidden=True)
    @commands.is_owner()
    async def cog_unload(self, ctx, *cogs):
        """Command which Unloads a Module.
        Remember to use dot path. e.g: cogs.owner"""
        for cog in cogs:
            try:
                self.bot.unload_extension(cog)
            except Exception as e:
                embed = Embed(colour=Colour(0xff0000))
                embed.set_author(name="ERROR")
                embed.add_field(name=type(e).__name__,value=e)
                await ctx.send(embed=embed)
            else:
                embed = Embed(colour=Colour(0x00ff00))
                embed.set_author(name="SUCCESS")
                embed.add_field(name="Successfully unloaded",value=cog)
                await ctx.send(embed=embed)

    @commands.command(name='reload', hidden=True)
    @commands.is_owner()
    async def cog_reload(self, ctx, *cogs):
        """Command which Reloads a Module.
        Remember to use dot path. e.g: cogs.owner"""
        for cog in cogs:
            try:
                try:
                    self.bot.unload_extension(cog)
                    self.bot.load_extension(cog)
                except Exception as e:
                    if type(e).__name__ == 'ClientException' and str(e) == 'extension does not have a setup function':
                        mod = imp.import_module(cog)
                        imp.reload(mod)
                        embed = Embed(colour=Colour(0x00ff00))
                        embed.set_author(name="SUCCESS")
                        embed.add_field(name="Successfully reloaded",value=cog)
                        await ctx.send(embed=embed)
                    else:
                        embed = Embed(colour=Colour(0xff0000))
                        embed.set_author(name="ERROR")
                        embed.add_field(name=type(e).__name__,value=e)
                        await ctx.send(embed=embed)
                else:
                    embed = Embed(colour=Colour(0x00ff00))
                    embed.set_author(name="SUCCESS")
                    embed.add_field(name="Successfully reloaded",value=cog)
                    await ctx.send(embed=embed)
            except Exception as e:
                trace = traceback.format_exception(type(e), e, e.__traceback__)
                out = '```'
                for i in trace:
                    if len(out+i+'```') > 2000:
                        await self.channel.send(out+'```')
                        out = '```'
                    out += i
                await self.channel.send(out+'```')

    @commands.command(name="stop",hidden=True)
    @commands.is_owner()
    async def bot_unload(self, ctx):
        await self.bot.logout()
    @commands.command(name="update",hidden=True)
    @commands.is_owner()
    async def bot_update(self, ctx, cog=None):
        await ctx.send("```"+run(["git", "pull", "https://github.com/Starwort/Combined-Splatbot.git"], stdout=PIPE,encoding="ASCII").stdout+"```")
        if cog:
            ctx.command = self.cog_reload
            await ctx.reinvoke()
    @commands.command(name="restart",hidden=True)
    @commands.is_owner()
    #@commands.is_owner()
    async def bot_reload(self, ctx):
        async with aiofiles.open('restart.txt','w') as file:
            await file.write(f'{ctx.channel.id}\n{ctx.author.id}')
        await ctx.send('brb')
        await self.bot.logout()
    @commands.command(hidden=True)
    @commands.is_owner()
    async def prefixdebug(self,ctx,guild_id : int, prefix : str):
        self.bot.additionalprefixdata[guild_id] = prefix
        if prefix == '': del self.bot.additionalprefixdata[guild_id]
        async with aiofiles.open('prefixes.txt','w') as file:
            await file.write(repr(self.bot.additionalprefixdata))
        guild = self.bot.get_guild(guild_id)
        await ctx.send(f'Set prefix for {guild.name if guild else "[INVALID SERVER]"} to `{prefix}`')
def setup(bot):
    bot.add_cog(OwnerCog(bot))
