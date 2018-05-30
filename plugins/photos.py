import commands
import discord
import requests
from io import BytesIO
from PIL import Image, ImageFilter
import random

client = None

@commands.registerEventHander(name="morejpeg")
async def morejpeg(triggerMessage):
    attachments = None
    if any("width" in a for a in triggerMessage.attachments):
        attachments = triggerMessage.attachments
    else:
        logs = client.logs_from(triggerMessage.channel, limit=50)
        async for message in logs:
            if any("width" in a for a in message.attachments):
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
    
    r = requests.get(attachment["url"])
    if r.status_code is not 200:
        await client.send_message(triggerMessage.channel, "Couldn't get image")
        return
        
    translationX = random.choice([-12,-4,0,4,12])
    translationY = random.choice([-12,-4,0,4,12])
    
    img = Image.open(BytesIO(r.content)).convert("RGB") #https://stackoverflow.com/a/13024547
    img = img.transform(img.size, Image.AFFINE, (1,0,translationX,0,1,translationY)).transpose(Image.ROTATE_90)
    img.save("more.jpeg", quality = 1)
    
    img = Image.open("more.jpeg").transpose(Image.ROTATE_270)
    img = img.transform(img.size, Image.AFFINE, (1,0,-translationX,0,1,-translationY))
    img.save("more.jpeg", quality = 1)
    with open("more.jpeg", "rb") as image:
        await client.send_file(triggerMessage.channel, image, filename="more.jpeg", content="Now with more JPEG")
    