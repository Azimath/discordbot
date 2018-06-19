import discord
import discord.voice_client

import asyncio

import permissions
import commands

import time
import re
from youtube_dl import YoutubeDL
import json
import subprocess

cd = 2
lastTime = time.time() - cd # for cooldowns

def voiceCommandExclusive(func):
    global player
    global voice
    async def command(triggerMessage):
        global voice
        global lastTime
        if voice is None:
            channel = None
            for c in client.get_all_channels():
                if c.type==discord.ChannelType.voice and triggerMessage.author in c.voice_members:
                    channel = c
                    break
            
            if channel is not None:            
                voice = await client.join_voice_channel(channel) # there is no better way to do this
            else:
                return
        #print(str(time.time()) + ">" + str(lastTime) + "+" + str(cd))
        if time.time() > lastTime + cd:
            if not voice.is_connected():
                await client.send_message(triggerMessage.channel, "Error: not connected to voice")
            else:
                if player is not None:
                    if hasattr(player, "is_playing"):
                        if player.is_playing():
                            await client.send_message(triggerMessage.channel, "Fuck you")
                            return
                lastTime = time.time()
                await func(triggerMessage)
    return command
    
"""A plugin for playing various sound clips.
    !setcd : Changes the cooldown between commands. Default is 30 seconds.
    !sound, !play <soundname> : plays <soundname> sound clip from our library
    !listsounds : lists the sounds in our library
    !addsound <name> <link> : downloads the sound from a youtube_dl compatible <link> and puts it in our library as <name>
    !youtube <link> : plays the audio from any youtube_dl compatible page
    """
client = None
voice = None
player = None
message = None

if not discord.opus.is_loaded():
    discord.opus.load_opus('/usr/include/opus')

audiobank = {}
with open('audiobank.json', 'r') as database:
    audiobank = json.loads(database.read())
    #asyncio.ensure_future(join())

@commands.registerEventHander(name="join")    
async def join(triggerMessage):
    global voice
    channel = None
    if len(triggerMessage.content.split()) < 2:
        for c in client.get_all_channels():
            if c.type==discord.ChannelType.voice and triggerMessage.author in c.voice_members:
                channel = c
                print("Got channel " + c.name)
                break
        
        if channel is not None:            
            if voice is not None:
                await voice.disconnect()
            voice = await client.join_voice_channel(channel) # there is no better way to do this
    else:
        channel = discord.utils.get(triggerMessage.server.channels, name=triggerMessage.content[6:], type=discord.ChannelType.voice)
        if channel is not None:
            if voice is not None:
                await voice.disconnect()
            voice = await client.join_voice_channel(channel) # there is no better way to do this
        else:
            await client.send_message(triggerMessage.channel, "That's not a valid voice channel on this server!")

@commands.registerEventHander(name="disconnect") 
async def disconnect(triggerMessage):
    if voice is not None:
        await voice.disconnect()

@commands.registerEventHander(name="addsound") 
@permissions.needs_admin
async def addSound(triggerMessage):
    await client.send_typing(triggerMessage.channel)
    name = triggerMessage.content.split()[1]
    link = triggerMessage.content.split()[2]
    try:
        filename = re.sub('[-.() ]', '', name)
        filepath = "/home/azimath/discordbot/sounds/" + filename + ".mp3"
        
        ydlopts = { "outtmpl" : filepath[:-4]
                    #, 'format': 'bestaudio/best'
                     ,'postprocessors': [{
                         'key': 'FFmpegExtractAudio',
                         'preferredcodec': 'mp3',
                         'preferredquality': '192',
                     }]
                    }
        with YoutubeDL(ydlopts) as ydl:
            ydl.download([link])
        
        audiobank.update({name : filepath})
        with open('audiobank.json', 'w') as database:
                database.write(json.dumps(audiobank, indent=4))
                await client.send_message(triggerMessage.channel, "Added sound " + name)
    except:
        name, link = link, name
        filename = re.sub('[-.() ]', '', name)
        filepath = "/home/azimath/discordbot/sounds/" + filename + ".mp3"
        
        ydlopts = { "outtmpl" : filepath[:-4]
                    #, 'format': 'bestaudio/best'
                     ,'postprocessors': [{
                         'key': 'FFmpegExtractAudio',
                         'preferredcodec': 'mp3',
                         'preferredquality': '192',
                     }]
                    }
        with YoutubeDL(ydlopts) as ydl:
            ydl.download([link])
        
        audiobank.update({name : filepath})
        with open('audiobank.json', 'w') as database:
                database.write(json.dumps(audiobank, indent=4))
                await client.send_message(triggerMessage.channel, "Added sound " + name)

