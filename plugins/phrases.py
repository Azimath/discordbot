import random
import json
import asyncio
import aiohttp
import permissions
import commands
from random_words import RandomWords

"""A plugin for giving various kinds of random phrases.
   !lart user : uses the LART on the given user.
   !praise user : praises the user.
   !pal : is this pal?
   !mango : where is mang0?
   !eightball : Ask the magic eightball a question. Satisfaction not guarunteed.
   !addphrase phrasebank phrase : adds phrase to the given phrasebank. The phrasebank for a given command is generally the plural of the command
   !baddragon : give me some sugah, baby
   !wiki : links to the iaa wiki
   !application : links to the membership application
   !tests : PMs the user links to all required membership tests
   !constitution : links to the constitution
   !sonic : links to a random page on either the archie sonic wiki or the sonic fanon wiki
   !tingle : links to a random tingler
   !lmgtfy, !google: generates an lmgtfy link from the given query
   !IAA : explains what IAA stands for
   !trivia : gives a random true fact
   """

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
    
    await triggerMessage.channel.send( "Downloaded new dragons. There are now " + str(len(phrasebank["dragons"])) 
                                                      + " dragons. Got " + str(len(phrasebank["dragons"])-oldnum) + " new dragons")
    if len(phrasebank["dragons"]) - oldnum > 0:
        pass#await triggerMessage.channel.send( "@everyone")
      
@commands.registerEventHandler(name="trivia")
async def trivia(triggerMessage):
   await triggerMessage.channel.send(random.choice(phrasebank["trivia"]))

@commands.registerEventHandler(name="lart")
async def lart(triggerMessage):
    lart = random.choice(phrasebank["larts"])
    target = triggerMessage.content[6:]
    if not target:
        target = triggerMessage.author.name
    lart = lart.replace("$who", target)
    print("Lart: " + lart)
    await triggerMessage.channel.send( lart)

@commands.registerEventHandler(name="praise")
async def praise(triggerMessage):
    praise = random.choice(phrasebank["praises"])
    target = triggerMessage.content[8:]
    if not target:
        target = triggerMessage.author.name
    praise = praise.replace("$who", target)
    print("praise: " + praise)
    await triggerMessage.channel.send( praise)

@commands.registerEventHandler(triggerType="\\messageNoBot", name="keikaku")
@commands.messageHandlerFilter("keikaku", filterType="cqc")
async def keikaku(triggerMessage):
    await triggerMessage.channel.send( "tl note: keikaku means plan")
      
@commands.registerEventHandler(triggerType="\\messageNoBot", name="ifonly")
@commands.messageHandlerFilter("if only there was something", filterType="cqc")
async def ifonly(triggerMessage):
    options = ["https://en.wikipedia.org/wiki/Satan_(missile)", "https://en.wikipedia.org/wiki/LGM-30_Minuteman", "https://en.wikipedia.org/wiki/TOS-1", "https://en.wikipedia.org/wiki/M240_machine_gun", "https://en.wikipedia.org/wiki/Killdozer_(Bulldozer)"]
    await triggerMessage.reply(random.choice(options), mention_author=True)

@commands.registerEventHandler(name="help")
async def help(triggerMessage):
    await triggerMessage.author.send(phrasebank["help"][0])
    await triggerMessage.author.send(phrasebank["help"][1])
      
@commands.registerEventHandler(name="lmgtfy")
async def lmgtfy(triggerMessage):
    query = triggerMessage.content[8:]
    query = query.replace(" ", "+")
    query = ''.join(e for e in query if e.isalnum() or e == "+")
    await triggerMessage.channel.send( "http://lmgtfy.com/?q=" + query)

@commands.registerEventHandler(name="buydinner")
async def buydinner(triggerMessage):
    praise = random.choice(phrasebank["praises"])
    target = triggerMessage.author.name
    praise = praise.replace("$who", target)
    print("praise: " + praise)
    await triggerMessage.channel.send( praise)

@commands.registerEventHandler(name="baddragon")
async def baddragon(triggerMessage):
    dragon = random.choice(phrasebank["dragons"])
    print("dragon: " + dragon)
    await triggerMessage.channel.send( "https://bad-dragon.com/products/"+dragon)

@commands.registerEventHandler(name="tingle")
async def tingle(triggerMessage):
    tingle = "http://amazon.com/" + random.choice(phrasebank["tingles"])
    print("tingle: " + tingle)
    await triggerMessage.channel.send( tingle)

@commands.registerEventHandler(name="pal")
async def pal(triggerMessage):
    if random.randrange(100) < 2:
        await triggerMessage.channel.send( "Go fuck yourself " + triggerMessage.author.name)
    else:
        await triggerMessage.channel.send( "Yes this is pal, yes this is 60 FPS")

@commands.registerEventHandler(name="mango")
async def mango(triggerMessage):
    mango = random.choice(phrasebank["mango"])
    await triggerMessage.channel.send( mango)

@commands.registerEventHandler(name="8ball")
async def eightball(triggerMessage):
    ball = random.choice(phrasebank["8balls"])
    #print("8ball: " + ball)
    await triggerMessage.channel.send( ":8ball: " + ball)

