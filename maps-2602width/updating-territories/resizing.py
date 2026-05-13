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