@commands.registerEventHander(name="listsounds") 
async def listSounds(triggerMessage):
    result = "Available audio clips: \n"
    for key in sorted(audiobank.keys()):
        result = result + key + "\n"
    await client.send_message(triggerMessage.channel, result)

@commands.registerEventHander(name="sound")
@commands.registerEventHander(name="play")  
@voiceCommandExclusive
async def sound(triggerMessage):
    global player
    sound = triggerMessage.content.split()[-1]
    
    if sound in audiobank:
        print("Sound " + sound + " started by user " + triggerMessage.author.id)
        player = voice.create_ffmpeg_player(audiobank[sound], use_avconv=True)
        player.start()
    else:
        client.send_message(triggerMessage.channel, "Sound not found")

@commands.registerEventHander(name="radio") 
@voiceCommandExclusive
async def radio(triggerMessage):
    global player
    if len(triggerMessage.content.split()) < 2:
        client.send_message(triggerMessage.channel, "Not enough args for !radio")
        return
    
    freq = triggerMessage.content.split()[1]
    
    if len(triggerMessage.content.split()) > 2:
        modulation = triggerMessage.content.split()[2]
    else:
        modulation = "wbfm"
    
    voice.encoder_options(sample_rate=48000, channels=1)
    rtlfm = subprocess.Popen(["rtl_fm", "-f", freq, "-p","100", "-M", modulation, "-r", "48k", "-l", "0"], stdout=subprocess.PIPE)
    
    player = discord.voice_client.ProcessPlayer(rtlfm, voice, None)
    player.start()
    
    client.send_message(triggerMessage.channel, "Radio Started")

@commands.registerEventHander(name="youtube")
@commands.registerEventHander(name="websound")  
@voiceCommandExclusive
async def youtube(triggerMessage):
    global player
    global message
    if triggerMessage.channel.is_private:
        await client.send_message(triggerMessage.channel, "Go fuck yourself")
        await client.send_message(discord.utils.get(client.get_all_channels(), server__name="IAA-Official", name='genearl', type=discord.ChannelType.text), triggerMessage.author.name + " should go fuck themselves")
        return
        
    await client.send_message(triggerMessage.channel, "Loading song at the request of " + triggerMessage.author.name)
    
    player = await voice.create_ytdl_player(triggerMessage.content.split()[1], use_avconv=True)
    
    player.start()
    
    await client.change_presence(game=discord.Game(name=player.title, url=triggerMessage.content.split()[1], type=2))
    message = await client.send_message(triggerMessage.channel, "Now playing " + player.title)
    
    await client.add_reaction(message, '\u23ef')
    await client.add_reaction(message, '\u23f9')
    
    print("User " + triggerMessage.author.id + " started video: " + triggerMessage.content.split()[1])
    
    try:
        await client.delete_message(triggerMessage)
    except:
        pass

@commands.registerEventHander(triggerType="\\reactionChanged", name="soundControl")
async def soundControl(triggerMessage, reaction, user):
    global message
    if message is None:
        return
        
    if message.id is not None:
        if(type(reaction.emoji) is str) and voice.is_connected() and client.user != user and message.id == triggerMessage.id:
            if(reaction.emoji == '\u25b6') and not player.is_playing() and not player.is_done():
                print("Play Music")
                player.resume()
            elif(reaction.emoji == '\u23ef') and not player.is_done():
                print("Play/pause")
                if player.is_playing():
                    player.pause()
                else:
                    player.resume()
            elif(reaction.emoji == '\u23f8') and player.is_playing():
                print("Pause")
                player.pause()
            elif(reaction.emoji == '\u23f9') and not player.is_done():
                print("Stop")
                player.stop()
                await client.clear_reactions(triggerMessage)
    #print(user.name.encode('unicode_escape').decode('ascii'))
        
@commands.registerEventHander(name="stop") 
async def stop(triggerMessage):
    if voice is not None:
        if player.is_playing():
            player.stop()
            if hasattr(player, "yt"):
                await client.change_presence()
            if hasattr(player, "process"):
                player.process.kill()

@commands.registerEventHander(name="setcd") 
@permissions.needs_moderator
async def setcd(triggerMessage):
    global cd
    try:
        cd = int(triggerMessage.content[7:])
        await client.send_message(triggerMessage.channel, "Cooldown is now " + triggerMessage.content[7:] + " seconds")
    except ValueError:
        await client.send_message(triggerMessage.channel, "Invalid input")
