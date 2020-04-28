from objects import *
from tasks import *

#world.append(Person(128, 128, None, task_platoonleader, (10,50,10)))
#world.append(Person(500, 500, None, task_platoonleader, (210,240,210)))

for i in range(40):
    world.append(Person(128, 128, None, task_worker, (255,255,0)))

from PIL import Image, ImageDraw, ImageFont

fnt = ImageFont.truetype('LiberationMono-Regular.ttf', 13)

iscale = 16
iw = 640//iscale
ih = 480//iscale

img = Image.new("1", (iw,ih))
draw = ImageDraw.Draw(img)

draw.text((0,0), "Hello", font=fnt, fill=1)
draw.text((0,16), "World!", font=fnt, fill=1)
#img.show()

for y in range(ih):
    for x in range(iw):
        if img.getpixel((x,y)) == 1:
            world.append(Wood(randint(0,640), randint(0,480), Task(f"gotome pickmeup {x*iscale} {y*iscale} carryme dropme 'Chair transform end".split())))

for i in range(50):
    #world.append(Box(randint(0,400), randint(0,400)))
    #world.append(Wood(randint(0,400), randint(0,400)))
    #world.append(Tree(randint(0,400), randint(0,400)))
    pass
