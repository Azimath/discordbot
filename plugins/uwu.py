import commands

client = None

@commands.registerEventHandler(triggerType="\\messageNoBot", name="dewetethis")
async def dewetethis(triggerMessage):
    if ("r" in triggerMessage.content.lower() or "l" in triggerMessage.content.lower()) and not ("uwu" in triggerMessage.content.lower() or "owo" in triggerMessage.content.lower()):
        if (triggerMessage.server.id == "102981131074297856"):
            await client.send_message(triggerMessage.author, "UwU Pwease wewwite youw message without iwwegaw chawactews and/ow add owo ow uwu.")
            await client.delete_message(triggerMessage)

@commands.registerEventHandler(triggerType="\\messageEdit", name="dewetethis2")
async def dewetethis2(before, after):
    if ("r" in after.content.lower() or "l" in after.content.lower()) and not ("uwu" in after.content.lower() or "owo" in after.content.lower()):
        if (after.server.id == "102981131074297856"):
            await client.send_message(after.author, "UwU Pwease wewwite youw message without iwwegaw chawactews and/ow add owo ow uwu.")
            await client.delete_message(after)
