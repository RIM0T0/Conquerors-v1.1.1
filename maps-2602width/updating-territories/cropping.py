from PIL import Image

for i in range(1, 3):
    old = Image.open(f'./{i}-brown.png', 'r')
    new = Image.new('RGBA', (2602, 1952))

    for x in range(2602):
        for y in range(1952):
            r,g,b,a = old.getpixel((x,y))
            if (r,g,b,a) in [(0,0,0,255), (255,255,255,255)]:
                new.putpixel((x,y), (r,g,b,a))

    new.save(f'./{i}.png')