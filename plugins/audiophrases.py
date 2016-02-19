import discord
import asyncio
import time

class AudioPhrases:
    legacy = True
    """A plugin for playing various sound clips.
        !swoosh : plays the iron chef swoosh"""
        
    def __init__(self, client):
        self.client = client
        self.voice = None
        self.lastTime = time.time() # for cooldowns
        
        if not discord.opus.is_loaded():
            discord.opus.load_opus('/usr/include/opus')
            
    async def swoosh(self, message):
        if self.voice is None:
            check = lambda c: c.name == "Genearl" and c.type == discord.ChannelType.voice # this is definitely the best way to do this
            # "just copy it from the example"
            self.voice = await self.client.join_voice_channel(discord.utils.find(check, message.server.channels)) # there is no better way to do this

        
        if time.time() > self.lastTime + 30:
            if not self.voice.is_connected():
                await self.client.send_message(message.channel, "Error: not connected to voice")
            else:
                self.lastTime = time.time()
                self.player = self.voice.create_ffmpeg_player("/home/pi/discordbot/sounds/swoosh.mp3")
                self.player.start()
                
    commandDict = { "!swoosh" : "swoosh" }
Class = AudioPhrases