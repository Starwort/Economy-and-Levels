import discord
from discord.ext import commands
from cogs.lib.profilesave import save
from random import randint
def hasaccount():
    async def predicate(ctx):
        return bool(ctx.bot.profiles.get(ctx.author.id,None))
    return commands.check(predicate)
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
    @hasaccount()
    async def givemoney(self,ctx,target:discord.User,amount:int):
        '''Give another user money.
        Example:
        [p]give-money @Starwort 100
        '''
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
        if target.id == ctx.author.id:
            await ctx.send('Don\'t bother sending yourself money, nothing will happen!')
            return
        self.bot.profiles[ctx.author.id]['money'] -= amount
        self.bot.profiles[target.id]['money'] += amount
        await ctx.send('Successfully sent {} £{}'.format(target,amount))
        await save(self.bot.profiles)
    @commands.command()
    async def register(self,ctx):
        '''Add yourself to the profile list. This enables economy and levelling for your account.'''
        if self.bot.profiles.get(ctx.author.id,None):
            await ctx.send('You can\'t add yourself again!')
            return
        self.bot.profiles[ctx.author.id] = self.profileproto.copy()
        await ctx.send('You have been added successfully!')
        await save(self.bot.profiles)
    @commands.command()
    async def profile(self,ctx,target:discord.User=None):
        '''Who are you again? You can check this!'''
        if not target:
            target = ctx.author
        if not self.bot.profiles.get(target.id, None):
            await ctx.send(f'{str(target) + " does" if target.id != ctx.author.id else "You do"} not have a profile.')
            return
        def generatetext(*,level,money,note,xp):
            xptonext = (level**2)*100+10
            progress = xp / xptonext * 100
            bar = '['+'#'*round(progress/5) + '='*(20-round(progress/5))+']'
            return f'''```
Profile for user: {target}
Level: {level} ({xp}/{xptonext}, {progress:.2f}%)
{bar}
Money: £{money}
{'"'+note+'"' if note else ''}```'''
        await ctx.send(generatetext(**self.bot.profiles[target.id]))
    @commands.command()
    @hasaccount()
    @commands.cooldown(1, 86400, commands.BucketType.user)
    async def earn(self,ctx):
        '''Earn yourself some money! Works once per day.'''
        moneyearned = randint(50,100)
        self.bot.profiles[ctx.author.id]['money'] += moneyearned
        await ctx.send(f'You earned £{moneyearned}!')
    @commands.command()
    @hasaccount()
    @commands.cooldown(1, 3600, commands.BucketType.channel)
    async def beg(self,ctx):
        '''Scrape the channel for money! Works once per hour, *per channel*.'''
        moneyearned = randint(5,10)
        self.bot.profiles[ctx.author.id]['money'] += moneyearned
        await ctx.send(f'You earned £{moneyearned}!')
def setup(bot):
    bot.add_cog(Profile(bot))