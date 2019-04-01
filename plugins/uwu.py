import commands
import discord

client = None

@commands.registerEventHandler(triggerType="\\messageNoBot", name="dewetethis")
async def dewetethis(triggermessage):
    if ("r" in message.content.lower() or "l" in message.content.lower()) and not ("uwu" in message.content.lower() or "owo" in message.content.lower()):
        if (triggerMessage.server.id == "102981131074297856"):
            await client.send_message(triggerMessage.author, "UwU Pwease wewwite youw message without iwwegaw chawactews and/ow add owo ow uwu."
            await client.delete_message(triggerMessage)
