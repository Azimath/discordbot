from urllib import request
import permissions
import commands
import asyncio
import json
import sys
import re
import metadata_parser

"""This is a plugin for a few basic admin functions and the almighty censorship cannon.
   Feared by Jerries everywhere.
   !leaveserver: Tells the bot to leave. Only works if you're Azimath.
   !invite: Invites the bot to a new server. Only works if you're Azimath.
   !register: adds you to the permissions system
   !addnode: adds a permissions node to a user if you are a manager
   !setavatar: sets the bot's avatar to the attached image
   !delete @Target <channel> numberofmessages : Deletes numberofmessages sent by Target. If no channel is specified assumes channel it was sent in."""    


client = None

@commands.registerEventHandler(name="leaveserver")
@permissions.needs_owner    
async def leave(triggerMessage):
    await client.leave_server(triggerMessage.channel.server)

@commands.registerEventHandler(name="invite")
@permissions.needs_owner
async def invite(triggerMessage):
    print("Got an invite: " + triggerMessage.content[8:])
    await client.accept_invite(triggerMessage.content[8:])

#@commands.registerEventHandler(triggerType="\\message", name="newsPurge")
async def newsPurge(triggerMessage):
    if triggerMessage.author.id == "102980090970779648" and triggerMessage.channel.id != "102984909320110080":
        await client.delete_message(triggerMessage)

def isAmp(word):
    return any(map(word.__contains__, ampKeywords)) and any(map(word.__contains__, ["http://", "https://"]))

def deAmp(link):
    try:
        page = metadata_parser.MetadataParser(url=link, search_head_only=True)
        amputee = page.get_url_canonical()
        if amputee is not None:
            return amputee
        else:
            return link
    except:
        return link

ampKeywords = ["/amp", "amp/", ".amp", "amp.", "?amp", "amp?", "=amp",
                "amp=", "&amp", "amp&", "%amp", "amp%", "_amp", "amp_"]

#https://github.com/KilledMufasa/AmputatorBot/
@commands.registerEventHandler(triggerType="\\messageNoBot", name="newsPurge")
async def deAmpMessage(triggerMessage):
    words = triggerMessage.content.split()
    if words is None:
        words = triggerMessage.content
    if any(map(isAmp, words)):

        new_words = [deAmp(word) if isAmp(word) else word for word in words]
        if new_words != words:
            # only delete the message if any of the links were actually amp links
            message = [triggerMessage.author.name + ":"]
            message.extend(new_words)

            await triggerMessage.channel.send(" ".join(message))
            await triggerMessage.delete()

@commands.registerEventHandler(triggerType="\\messageNoBot", name="fixTwit")
@commands.messageHandlerFilter("://twitter", filterType="cqc")
async def fixTwit(triggerMessage):
    #should we limit this to only certain servers?
    message = triggerMessage.content
    message = message.replace("://twitter", "://vxtwitter")
    message = triggerMessage.author.name + ": " + message

    await triggerMessage.channel.send(message)
    await triggerMessage.delete()
    

@commands.registerEventHandler(name="register")
async def registerNewUser(triggerMessage):  
    if triggerMessage.mentions.__len__() == 0:
        id = triggerMessage.author.id
        name = triggerMessage.author.name
        if permissions.register(permissions.User(id, name, ["base"]), triggerMessage):
            await triggerMessage.channel.send( "User id " + triggerMessage.author.id + " has been registered")
        else:
            await triggerMessage.channel.send( "User id " + triggerMessage.author.id + " is already registered")
    else:
        id = triggerMessage.mentions[0].id
        name = triggerMessage.mentions[0].name
        if permissions.register(permissions.User(id, name, ["base"]), triggerMessage):
            await triggerMessage.channel.send( "User id " + id + " has been registered")
        else:
            await triggerMessage.channel.send( "User id " + id + " is already registered")

