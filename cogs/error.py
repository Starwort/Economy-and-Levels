import discord
from discord.ext import commands
import traceback
import sys
import io

class ErrorCog():
    def __init__(self, bot):
        self.bot = bot
        self.channel = self.bot.get_channel(485446051298541568)

    async def on_command_error(self, ctx, error):
        if isinstance(error, commands.errors.CommandNotFound):
            pass
        elif isinstance(error, discord.errors.Forbidden):
            pass
        elif isinstance(error, commands.errors.CheckFailure):
            await ctx.send('You do not have permission to use this command.')
        elif isinstance(error, commands.errors.MissingRequiredArgument):
            formatter = commands.formatter.HelpFormatter()
            help = await formatter.format_help_for(ctx, ctx.command)
            await ctx.send('You are missing required arguments.'+"\n" + help[0])
        elif isinstance(error, commands.errors.BadArgument):
            await ctx.send('You have given an invalid argument.')
        else:
            await ctx.send('An error occurred in the `{}` command. This has been automatically reported for you.'.format(ctx.command.name))
            print("Ignoring exception in command {}".format(ctx.command.name))
            trace = traceback.format_exception(type(error), error, error.__traceback__)
            out = '```'
            for i in trace:
                if len(out+i+'```') > 2000:
                    await self.channel.send(out+'```')
                    out = '```'
                out += i
            await self.channel.send(out+'```')
    @commands.command(hidden=True)
    async def errorme(self,ctx):
        raise Exception
def setup(bot):
    bot.add_cog(ErrorCog(bot))