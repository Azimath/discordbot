import random
import commands
import discord

"""This is a plugin for fun things you can use to play with [^_^].
   !flip, !coin: Flips a coin
   !trick: Does a super cool magic trick"""
client = None

@commands.registerEventHandler(name="flip")
@commands.registerEventHandler(name="coin")
async def flip(triggerMessage):
    await triggerMessage.channel.send( random.choice(["heads", "tails"]))

@commands.registerEventHandler(name="trick")
async def trick(triggerMessage):
    target = triggerMessage.channel
    suits = [":hearts:", ":clubs:", ":diamonds:", ":spades:"]
    values = ["Ace", "Two", "Three", "Four", "Five", "Six", "Seven", "Eight", "Nine", "Ten", "Jack", "Queen", "King"]
    suit = random.choice(suits)
    value = random.choice(values)
    await target.send("This is your card. Remember it, but don't tell me what it is. " + suit + " " + value)
    await target.send("*shuffles*")
    await target.send("*shuffles*")
    await target.send("*shuffles*")
    await target.send("*cuts*")
    await target.send("Is this your card? " + suit + " " + value)


@commands.registerEventHandler(name="ship")
async def ship(triggerMessage):
   if triggerMessage.server is not None:
      membs = triggerMessage.guild.members
      
      #filter out offline members
      onlineMembs = []
      for memb in membs:
         if memb.status is discord.Status.online:
            onlineMembs.append(memb)
      
      winners = random.sample(onlineMembs, 2)
      await triggerMessage.channel.send( "I ship {0} and {1}. Now kiss. :heart:".format(winners[0].mention, winners[1].mention))
   else:
      await triggerMessage.channel.send( "I ship us. :heart:")
      

@commands.registerEventHandler(triggerType="\\messageNoBot", name="fuck quest go")
@commands.messageHandlerFilter("fuck quest go", filterType="cqc")
async def fuckRoll(triggerMessage):
    await triggerMessage.channel.send( "Fuck quest: " + str(random.randrange(1, 100)))



def modString(mod):
   if mod == 0:
      return ""
   if mod < 0:
      return str(mod)
   else:
      return "+" + str(mod)

lastRoll = None
   
@commands.registerEventHandler(name="roll")
@commands.registerEventHandler(name="r")
async def roll(triggerMessage):
   global lastRoll
   target = triggerMessage.channel
   pivot = triggerMessage.content.find(" ")
   if pivot == -1 and lastRoll is not None:
      toParse = lastRoll
   else:
      toParse = triggerMessage.content[triggerMessage.content.find(" "):]
      lastRoll = toParse
      
   if "∞" in toParse:
       result = "∞"
       await target.send("Rolled " + toParse + ": " + "∞")

   else:    
       rolls = int(toParse[1:toParse.index('d')])
       toParse = toParse[toParse.index('d'):]
       index = toParse.find('+')
       if index == -1:
           index = toParse.find('-')
       if index == -1:
           size = int(toParse[toParse.index('d')+1:])
           mod = 0
       else:
           size = int(toParse[1:index])
           mod = int(toParse[index:])
       
       result = 0
       
       if rolls > 100000:
           await target.send("Fuck off")
       else:
           for i in range(0, rolls):
               result += random.randrange(1, size+1)
           
           result += mod
           await target.send("Rolled {0}d{1}{2}: **{3}**".format(str(rolls), str(size), modString(mod), str(result)))
