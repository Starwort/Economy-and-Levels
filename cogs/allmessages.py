import discord
import traceback
import cogs.lib.scorer as score
class AllMessages():
    def __init__(self, bot):
        self.bot = bot
        self.msg_old = bot.on_message
        self.error_channel = bot.get_channel(485446051298541568)
        self.log_channel = bot.get_channel(486887207303512074)
        self.users = {}
        async def new(message):
            pass
        bot.on_message = new
    def __unload(self):
        self.bot.on_message = self.msg_old
    async def on_message(self, message):
        if self.bot.profiles.get(message.author.id,None):
            print(f'user {message.author} has a profile')
            if not self.users.get(message.author.id, 0):
                print(f'user {message.author} is not under a ratelimit')
                messagescore = score.score(message.content)
                print(f'user {message.author} scored {messagescore}')
                self.users[message.author.id] = score.cooldown
                print(f'user {message.author} is now on cooldown')
                self.bot.profiles[message.author.id]['xp'] += messagescore
                xp = self.bot.profiles[message.author.id]['xp']
                print(f'user {message.author} has {xp}')
                oldlvl = self.bot.profiles[message.author.id]['level']
                print(f'user {message.author} is {oldlvl}')
                while (self.bot.profiles[message.author.id]['level']**2)*100+10 < self.bot.profiles[message.author.id]['xp']:
                    self.bot.profiles[message.author.id]['level'] += 1
                    self.bot.profiles[message.author.id]['xp'] -= (self.bot.profiles[message.author.id]['level']**2)*100+10
                    lvl = self.bot.profiles[message.author.id]['level']
                    xp = self.bot.profiles[message.author.id]['xp']
                    print(f'user {message.author} levelled up (now level {lvl} xp {xp})')
                if oldlvl != lvl:
                    try:
                        await message.channel.send(f'{message.author} levelled up! ({oldlvl} -> {self.bot.profiles[message.author.id]["level"]})',delete_after=10)
                    except:
                        pass
            else:
                self.users[message.author.id] -= 1
                cd = self.users[message.author.id]
                print(f'user {message.author}\'s cooldown has been decremented. now: {cd}')
        try:
            if message.author.bot:
                return
            ctx = await self.bot.get_context(message)
            perms = ctx.channel.permissions_for(ctx.me)
            if perms.value & 114688 != 114688 and perms.value & 8 != 8 and ctx.command is not None:
                try:
                    missing_req = ''
                    if not perms.embed_links:
                        missing_req += 'Embed Links\n'
                    if not perms.read_message_history:
                        missing_req += 'Read Message History\n'
                    if not perms.attach_files:
                        missing_req += 'Attach Files'
                    missing_req = missing_req.strip()
                    missing_add = ''
                    if not perms.manage_messages:
                        missing_add += 'Manage Messages'
                    if not perms.add_reactions:
                        missing_add += 'Add Reactions'
                    if missing_add == '':
                        missing_add = 'None :D'
                    else:
                        missing_add = missing_add.strip()
                    await message.channel.send('''Economy and Levels does not have all the permissions required for commands

Without these permissions, all commands will be withheld.

The required permissions for Economy and Levels are:
```Embed Links
Read Message History
Attach Files```


The additional recommended permissions for Economy and Levels are:
```Manage Messages
Add Reactions```

Note that applying 'Administrator' will also prevent this message from appearing.

Currently missing required permissions:
```{}```


Currently missing recommended permissions:
```{}```


If the `Economy and Levels` role (or any other applied role) has these permissions, confirm that no channel overrides are causing the issue.
If problems persist, join the support server: `3xuDR3G`'''.format(missing_req, missing_add))
                except discord.errors.Forbidden:
                    pass
                return
            await self.bot.process_commands(message)

        except Exception as error:
            if not isinstance(error, discord.errors.Forbidden):
                try:
                    trace = traceback.format_exception(type(error), error, error.__traceback__)
                    out = '```'
                    for i in trace:
                        if len(out+i+'```') > 2000:
                            await self.error_channel.send(out+'```')
                            out = '```'
                        out += i
                    await self.error_channel.send(out+'```')
                except:
                    pass
            await self.bot.process_commands(message)
def setup(bot):
    bot.add_cog(AllMessages(bot))