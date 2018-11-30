import random
import json
import asyncio
import aiohttp
import permissions
import commands

"""A plugin for giving various kinds of random phrases.
   !lart user : uses the LART on the given user.
   !praise user : praises the user.
   !pal : is this pal?
   !mango : where is mang0?
   !eightball : Ask the magic eightball a question. Satisfaction not guarunteed.
   !addphrase phrasebank phrase : adds phrase to the given phrasebank. The phrasebank for a given command is generally the plural of the command
   !baddragon : give me some sugah, baby
   !wiki : links to the iaa wiki
   !apply : links to the membership application
   !tests : PMs the user links to all required membership tests
   !constitution : links to the constitution
   !sonic : links to a random page on either the archie sonic wiki or the sonic fanon wiki
   !tingle : links to a random tingler
   !lmgtfy, !google: generates an lmgtfy link from the given query"""

client = None

phrasebank = {}
with open('phrasebank.json', 'r') as lartfile:
    phrasebank = json.loads(lartfile.read())

@commands.registerEventHandler(name="getdragons")
async def refreshDragons(triggerMessage):
    global phrasebank
    
    oldnum = len(phrasebank["dragons"])
    
    response = await aiohttp.request('GET', 'https://bad-dragon.com/api/products')
    body = await response.text()
    
    phrasebank["dragons"] = [x["sku"] for x in json.loads(body)]
    
    with open('phrasebank.json', "w") as lartfile:
            json.dump(phrasebank, lartfile, indent=4)
    
    await client.send_message(triggerMessage.channel, "Downloaded new dragons. There are now " + str(len(phrasebank["dragons"])) 
                                                      + " dragons. Got " + str(len(phrasebank["dragons"])-oldnum) + " new dragons")
    if len(phrasebank["dragons"]) - oldnum > 0:
        pass#await client.send_message(triggerMessage.channel, "@everyone")

@commands.registerEventHandler(name="lart")
async def lart(triggerMessage):
    lart = random.choice(phrasebank["larts"])
    target = triggerMessage.content[6:]
    if not target:
        target = triggerMessage.author.name
    lart = lart.replace("$who", target)
    print("Lart: " + lart)
    await client.send_message(triggerMessage.channel, lart)

@commands.registerEventHandler(name="praise")
async def praise(triggerMessage):
    praise = random.choice(phrasebank["praises"])
    target = triggerMessage.content[8:]
    if not target:
        target = triggerMessage.author.name
    praise = praise.replace("$who", target)
    print("praise: " + praise)
    await client.send_message(triggerMessage.channel, praise)

@commands.registerEventHandler(triggerType="\\messageNoBot", name="keikaku")
@commands.messageHandlerFilter("keikaku", filterType="cqc")
async def keikaku(triggerMessage):
    await client.send_message(triggerMessage.channel, "tl note: keikaku means plan")

@commands.registerEventHandler(name="help")
async def help(triggerMessage):
    await client.send_message(triggerMessage.author, phrasebank["help"][0])
    await client.send_message(triggerMessage.author, phrasebank["help"][1])
      
@commands.registerEventHandler(name="lmgtfy")
async def lmgtfy(triggerMessage):
    query = triggerMessage.content[8:]
    query = query.replace(" ", "+")
    query = ''.join(e for e in query if e.isalnum() or e == "+")
    await client.send_message(triggerMessage.channel, "http://lmgtfy.com/?q=" + query)

@commands.registerEventHandler(name="buydinner")
async def buydinner(triggerMessage):
    praise = random.choice(phrasebank["praises"])
    target = triggerMessage.author.name
    praise = praise.replace("$who", target)
    print("praise: " + praise)
    await client.send_message(triggerMessage.channel, praise)

@commands.registerEventHandler(name="baddragon")
async def baddragon(triggerMessage):
    dragon = random.choice(phrasebank["dragons"])
    print("dragon: " + dragon)
    await client.send_message(triggerMessage.channel, "https://bad-dragon.com/products/"+dragon)

@commands.registerEventHandler(name="tingle")
async def tingle(triggerMessage):
    tingle = "http://amazon.com/" + random.choice(phrasebank["tingles"])
    print("tingle: " + tingle)
    await client.send_message(triggerMessage.channel, tingle)

@commands.registerEventHandler(name="pal")
async def pal(triggerMessage):
    if random.randrange(100) < 2:
        await client.send_message(triggerMessage.channel, "Go fuck yourself " + triggerMessage.author.name)
    else:
        await client.send_message(triggerMessage.channel, "Yes this is pal, yes this is 60 FPS")

@commands.registerEventHandler(name="mango")
async def mango(triggerMessage):
    mango = random.choice(phrasebank["mango"])
    await client.send_message(triggerMessage.channel, mango)

@commands.registerEventHandler(name="8ball")
async def eightball(triggerMessage):
    ball = random.choice(phrasebank["8balls"])
    #print("8ball: " + ball)
    await client.send_message(triggerMessage.channel, ":8ball: " + ball)

