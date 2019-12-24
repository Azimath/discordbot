import asyncio
import permissions
import commands


"""A plugin to make the bot say things in channels. Mods only.
!sudo channel :stuff says stuff in channel"""

client = None

@commands.registerEventHandler(name="sudo")
@permissions.needs_moderator
async def sudo(triggerMessage):
    args = triggerMessage.content.split()
    
    if args.__len__() < 3:
        await triggerMessage.channel.send( "Not enough args")
        return
    
    sayingstart = [i for i, ltr in enumerate(triggerMessage.content) if ltr == ':'][0]
    saying = triggerMessage.content[sayingstart+1:]
    
    for target in triggerMessage.channel_mentions:
        await target.send(saying)
    for target in triggerMessage.mentions:
        await target.send(saying)

    await triggerMessage.channel.send( "message sent")
