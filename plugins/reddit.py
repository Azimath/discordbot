import discord
import asyncio
import commands
import json
from datetime import datetime

client = None

karma = {}
lastSave = datetime.fromtimestamp(0)

try:
    with open('karma.json', 'r') as karmafile:
        print("Got karma file!")
        karma = json.loads(karmafile.read())
except:
    print("No karma file!")

def saveKarmaToFile(karma):
    with open('karma.json', 'w') as karmafile:
        json.dump(karma, karmafile, indent=4)


#@commands.registerEventHandler(triggerType="\\messageNoBot", name="redditVoteReact")
async def addReactVotes(triggerMessage):
    if (triggerMessage.guild.id == 102981131074297856):
        await triggerMessage.add_reaction(client.get_emoji(826584584866627684))
        await triggerMessage.add_reaction(client.get_emoji(826584671940640790))
     
@commands.registerEventHandler(triggerType="\\reactionAdded", name="processVoteCast")
async def processVoteCast(triggerMessage, reaction, user):
    if user.id == client.user.id:
        return
    if (reaction.emoji == client.get_emoji(826584584866627684)):
        if triggerMessage.author.name in karma:
            karma[triggerMessage.author.name] += 1
        else:
            karma[triggerMessage.author.name] = 1
    elif(reaction.emoji == client.get_emoji(826584671940640790)):
        if triggerMessage.author.name in karma:
            karma[triggerMessage.author.name] -= 1
        else:
            karma[triggerMessage.author.name] = -1
    now = datetime.now()
    if (now - lastSave).total_seconds() > 600:
         saveKarmaToFile(karma)

@commands.registerEventHandler(triggerType="\\reactionRemoved", name="processVoteUncast")
async def processVoteRemoved(triggerMessage, reaction, user):
    if user.id == client.user.id:
        return
    if (reaction.emoji == client.get_emoji(826584584866627684)):
        if triggerMessage.author.name in karma:
            karma[triggerMessage.author.name] -= 1
        else:
            karma[triggerMessage.author.name] = -1
    elif(reaction.emoji == client.get_emoji(826584671940640790)):
        if triggerMessage.author.name in karma:
            karma[triggerMessage.author.name] += 1
        else:
            karma[triggerMessage.author.name] = 1
    now = datetime.now()
    if (now - lastSave).total_seconds() > 600:
         saveKarmaToFile(karma)
        
@commands.registerEventHandler(name="showkarma")    
async def showKarma(triggerMessage):
     if triggerMessage.author.name not in karma:
         karma[triggerMessage.author.name] = 0
     await triggerMessage.channel.send("Karma: " + str(karma[triggerMessage.author.name]))
     saveKarmaToFile(karma)
