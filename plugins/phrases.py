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

@commands.registerEventHander(name="getdragons")
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

@commands.registerEventHander(name="lart")
async def lart(triggerMessage):
    lart = random.choice(phrasebank["larts"])
    target = triggerMessage.content[6:]
    if not target:
        target = triggerMessage.author.name
    lart = lart.replace("$who", target)
    print("Lart: " + lart)
    await client.send_message(triggerMessage.channel, lart)

@commands.registerEventHander(name="praise")
async def praise(triggerMessage):
    praise = random.choice(phrasebank["praises"])
    target = triggerMessage.content[8:]
    if not target:
        target = triggerMessage.author.name
    praise = praise.replace("$who", target)
    print("praise: " + praise)
    await client.send_message(triggerMessage.channel, praise)

@commands.registerEventHander(triggerType="\\messageNoBot", name="keikaku")
@commands.messageHandlerFilter("keikaku", filterType="cqc")
async def keikaku(triggerMessage):
    await client.send_message(triggerMessage.channel, "tl note: keikaku means plan")

      
<<<<<<< HEAD
@commands.registerEventHander(triggerType="\\messageNoBot", name="help")
@commands.messageHandlerFilter("help")
async def keikaku(triggerMessage):
    await client.send_message(triggerMessage.author, """admin\n
This is a plugin for a few basic admin functions and the almighty censorship cannon.\n
Feared by Jerries everywhere.\n
!leave: Tells the bot to leave. Only works if you're Azimath.\n
!invite: Invites the bot to a new server. Only works if you're Azimath.\n
!register: adds you to the permissions system\n
!addnode: adds a permissions node to a user if you are a manager\n
!delete @Target <channel> numberofmessages : Deletes numberofmessages sent by Target. If no channel is specified assumes channel it was sent in.\n
audiophrases\n
A plugin for playing various sound clips.\n
!setcd : Changes the cooldown between commands. Default is 30 seconds.\n
!sound, !play <soundname> : plays <soundname> sound clip from our library\n
!listsounds : lists the sounds in our library\n
!addsound <name> <link> : downloads the sound from a youtube_dl compatible <link> and puts it in our library as <name>\n
!youtube <link> : plays the audio from any youtube_dl compatible page\n
daygetter\n
None\n
dunnos\n
None\n
games\n
This is a plugin for fun things you can use to play with [^_^].\n
!flip, !coin: Flips a coin\n
!trick: Does a super cool magic trick\n
numbergame\n
A plugin that plays a simple high-low number guessing game.\n
!startgame <range> : starts a game with a number between 1 and range. range is 100 if not given.\n
!guess number : Enters a guess, then tells you if it is high, low, or correct. A correct guess ends the game. Guesses that have been guessed before are not acccepted.\n
!stop : stops the game in the current channel\n
phrases\n
A plugin for giving various kinds of random phrases.\n
!lart user : uses the LART on the given user.\n
!praise user : praises the user.\n
!pal : is this pal?\n
!mango : where is mang0?\n
!eightball : Ask the magic eightball a question. Satisfaction not guarunteed.\n
!addphrase phrasebank phrase : adds phrase to the given phrasebank. The phrasebank for a given command is generally the plural of the command\n
!baddragon : give me some sugah, baby\n
!wiki : links to the iaa wiki\n
!apply : links to the membership application\n
!tests : PMs the user links to all required membership tests\n
!constitution : links to the constitution\n
!sonic : links to a random page on either the archie sonic wiki or the sonic fanon wiki\n
!tingle : links to a random tingler\n
sudo\n
A plugin to make the bot say things in channels. Mods only.\n
!sudo channel stuff : says stuff in channel\n
util\n
This is a plugin for developer utilities to aid in programming and debugging.\n
!info: pms information about the channel, server, and author\n
!game: sets the name of the game the bot is playing\n
wingdings\n
A plugin for translating to and from WingDings. All credit goes to Dublo.\n
!translate <message> : :snowflake::white_square_button::cancer::black_small_square::small_orange_diamond::black_circle::cancer::large_orange_diamond::scorpius::small_orange_diamond:       :cancer:       :white_circle::scorpius::small_orange_diamond::small_orange_diamond::cancer::capricorn::scorpius:       :large_orange_diamond::white_small_square:       :white_small_square::white_square_button:       :sagittarius::white_square_button::white_small_square::white_circle:       :sparkle::pisces::black_small_square::capricorn::thumbsdown::pisces::black_small_square::capricorn::small_orange_diamond:""")
=======
@commands.registerEventHander(name="help")
async def help(triggerMessage):
    await client.send_message(triggerMessage.author, phrasebank["help"])
>>>>>>> patch-3
      
@commands.registerEventHander(name="lmgtfy")
async def lmgtfy(triggerMessage):
    query = triggerMessage.content[8:]
    query = query.replace(" ", "+")
    query = ''.join(e for e in query if e.isalnum() or e == "+")
    await client.send_message(triggerMessage.channel, "http://lmgtfy.com/?q=" + query)

