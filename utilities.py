import discord
from textwrap import wrap

async def big_send(dest, string, box=""):
    strings = wrap(string, 1950)
    for s in strings:
        await dest.send(box + s + box)
