import subprocess
import discord
import asyncio 


class WingDings:
    """A plugin for translating to and from WingDings. All credit goes to Dublo.
    !translate <message> : :snowflake::white_square_button::cancer::black_small_square::small_orange_diamond::black_circle::cancer::large_orange_diamond::scorpius::small_orange_diamond:       :cancer:       :white_circle::scorpius::small_orange_diamond::small_orange_diamond::cancer::capricorn::scorpius:       :large_orange_diamond::white_small_square:       :white_small_square::white_square_button:       :sagittarius::white_square_button::white_small_square::white_circle:       :sparkle::pisces::black_small_square::capricorn::thumbsdown::pisces::black_small_square::capricorn::small_orange_diamond:"""
    legacy = True
    def __init__(self, client):
        self.client = client
    
    async def translate(self, message):
        toSend = message.content[11:]

        p = subprocess.Popen(["java", "-cp", "./plugins", "WingDingsChan", message.content[11:]], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        p.wait()
        output = p.stdout.read().decode('utf-8')
        signal = p.stderr.read().decode('utf-8')
        if signal == "1":
            await self.client.send_message(message.channel, output)

        else:
            splitPoint = output.find("-")
            translated = output[:splitPoint]
            plainText = output[splitPoint+1:]
            await self.client.send_message(message.author, plainText[:-1])
            await self.client.send_message(message.channel, translated)
    
    commandDict = {"!translate" : "translate"}
Class = WingDings
