import asyncio
import permissions
import commands
from PIL import ImageFont, Image, ImageDraw

client = None

def count_pixels(image, color):
    count = 0
    for x in range(image.width):
        for y in range(image.height):
            if image.getpixel((x,y)) == color:
                count += 1

    return count

l = lambda x : (x[2] - x[0], x[3] - x[1])
# world's greatest text fitting algorithm patent pending
def solvefont(text, font_name, rect):
    words = text.split(" ")

    image = Image.new("RGB", rect, (255,255,255))
    d = ImageDraw.Draw(image)

    best_string = ""
    best_size = 0
    best_score = rect[0]*rect[1]

    #guess a starting size
    size = rect[1] // 5
    smaller_size = 1
    bigger_size = 1000

    while (True):
        this_text = ""
        font = ImageFont.truetype(font_name, size=size)
        # start filling the line with words
        flag = False

        for word in words:
            if this_text == "":
                next_text = word
            else:
                next_text = this_text + " " + word
            box = l(d.multiline_textbbox((0, 0), next_text, font))
            if box[0] < rect[0]:
                this_text = next_text
                # go on to the next word
                continue
            else:
                # didn't fit
                next_text = this_text + "\n" + word
                # does it fit now?
                box = l(d.multiline_textbbox((0, 0), next_text, font))
                if box[0] < rect[0]:
                    # but is it too tall now?
                    if box[1] < rect[1]:
                        # not too tall
                        this_text = next_text
                    else:
                        # too tall, go smaller
                        # binary search for size
                        temp = size
                        size = (smaller_size + size) // 2
                        bigger_size = temp
                        if size == temp:
                            raise Exception("Sizes converged!")
                        flag = True
                        break

                else:
                    # the next word is too big to fit even on a line of its own
                    # we need to go smaller

                    temp = size
                    size = (smaller_size + size) // 2
                    bigger_size = temp
                    if size == temp:
                        raise Exception("Sizes converged!")
                    flag = True
                    break

        if flag:
            # abandoned because too big
            # don't score the attempt
            pass
        else:
            # all tokens fit, lets try it for real
            d.multiline_text((0,0), this_text, (0,0,0))
            # now count coverage
            score = count_pixels(image, (255,255,255))
            if score < best_score:
                best_size = size
                best_string = this_text
                best_score = score
            else:
                # oh no we made it worse somehow
                # but bigger is ALWAYS better, right?
                if size > best_size:
                    best_size = size
                    best_string = this_text
                    best_score = score

            # okay now figure out the next size
            # we want to keep going bigger until it stops fitting

            temp = size
            size = (bigger_size+size)//2
            smaller_size = temp
            if temp == size:
                return best_string, best_size, best_score

        if size == 95:
            pass
        print(smaller_size, '<', size, '<', bigger_size)

    return best_string, best_size, best_score
  
def make_tiw(text):
  image = Image.open("./resources/tiw.jpg")
  name = "comic.ttf"
  offset = (228, 100)
  box = (117, 174)
  wrapped_text, size, score = solvefont(text, name, box)
  draw = ImageDraw.Draw(image)
  font = ImageFont.truetype(name, size)

  draw.text(offset, wrapped_text, font=font, fill=(0,0,0))
  return image

@commands.registerEventHandler(name="tiw")
async def tiw(triggerMessage):
  text = triggerMessage.content.split(" ", 1)[1]
  image = make_tiw(text)
  output = io.BytesIO()
  image.save(output, format="PNG")
  output.seek(0)
  data = io.BufferedReader(output)
  await triggerMessage.channel.send(file=discord.File(data, filename="tiw.png"))
  
