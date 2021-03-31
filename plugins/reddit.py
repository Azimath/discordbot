import discord
import asyncio
import commands

client = None

karma = {}

def loadKarmaFromFile():
    return

def saveKarmaToFile():
    return
  
@commands.registerEventHandler(triggerType="\\messageNoBot")
def addReactVotes(triggerMessage):
    if (triggerMessage.guild.id == 102981131074297856):
        await triggerMessage.add_reaction(client.get_emoji(826584584866627684))
        await triggerMessage.add_reaction(client.get_emoji(826584671940640790))
      
@commands.registerEventHandler(triggerType="\\reactionChanged", name="processVoteCast")
def processVoteCast(triggerMessage, reaction, user):
    if (reaction.emoji == client.get_emoji(826584584866627684)):
        if triggerMessage.author.name in karma:
            karma[triggerMessage.author.name] += 1
        else:
            karma[triggerMessage.author.name] = 1
    elif(reaction.emoji == client.get_emoji(826584671940640790):
        if triggerMessage.author.name in karma:
            karma[triggerMessage.author.name] -= 1
        else:
            karma[triggerMessage.author.name] = -1
         
@commands.registerEventHandler(name="showkarma")    
def showKarma(triggerMessage):
     if triggerMessage.author.name not in karma:
         karma[triggerMessage.author.name] = 0
     await triggerMessage.channel.send("Karma: " + karma[triggerMessage.author.name])
         
