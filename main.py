from discord import *
from discord.ext import commands
import time
import aiofiles, os
from os import listdir
from os.path import isfile, join
from ast import literal_eval
import sys, traceback
description = """Yet another economy and levels bot."""
cogs_dir = "cogs"
properties = open("economyandlevels.properties")
values = properties.readlines()
properties.close()
token = values[0].strip("\n")
pre = values[1].strip("\n")
with open('prefixes.txt') as file:
    prefixes = literal_eval(file.read())
with open('profiles.txt') as file:
    profiles = literal_eval(files.read())
def prefix(bot, ctx):
    global pre
    prefixes = bot.additionalprefixdata
    if type(ctx) == commands.Context:
        ctx = ctx.message
    try:
        extraprefix = prefixes[ctx.guild.id]
    except KeyError:
        extraprefix = None
    except AttributeError:
        #print('we in dm')
        extraprefix = ''
    if extraprefix is not None:
        #print('we adding a prefix which is '+repr(extraprefix))
        prefix = [extraprefix, pre]
    else:
        prefix = [pre]
    newpre = commands.when_mentioned_or(*prefix)(bot, ctx)
    #print(repr(newpre))
    return newpre
bot = commands.Bot(command_prefix=prefix, description=description)
bot.additionalprefixdata = prefixes
bot.profiles = profiles
@bot.event
async def on_ready():
    print("Logged in as\n{0} ({1})\n--------------------".format(bot.user.name,bot.user.id))
    t = time.time()
    bot.startuptime = time.strftime("(UTC) %H:%M:%S on %d/%m/%Y", time.gmtime(t))
    await bot.change_presence(activity=Game(name="Running the economy and levelling systems for {2} guilds. Last restart: {0}. Prefix: {1}".format(bot.startuptime,pre,len(bot.guilds))))
    try:
        async with aiofiles.open('restart.txt') as file:
            data = await file.read()
            data = data.split('\n')
            channel = bot.get_channel(int(data[0]))
            user = bot.get_user(int(data[1]))
            await channel.send(f'{user.mention} I\'m back baby')
            os.remove("restart.txt")
    except:
        pass
@bot.event
async def on_guild_join(guild):
    await bot.change_presence(activity=Game(name="Running the economy and levelling systems for {2} guilds. Last restart: {0}. Prefix: {1}".format(bot.startuptime,pre,len(bot.guilds))))
@bot.event
async def on_guild_remove(guild):
    await bot.change_presence(activity=Game(name="Running the economy and levelling systems for {2} guilds. Last restart: {0}. Prefix: {1}".format(bot.startuptime,pre,len(bot.guilds))))
if __name__ == '__main__':
    for extension in [f.replace('.py', '') for f in listdir(cogs_dir) if isfile(join(cogs_dir, f))]:
        try:
            bot.load_extension(cogs_dir + "." + extension)
        except (ClientException, ModuleNotFoundError):
            print(f'Failed to load extension {extension}.')
            traceback.print_exc()
    bot.run(token, bot=True, reconnect=True)
