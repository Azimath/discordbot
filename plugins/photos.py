import commands
import permissions
import discord
import requests
from io import BytesIO
from PIL import Image, ImageFilter
import random
import time
import bs4

client = None
timeout = dict()
COOLDOWN = 30

@permissions.needs_moderator
@commands.registerEventHandler(name="jpegcd")
async def jpegcd(triggerMessage):
    global COOLDOWN
    try:
        COOLDOWN = int(triggerMessage.content.split()[1])
        await client.send_message(triggerMessage.channel, "JPEG Cooldown is now " + triggerMessage.content.split()[1])
    except:
        print("Failed to parse jpegcd time")
        raise
        
    
@commands.registerEventHandler(name="morejpeg")
async def morejpeg(triggerMessage):
    global COOLDOWN
    attachments = None
    if any("width" in a for a in triggerMessage.attachments) and triggerMessage.author.id != "245814417609064448":
        attachments = triggerMessage.attachments
    else:
        logs = client.logs_from(triggerMessage.channel, limit=50)
        async for message in logs:
            if any("width" in a for a in message.attachments):
                print(message.author.id)
                if message.author.id == "245814417609064448":
                    await client.send_message(triggerMessage.channel, "Chaining disallowed")
                    break
                attachments = message.attachments 
                break
    
    if attachments is None:
        await client.send_message(triggerMessage.channel, "Couldn't find anything recent to jpegify")
        return
    
    attachment = None
    for a in attachments:
        if "width" in a and "url" in a:
            attachment = a
            break
    
    if attachment is None:
        await client.send_message(triggerMessage.channel, "Something made a fucky wucky")
        return
    await client.send_typing(triggerMessage.channel)
    
    r = requests.get(attachment["url"])
    if r.status_code is not 200:
        await client.send_message(triggerMessage.channel, "Couldn't get image")
        return
    if not (triggerMessage.channel.type == discord.ChannelType.private or (triggerMessage.channel.name is not None and "deepfry" in triggerMessage.channel.name)):
        nowtime = int(time.time())
        user = triggerMessage.author.id
        if user in timeout and (timeout[user] + COOLDOWN > nowtime):
            if triggerMessage.author.nick is not None:
                await client.send_message(triggerMessage.channel, triggerMessage.author.nick + " is on Cooldown")
            else:
                await client.send_message(triggerMessage.channel, triggerMessage.author.name + " is on Cooldown")
            return

        timeout[user] = nowtime
    
    iters = 1
    try:
        iters = int(triggerMessage.content.split()[1])
    except:
        print ("Couldn't get jpeg iterations, defaulting to 1")
    iters = min(iters, 10)    
    img = Image.open(BytesIO(r.content)).convert("RGB") #https://stackoverflow.com/a/13024547
    img.save("more.jpeg", quality = 100)
    for i in range(iters):
        translationX = random.choice([-12,-4,0,4,12])
        translationY = random.choice([-12,-4,0,4,12])

        img = Image.open("more.jpeg").convert("RGB") 
        img = img.transform(img.size, Image.AFFINE, (1,0,translationX,0,1,translationY)).transpose(Image.ROTATE_90)
        img.save("more.jpeg", quality = 1)

        img = Image.open("more.jpeg").transpose(Image.ROTATE_270)
        img = img.transform(img.size, Image.AFFINE, (1,0,-translationX,0,1,-translationY))
        img.save("more.jpeg", quality = 1)

    with open("more.jpeg", "rb") as image:
        await client.send_file(triggerMessage.channel, image, filename="more.jpeg", content="Now with more JPEG")
    
async def hugeify(url):
    session = requests.Session()
    response = session.get("https://waifu2x.booru.pics/Home/fromlink?url=" + url + "&denoise=1&scale=2&submit=")
    return "https://waifu2x.booru.pics" + bs4.BeautifulSoup(response.text, "lxml").find_all(class_="btn")[0]["href"]
