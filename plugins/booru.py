import commands
import permissions
import discord
import requests
import random
import time
import json
from xml.dom import minidom

from json import JSONDecodeError

client = None
    
def getResponse(endpoint, tags, limit=10):
    headers = {"user-agent":"[^_^]/1.0"}
    t = tags.pop(0)
    for x in tags:
        t+="+"+x
    session = requests.Session()
    session.headers.update(headers)

    response = session.get(endpoint.format(limit, t))
    return response

def getData(endpoint, tags, limit=10): # json
    response = getResponse(endpoint, tags, limit=10)
    j = response.json()
    return j

def getDOM(endpoint, tags, limit=10)
    response = getResponse(endpoint, tags, limit=10)
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
    
def gelbooru(tags):
    j = getData("http://gelbooru.com/index.php?page=dapi&limit={0}&s=post&&q=index&json=1&tags={1}", tags)
    
    target = j[random.randint(0, len(j))]['file_url']
    return downloadImage(target)

#tags should be a list of desired tags
def e621(tags):
    j = getData("http://e621.net/post/index.json?limit={0}&tags={1}", tags)
    
    target = j[random.randint(0, len(j))]['file_url']
    return downloadImage(target)

def rule34(tags):
    dom = getDom("https://rule34.xxx/index.php?page=dapi&s=post&q=index&limit={0}&tags={1}", tags)
    posts = dom.getElementsByTagName("post")
    
    target = posts[random.randint(0, len(posts))].getAttribute('file_url')
    return downloadImage(target)    
    
functionMap = {"e621":e621, "gelbooru":gelbooru, "rule34":rule34}

async def postRandom(booru, tags):
    try:
        out = functionMap[booru](tags)
        
        with open(out, "rb") as image:
            await client.send_file(triggerMessage.channel, image, filename=out)
    except IndexError:
        await client.send_message(triggerMessage.channel, "Oopsie woopsie Uwu. " + tokens[1] + " returned no search results.")
    except KeyError:
        await client.send_message(triggerMessage.channel, "Oopsie woopsie. " + tokens[1] + " is not supported.\nSupported boorus: "+str(SUPPORTED))
    except JSONDecodeError:
        await client.send_message(triggerMessage.channel, "Oopsie Woopsie. Failed to decode json. " + tokens[1] + " returned an empty response, or something weird")
    except Exception as e:
        await client.send_message(triggerMessage.channel, "Oopsie woopsie Uwu. One of many possible disasters has occured. Try `!booru help`\nException: " + type(e).__name__)
        print(e) #hopefully this does something useful

@commands.registerEventHandler(name="booru", exclusivity="global")
async def booru(triggerMessage):
    await client.send_typing(triggerMessage.channel)
    global SUPPORTED
    tokens = triggerMessage.content.split()
    #if (len(tokens) == 1 or tokens[1].lower() == "help"):
    if (len(tokens) <= 2):
        await client.send_message(triggerMessage.channel, "Syntax is `!booru booru_name tag0 ...`\nCurrently supported boorus: " + str(list(functionMap.keys())))
        return
    
    postRandom(tokens[1], tokens[2:])
    
    return    
    
@commands.registerEventHandler(name="unbusy")
async def unbusy(triggerMessage):
    global busy
    busy = False

class BooruGame:
    def __init__(self, tags):
        self.userScores = {}
        self.tags = tags
        self.previousGuesses = []
        self.timeRemaining = 15 + 3 * len(tags)
        
    def wasguessed(self, guess):
        return guess in self.previousGuesses
        
    def guess(self, guess, user):
        guess = guess.replace("`", "").casefold()
        if user not in self.userScores:
            self.userScores[user] = 0
            
        if guess in self.previousGuesses:
            self.timeRemaining -= 1
            return "`" + guess + "` was already guessed."
        
        if guess in self.tags:
            self.userScores[user] += 1
            self.previousGuesses.append(guess)
            self.tags.remove(guess)
            self.timeRemaining += 5
            return "`" + guess + "`: Correct! " + str(1) + " points. " + str(len(self.tags)) + " tags left."
        else:    
            return "`" + guess + "`: Nope!"
            
