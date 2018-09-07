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
            if ctx.cog.__module__ == 'cogs.profile':
                await ctx.send('You do not have an account! Register with {}register first!'.format(ctx.bot.command_prefix(ctx.bot,ctx)[0]))
            else:
                await ctx.send('You do not have permission to use this command.')
        elif isinstance(error, commands.errors.MissingRequiredArgument):
            formatter = commands.formatter.HelpFormatter()
            help = await formatter.format_help_for(ctx, ctx.command)
            await ctx.send('You are missing required arguments.'+"\n" + help[0])
        elif isinstance(error, commands.errors.BadArgument):
            await ctx.send('You have given an invalid argument.')
        elif isinstance(error, commands.CommandOnCooldown):
            timeleft = float(str(error).split('You are on cooldown. Try again in ')[1].rstrip('s'))
            s = round(timeleft % 60,2)
            if s == round(timeleft,2):
                cooldown = f'{s}s'
            else:
                timeleft = timeleft // 60
                m = int(timeleft % 60)
                if m == timeleft:
                    cooldown = f'{m}m{s}s'
                else:
                    timeleft = timeleft // 60
                    cooldown = f'{timeleft}h{m}m{s}s'
            await ctx.send('Hold up! You\'re being ratelimited with this command. You can use this again in: '+cooldown)
            print(error)
        else:
            await ctx.send('An error occurred in the `{}` command. This has been automatically reported for you.'.format(ctx.command.name))
            trace = traceback.format_exception(type(error), error, error.__traceback__)
            print("Ignoring exception in command {}".format(ctx.command.name))
            print(''.join(trace))
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
    @commands.command(hidden=True)
    @commands.cooldown(1, 120, commands.BucketType.user)
    async def ratelimit(self,ctx):
        pass
def setup(bot):
    bot.add_cog(ErrorCog(bot))