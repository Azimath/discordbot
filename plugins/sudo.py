import asyncio
import permissions
import commands


"""A plugin to make the bot say things in channels. Mods only.
!sudo channel stuff : says stuff in channel"""

client = None

@commands.registerEventHander(name="sudo")
@permissions.needs_moderator
async def sudo(triggerMessage):
    args = triggerMessage.content.split()
    
    if args.__len__() < 3:
        await client.send_message(triggerMessage.channel, "Not enough args")
        return
    
    sayingstart = [i for i, ltr in enumerate(triggerMessage.content) if ltr == ':'][0]
    saying = triggerMessage.content[sayingstart+1:]
    
    for target in triggerMessage.channel_mentions:
        client.send_message(target, saying)
    for target in triggerMessage.mentions:
        client.send_message(target, saying)

    await client.send_message(triggerMessage.channel, "message sent")
