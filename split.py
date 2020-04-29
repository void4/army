from PIL import Image

img = Image.open("result.png")

w, h = img.size
bw = bh = 20

for y in range(0, h, bh):
    for x in range(0, w, bw):
        crop = img.crop((x,y,x+bw,y+bw))
        crop.save(f"split/{x}-{y}.png")
