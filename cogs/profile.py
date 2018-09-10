import discord
from discord.ext import commands
from cogs.lib.profilesave import save
from random import randint
from concurrent.futures import ThreadPoolExecutor as TPE
from PIL import Image, ImageFont, ImageDraw
from PIL.ImageColor import getcolor, getrgb
from PIL.ImageOps import grayscale
import colour
import io
import asyncio
import urllib
from io import BytesIO
import requests
def image_tint(src, tint='#ffffff'):
    if Image.isStringType(src):  # file path?
        src = Image.open(src)
    if src.mode not in ['RGB', 'RGBA']:
        raise TypeError('Unsupported source image mode: {}'.format(src.mode))
    src.load()
    tr, tg, tb = getrgb(tint)
    tl = getcolor(tint, "L")  # tint colour's overall luminosity
    if not tl: tl = 1  # avoid division by zero
    tl = float(tl)  # compute luminosity preserving tint factors
    sr, sg, sb = map(lambda tv: tv/tl, (tr, tg, tb))  # per component
                                                      # adjustments
    # create look-up tables to map luminosity to adjusted tint
    # (using floating-point math only to compute table)
    luts = (tuple(map(lambda lr: int(lr*sr + 0.5), range(256))) +
            tuple(map(lambda lg: int(lg*sg + 0.5), range(256))) +
            tuple(map(lambda lb: int(lb*sb + 0.5), range(256))))
    l = grayscale(src)  # 8-bit luminosity version of whole image
    if Image.getmodebands(src.mode) < 4:
        merge_args = (src.mode, (l, l, l))  # for RGB version of greyscale
    else:  # include copy of src image's alpha layer
        a = Image.new("L", src.size)
        a.putdata(src.getdata(3))
        merge_args = (src.mode, (l, l, l, a))  # for RGBA version of greyscale
        luts += tuple(range(256))  # for 1:1 mapping of copied alpha values
    return Image.merge(*merge_args).point(luts)
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
        '''Add yourself to the profile list. This enables economy and levelling for your account and reveals the rest of the commands.'''
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
        level,money,note,xp = self.bot.profiles[target.id].values()
        xptonext = (level**2)*100+10
        progress = xp / xptonext * 100
        image = Image.new("RGBA",(768,250),(0,0,0,51))
        colour = 
        def drawavatar():
            try:
                pfp = Image.open(requests.get(target.avatar_url.rstrip('?size=1024'), stream=True).raw)
                pfp = pfp.convert("RGBA")   
                pfp = pfp.resize((128,128))
                image.alpha_composite(pfp,dest=(8,8))
            except Exception as e:
                raise e
        def drawxp():
            bar = Image.open("xpbar-empty.png").convert()
            image.alpha_composite(bar,dest=(8,144))
            bar = image_tint(bar,colour.hsl2hex(((level%36)/36,1,0.5)))
            bar = bar.crop((0,0,round(752*progress),104))
            image.alpha_composite(bar,dest=(8,144))
        def drawtext(array):
            draw.text(xy=(array[0][0],array[0][1]),text=array[1],fill=array[2],font=array[3])
        font = ImageFont.truetype("calibri.ttf",32)
        level_font = ImageFont.truetype("calibri.ttf",72)
        draw = ImageDraw.Draw(image)
        white = (255,255,255)
        black = (200,200,200)
        listie = [
            [(144,8),"Profile for:",black,font],
            [(398,8),"Money:",black,font],
            [(540,8),"Level:",black,font],
            [(144,105),"XP:",black,font],
            [(144,58),str(target),white,font],
            [(477,58),"£"+str(money),white,font],
            [(215,105),f'({round(xp)}/{xptonext}, {progress:.2f}%)',white,font],
            [(650,8),level,white,level_font]
        ]
        with TPE(max_workers=9) as executor:
            for thing in listie:
                executor.submit(drawtext,thing)
            executor.submit(drawxp)
        drawavatar()
        imgByteArr = io.BytesIO()
        image.save(imgByteArr,format="PNG")
        await ctx.send('"'+note+'"' if note else '',file=discord.File(imgByteArr.getvalue(),filename="level.png"))
        """ def generatetext(*,level,money,note,xp):
            xptonext = (level**2)*100+10
            progress = xp / xptonext * 100
            bar = '['+'#'*round(progress/5) + '='*(20-round(progress/5))+']'
            return f'''```
Profile for user: {target}
Level: {level} ({xp}/{xptonext}, {progress:.2f}%)
{bar}
Money: £{money}
{'"'+note+'"' if note else ''}```'''
        await ctx.send(generatetext(**self.bot.profiles[target.id])) """
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
    @commands.command()
    @hasaccount()
    async def setnote(self,ctx,*,note):
        '''Set your profile note. This will be included in your profile.'''
        if len(note) <= 50:
            self.bot.profiles[ctx.author.id]['note'] = note
            await ctx.send(f'Your profile note has been set to {note}')
            save(self.bot.profiles)
        else:
            await ctx.send('That note is too long and to prevent abuse to my disk has not been added. (Max length: 50 characters)')
def setup(bot):
    bot.add_cog(Profile(bot))