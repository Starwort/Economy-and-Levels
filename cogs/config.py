import discord
from discord.ext import commands
import aiofiles
class Configuration:
    def __init__(self,bot):
        self.bot = bot
    @commands.command()
    @commands.has_permissions(manage_guild=True)
    async def setprefix(self,ctx,newprefix):
        '''Sets the server's custom prefix (the original will still work). Requires the Manage Server permission. To use spaces in your prefix quote it.
        You can even use a space at the end of the prefix.
        
        Example 1 (no spaces):
        [p]setprefix eal!
        Example 2 (with trailing space):
        [p]setprefix "eal "
        
        To remove your server's prefix:
        [p]setprefix ""'''
        newprefix = newprefix.lstrip(' ')
        if len(newprefix) > 10:
            return await ctx.send('In order to prevent abuse to my disk, the custom prefix length has been capped at 10. Sorry!')
        add = ('removed' if newprefix == '' else f'changed to `{newprefix}`') if ctx.guild.id in self.bot.additionalprefixdata else f'set to `{newprefix}`'
        outmsg = f'Your server\'s custom prefix has been {add}'
        self.bot.additionalprefixdata[ctx.guild.id] = newprefix
        if newprefix == '': del self.bot.additionalprefixdata[ctx.guild.id]
        async with aiofiles.open('prefixes.txt','w') as file:
            await file.write(repr(self.bot.additionalprefixdata))
        await ctx.send(outmsg)
    @commands.command()
    @commands.has_permissions(manage_guild=True)
    async def worthinessmessages(self,ctx,enabled:bool):
        '''Turn on or off the 'Worthiness' messages on member join/leave.
        `[p]worthinessmessages True` for on, `[p]worthinessmessages False` for off.'''
        if enabled:
            if self.bot.disabledGuilds.get(ctx.guild.id,None):
                del self.bot.disabledGuilds[ctx.guild.id]
                await ctx.send('Worthiness messages re-enabled for your guild!')
            else:
                await ctx.send('Your guild\'s worthiness messages were already on!')
        else:
            self.bot.disabledGuilds[ctx.guild.id] = ''
        async with aiofiles.open('disabledguilds.txt','w') as file:
            await file.write('\n'.join([str(i) for i in self.bot.disabledGuilds]))
def setup(bot):
    bot.add_cog(Configuration(bot))