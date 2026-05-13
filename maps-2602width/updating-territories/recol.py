from PIL import Image

# 'nobody': (255,255,255),
cols = {
    'red': (237,28,36,255),
    'green': (34,177,76,255),
    'yellow': (255,221,42,255),
    'blue': (32,50,162,255)
}


for i in range(1, 3):
    old = Image.open(f'./{i}.png', 'r')
    new = Image.new('RGBA', (2602, 1952))

    for col_name, col in cols.items():
        
        for x in range(2602):
            for y in range(1952):
                r,g,b,a = old.getpixel((x,y))
                if (r,g,b,a) == (255,255,255,255):
                    new.putpixel((x,y), col)
                else:
                    new.putpixel((x,y), (r,g,b,a))

        new.save(f'./{i} {col_name}.png')
    