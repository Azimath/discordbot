import random
import commands

"""This is a plugin for fun things you can use to play with [^_^].
   !flip, !coin: Flips a coin
   !trick: Does a super cool magic trick"""
client = None

@commands.registerEventHander(name="flip")
@commands.registerEventHander(name="coin")
async def flip(triggerMessage):
    await client.send_message(triggerMessage.channel, random.choice(["heads", "tails"]))

@commands.registerEventHander(name="trick")
async def trick(triggerMessage):
    target = triggerMessage.channel
    suits = [":hearts:", ":clubs:", ":diamonds:", ":spades:"]
    values = ["Ace", "Two", "Three", "Four", "Five", "Six", "Seven", "Eight", "Nine", "Ten", "Jack", "Queen", "King"]
    suit = random.choice(suits)
    value = random.choice(values)
    await client.send_message(target, "This is your card. Remember it, but don't tell me what it is. " + suit + " " + value)
    await client.send_message(target, "*shuffles*")
    await client.send_message(target, "*shuffles*")
    await client.send_message(target, "*shuffles*")
    await client.send_message(target, "*cuts*")
    await client.send_message(target, "Is this your card? " + suit + " " + value)

@commands.registerEventHander(triggerType="\\messageNoBot", name="fuck quest go")
@commands.messageHandlerFilter("fuck quest go", filterType="cqc")
async def fuckRoll(triggerMessage):
    await client.send_message(triggerMessage.channel, "Fuck quest: " + str(random.randrange(1, 100)))

@commands.registerEventHander(name="roll")
async def roll(triggerMessage):
    target = triggerMessage.channel
    toParse = triggerMessage.content[5:]
    if "∞" in toParse:
        result = "∞"
        await client.send_message(target, "Rolled " + toParse + ": " + "∞")

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
            mod = int(int(toParse[index:]))
        
        result = 0
        
        if rolls > 100000:
            await client.send_message(target, "Fuck off")
        else:
            for i in range(0, rolls):
                result = result + random.randrange(1, size+1)
            
            result = result + mod
            await client.send_message(target, "Rolled " + str(rolls) + "d" + str(size) + "+" + str(mod) + ": " + "**" + str(result) + "**")