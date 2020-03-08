import commands
import permissions
import discord
import requests
import random
import time
import json
from xml.dom import minidom
import sqlite3, atexit
from json import JSONDecodeError
from PIL import Image, ImageDraw, ImageFont
import io

client = None
    
def getResponse(endpoint, tags, limit=20):
    headers = {"user-agent":"[^_^]/1.0"}
    t = tags.pop(0)
    for x in tags:
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
    print(len(data))
    with open("out."+file_extension, 'wb') as f:
        f.write(data)
        f.close()
        
    return "out."+file_extension
    
def gelbooru(tags, return_tags=False):
    tags.append("-loli")
    tags.append("-shota")
    j = getData("http://gelbooru.com/index.php?page=dapi&limit={0}&s=post&&q=index&json=1&tags={1}", tags)
    if not return_tags:
        target = j[random.randint(0, len(j))]['file_url']
        return downloadImage(target)
    else:
        i = random.randint(0, len(j))
        target = j[i]['file_url']
        return (downloadImage(target), j[i]['tags'])

#tags should be a list of desired tags
def e621(tags, return_tags=False):
    j = getData("http://e621.net/posts.json?limit={0}&tags={1}", tags)['posts']
    if not return_tags:
        target = j[random.randint(0, len(j))]['file']['url']
        return downloadImage(target)
    else:
        i = random.randint(0, len(j))
        target = j[i]['file']['url']
        tags = []
        for t in ['general', 'species', 'artist', 'character', 'copyright', 'lore', 'meta']:
            for tag in j[i]['tags'][t]:
                tags.append(tag)
        return (downloadImage(target), tags)

def rule34(tags, return_tags=False):
    dom = getDOM("https://rule34.xxx/index.php?page=dapi&s=post&q=index&limit={0}&tags={1}", tags)
    if not return_tags:
        target = j[random.randint(0, len(j))]['file_url']
        return downloadImage(target)
    else:
        i = random.randint(0, len(j))
        target = j[i]['file_url']
        return (downloadImage(target), j[i]['tags'])
    
functionMap = {"e621":e621, "gelbooru":gelbooru, "rule34":rule34}

async def postRandom(channel, booru, tags):
    try:
        out = functionMap[booru](tags)
        async with channel.typing():
            with open(out, "rb") as image:
                await channel.send(file=discord.File(image, filename=out))
    except IndexError:
        await channel.send("Oopsie woopsie Uwu. " + booru + " returned no search results.")
    except KeyError:
        await channel.send("Oopsie woopsie. " + booru + " is not supported.\nSupported boorus: "+str(SUPPORTED))
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
        await triggerMessage.channel.send( "Syntax is `!booru booru_name tag0 ...`\nCurrently supported boorus: " + str(list(functionMap.keys())))
        return
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
    filename = addsecret(e621(["furry"]))[0]
    if filename is not None:
        with open(filename, "rb") as image:
            await triggerMessage.channel.send(file=discord.File(image, filename="secret.png"))
    else:
        await triggerMessage.channel.send("Failed to generate image")

def addsecret(file_name):
    chars = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghkmnopqrstuvwxyz1234567890"
    pw = ""
    for i in range(6):
        pw += random.choice(chars)
        
    #get an image from e621
    #we can mess with tags later
    bg = Image.open(file_name)
    
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
    out = io.BytesIO()
    bg.save("out.png", format="PNG")
    return ("out.png", pw)
  
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
    filename = makedoge(x, y)
    if filename is not None:
        with open(filename, "rb") as image:
            await triggerMessage.channel.send(file=discord.File(image, filename="doge.png"))
    else:
        await triggerMessage.channel.send("Failed to generate image")

    
def makedoge(file_name, tags):
    colors = ["Red", "Green", "GreenYellow", "Magenta", "Cyan", "Blue", "White", "Black", "Orange", "Yellow", "Grey"]
    colors = random.sample(colors, 8)
    # this lets us take either the string straight from the json or an already split up list
    if type(tags) == str:
        tags = tags.split(" ")

    img = Image.open(file_name)
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
        
    img.save("out.png")
    return "out.png"

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
    member = discord.utils.find(lambda m: m.id == id, channel.server.members)
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
            j = getData("http://e621.net/post/index.json?limit={0}&tags={1}", ["order:random","-scat","-young","-fart"])
            target = None
            for i in j: # look for a suitable post
                file_ext = i["file_ext"]
                if i["file_ext"] not in ['png', 'jpg']:
                    continue
                if len(i["tags"]) <= 5:
                    continue
                target = i
                break
                
            if target is None:
                await triggerMessage.channel.send( "Oopsie woopsie Uwu. Couldn't find a suitable post. Try again?")
                return   
            tags = target["tags"].casefold().split(" ")
            target = target["file_url"]
            async with triggerMessage.channel.typing():
                filename = downloadImage(target)
                
                with open(filename, "rb") as image:
                    await triggerMessage.channel.send(file=discord.File(image, filename=filename))
                
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
    if triggerMessage.channel not in gameInstances:
        await triggerMessage.channel.send( "No game in progress")
        return
    
    args = triggerMessage.content.split()
    resultText = ""
    for arg in args[1:]:
        resultText += gameInstances[triggerMessage.channel].guess(str(arg), triggerMessage.author.id) + "\n"
    await triggerMessage.channel.send( resultText)
        
    if len(gameInstances[triggerMessage.channel].tags) == 0:
        await endBooruGame(triggerMessage)

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
