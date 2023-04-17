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
        lock = True
        prompt = triggerMessage.content.split(" ", 1)
        await triggerMessage.channel.typing()
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
        
        
@commands.registerEventHandler(name="meds")
async def meds(triggerMessage):
    global lock
    if lock:
        await triggerMessage.channel.send("One at a time please!")
        return
    m = None
    try:
        lock = True
        await triggerMessage.channel.typing()
        m = GPT4All()
        m.open()
        await triggerMessage.channel.send("Sorry, I don't know what came over me. I took a double dose of normal pills and now I should be better.")
    except:
        print("Unable to load model :(")
        exc_type, exc_value, exc_traceback = sys.exc_info()
        print("Unexpected error:", exc_value)
        traceback.print_tb(exc_traceback)
        await triggerMessage.channel.send("oopsie woopsie. A terrible disaster has occurred.")
    finally:
        lock = False
    
