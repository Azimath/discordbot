import discord
import discord.voice_client

import asyncio

import permissions
import commands

import time
import re
from youtube_dl import YoutubeDL, DownloadError
import json
import subprocess
import functools

cd = 2
lastTime = time.time() - cd # for cooldowns

def voiceCommandExclusive(func):
    global voice
    async def command(triggerMessage):
        global voice
        global lastTime
        if voice is None:
            channel = None
            for c in client.get_all_channels():
                if c.type==discord.ChannelType.voice and triggerMessage.author in c.members:
                    channel = c
                    break
            
            if channel is not None:            
                voice = await channel.connect() # there is no better way to do this
            else:
                return
        #print(str(time.time()) + ">" + str(lastTime) + "+" + str(cd))
        if time.time() > lastTime + cd:
            if not voice.is_connected():
                await triggerMessage.channel.send( "Error: not connected to voice")
            else:
                if voice is not None:
                    if hasattr(voice, "is_playing"):
                        if voice.is_playing():
                            await triggerMessage.channel.send( "Fuck you")
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
message = None

if not discord.opus.is_loaded():
    discord.opus.load_opus('/usr/lib/x86_64-linux-gnu/libopus.so')

audiobank = {}
with open('audiobank.json', 'r') as database:
    audiobank = json.loads(database.read())
    #asyncio.ensure_future(join())

@commands.registerEventHandler(name="join")    
async def join(triggerMessage):
    global voice
    channel = None
    if len(triggerMessage.content.split()) < 2:
        for c in client.get_all_channels():
            if c.type==discord.ChannelType.voice and triggerMessage.author in c.members:
                channel = c
                print("Got channel " + c.name)
                break
        
        if channel is not None:            
            if voice is not None:
                await voice.disconnect()
            voice = await channel.connect() # there is no better way to do this
    else:
        channel = discord.utils.get(triggerMessage.guild.voice_channels, name=triggerMessage.content[6:])
        if channel is not None:
            if voice is not None:
                await voice.disconnect()
            voice = await channel.connect() # there is no better way to do this
        else:
            await triggerMessage.channel.send( "That's not a valid voice channel on this server!")

@commands.registerEventHandler(name="disconnect") 
async def disconnect(triggerMessage):
    if voice is not None:
        await voice.disconnect()

