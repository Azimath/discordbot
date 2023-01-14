import asyncio
import discord
import commands
import os
import permissions
from datetime import datetime

"""This is a plugin for developer utilities to aid in programming and debugging.
   !info: pms information about the channel, server, and author
   !game: sets the name of the game the bot is playing"""

client = None

@commands.registerEventHandler(name="info")
async def info(triggerMessage):
    target = triggerMessage.author
    if triggerMessage.mentions.__len__() == 1:
        targetUser = triggerMessage.mentions[0]
        unixtime=((int(targetUser.id)>>22)+ 1420070400000)
        acctCreateDate = datetime.utcfromtimestamp(unixtime/1000).strftime('%Y-%m-%d %H:%M:%S')
        await target.send("User name: " + targetUser.name + 
                                  "\nUser id: " + targetUser.id + 
                                  "\nUser discriminator: " + targetUser.discriminator +
                                  "\nAccount Create Date:" + acctCreateDate)
        await client.delete_message(triggerMessage)
    else:
        unixtime=((int(target.id)>>22)+ 1420070400000)
        acctCreateDate = datetime.utcfromtimestamp(unixtime/1000).strftime('%Y-%m-%d %H:%M:%S')
        await target.send("Channel name: " + triggerMessage.channel.name + 
                                  "\nChannel id: " + str(triggerMessage.channel.id) + 
                                  "\nServer  name: " + triggerMessage.guild.name + 
                                  "\nServer id: " + str(triggerMessage.guild.id) + 
                                  "\nAuthor name: " + triggerMessage.author.name + 
                                  "\nAuthor id: " + str(triggerMessage.author.id) +
                                  "\nAccount Create Date:" + str(acctCreateDate) +
                                  "\nChannel Type:" + str(triggerMessage.channel.type) +
                                  "\nChannel NSFW:" + str(triggerMessage.channel.is_nsfw())
                         )

@commands.registerEventHandler(name="game")
async def game(triggerMessage):
    await client.change_presence(game=discord.Game(name=triggerMessage.content[6:]))

@commands.registerEventHandler(name="embeds")
async def embeds(triggerMessage):
    print(str(len(triggerMessage.embeds)) + " embeds in message")
    for embed in triggerMessage.embeds:
        await triggerMessage.author.send(str(dir(embed)))

@permissions.needs_moderator        
@commands.registerEventHandler(name="gitpull")
async def gitpull(triggerMessage):
    os.system("git pull origin master")
    await triggerMessage.channel.send("Git pulled")

@permissions.needs_admin        
@commands.registerEventHandler(name="oauth")
async def oauthlink(triggerMessage):  
   await triggerMessage.author.send("https://discordapp.com/oauth2/authorize?client_id=245814417609064448&scope=bot")
    
