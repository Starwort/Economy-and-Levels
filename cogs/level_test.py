from concurrent.futures import ThreadPoolExecutor as TPE
from PIL import Image, ImageFont, ImageDraw
from PIL.ImageColor import getcolor, getrgb
from PIL.ImageOps import grayscale
import io
import discord
from discord.ext import commands
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
class Testing():
    
    def __init__(self, bot):
        self.bot = bot
            
    @commands.command(pass_context=True)
    async def profiletest(self, ctx):
        image = Image.new("RGBA",(768,250),(0,0,0,51))
        percentage=0.5
        def drawavatar():
            try:
                pfp = Image.open(requests.get(ctx.author.avatar_url.rstrip('?size=1024'), stream=True).raw)
                pfp = pfp.convert("RGBA")   
                pfp = pfp.resize((128,128))
                image.alpha_composite(pfp,dest=(8,8))
            except Exception as e:
                raise e
        def drawxp():
            bar = Image.open("xpbar-empty.png").convert()
            image.alpha_composite(bar,dest=(8,144))
            bar = image_tint(bar,'#abcdef')
            bar.crop(0,0,round(752*percentage),104)
            image.alpha_composite(bar,dest=(8,144))
        def drawtext(array):
            draw.text(xy=(array[0][0],array[0][1]),text=array[1],fill=array[2],font=array[3])
        font = ImageFont.truetype("calibri.ttf",32)
        level_font = ImageFont.truetype("calibri.ttf",72)
        draw = ImageDraw.Draw(image)
        white = (255,255,255)
        black = (200,200,200)
        listie = [[(144,8),"Profile for:",black,font],
                    [(398,8),"Money:",black,font],
                    [(540,8),"Level:",black,font],
                    [(144,105),"XP:",black,font],
                    [(144,58),str(ctx.author),white,font],
                    [(477,58),"£0",white,font],
                    [(215,105),"55.0/110 (50%)",white,font],
                    [(650,8),"01",white,level_font],
                    ]
        with TPE(max_workers=9) as executor:
            for thing in listie:
                executor.submit(drawtext,thing)
            executor.submit(drawxp)
        drawavatar()
        imgByteArr = io.BytesIO()
        image.save(imgByteArr,format="PNG")
        await ctx.send(file=discord.File(imgByteArr.getvalue(),filename="level.png"))
    @commands.command(pass_context=True)
    async def tinttest(self,ctx):
        image = Image.open('xpbar-empty.png').convert()
        out = image_tint(image,'#abcdef')
        outF = io.BytesIO()
        out.save(outF,format='PNG')
        await ctx.send(file=discord.File(outF.getvalue(),filename='test.png'))
        
def setup(bot):
    bot.add_cog(Testing(bot))