@commands.registerEventHandler(name="addnode")
@permissions.needs_permissionsManager
async def addNode(triggerMessage):
    if triggerMessage.mentions.__len__() == 0:
        await triggerMessage.channel.send( "Specify one or more users")
    else:
        permNode = triggerMessage.content.split()[-1]
        if permNode == "manager":
            return
            
        for user in triggerMessage.mentions:
            permissions.addPermission(user, permNode)
        await triggerMessage.channel.send( "Permissions added")      

@commands.registerEventHandler(name="setavatar")
@permissions.needs_moderator
async def setAvatar(triggerMessage):
    if triggerMessage.attachments is not None:
        #print("Got " + str(len(triggerMessage.attachments)) + " attachments, setting image")
        for x in triggerMessage.attachments:
            #print("Checking attachment " + x["url"])
            if x["url"] is not None:
                #print("Downloading attachment")
                req = request.Request(x["url"], headers={
                    "User-Agent": "A discord bot"
                  })
                image = request.urlopen(req).read()
                await client.edit_profile(avatar=image)
                await triggerMessage.channel.send( "Avatar set!")
                return
        await triggerMessage.channel.send( "Couldnt get an image")          

class RestartException(Exception):
    pass

@commands.registerEventHandler(name="restart")
@commands.registerEventHandler(name="reeeeestart")
@permissions.needs_moderator
async def restart(triggerMessage):
    await triggerMessage.channel.send("Ok I guess I'll just die")
    raise RestartException

@commands.registerEventHandler(name="nameall")
@permissions.needs_moderator 
async def changeAllNames(triggerMessage):
    names = {}
    for member in triggerMessage.guild.members:
        names.update({ member.id : member.nick})
        try:
            await member.edit(nick=triggerMessage.content.split()[1],reason="Scoobert Doobert")
        except:
            print(sys.exc_info()[0])
            print("Couldn't scoobert " + member.name.encode('ascii', 'ignore').decode('ascii'))
    with open('names.json', 'w') as database:
            database.write(json.dumps(names, indent=4))

@commands.registerEventHandler(name="revertnames")
@permissions.needs_moderator 
async def unchangeAllNames(triggerMessage):
    with open('names.json', 'r') as database:
        names = json.loads(database.read())
        for member in triggerMessage.guild.members:
            try:
                await member.edit(nick=names[str(member.id)], reason="Scoobert Doobert")
            except:
                print(sys.exc_info()[0])
                print("Couldn't unscoobert " + str(member.id) + ":" + member.name.encode('ascii', 'ignore').decode('ascii'))
            
@commands.registerEventHandler(name="delete")
@permissions.needs_moderator
async def delete(triggerMessage):
    #find out if the sender has delete permissions
    victim = None
    channel = None
    command = triggerMessage.content.split() #probably the best way to do this, right?
    if len(command) > 1: #parse the fuck out of it
        if len(triggerMessage.mentions) == 0:
            victim = None
        elif len(triggerMessage.mentions) > 1:
            channel = None
        else:
            victim = triggerMessage.mentions[0]
        
        if len(command) > 2:
            for n in range(1, command.__len__()):
                try:
                    number = int(command[n])
                    break
                except:
                    number = 1
        
        if len(triggerMessage.channel_mentions) == 0:
            channel = triggerMessage.channel
        elif len(triggerMessage.channel_mentions) > 1:
            channel = None
        else:
            channel = triggerMessage.channel_mentions[0]
    #actually do the stuff
    
        if channel is not None:
            #print("authorized, channel is " + channel.name + " target is " + victim.name)
            print("deleting " + str(number) + " messages")
            deleted = 0
            async for msg in triggerMessage.channel.history(limit=100*number):
                if (msg.author == victim or victim is None) and deleted < number:
                    await client.delete_message(msg)
                    deleted = deleted + 1
                    #print("deleted " + str(deleted))
                if deleted >= number and victim is not None:
                    await channel.send( triggerMessage.author.name + " removed " + str(deleted) + " messages belonging to " + victim.name)
                    break
            #print("messages remaining: " + str(number-deleted))
        else:
            print("Invalid victim or channel")
            print("has victim: " + victim == None)
            print("has channel: " + channel == None)
              
