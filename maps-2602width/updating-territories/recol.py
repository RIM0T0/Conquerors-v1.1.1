'''
Copyright (C) 2026 Rimantas Rimkevičius

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program. If not, see https://www.gnu.org/licenses/
'''

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
    