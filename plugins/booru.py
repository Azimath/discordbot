import asyncio
import atexit
import io
import json
import random
import sqlite3
import time
from json import JSONDecodeError
from xml.dom import minidom
import math

import discord
import requests
try:
    from buttplug.client import (ButtplugClient, ButtplugClientConnectorError,
                                 ButtplugClientDevice,
                                 ButtplugClientWebsocketConnector)
except:
    print("Couldn't find module 'buttplug'")

from PIL import Image, ImageDraw, ImageFont

import commands
import permissions

client = None
    
def getResponse(endpoint, tags, limit=20):
    headers = {"user-agent":"[^_^]/1.0"}
    t = tags[0]
    for x in tags[1:]:
        t+="+"+x
    session = requests.Session()
    session.headers.update(headers)

    response = session.get(endpoint.format(limit, t))
    return response

def getData(endpoint, tags, limit=20): # json
    response = getResponse(endpoint, tags, limit=limit)
    j = response.json()
    return j

def getDOM(endpoint, tags, limit=20):
    response = getResponse(endpoint, tags, limit=limit)
    return minidom.parseString(response.text)

def downloadImage(url):
    headers = {"user-agent":"[^_^]/1.0"}
    session = requests.Session()
    session.headers.update(headers)
    
    file_response = session.get(url)
    file_extension = url[url.rfind(".")+1:]
    
    #https://stackoverflow.com/a/39217788
    data = file_response.content
    
        
    return io.BufferedReader(io.BytesIO(data)), file_extension
    
def gelbooru(tags, return_tags=False):
    tags.append("-loli")
    tags.append("-shota")
    j = getData("http://gelbooru.com/index.php?page=dapi&limit={0}&s=post&&q=index&json=1&tags={1}", tags)
    if not return_tags:
        target = random.choice(j['post'])['file_url']
        return downloadImage(target)
    else:
        target = random.choice(j['post'])
        return (downloadImage(target['file_url']), target['tags'])

#tags should be a list of desired tags
def e621(tags, return_tags=False):
    j = getData("http://e621.net/posts.json?limit={0}&tags={1}", tags)['posts']
    if not return_tags:
        i = random.randint(0, len(j)-1)
        target = j[i]['file']['url']
        if target is not None:
            return downloadImage(target)
        else:
            print(j[i])
            return None
    else:
        i = random.randint(0, len(j)-1)
        target = j[i]['file']['url']
        tags = []
        for t in ['general', 'species', 'artist', 'character', 'copyright', 'lore', 'meta']:
            for tag in j[i]['tags'][t]:
                tags.append(tag)
        return (downloadImage(target), tags)

def rule34(tags, return_tags=False):
    j = getDOM("https://rule34.xxx/index.php?page=dapi&s=post&q=index&limit={0}&tags={1}", tags).getElementsByTagName("post")
    if not return_tags:
        target = j[random.randint(0, len(j)-1)].attributes['file_url'].value
        return downloadImage(target)
    else:
        i = random.randint(0, len(j)-1)
        target = j[i].attributes['file_url'].value
        return (downloadImage(target), j[i].attributes['tags'].value.split(" ")[1:-1])
    
functionMap = {"e621":e621, "gelbooru":gelbooru, "rule34":rule34}
SUPPORTED = str(list(functionMap.keys()))

async def postRandom(channel, booru, tags):
    global SUPPORTED
    if booru not in functionMap:
        await channel.send("Oopsie woopsie. " + booru + " is not supported.\nSupported boorus: " + SUPPORTED)
        return
    try:
        data, extension = functionMap[booru](tags)
        async with channel.typing():
            await channel.send(file=discord.File(data, filename="fur."+extension))
            data.close()
    except IndexError:
        await channel.send("Oopsie woopsie Uwu. " + booru + " returned no search results.")
    except KeyError:
        await channel.send("Oopsie woopsie. " + booru + " changed their api format or something probably.")
    except JSONDecodeError:
        await channel.send("Oopsie Woopsie. Failed to decode json. " + booru + " returned an empty response, or something weird")
    except Exception as e:
        await channel.send("Oopsie woopsie Uwu. One of many possible disasters has occured. Try `!booru help`\nException: " + type(e).__name__)
        print(e) #hopefully this does something useful