@commands.registerEventHandler(name="addsound") 
@permissions.needs_admin
async def addSound(triggerMessage):
    async with triggerMessage.channel.typing():
        name = triggerMessage.content.split()[1]
        link = triggerMessage.content.split()[2]
        try:
            filename = re.sub('[-.() ]', '', name)
            filepath = "/home/seve/discordbot/sounds/" + filename + ".mp3"
            
            ydlopts = { "outtmpl" : filepath[:-4] + ".%(ext)s",
                        'format': 'webm[abr>0]/bestaudio/best',
                        'postprocessors': [{
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
                    await triggerMessage.channel.send( "Added sound " + name)
        except:
            name, link = link, name
            filename = re.sub('[-.() ]', '', name)
            filepath = "/home/seve/discordbot/sounds/" + filename + ".mp3"
            
            ydlopts = { "outtmpl" : filepath[:-4],
                        'format': 'webm[abr>0]/bestaudio/best',
                        'postprocessors': [{
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
                    await triggerMessage.channel.send( "Added sound " + name)

@commands.registerEventHandler(name="listsounds") 
async def listSounds(triggerMessage):
    result = "Available audio clips: \n"
    for key in sorted(audiobank.keys()):
        result = result + key + "\t"
    await triggerMessage.channel.send( result)

@commands.registerEventHandler(name="sound")
@commands.registerEventHandler(name="play")  
@voiceCommandExclusive
async def sound(triggerMessage):
    sound = triggerMessage.content.split()[-1]
    
    if sound in audiobank:
        print("Sound " + sound + " started by user " + str(triggerMessage.author.id))
        voice.play(discord.FFmpegPCMAudio(audiobank[sound]))
    else:
        await triggerMessage.channel.send( "Sound not found")

@commands.registerEventHandler(name="radio") 
@voiceCommandExclusive
async def radio(triggerMessage):
    if len(triggerMessage.content.split()) < 2:
        triggerMessage.channel.send( "Not enough args for !radio")
        return
    
    freq = triggerMessage.content.split()[1]
    
    if len(triggerMessage.content.split()) > 2:
        modulation = triggerMessage.content.split()[2]
    else:
        modulation = "wbfm"
    
    voice.encoder_options(sample_rate=48000, channels=1)
    rtlfm = subprocess.Popen(["rtl_fm", "-f", freq, "-p","100", "-M", modulation, "-r", "48k", "-l", "0"], stdout=subprocess.PIPE)
    
    discord.voice_client.ProcessPlayer(rtlfm, voice, None)
    
    triggerMessage.channel.send( "Radio Started")

@commands.registerEventHandler(name="youtube")
@commands.registerEventHandler(name="websound")  
@voiceCommandExclusive
async def youtube(triggerMessage):
    global message
    if triggerMessage.channel.type != discord.ChannelType.text:
        await triggerMessage.channel.send( "Go fuck yourself")
        await discord.utils.get(client.get_all_channels(), server__name="IAA-Official", name='genearl', type=discord.ChannelType.text).send(triggerMessage.author.name + " should go fuck themselves")
        return
        
    await triggerMessage.channel.send( "Loading song at the request of " + triggerMessage.author.name)
    
    url=triggerMessage.content.split()[1]

    ydlopts = { 'format': 'webm[abr>0]/bestaudio/best',
                'verbose': True,
                'no_color': True
                }
    ydl = YoutubeDL(ydlopts)
    try:
        info = ydl.extract_info(url, download=False)
        if "entries" in info:
            info = info['entries'][0]

        source = discord.FFmpegPCMAudio(info['url'], before_options="-probesize 42M")
        voice.play(source)
    except DownloadError as err:
        await triggerMessage.channel.send(err)
        return

    
    await client.change_presence(activity=discord.Game(name=info['title'], url=url, type=2))
    message = await triggerMessage.channel.send( "Now playing " + info['title'])
    
    await message.add_reaction('\u23ef')
    await message.add_reaction('\u23f9')
    
    print("User " + str(triggerMessage.author.id) + " started video: " + url)
    
    try:
        await triggerMessage.delete()
    except discord.Forbidden:
        pass

@commands.registerEventHandler(triggerType="\\reactionChanged", name="soundControl")
async def soundControl(triggerMessage, reaction, user):
    global message
    if message is None:
        return
        
    if message.id is not None:
        print(voice.is_connected())
        if(type(reaction.emoji) is str) and voice.is_connected() and client.user != user and message.id == triggerMessage.id:
            if(reaction.emoji == '\u25b6') and voice.is_paused():
                print("Play Music")
                voice.resume()
            elif(reaction.emoji == '\u23ef') and (voice.is_playing() or voice.is_paused()):
                print("Play/pause")
                if not voice.is_paused():
                    voice.pause()
                else:
                    voice.resume()
            elif(reaction.emoji == '\u23f8') and voice.is_playing():
                print("Pause")
                voice.pause()
            elif(reaction.emoji == '\u23f9') and (voice.is_playing() or voice.is_paused()):
                print("Stop")
                voice.stop()
                await triggerMessage.clear_reactions()
    #print(user.name.encode('unicode_escape').decode('ascii'))
        
@commands.registerEventHandler(name="stop") 
async def stop(triggerMessage):
    if voice is not None:
        if voice.is_playing():
            voice.stop()
            await client.change_presence()

@commands.registerEventHandler(name="setcd") 
@permissions.needs_moderator
async def setcd(triggerMessage):
    global cd
    try:
        cd = int(triggerMessage.content[7:])
        await triggerMessage.channel.send( "Cooldown is now " + triggerMessage.content[7:] + " seconds")
    except ValueError:
        await triggerMessage.channel.send( "Invalid input")