@commands.registerEventHander(name="buydinner")
async def buydinner(triggerMessage):
    praise = random.choice(phrasebank["praises"])
    target = triggerMessage.author.name
    praise = praise.replace("$who", target)
    print("praise: " + praise)
    await client.send_message(triggerMessage.channel, praise)

@commands.registerEventHander(name="baddragon")
async def baddragon(triggerMessage):
    dragon = random.choice(phrasebank["dragons"])
    print("dragon: " + dragon)
    await client.send_message(triggerMessage.channel, "https://bad-dragon.com/products/"+dragon)

@commands.registerEventHander(name="tingle")
async def tingle(triggerMessage):
    tingle = "http://amazon.com/" + random.choice(phrasebank["tingles"])
    print("tingle: " + tingle)
    await client.send_message(triggerMessage.channel, tingle)

@commands.registerEventHander(name="pal")
async def pal(triggerMessage):
    if random.randrange(100) < 2:
        await client.send_message(triggerMessage.channel, "Go fuck yourself " + triggerMessage.author.name)
    else:
        await client.send_message(triggerMessage.channel, "Yes this is pal, yes this is 60 FPS")

@commands.registerEventHander(name="mango")
async def mango(triggerMessage):
    mango = random.choice(phrasebank["mango"])
    await client.send_message(triggerMessage.channel, mango)

@commands.registerEventHander(name="8ball")
async def eightball(triggerMessage):
    ball = random.choice(phrasebank["8balls"])
    #print("8ball: " + ball)
    await client.send_message(triggerMessage.channel, ":8ball: " + ball)

@commands.registerEventHander(name="tests")
async def tests(triggerMessage):
    target = triggerMessage.author
    await client.send_message(target, "Take each of the following tests. Save a screenshot of each result.\nMBTI: http://www.humanmetrics.com/cgi-win/jtypes2.asp\nEnneagram: http://www.eclecticenergies.com/enneagram/test.php Take both tests for best results.\nBIG5: http://personality-testing.info/tests/BIG5.php\nTemperaments: http://personality-testing.info/tests/O4TS/")
    # client.send_message(target, "MBTI: http://www.humanmetrics.com/cgi-win/jtypes2.asp")
    # client.send_message(target, "Enneagram: http://www.eclecticenergies.com/enneagram/test.php")
    # client.send_message(target, "Take both tests for best results.")
    # client.send_message(target, "BIG5: http://personality-testing.info/tests/BIG5.php")
    # client.send_message(target, "Temperaments: http://personality-testing.info/tests/O4TS/")    

@commands.registerEventHander(name="popori")
async def popori(triggerMessage):
    await client.send_message(triggerMessage.channel, "https://www.youtube.com/watch?v=gbNN3grTdDk")

@commands.registerEventHander(name="constitution")
async def constitution(triggerMessage):
    await client.send_message(triggerMessage.channel, "https://docs.google.com/document/d/1XKFRQhzxwhjjtW1RnCc_ZhesRqavvM3F5z1LALfve48/")

@commands.registerEventHander(name="wiki")
async def wiki(triggerMessage):
    await client.send_message(triggerMessage.channel, "http://iaa.wikia.com")

@commands.registerEventHander(name="application")
async def application(triggerMessage):
    await client.send_message(triggerMessage.channel, "https://docs.google.com/forms/d/1bURXLKIo30XLX3RASg2B8XVLsYpp6GYXn84IT2F9hbM/viewform")

@commands.registerEventHander(triggerType="\\messageNoBot", name="unflip")
@commands.messageHandlerFilter("(╯°□°）╯︵ ┻━┻")
async def unflip(triggerMessage):
    await client.send_message(triggerMessage.channel, "┬─┬﻿ ノ( ゜-゜ノ)")

@commands.registerEventHander(triggerType="\\messageNoBot", name="kk")
@commands.messageHandlerFilter("kk")
async def kkk(triggerMessage):
    if triggerMessage.content.__len__() == 2:
        await client.send_message(triggerMessage.channel, "k")

@commands.registerEventHander(name="floor")
async def floor(triggerMessage):
    await client.send_message(triggerMessage.channel, "http://i.imgur.com/3OYeOxK.jpg")

@commands.registerEventHander(name="sonic")
async def sonic(triggerMessage):
    if random.randint(0,1) != 0:
        await client.send_message(triggerMessage.channel, "http://archiesonic.wikia.com/wiki/Special:Random")
    else:
        await client.send_message(triggerMessage.channel, "http://sonicfanon.wikia.com/wiki/Special:Random")
        
@commands.registerEventHander(triggerType="\\messageNoBot", name="plot")
@commands.messageHandlerFilter("plot", filterType="contains")
async def plot(triggerMessage):
    if client.user in triggerMessage.mentions:
        await client.send_message(triggerMessage.channel, random.choice(phrasebank["plots"]))

@commands.registerEventHander(triggerType="\\messageNoBot", name="F")
@commands.messageHandlerFilter("F")
async def respects(triggerMessage):
    if triggerMessage.content.__len__() == 1:
        await client.send_message(triggerMessage.channel, triggerMessage.author.name + " has paid their respects.")

@commands.registerEventHander(name="addphrase")
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
            