@commands.registerEventHandler(name="booru", exclusivity="global")
async def booru(triggerMessage):
    global SUPPORTED
    tokens = triggerMessage.content.split()
    #if (len(tokens) == 1 or tokens[1].lower() == "help"):
    if (len(tokens) <= 2):
        await triggerMessage.channel.send( "Syntax is `!booru booru_name tag0 ...`\nCurrently supported boorus: " + SUPPORTED)
        return
    if (triggerMessage.channel.type is discord.ChannelType.text and not triggerMessage.channel.is_nsfw()):
        tokens.append("rating:safe")
    else:
        tokens.extend(["-young", "-scat","-fart"]) #Anti trash
    await postRandom(triggerMessage.channel, tokens[1], tokens[2:8]) # chop off extra tags
    # TODO: Filter remaining blacklist tags from results
    return   
    
@commands.registerEventHandler(name="unbusy")
async def unbusy(triggerMessage):
    global busy
    busy = False
    
@commands.registerEventHandler(name="secret", exclusivity="global")
async def postsecret(triggerMessage):
    data_in = e621(["anthro"])
    if data_in is not None:
            data, _ = addsecret(data_in[0])
            await triggerMessage.channel.send(file=discord.File(data, filename="secret.png"))
            data.close()
    else:
        await triggerMessage.channel.send("Failed to generate image")

def addsecret(data_in):
    chars = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghkmnopqrstuvwxyz1234567890"
    pw = ""
    for i in range(6):
        pw += random.choice(chars)
        
    #get an image from e621
    #we can mess with tags later
    bg = Image.open(data_in)
    
    #make sure the image has an alpha channel so alpha_composite will work later
    bg = bg.convert(mode="RGBA")
    bg.putalpha(255)
    
    # magic formula: size = x/y/z
    # where x is the x dimension of the image
    # y is the ratio of image width to text width
    # and z is the ratio of pixels to points
    # this finds the font size to produce text of the correct pixel width
    fontsize = int(bg.size[0]/8/5.3)
    fontsize = (fontsize, 12)[fontsize < 12]
    # font can be changed later
    font = ImageFont.truetype("arial.ttf", fontsize)
    
    #get the dimensions of rendered text
    x,y = font.getsize(pw)
    img = Image.new("RGBA", (x+6, y+6), (0,0,0,0))
    draw = ImageDraw.Draw(img)
    
    #draw the text on a canvas, rotate, then get new dimensions
    draw.text((0, 1), pw, font=font, fill=(0, 0, 0, 127))
    draw.text((2, 1), pw, font=font, fill=(0, 0, 0, 127))
    draw.text((1, 0), pw, font=font, fill=(0, 0, 0, 127))
    draw.text((1, 2), pw, font=font, fill=(0, 0, 0, 127))
    draw.text((1,1), pw, fill=(255, 255, 255, 127), font=font)
    img = img.rotate(random.randrange(0,360), resample=Image.NEAREST, expand=1)
    
    #randomly pad the text image to align the text with a random location on the background image
    x,y = img.size
    xb,yb = bg.size

    if xb-x <= 0 or yb-y <= 0:
        print("Too small image {} by {}, text size {} by {}, {} points".format(xb, yb, x, y, fontsize))
        return None

    x1 = random.randrange(0, xb-x)
    x2 = xb-x1
    y1 = random.randrange(0, yb-y)
    y2 = yb-y1
    img = img.crop((-x1, -y1, x2+x, y2+y))
    
    #composite images and save
    bg.alpha_composite(img)
    output = io.BytesIO()
    bg.save(output, format="PNG")
    output.seek(0)
    return (io.BufferedReader(output), pw)
  
@commands.registerEventHandler(name="doge", exclusivity="global")      
async def doge(triggerMessage):
    global SUPPORTED
    tokens = triggerMessage.content.split()
    if (len(tokens) == 1):
        site = "e621"
    else:
        site = tokens[1]
        
    if len(tokens) <= 2:
        tags = ["dog", "rating:explicit"]
    else:
        tags = tokens[2:8]

    tags.extend(["-young", "-scat","-fart"]) #Anti trash
    
    x,y = functionMap[site](tags, return_tags=True)
    data = makedoge(x[0], y)
    if data is not None:
        await triggerMessage.channel.send(file=discord.File(data, filename="doge.png"))
        data.close()
    else:
        await triggerMessage.channel.send("Failed to generate image")

    
