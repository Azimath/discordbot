import discord
import asyncio
import permissions
import time
import re
from youtube_dl import YoutubeDL
import json


def voiceCommandExclusive(func):
    async def command(self, message):
        if self.voice is None:
           self.voice = await self.client.join_voice_channel(discord.utils.get(self.client.get_all_channels(), server__name="IAA-Official", name='Genearl', type=discord.ChannelType.voice)) # there is no better way to do this
        
        if time.time() > self.lastTime + self.cd:
            if not self.voice.is_connected():
                await self.client.send_message(message.channel, "Error: not connected to voice")
            else:
                if self.player is not None:
                    if hasattr(self.player, "is_playing"):
                        if self.player.is_playing():
                            await self.client.send_message(message.channel, "Fuck you")
                            return
                self.lastTime = time.time()
                await func(self,message)
    return command
    
class AudioPhrases:
    """A plugin for playing various sound clips.
        !setcd : Changes the cooldown between commands. Default is 30 seconds.
        !sound, !play <soundname> : plays <soundname> sound clip from our library
        !listsounds : lists the sounds in our library
        !addsound <name> <link> : downloads the sound from a youtube_dl compatible <link> and puts it in our library as <name>
        !youtube <link> : plays the audio from any youtube_dl compatible page
        """
        
    legacy = True    
    def __init__(self, client):
        self.client = client
        self.voice = None
        self.player = None
        self.cd = 30
        self.lastTime = time.time() - self.cd # for cooldowns
        
        if not discord.opus.is_loaded():
            discord.opus.load_opus('/usr/include/opus')
        
        self.audiobank = {}
        with open('audiobank.json', 'r') as database:
            self.audiobank = json.loads(database.read())
        #asyncio.ensure_future(join())
        
    async def join(self, message=None):
        if message is None:
            if self.voice is None:
                self.voice = await self.client.join_voice_channel(discord.utils.get(self.client.get_all_channels(), server__name="IAA-Official", name='Genearl', type=discord.ChannelType.voice)) # there is no better way to do this
        else:
            if self.voice is not None:
                await self.voice.disconnect()
            self.voice = await self.client.join_voice_channel(discord.utils.get(message.server.channels, name=message.content[6:], type=discord.ChannelType.voice)) # there is no better way to do this
    
    @permissions.needs_admin
    async def addSound(self, message):
        name = message.content.split()[1]
        link = message.content.split()[2]
        filename = re.sub('[-.() ]', '', name)
        filepath = "/home/pi/discordbot/sounds/" + filename + ".mp3"
        
        ydlopts = { "outtmpl" : filepath
                    #, 'format': 'bestaudio/best'
                    # ,'postprocessors': [{
                        # 'key': 'FFmpegExtractAudio',
                        # 'preferredcodec': 'mp3',
                        # 'preferredquality': '192',
                    # }]
                    }
        with YoutubeDL(ydlopts) as ydl:
            ydl.download([link])
        
        self.audiobank.update({name : filepath})
        with open('audiobank.json', 'w') as database:
                database.write(json.dumps(self.audiobank, indent=4))
                await self.client.send_message(message.channel, "Added sound " + name)
    
    async def listSounds(self, message):
        result = "Available audio clips: \n"
        for key in self.audiobank:
            result = result + key + "\n"
        await self.client.send_message(message.channel, result)
    
    @voiceCommandExclusive
    async def sound(self, message):
        sound = message.content.split()[-1]
        
        if sound in self.audiobank:
            print("Sound " + sound + " started by user " + message.author.name + ":" + message.author.id)
            self.player = self.voice.create_ffmpeg_player(self.audiobank[sound], use_avconv=True)
            self.player.start()
        else:
            self.client.send_message(message.channel, "Sound not found")
        
    def setgamenone(self):
        asyncio.ensure_future(self.client.change_status(None))
        
    @voiceCommandExclusive
    async def youtube(self, message):
        if message.channel.is_private:
            await self.client.send_message(message.channel, "Go fuck yourself")
            await self.client.send_message(discord.utils.get(self.client.get_all_channels(), server__name="IAA-Official", name='genearl', type=discord.ChannelType.text), message.author.name + " should go fuck themselves")
            return
			
        await self.client.send_message(message.channel, "Loading song at the request of " + message.author.name)
        
        self.player = await self.voice.create_ytdl_player(message.content.split()[1], after=self.setgamenone, use_avconv=True)
        if 'JELLY' in self.player.title.upper() and 'BELLY' in self.player.title.upper():
            await ban(message.author, delete_message_days=0)
            return
        
        self.player.start()
        
        await self.client.change_status(discord.Game(name=self.player.title))
        await self.client.send_message(message.channel, "Now playing " + self.player.title)
        print("User " + message.author.name + ":" + message.author.id + " started video: " + message.content.split()[1])
        await self.client.delete_message(message)
                
    async def stop(self, message):
        if self.voice is not None:
            if self.player.is_playing():
                self.player.stop()
                if hasattr(self.player, "yt"):
                    await self.client.change_status(None)
    
    @permissions.needs_moderator
    async def setcd(self, message):
        try:
            self.cd = int(message.content[7:])
            await self.client.send_message(message.channel, "Cooldown is now " + message.content[7:] + " seconds")
        except ValueError:
            await self.client.send_message(message.channel, "Invalid input")
            
    commandDict = { "!listsounds" : "listSounds", "!sound" : "sound", "!play" : "sound", "!setcd" : "setcd", "!youtube" : "youtube", "!join" : "join", "!stop" : "stop", "!addsound" : "addSound"}
Class = AudioPhrases
