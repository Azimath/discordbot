import discord
import pkgutil
import sys
import json
import asyncio
import inspect
import time
import threading

import commands
import permissions

import PyREPL
interactive = None
loaded = False

import traceback
import warnings
import sys

def warn_with_traceback(message, category, filename, lineno, file=None, line=None):

    log = file if hasattr(file,'write') else sys.stderr
    traceback.print_stack(file=log)
    log.write(warnings.formatwarning(message, category, filename, lineno, line))

warnings.showwarning = warn_with_traceback
warnings.simplefilter("always")
####Helper stuff
async def loadPlugins():
    
    def load_all_modules_from_dir(dirname): #modded from: http://stackoverflow.com/questions/1057431/loading-all-modules-in-a-folder-in-python/8556471#8556471
        modules = []
        for importer, package_name, _ in pkgutil.iter_modules([dirname]):
            full_package_name = '%s.%s' % (dirname, package_name)
            if full_package_name not in sys.modules:
                mod = importer.find_module(package_name).load_module(package_name)
                modules.append(mod)
                print(mod)
        return modules
        
    plugins = load_all_modules_from_dir("plugins")
    for plugin in plugins:
        plugin.client = client
    
    context = globals()
    context.update(locals())
    #await commands.executeEvent(triggerType="\\set_root_context_on_load", rootContext=context)#TODO: probably dont need to pass locals()
    interactive.setRootContext(context)
    print("%s plugins loaded" % len(plugins))

def timeLoop(asyncLoop):
    while True:
        time.sleep(1)
        asyncLoop.call_soon_threadsafe(asyncio.ensure_future, commands.executeEvent(triggerType="\\timeTick"))
        
if __name__ == "__main__":
    print("Loading config")
    with open('config.json', 'r') as configfile:
        config = json.loads(configfile.read())

    print("Config loaded")
    client = discord.Client()
    permissions.client = client
    interactive = PyREPL.REPL(client)
    def listen():
        @client.event
        async def on_reaction_add(reaction, user):
            await commands.executeEvent(triggerType="\\reactionChanged", triggerMessage=reaction.message, reaction=reaction, user=user)
            
        @client.event
        async def on_reaction_remove(reaction, user):
            await commands.executeEvent(triggerType="\\reactionChanged", triggerMessage=reaction.message, reaction=reaction, user=user)
        
        @client.event
        async def on_message(message):
            await commands.executeEvent(triggerType="\\message", triggerMessage=message)

            if message.author.id != client.user.id:#we ignore our own messages
                await commands.executeEvent(triggerType="\\messageNoBot", triggerMessage=message)
                #print("Got message")
                #commands
                if message.content.startswith("!"):
                    commandName = message.content.split()[0][1:]#TODO:im not sure if this should be done in *this* part of the code, but then how?
                    print("Got command " + commandName)
                    await commands.executeEvent(triggerType="\\command", name=commandName, triggerMessage=message)
                return

        @client.event
        async def on_channel_update(before, after):
            await commands.executeEvent(triggerType="\\channelUpdate", before=before, after=after)

        @client.event
        async def on_ready():
            global loaded

            print("Logged in as")
            print(client.user.name)
            print(client.user.id)
            print("------")
            
            if not loaded:
                await loadPlugins()
            
                loop = asyncio.get_event_loop()
                timeTickThread = threading.Thread(target=timeLoop, kwargs={"asyncLoop":loop})
                timeTickThread.daemon = True
                timeTickThread.start()
                
                loaded = True
        
        @client.event
        async def on_error(event, *args, **kwargs):
            await client.close()
            sys.exit(event)
            
        loaded = False
        client.run(config["DiscordToken"])
    
    print("Logging in")
    listen()#hey, listen,