def makedoge(data, tags):
    colors = ["Red", "Green", "GreenYellow", "Magenta", "Cyan", "Blue", "White", "Black", "Orange", "Yellow", "Grey"]
    colors = random.sample(colors, 8)
    # this lets us take either the string straight from the json or an already split up list
    if type(tags) == str:
        tags = tags.split(" ")

    img = Image.open(data)
    draw = ImageDraw.Draw(img)
    
    phrases = ["wow."]
    tags = random.sample(tags, 5) # pick 5 tags at random
    
    phrases.append("such {}".format(tags[0]))
    phrases.append("much {}".format(tags[1]))
    phrases.append("very {}".format(tags[2]))
    phrases.append("so {}".format(tags[3]))
    phrases.append("how {}".format(tags[4]))
    phrases.append("Cool")
    phrases.append("neat")
    
    random.shuffle(phrases)
    
    xs = [int(img.size[0]*(i/10))+(i==0)*10 for i in range(0,9)] # fun list iteration
    ys = [int(img.size[1]*(i/9)) for i in range(0,9)]
    random.shuffle(xs)
    
    font = ImageFont.truetype(font="comic.ttf", size=int((img.size[0], img.size[1])[img.size[0] < img.size[1]]/6/5.3))
    for i in range(len(phrases)):
        draw.text((xs[i],ys[i]), phrases[i], fill=colors[i], font=font)
        
    output = io.BytesIO()
    img.save(output, format="PNG")
    output.seek(0)
    return io.BufferedReader(output)

buttplugClients = {}

@commands.registerEventHandler(name="keister", exclusivity="global")  
async def keister(triggerMessage):
    global buttplugClients

    if triggerMessage.author.id in buttplugClients:
        buttplugClients[triggerMessage.author.id].stop_scanning()
        buttplugClients[triggerMessage.author.id].disconnect()

    buttplugClients[triggerMessage.author.id] = ButtplugClient(triggerMessage.author.name)
    connector = ButtplugClientWebsocketConnector(triggerMessage.content.split()[1])

    await buttplugClients[triggerMessage.author.id].connect(connector)
    await buttplugClients[triggerMessage.author.id].start_scanning()
    await triggerMessage.channel.send("Keistered!")

@commands.registerEventHandler(name="unkeister", exclusivity="global")  
async def unkeister(triggerMessage):
    global buttplugClients

    if triggerMessage.author.id in buttplugClients:
        for devid in buttplugClients[triggerMessage.author.id].devices:
            await buttplugClients[triggerMessage.author.id].devices[devid].send_stop_device_cmd()
        await buttplugClients[triggerMessage.author.id].stop_scanning()
        await buttplugClients[triggerMessage.author.id].disconnect()
        buttplugClients.pop(triggerMessage.author.id)

        await triggerMessage.channel.send("Unkeistered!")

class BooruGame:
    def __init__(self, tags, url):
        self.userScores = {}
        self.tags = tags
        self.previousGuesses = []
        self.timeRemaining = 30 + 2 * len(tags)
        self.url = url
        
    def wasguessed(self, guess):
        return guess in self.previousGuesses
        
    def guess(self, guess, user):
        guess = guess.replace("`", "").casefold()
        if user not in self.userScores:
            self.userScores[user] = []
            
        if guess in self.previousGuesses:
            self.timeRemaining -= 1
            return "`" + guess + "` was already guessed."
        
        if guess in self.tags:
            self.userScores[user].append(guess)
            self.previousGuesses.append(guess)
            self.tags.remove(guess)
            self.timeRemaining += 5
            return "`" + guess + "`: Correct! " + str(1) + " points. " + str(len(self.tags)) + " tags left."
        else:    
            return "`" + guess + "`: Nope!"
            
gameInstances = {}


gameHistoryDB = None
@atexit.register
def exit():
    gameHistoryDB.close()
    
gameHistoryDB = sqlite3.connect("boorugame.db")
gameHistoryDBCursor= gameHistoryDB.cursor()
gameHistoryDBCursor.execute("create table if not exists Games (time integer, image text, channel text, remainingTags text, guessedTags text, results text, winner text, playercount integer)")
gameHistoryDB.commit()
    
def nameFromId(channel, id):
    member = channel.guild.get_member(id)
    name = member.name
    if member.nick is not None:
        name = member.nick
    return name
        
