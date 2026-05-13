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

# old = Image.open('./nobody.png', 'r')
# new = old.resize((200, 150))
# new.save('./nobody1.png')

locs = [
    'rusijos-centras',
    'rusijos-siaure',
    'rusijos-pietus',
    'rusijos-vakarai',
    'rusijos-rytai',

    'svedijos-siaure',
    'svedijos-pietus',

    'norvegijos-siaure',
    'norvegijos-pietus',

    'ukrainos-rytai',
    'ukrainos-vakarai',

    'ispanijos-siaure',
    'ispanijos-pietus',

    'prancuzijos-siaure',
    'prancuzijos-pietus'
]

for l in locs:
    for col in ('nobody', 'blue', 'red', 'green', 'yellow'):
        old = Image.open(f'./maps-2602width/{l}/{col}.png', 'r')
        new = old.resize((200, 150))
        new.save(f'./maps/{l}/{col}.png')