import aiofiles
async def save(profiles):
    async with aiofiles.open('profiles.txt','w') as file:
        await file.write(repr(profiles))