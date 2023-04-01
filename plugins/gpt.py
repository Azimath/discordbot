import discord
import sys
import traceback
from nomic.gpt4all import GPT4All
import commands

lock = False

m = None

try:
    m = GPT4All()
    m.open()
except:
    print("Unable to load model :(")
    exc_type, exc_value, exc_traceback = sys.exc_info()
    print("Unexpected error:", exc_value)
    traceback.print_tb(exc_traceback)
    m = None

@commands.registerEventHandler(name="chat")
async def chat(triggerMessage):
    global lock
    if m is None:
        await triggerMessage.channel.send("oopsie woopsie. I couldn't load the model and now I'm broken.")
        return

    if lock:
        await triggerMessage.channel.send("One at a time please!")
        return

    try:
        async with triggerMessage.channel.typing():
            prompt = triggerMessage.content.split(" ", 1)
            re = m.prompt(prompt)

            # todo: split up full response across multiple messags
            if len(re) > 1990:
                re = re[:1990] + "...."
            await triggerMessage.channel.send(re)


    except:
        await triggerMessage.channel.send("oopsie woopsie. A terrible disaster has occurred.")
        exc_type, exc_value, exc_traceback = sys.exc_info()
        print("Unexpected error:", exc_value)
        traceback.print_tb(exc_traceback)
    finally:
        lock = False