async def endGame(channel):
    global gameInstances
    
    game = gameInstances[channel]
    del gameInstances[channel]
    
    endMsg = "Game Complete!\n" + "Unguessed tags were: `" + str(game.tags)+"`\n" + "Guessed tags were: `" + str(game.previousGuesses) + "`"
    await channel.send(endMsg)
    scoreDict = game.userScores
    scores = sorted([(k, len(scoreDict[k])) for k in scoreDict], key=lambda tup: tup[1], reverse=True)
    if len(scores) > 0:
        scoreString = ""
        for id, score in scores:
            name = nameFromId(channel, id)
            scoreString += "User " + str(name) + " scored " + str(score) + "\n"
        
        name = nameFromId(channel, scores[0][0])
        await channel.send(scoreString + "\n" + str(name) + " wins!")
        
        remainingJson = json.dumps(game.tags)
        guessedJson = json.dumps(game.previousGuesses)
        resultJson = json.dumps(game.userScores)
        gameData = (time.time(), game.url, channel.id, remainingJson, guessedJson, resultJson, scores[0][0], len(scores))
        gameHistoryDBCursor.execute("INSERT INTO Games VALUES (?,?,?,?,?,?,?,?)", gameData)
        gameHistoryDB.commit()

@commands.registerEventHandler(triggerType="\\timeTick", name="boorugametick")
async def updateTime():
    global gameInstances
    gamesToStop = []
    for c in gameInstances:
        gameInstances[c].timeRemaining -= 1
        if gameInstances[c].timeRemaining <= 0:
            gamesToStop.append(c)
            print("Stopping " + str(c))
    for c in gamesToStop:
        await c.send("Timed out!")
        await endGame(c)
        
def lookup_tag(tag):
    global headers
    session = requests.Session()
    session.headers.update(headers)
    response = session.get("http://e621.net/tag/index.json?name=" + tag)
    j = response.json()
    if (len(j) == 0):
        return 0
    else:
        return j[0]["count"]

@commands.registerEventHandler(name="bgs")
@commands.registerEventHandler(name="boorugamestart")
async def startBooruGame(triggerMessage):
    if triggerMessage.channel in gameInstances:
        await triggerMessage.channel.send( "A game is already in progress in this channel")
    else:
        tags = []
        target = ""
        try:    
            j = getData("http://e621.net/posts.json?limit={0}&tags={1}", ["order:random","-scat","-young","-fart"])['posts']
            target = None
            for i in j: # look for a suitable post
                if i["file"]["ext"] not in ['png', 'jpg']:
                    continue
                if len(i["tags"]) <= 5:
                    continue
                target = i
                break
                
            if target is None:
                await triggerMessage.channel.send( "Oopsie woopsie Uwu. Couldn't find a suitable post. Try again?")
                return

            for t in ['general', 'species', 'artist', 'character', 'copyright', 'lore', 'meta']:
                for tag in target['tags'][t]:
                    tags.append(tag)

            target = target["file"]["url"]
            async with triggerMessage.channel.typing():
                data, extension = downloadImage(target)
                
                await triggerMessage.channel.send(file=discord.File(data, filename="fur."+extension))
                data.close()
                
        except JSONDecodeError:
            await triggerMessage.channel.send( "Oopsie Woopsie. Failed to decode json.")
            return
        except Exception as e:
            await triggerMessage.channel.send( "Oopsie woopsie Uwu. One of many possible disasters has occured. Try `!booru help`\nException: " + type(e).__name__)
            print(e) #hopefully this does something useful
            return
        
        print(tags)
        
        gameInstances[triggerMessage.channel] = BooruGame(tags, target)
        await triggerMessage.channel.send( "Game started. The post has " + str(len(tags)) + " tags to guess.")

@commands.registerEventHandler(name="boorugamestop")
@commands.registerEventHandler(name="boorugamequit")
@commands.registerEventHandler(name="bgq")
async def endBooruGame(triggerMessage):
    await endGame(triggerMessage.channel)

@commands.registerEventHandler(name="bg")
@commands.registerEventHandler(name="booruguess")
async def booruGameGuess(triggerMessage):
    global buttplugClients

    if triggerMessage.channel not in gameInstances:
        await triggerMessage.channel.send( "No game in progress")
        return
    
    args = triggerMessage.content.split()
    resultText = ""
    for arg in args[1:]:
        resultText += gameInstances[triggerMessage.channel].guess(str(arg), triggerMessage.author.id) + "\n"
    await triggerMessage.channel.send(resultText)
        
    if len(gameInstances[triggerMessage.channel].tags) == 0:
        await endBooruGame(triggerMessage)
        for user, bpclient in buttplugClients.items():
            for devid, dev in bpclient.items():
                await dev.send_stop_device_cmd()
    else:
        for user, bpclient in buttplugClients.items():
            if user in gameInstances[triggerMessage.channel].userScores:
                score = len(gameInstances[triggerMessage.channel].userScores[user])
                for devid, dev in bpclient.items():
                    if "VibrateCmd" in dev.allowed_messages.keys():
                        await dev.send_vibrate_cmd(min(score/5, 1.0))

