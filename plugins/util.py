import asyncio
import discord
import commands


"""This is a plugin for developer utilities to aid in programming and debugging.
   !info: pms information about the channel, server, and author
   !game: sets the name of the game the bot is playing"""

client = None

@commands.registerEventHander(name="info")
async def info(triggerMessage):
    target = triggerMessage.author
    if triggerMessage.mentions.__len__() == 1:
        targetUser = triggerMessage.mentions[0]
        await client.send_message(target, "User name: " + targetUser.name + "\nUser id: " + targetUser.id + "\nUser discriminator: " + targetUser.discriminator)
        # client.send_message(target, "User id: " + targetUser.id)
        # client.send_message(target, "User discriminator: " + targetUser.discriminator)
        await client.delete_message(message)
    else:
        await client.send_message(target, "Channel name: " + triggerMessage.channel.name + "\nChannel id: " + triggerMessage.channel.id + "\nServer  name: " + triggerMessage.server.name + "\nServer id: " + triggerMessage.server.id + "\nAuthor name: " + triggerMessage.author.name + "\nAuthor id: " + triggerMessage.author.id)
        # client.send_message(target, "Channel id: " + triggerMessage.channel.id)
        # client.send_message(target, "Server  name: " + triggerMessage.server.name)
        # client.send_message(target, "Server id: " + triggerMessage.server.id)
        # client.send_message(target, "Author name: " + triggerMessage.author.name)
        # client.send_message(target, "Author id: " + triggerMessage.author.id)

@commands.registerEventHander(name="game")
async def game(triggerMessage):
    await client.change_presence(discord.Game(triggerMessage.content[6:]))

@commands.registerEventHander(name="embeds")
async def embeds(triggerMessage):
    print(str(len(triggerMessage.embeds)) + " embeds in message")
    for embed in triggerMessage.embeds:
        await client.send_message(triggerMessage.author, str(dir(embed)))