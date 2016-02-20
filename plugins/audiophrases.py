import discord
import asyncio
import permissions
import time

class AudioPhrases:
    legacy = True
    """A plugin for playing various sound clips.
        !setcd : Changes the cooldown between commands. Default is 30 seconds.
        !swoosh : plays the iron chef swoosh
        !destruction : from EVO 2014 Axe vs Silent Wolf"""
        
    def __init__(self, client):
        self.client = client
        self.voice = None
        self.cd = 30
        self.lastTime = time.time() - self.cd # for cooldowns
        
        
        if not discord.opus.is_loaded():
            discord.opus.load_opus('/usr/include/opus')
            
    async def swoosh(self, message):
        if self.voice is None:
            check = lambda c: c.name == "Genearl" and c.type == discord.ChannelType.voice # this is definitely the best way to do this
            # "just copy it from the example"
            self.voice = await self.client.join_voice_channel(discord.utils.find(check, message.server.channels)) # there is no better way to do this

        
        if time.time() > self.lastTime + self.cd:
            if not self.voice.is_connected():
                await self.client.send_message(message.channel, "Error: not connected to voice")
            else:
                self.lastTime = time.time()
                player = self.voice.create_ffmpeg_player("/home/pi/discordbot/sounds/swoosh.mp3")
                player.start()
    
    async def destruction(self, message):
        if self.voice is None:
            check = lambda c: c.name == "Genearl" and c.type == discord.ChannelType.voice # this is definitely the best way to do this
            # "just copy it from the example"
            self.voice = await self.client.join_voice_channel(discord.utils.find(check, message.server.channels)) # there is no better way to do this

        
        if time.time() > self.lastTime + self.cd:
            if not self.voice.is_connected():
                await self.client.send_message(message.channel, "Error: not connected to voice")
            else:
                self.lastTime = time.time()
                player = self.voice.create_ffmpeg_player("/home/pi/discordbot/sounds/destruction.mp3")
                player.start()

    @permissions.needs_moderator
    async def setcd(self, message):
        try:
            self.cd = int(message.content[7:])
            await self.client.send_message(message.channel, "Cooldown is now " + message.content[7:] + " seconds")
        except ValueError:
            await self.client.send_message(message.channel, "Invalid input")

    commandDict = { "!swoosh" : "swoosh", "!destruction" : "destruction", "!setcd" : "setcd" }
Class = AudioPhrases