@commands.registerEventHandler(name="tests")
async def tests(triggerMessage):
    target = triggerMessage.author
    await target.send("Take each of the following tests. Save a screenshot of each result.\nMBTI: http://www.humanmetrics.com/cgi-win/jtypes2.asp\nEnneagram: http://www.eclecticenergies.com/enneagram/test.php Take both tests for best results.\nBIG5: http://personality-testing.info/tests/BIG5.php\nTemperaments: http://personality-testing.info/tests/O4TS/")
    # target.send("MBTI: http://www.humanmetrics.com/cgi-win/jtypes2.asp")
    # target.send("Enneagram: http://www.eclecticenergies.com/enneagram/test.php")
    # target.send("Take both tests for best results.")
    # target.send("BIG5: http://personality-testing.info/tests/BIG5.php")
    # target.send("Temperaments: http://personality-testing.info/tests/O4TS/")    

@commands.registerEventHandler(name="popori")
async def popori(triggerMessage):
    await triggerMessage.channel.send( "https://www.youtube.com/watch?v=gbNN3grTdDk")

@commands.registerEventHandler(name="constitution")
async def constitution(triggerMessage):
    await triggerMessage.channel.send( "https://docs.google.com/document/d/1XKFRQhzxwhjjtW1RnCc_ZhesRqavvM3F5z1LALfve48/")

@commands.registerEventHandler(name="wiki")
async def wiki(triggerMessage):
    await triggerMessage.channel.send( "http://iaa.wikia.com")

@commands.registerEventHandler(name="application")
async def application(triggerMessage):
    await triggerMessage.channel.send( "https://docs.google.com/forms/d/1a6fXy0b9uimE789VLFUyUUvkbjVDEx3cYfutXBT8WOQ/viewform")

@commands.registerEventHandler(triggerType="\\messageNoBot", name="unflip")
@commands.messageHandlerFilter("(╯°□°）╯︵ ┻━┻")
async def unflip(triggerMessage):
    await triggerMessage.channel.send( "┬─┬﻿ ノ( ゜-゜ノ)")

@commands.registerEventHandler(triggerType="\\messageNoBot", name="kk")
@commands.messageHandlerFilter("kk")
async def kkk(triggerMessage):
    if triggerMessage.content.__len__() == 2:
        await triggerMessage.channel.send( "k")

@commands.registerEventHandler(name="floor")
async def floor(triggerMessage):
    await triggerMessage.channel.send( "http://i.imgur.com/3OYeOxK.jpg")

@commands.registerEventHandler(name="sonic")
async def sonic(triggerMessage):
    if random.randint(0,1) != 0:
        await triggerMessage.channel.send( "http://archiesonic.wikia.com/wiki/Special:Random")
    else:
        await triggerMessage.channel.send( "http://sonicfanon.wikia.com/wiki/Special:Random")
        
@commands.registerEventHandler(triggerType="\\messageNoBot", name="plot")
@commands.messageHandlerFilter("plot", filterType="contains")
async def plot(triggerMessage):
    if client.user in triggerMessage.mentions:
        await triggerMessage.channel.send( random.choice(phrasebank["plots"]))

@commands.registerEventHandler(triggerType="\\messageNoBot", name="ㅋ")
@commands.messageHandlerFilter("ㅋ")
async def disrespects(triggerMessage):
    if triggerMessage.content.__len__() == 1:
        await triggerMessage.channel.send( triggerMessage.author.name + " has revoked their respects.")
      
@commands.registerEventHandler(triggerType="\\messageNoBot", name="F")
@commands.messageHandlerFilter("F")
async def respects(triggerMessage):
    if triggerMessage.content.__len__() == 1:
        raremsg = random.randrange(100)
        if raremsg < 2:
            await triggerMessage.channel.send( triggerMessage.author.name + " has sold missiles to Iran.")
        elif raremsg < 5:
            await triggerMessage.channel.send( triggerMessage.author.name + " has sent crack to inner cities.")
        else:
            await triggerMessage.channel.send( triggerMessage.author.name + " has paid their respects.")
      
@commands.registerEventHandler(triggerType="\\messageNoBot", name="X")
@commands.messageHandlerFilter("X")
async def doubt(triggerMessage):
    if triggerMessage.content.__len__() == 1:
        await triggerMessage.channel.send( triggerMessage.author.name + " doubts that.")
      

@commands.registerEventHandler(name="iaa")
@commands.registerEventHandler(name="IAA")
async def IAA(triggerMessage):
 #   rw = RandomWords()
 #   NewName = rw.random_word('i').capitalize() + " " + rw.random_word('a').capitalize() + " " + rw.random_word('a').capitalize()
 #   await triggerMessage.guild.edit(name=f"{NewName}-Official")
    await triggerMessage.channel.send("IAA, more like I Am Gay")

@commands.registerEventHandler(name="Contributors")
@commands.registerEventHandler(name="contributors")
async def CONTRIBUTER(triggerMessage):
    await triggerMessage.channel.send("The Contributors are")
    for member in triggerMessage.guild.members:
        for role in member.roles:
            if role.name == "Contributors":
                await triggerMessage.channel.send(f"{member.display_name}")

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
            await triggerMessage.channel.send( "Added phrase " + phrase)
            