@commands.registerEventHandler(name="boorucoin")        
@commands.registerEventHandler(name="booruleaders")
async def booruLeaders(triggerMessage):
    ids = [x.id for x in triggerMessage.server.members]
    leaderboard = { k: winnerTally[k] for k in winnerTally if k in ids}
    
    leaderboardString = "YiffCoins earned:\n"
    for id in leaderboard:
        name = nameFromId(triggerMessage.channel, id)
        leaderboardString += name + " : " + str(leaderboard[id]) + "\n"
    await triggerMessage.channel.send( leaderboardString)

border = Image.open("tarot_frame.png")
font = ImageFont.truetype(font="comic.ttf", size=25)
def makecard(image, name, flipped):
    #Target size: 370x640
    #Border: 40 on top, 10 on bottom, 10 on sides
    cw = 370
    ch = 640

    bordw = 10

    tw = cw - 2 * bordw
    th = ch - 50

    cardimg = Image.new("RGBA", (cw,ch))

    if image.height < image.width:
        image = image.rotate(90, expand=True)
    
    sf = min(image.height/th, image.width/tw)
    image = image.resize((math.floor(image.width/sf), math.floor(image.height/sf)))
    print(image.width, image.height)
    image = image.crop(box=(image.width//2-tw//2, image.height//2-th//2, image.width//2+tw//2, image.height//2+th//2))

    cardimg.paste(image, (bordw,40))
    cardimg.paste(border, (0,0), border)
    
    draw = ImageDraw.Draw(cardimg)

    textx = math.floor(cw/2 - draw.textsize(name, font=font)[0]/2)
    draw.text((textx,0), name, font=font, fill=(0,0,0,255))

    if flipped:
        cardimg = cardimg.rotate(180)

    return cardimg

def stitch_images(images):
    endWidth = 10
    endHeight = 0

    for image in images:
        endWidth += image.width + 10
        endHeight = max(endHeight, image.height)
    
    result = Image.new('RGB', (endWidth, endHeight+20))

    xpos = 10
    for image in images:
        result.paste(image, (xpos, 10))
        xpos += image.width + 10
    
    return result

@commands.registerEventHandler(name="tarot")
async def e621_tarot(triggerMessage):
    # pick 3 cards
    
    deck = [
            (["anthro", "rating:explicit"], "The Anthro"),
            (["feral", "rating:explicit"], "The Feral"),
            (["human", "rating:explicit"], "The Human"),
            (["vore"], "The Devourer"),
            (["hyper_penis"], "The Tower"),
            (["hyper_breasts"], "The Sun and Moon"),
            (["cum_inflation"], "The Cum Inflation"),
            (["mammal", "rating:explicit"], "The Mammal"),
            (["scalie", "-dragon", "rating:explicit"], "The Scalie"),
            (["avian", "rating:explicit"], "The Bird"),
            (["tentacles", "rating:explicit"], "The Tentacles"),
            (["ejaculation"], "The Fountain"),
            (["sonic_the_hedgehog_(series)", "rating:explicit"], "The Sonic The Hedgehog Franchise"),
            (["my_little_pony", "rating:explicit"], "The Pony"),
            (["pokémon", "rating:explicit"], "The Pokémon"),
            (["bondage", "rating:explicit"], "The Bound Man"),
            (["diaper", "rating:safe"], "The Diaper"),
            (["dragon", "rating:explicit"], "The Dragon"),
            (["male/male", "rating:explicit"], "The Emperors"),
            (["male/female", "rating:explicit"], "The Lovers"),
            (["female/female", "rating:explicit"], "The Empresses"),
            (["clown"], "The Fool"),
            (["group_sex"], "The Orgy")        
            ]
    
    cards = random.sample(deck, 3)
    status = "Shuffles"
    statusMsg = await triggerMessage.channel.send(status)
    try:
        #fetch images and turn into tarots
        images = []
        for tags,name in cards:
            tags.extend(["-young", "order:random"])
            print(tags)
            images.append(makecard(image=Image.open(e621(tags)[0]), name=name, flipped=random.choice([False, False, True]) ))
            status += "\nDraws a card"
            await statusMsg.edit(content=status)
            
        # stitch into one image to post
        stitched = stitch_images(images)

        output = io.BytesIO()
        stitched.save(output, format="PNG")
        output.seek(0)
        data = io.BufferedReader(output)
        
        await triggerMessage.channel.send(file=discord.File(data, filename="tarot.png"))

        output.close()
    except Exception as e:
        await triggerMessage.channel.send("Reply hazy try again")
        raise e

