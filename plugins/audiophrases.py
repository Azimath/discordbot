import discord
import asyncio
import permissions
import time

class AudioPhrases:
    legacy = True
    """A plugin for playing various sound clips.
        !setcd : Changes the cooldown between commands. Default is 30 seconds.
        !swoosh : plays the iron chef swoosh
        !destruction : from EVO 2014 Axe vs Silent Wolf
        !darksouls : you have died"""
        
    def __init__(self, client):
        self.client = client
        self.voice = None
        self.player = None
        self.cd = 30
        self.lastTime = time.time() - self.cd # for cooldowns
        
        if not discord.opus.is_loaded():
            discord.opus.load_opus('/usr/include/opus')
        #asyncio.ensure_future(join())
        
    async def join(self, message=None):
        if message is None:
            if self.voice is None:
                self.voice = await self.client.join_voice_channel(discord.utils.get(self.client.get_all_channels(), server__name="IAA-Official", name='Genearl', type=discord.ChannelType.voice)) # there is no better way to do this
        else:
            await self.voice.disconnect()
            self.voice = await self.client.join_voice_channel(discord.utils.get(message.server.channels, name=message.content[6:], type=discord.ChannelType.voice)) # there is no better way to do this

    async def swoosh(self, message):
        if self.voice is None:
           self.voice = await self.client.join_voice_channel(discord.utils.get(message.server.channels, name='Genearl', type=discord.ChannelType.voice)) # there is no better way to do this
           
        if time.time() > self.lastTime + self.cd:
            if not self.voice.is_connected():
                await self.client.send_message(message.channel, "Error: not connected to voice")
            else:
                self.lastTime = time.time()
                self.player = self.voice.create_ffmpeg_player("/home/pi/discordbot/sounds/swoosh.mp3")
                self.player.start()
    
    async def destruction(self, message):
        if self.voice is None:
            self.voice = await self.client.join_voice_channel(discord.utils.get(message.server.channels, name='Genearl', type=discord.ChannelType.voice)) # there is no better way to do this
        
        if time.time() > self.lastTime + self.cd:
            if not self.voice.is_connected():
                await self.client.send_message(message.channel, "Error: not connected to voice")
            else:
                self.lastTime = time.time()
                self.player = self.voice.create_ffmpeg_player("/home/pi/discordbot/sounds/destruction.mp3")
                self.player.start()
    
    async def darksouls(self, message):
        if self.voice is None:
            self.voice = await self.client.join_voice_channel(discord.utils.get(message.server.channels, name='Genearl', type=discord.ChannelType.voice)) # there is no better way to do this
        
        if time.time() > self.lastTime + self.cd:
            if not self.voice.is_connected():
                await self.client.send_message(message.channel, "Error: not connected to voice")
            else:
                self.lastTime = time.time()
                self.player = self.voice.create_ffmpeg_player("/home/pi/discordbot/sounds/darksouls.mp3")
                self.player.start()
    
    async def youtube(self, message):
        if self.voice is None:
            self.voice = await self.client.join_voice_channel(discord.utils.get(message.server.channels, name='Genearl', type=discord.ChannelType.voice)) # there is no better way to do this
        
        if time.time() > self.lastTime + self.cd:
            if not self.voice.is_connected():
                await self.client.send_message(message.channel, "Error: not connected to voice")
            else:
                await self.client.send_message(message.channel, "Loading song")
                self.lastTime = time.time()
                if self.player is not None:
                    self.player.stop()
                self.player = await self.voice.create_ytdl_player(message.content.split()[1])
                self.player.start()
                await self.client.change_status(discord.Game(name=self.player.title))
                await self.client.send_message(message.channel, "Now playing " + self.player.title)
                print("User " + message.author.name + ":" + message.author.id + " started video: " + message.content.split()[1])
                await self.client.delete_message(message)
                
    async def stop(self, message):
        if self.voice is not None:
            if self.player.is_playing():
                self.player.stop()
                
    @permissions.needs_moderator
    async def setcd(self, message):
        try:
            self.cd = int(message.content[7:])
            await self.client.send_message(message.channel, "Cooldown is now " + message.content[7:] + " seconds")
        except ValueError:
            await self.client.send_message(message.channel, "Invalid input")

    commandDict = { "!swoosh" : "swoosh", "!destruction" : "destruction", "!setcd" : "setcd", "!darksouls" : "darksouls", "!danksouls" : "darksouls",
                    "!youtube" : "youtube", "!join" : "join", "!stop" : "stop"}
Class = AudioPhrases