gameInstances = {}

winnerTally = {}

try:
    with open("booruwins.json", "r") as winfile:
        winnerTally = json.loads(winfile.read())
except FileNotFoundError:
    with open("booruwins.json", "w") as winfile:
        winfile.write(json.dumps({}))
    
def nameFromId(channel, id):
    member = discord.utils.find(lambda m: m.id == scores[0][0], channel.server.members)
    name = member.name
    if member.nick is not None:
        name = member.nick
    return name
    
async def endGame(channel):
    global gameInstances
    
    game = gameInstances[channel]
    del gameInstances[channel]
    
    endMsg = "Game Complete!\n" + "Unguessed tags were: `" + str(game.tags)+"`\n" + "Guessed tags were: `" + str(game.previousGuesses) + "`"
    await client.send_message(channel, endMsg)
    scoreDict = game.userScores
    scores = [(k, scoreDict[k]) for k in sorted(scoreDict, key=scoreDict.get, reverse=True)]
    if len(scores) > 0:
        scoreString = ""
        for id, score in scores:
            name = nameFromId(channel, id)
            scoreString += "User " + str(name) + " scored " + str(score) + "\n"
        
        name = nameFromId(channel, scores[0][0])
        await client.send_message(channel, scoreString + "\n" + str(name) + " wins!")
        
        if len(scores) > 2:
            if member.id not in winnerTally:
                winnerTally[member.id] = 0
                
            winnerTally[member.id] += 1
            with open("booruwins.json", "w") as winfile:
                winfile.write(json.dumps(winnerTally, indent=4))

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
        await client.send_message(c, "Timed out!")
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
        await client.send_message(triggerMessage.channel, "A game is already in progress in this channel")
    else:
        tags = []
        try:    
            j = getData("http://e621.net/post/index.json?limit={0}&tags={1}", ["order:random","-cub"])
            
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
                await client.send_message(triggerMessage.channel, "Oopsie woopsie Uwu. Couldn't find a suitable post. Try again?")
                return
                
            tags = target["tags"].casefold().split(" ")
            target = target["file_url"]
            
            filename = downloadImage(target)
            
            with open(filename, "rb") as image:
                await client.send_file(triggerMessage.channel, image, filename=filename)
                
        except JSONDecodeError:
            await client.send_message(triggerMessage.channel, "Oopsie Woopsie. Failed to decode json.")
            return
        except Exception as e:
            await client.send_message(triggerMessage.channel, "Oopsie woopsie Uwu. One of many possible disasters has occured. Try `!booru help`\nException: " + type(e).__name__)
            print(e) #hopefully this does something useful
            return
        
        print(tags)
        
        gameInstances[triggerMessage.channel] = BooruGame(tags)
        await client.send_message(triggerMessage.channel, "Game started. The post has " + str(len(tags)) + " tags to guess.")

@commands.registerEventHandler(name="boorugamestop")
@commands.registerEventHandler(name="boorugamequit")
@commands.registerEventHandler(name="bgq")
async def endBooruGame(triggerMessage):
    await endGame(triggerMessage.channel)

@commands.registerEventHandler(name="bg")
@commands.registerEventHandler(name="booruguess")
async def booruGameGuess(triggerMessage):
    args = triggerMessage.content.split()
    for arg in args[1:]:
        await client.send_message(triggerMessage.channel, gameInstances[triggerMessage.channel].guess(str(arg), triggerMessage.author.id))
        
    if len(gameInstances[triggerMessage.channel].tags) == 0:
        await endBooruGame(triggerMessage)
        
@commands.registerEventHandler(name="booruleaders")
async def booruLeaders(triggerMessage):
    ids = [x.id for x in triggerMessage.server.members]
    leaderboard = { k: winnerTally[k] for k in winnerTally if k in ids}
    
    leaderboardString = ""
    for id in leaderboard:
        name = nameFromId(triggerMessage.channel, id)
        leaderboardString += name + " : " + str(leaderboard[id]) + "\n"
    await client.send_message(triggerMessage.channel, leaderboardString)
