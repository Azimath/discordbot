import asyncio
import permissions

class Sudo:
    """A plugin to make the bot say things in channels. Mods only.
    !sudo channel stuff : says stuff in channel"""
    legacy = True
    def __init__(self, client):
        self.client = client
        
    @permissions.needs_moderator
    async def sudo(self, message):
        args = message.content.split()
        
        if args.__len__() < 3:
            await self.client.send_message(message.channel, "Not enough args")
            return
        
        sayingstart = [i for i, ltr in enumerate(message.content) if ltr == ':'][0]
        saying = message.content[sayingstart+1:]
        
        for target in message.channel_mentions:
            self.client.send_message(target, saying)
        for target in message.mentions:
            self.client.send_message(target, saying)

        await self.client.send_message(message.channel, "message sent")
    commandDict = { "!sudo" : "sudo" }
Class = Sudo
