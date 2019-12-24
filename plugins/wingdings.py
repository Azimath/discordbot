import subprocess
import discord
import asyncio 
import commands


"""A plugin for translating to and from WingDings. All credit goes to Dublo.
!translate <message> : :snowflake::white_square_button::cancer::black_small_square::small_orange_diamond::black_circle::cancer::large_orange_diamond::scorpius::small_orange_diamond:       :cancer:       :white_circle::scorpius::small_orange_diamond::small_orange_diamond::cancer::capricorn::scorpius:       :large_orange_diamond::white_small_square:       :white_small_square::white_square_button:       :sagittarius::white_square_button::white_small_square::white_circle:       :sparkle::pisces::black_small_square::capricorn::thumbsdown::pisces::black_small_square::capricorn::small_orange_diamond:"""

client = None

@commands.registerEventHandler(name="translate")
async def translate(triggerMessage):
    toSend = triggerMessage.content[11:]

    p = subprocess.Popen(["java", "-cp", "./plugins", "WingDingsChan", triggerMessage.content[11:]], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    p.wait()
    output = p.stdout.read().decode('utf-8')
    signal = p.stderr.read().decode('utf-8')
    if signal == "1":
        await triggerMessage.channel.send( output)

    else:
        splitPoint = output.find("-")
        translated = output[:splitPoint]
        plainText = output[splitPoint+1:]
        await triggerMessage.author.send(plainText[:-1])
        await triggerMessage.channel.send( translated)