import asyncio
import commands

@commands.registerEventHandler(name="hop")
async def hop(triggerMessage):
  url = triggerMessage.content.split()[1]
  await triggerMessage.channel.send("https://12ft.io/proxy?ref=&q=" + url)
