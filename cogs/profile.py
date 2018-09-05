import discord
from discord.ext import commands
class Profile:
    def __init__(self,bot):
        self.bot = bot
        self.profileproto = {
            'level' : 0,
            'money' : 0,
            'xp'    : 0,
            'note'  : ''
        }
    @commands.command(name='give-money',aliases=['give'])
    async def givemoney(self,ctx,target:discord.Member,amount:int):
        '''Give another user money.
        Example:
        [p]give-money @Starwort 100
        '''
        if not self.bot.profiles.get(ctx.author.id,None):
            await ctx.send('You do not have an account! Register with {}register first!'.format(self.bot.command_prefix(self.bot,ctx)[0]))
            return
        if not self.bot.profiles.get(target.id,None):
            await ctx.send('They do not have an account! They must register before you can do this.')
            return
        if self.bot.profiles[ctx.author.id]['money'] < amount:
            await ctx.send('You do not have enough money to send them! You have: £{}'.format(self.bot.profiles[ctx.author.id]['money']))
            return
        if amount < 0:
            await ctx.send('You can\'t send people negative money!')
            return
        if amount == 0:
            await ctx.send('What\'s the point in sending £0?!')
            return
        self.bot.profiles[ctx.author.id]['money'] -= amount
        self.bot.profiles[target.id]['money'] += amount
        await ctx.send('Successfully sent {} £{}'.format(target,amount))
    @commands.command()
    async def register(self,ctx):
        '''Add yourself to the profile list. This enables economy and levelling for your account.'''
        if self.bot.profiles.get(ctx.author.id,None):
            await ctx.send('You can\'t add yourself again!')
            return
        self.bot.profiles[ctx.author.id] = self.profileproto.copy()
        await ctx.send('You have been added successfully!')
    @commands.command()
    async def profile(self,ctx,target:discord.Member=None):
        if not target:
            target = ctx.author
        level, money, xp, note = self.bot.profiles[target.id]
        xptonext = (level**2)*100+10
        progress = xp / xptonext * 100
        bar = '['+'#'*round(progress/5) + '='*(20-round(progress/5))+']'
        await ctx.send(f'''```
Profile for user: {target}
Level: {level} ({xp}/{xptonext}, {progress:.2f}%)
{bar}
Money: £{money}
"{note}""```''')
def setup(bot):
    bot.add_cog(Profile(bot))