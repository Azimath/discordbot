import commands
import discord

client = None

@commands.registerEventHandler(triggerType="\\messageNoBot", name="dewetethis")
async def dewetethis(triggerMessage):
    if ("r" in triggerMessage.content.lower() or "l" in triggerMessage.content.lower()) and not ("uwu" in triggerMessage.content.lower() or "owo" in triggerMessage.content.lower()):
        if (triggerMessage.server.id == "102981131074297856"):
            await client.send_message(triggerMessage.author, "UwU Pwease wewwite youw message without iwwegaw chawactews and/ow add owo ow uwu.")
            await client.delete_message(triggerMessage)
