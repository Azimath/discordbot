import discord
import sys
import traceback
#from nomic.gpt4all import GPT4All
import commands

import os
import requests
import subprocess
from tqdm import tqdm
from pathlib import Path
from loguru import logger
import platform
try:
    import torch
except ImportError:
    torch = None
    pass
import asyncio

lock = False

m = None

class GPT4Async():
    def __init__(self, model = 'gpt4all-lora-quantized', force_download=False, decoder_config=None):
        """
        :param model: The model to use. Currently supported are 'gpt4all-lora-quantized' and 'gpt4all-lora-unfiltered-quantized'
        :param force_download: If True, will overwrite the model and executable even if they already exist. Please don't do this!
        :param decoder_config: Default None. A dictionary of key value pairs to be passed to the decoder
        """
        if decoder_config is None:
            decoder_config = {}

        self.bot = None
        self.model = model
        self.decoder_config = decoder_config
        assert model in ['gpt4all-lora-quantized', 'gpt4all-lora-unfiltered-quantized']
        self.executable_path = Path("~/.nomic/gpt4all").expanduser()
        self.model_path = Path(f"~/.nomic/{model}.bin").expanduser()

        if force_download or not self.executable_path.exists():
            logger.info('Downloading executable...')
            self._download_executable()
        if force_download or not (self.model_path.exists() and self.model_path.stat().st_size > 0):                                   
            logger.info('Downloading model...')
            self._download_model()

    def __enter__(self):
        self.open()
        return self
    
    async def open(self):
        if self.bot is not None:
            self.close()
        # This is so dumb, but today is not the day I learn C++.
        creation_args = " ".join([str(self.executable_path), '--model', str(self.model_path)])
        print(creation_args)
        for k, v in self.decoder_config.items():
            creation_args.append(f"--{k}")
            creation_args.append(str(v))
        
        self.bot = await asyncio.create_subprocess_shell(creation_args,
                                    stdin=asyncio.subprocess.PIPE,
                                    stdout=asyncio.subprocess.PIPE)

        # queue up the prompt.
        await self._parse_to_prompt(write_to_stdout=False)

    def __exit__(self, exc_type, exc_val, exc_tb):
        logger.debug("Ending session...")
        self.close()

    def close(self):
        self.bot.kill()
        self.bot = None

    def _download_executable(self):
        if not self.executable_path.exists():
            plat = platform.platform()
            if 'macOS' in plat and 'arm64' in plat:
                upstream = 'https://static.nomic.ai/gpt4all/gpt4all-pywrap-mac-arm64'
            elif 'Linux' in plat:
                upstream = 'https://static.nomic.ai/gpt4all/gpt4all-pywrap-linux-x86_64'
            else:
                raise NotImplementedError(f"Your platform is not supported: {plat}. Current binaries supported are x86 Linux and ARM Macs.")
            response = requests.get(upstream, stream=True)
            if response.status_code == 200:
                os.makedirs(self.executable_path.parent, exist_ok=True)
                total_size = int(response.headers.get('content-length', 0))
                with open(self.executable_path, "wb") as f:
                    for chunk in tqdm(response.iter_content(chunk_size=8192), total=total_size // 8192, unit='KB'):
                        f.write(chunk)
                self.executable_path.chmod(0o755)                
                print(f"File downloaded successfully to {self.executable_path}")

            else:
                print(f"Failed to download the file. Status code: {response.status_code}")

    def _download_model(self):
        # First download the quantized model.

        if not self.model_path.exists():
            response = requests.get(f'https://the-eye.eu/public/AI/models/nomic-ai/gpt4all/{self.model}.bin',
                                    stream=True)
            if response.status_code == 200:
                os.makedirs(self.model_path.parent, exist_ok=True)
                total_size = int(response.headers.get('content-length', 0))
                with open(self.model_path, "wb") as f:
                    for chunk in tqdm(response.iter_content(chunk_size=8192), total=total_size // 8192, unit='KB'):
                        f.write(chunk)
                print(f"File downloaded successfully to {self.model_path}")
            else:
                print(f"Failed to download the file. Status code: {response.status_code}")

    async def _parse_to_prompt(self, write_to_stdout = True):
        bot_says = ['']
        point = b''
        bot = self.bot
        while True:
            point += await bot.stdout.read(1)
            try:
                character = point.decode("utf-8")
                if character == "\f": # We've replaced the delimiter character with this.
                    return "\n".join(bot_says)
                if character == "\n":
                    bot_says.append('')
                    if write_to_stdout:
                        sys.stdout.write('\n')
                        sys.stdout.flush()
                else:
                    bot_says[-1] += character
                    if write_to_stdout:
                        sys.stdout.write(character)
                        sys.stdout.flush()
                point = b''

            except UnicodeDecodeError:
                if len(point) > 4:
                    point = b''

    async def prompt(self, prompt, write_to_stdout = False):
        """
        Write a prompt to the bot and return the response.
        """
        bot = self.bot
        continuous_session = self.bot is not None
        if not continuous_session:
            logger.warning("Running one-off session. For continuous sessions, use a context manager: `with GPT4All() as bot: bot.prompt('a'), etc.`")
            await self.open()
        bot.stdin.write(prompt.encode('utf-8'))
        bot.stdin.write(b"\n")
        await bot.stdin.drain()
        await bot.stdin._
        return_value = await self._parse_to_prompt(write_to_stdout)
        if not continuous_session:
            self.close()
        return return_value        

async def asyncinit():
    global m
    try:
        m = GPT4Async()
        await m.open()
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
        async with triggerMessage.channel.typing():
            prompt = triggerMessage.content.split(" ", 1)[1]
            #prompt = triggerMessage.author.name + ": " + prompt + "\nreply:"
            re = await m.prompt(prompt)

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