@commands.registerEventHandler(name="tests")
async def tests(triggerMessage):
    target = triggerMessage.author
    await client.send_message(target, "Take each of the following tests. Save a screenshot of each result.\nMBTI: http://www.humanmetrics.com/cgi-win/jtypes2.asp\nEnneagram: http://www.eclecticenergies.com/enneagram/test.php Take both tests for best results.\nBIG5: http://personality-testing.info/tests/BIG5.php\nTemperaments: http://personality-testing.info/tests/O4TS/")
    # client.send_message(target, "MBTI: http://www.humanmetrics.com/cgi-win/jtypes2.asp")
    # client.send_message(target, "Enneagram: http://www.eclecticenergies.com/enneagram/test.php")
    # client.send_message(target, "Take both tests for best results.")
    # client.send_message(target, "BIG5: http://personality-testing.info/tests/BIG5.php")
    # client.send_message(target, "Temperaments: http://personality-testing.info/tests/O4TS/")    

@commands.registerEventHandler(name="popori")
async def popori(triggerMessage):
    await client.send_message(triggerMessage.channel, "https://www.youtube.com/watch?v=gbNN3grTdDk")

@commands.registerEventHandler(name="constitution")
async def constitution(triggerMessage):
    await client.send_message(triggerMessage.channel, "https://docs.google.com/document/d/1XKFRQhzxwhjjtW1RnCc_ZhesRqavvM3F5z1LALfve48/")

@commands.registerEventHandler(name="wiki")
async def wiki(triggerMessage):
    await client.send_message(triggerMessage.channel, "http://iaa.wikia.com")

@commands.registerEventHandler(name="application")
async def application(triggerMessage):
    await client.send_message(triggerMessage.channel, "https://docs.google.com/forms/d/1a6fXy0b9uimE789VLFUyUUvkbjVDEx3cYfutXBT8WOQ/viewform")

@commands.registerEventHandler(triggerType="\\messageNoBot", name="unflip")
@commands.messageHandlerFilter("(╯°□°）╯︵ ┻━┻")
async def unflip(triggerMessage):
    await client.send_message(triggerMessage.channel, "┬─┬﻿ ノ( ゜-゜ノ)")

@commands.registerEventHandler(triggerType="\\messageNoBot", name="kk")
@commands.messageHandlerFilter("kk")
async def kkk(triggerMessage):
    if triggerMessage.content.__len__() == 2:
        await client.send_message(triggerMessage.channel, "k")

@commands.registerEventHandler(name="floor")
async def floor(triggerMessage):
    await client.send_message(triggerMessage.channel, "http://i.imgur.com/3OYeOxK.jpg")

@commands.registerEventHandler(name="sonic")
async def sonic(triggerMessage):
    if random.randint(0,1) != 0:
        await client.send_message(triggerMessage.channel, "http://archiesonic.wikia.com/wiki/Special:Random")
    else:
        await client.send_message(triggerMessage.channel, "http://sonicfanon.wikia.com/wiki/Special:Random")
        
@commands.registerEventHandler(triggerType="\\messageNoBot", name="plot")
@commands.messageHandlerFilter("plot", filterType="contains")
async def plot(triggerMessage):
    if client.user in triggerMessage.mentions:
        await client.send_message(triggerMessage.channel, random.choice(phrasebank["plots"]))

@commands.registerEventHandler(triggerType="\\messageNoBot", name="ㅋ")
@commands.messageHandlerFilter("ㅋ")
async def disrespects(triggerMessage):
    if triggerMessage.content.__len__() == 1:
        await client.send_message(triggerMessage.channel, triggerMessage.author.name + " has revoked their respects.")
      
@commands.registerEventHandler(triggerType="\\messageNoBot", name="F")
@commands.messageHandlerFilter("F")
async def respects(triggerMessage):
    if triggerMessage.content.__len__() == 1:
        await client.send_message(triggerMessage.channel, triggerMessage.author.name + " has paid their respects.")
      
@commands.registerEventHandler(triggerType="\\messageNoBot", name="X")
@commands.messageHandlerFilter("X")
async def respects(triggerMessage):
    if triggerMessage.content.__len__() == 1:
        await client.send_message(triggerMessage.channel, triggerMessage.author.name + " doubts that.")

@commands.registerEventHandler(name="addphrase")
@permissions.needs_admin    
async def addphrase(triggerMessage):
    banktargetstart = triggerMessage.content.find(' ') + 1
    banktargetend = triggerMessage.content.find(' ', banktargetstart)
    phrasebanktarget = triggerMessage.content[banktargetstart:banktargetend]
    phrase = triggerMessage.content[banktargetend+1:len(triggerMessage.content)]
    
    print("splitting message at: " + str(banktargetstart) + " and: " + str(banktargetend))
    print("trying to add phrase: \"" + phrase + "\" to bank " + phrasebanktarget)
    
    if phrasebanktarget is not None and phrasebanktarget in phrasebank and phrase is not None:
        phrasebank[phrasebanktarget].append(phrase)
        
        with open('phrasebank.json', 'w') as phrasefile:
            phrasefile.write(json.dumps(phrasebank, indent=4))
            await client.send_message(triggerMessage.channel, "Added phrase " + phrase)
            
