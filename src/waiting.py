import pygame
from math import sin, cos, pi, floor
from common import HEIGHT, WIDTH, lang, FPS, default_lang, default_bot_strength
from objects import Button, Text
from time import sleep
from threading import Thread


pref_lang = default_lang
def init(window, pref):
    global win, buttons, text_boxes, pref_lang, bot_strength

    pref_lang = pref
    win = window
    bot_strength = default_bot_strength

    buttons = {
        'fill with bots': Button(win, lang[pref_lang]['Fill with bots'], 30, 'green', 'black', 'center', 650),
        'cancel': Button(win, lang[pref_lang]['Cancel'], 30, 'red', 'black', 'center', 700),
        '-': Button(win, ' - ', 35, 'red', 'black', WIDTH/2-65, 600),
        '+': Button(win, ' + ', 35, 'green', 'black', WIDTH/2+65, 600)
    }
    text_boxes = {
        'bot strength label': Text(lang[pref_lang]['Bot strength']+':', 22, 'white', 'black', WIDTH/2, 571),
        'bot strength': Text(f'{' '*(3-len(str(round(bot_strength*100))))}{round(bot_strength*100)}%', 35, 'white', 'black', WIDTH/2, 600),
        'joined': Text('?/? '+lang[pref_lang]['joined'], 20, 'white', 'black', WIDTH/2, 520)
    }


def temporarily_disable_bot_fill():
    global bot_fill_just_pressed, buttons
    bot_fill_just_pressed = True
    buttons['cancel'].clickable = False
    sleep(5)
    bot_fill_just_pressed = False
    buttons['cancel'].clickable = True


angle = 0
dot_count = 0.5
joined = 0
needed_players = '?'
bot_fill_enabled = True
bot_fill_just_pressed = False
bot_strength_step = .05
def show(pressed):
    global angle, buttons, text_boxes, dot_count, bot_fill_enabled, bot_strength

    # fonas
    image = pygame.image.load('img/waiting/loading.jpg') # realus dydis 500 x 333
    k = HEIGHT/333
    main_surface = pygame.transform.scale(image, (500*k, 333*k))



    # besisukantis tankas
    image = pygame.image.load('img/waiting/tank.png')
    surface = pygame.transform.rotate(image, 360-angle-90)

    center_x = win.get_width()/2
    center_y = win.get_height()/2
    y_diff = sin(angle*pi/180) * 80
    x_diff = cos(angle*pi/180) * 80

    main_surface.blit(surface, (center_x+x_diff-surface.get_width()/2, center_y+y_diff-surface.get_height()/2))


    # zeme
    image = pygame.image.load('img/waiting/earth.png')
    surface = pygame.transform.rotate(image, angle/6)
    main_surface.blit(surface, (center_x-surface.get_width()/2, center_y-surface.get_height()/2))


    # keiciu padeti
    angle -= 3


    # piesiu mygtukus
    selected = ''
    if (bot_fill_enabled and not bot_fill_just_pressed):
        buttons['fill with bots'].clickable = True
        buttons['+'].clickable = True
        buttons['-'].clickable = True
        text_boxes['bot strength'].greyed_out = False
        text_boxes['bot strength label'].greyed_out = False
    else:
        buttons['fill with bots'].clickable = False
        buttons['+'].clickable = False
        buttons['-'].clickable = False
        text_boxes['bot strength'].greyed_out = True
        text_boxes['bot strength label'].greyed_out = True
    
    for name, b in buttons.items():
        b.blit(main_surface)
        if b.is_pressed(pressed):
            selected = name
            if name == 'fill with bots':
                Thread(target=temporarily_disable_bot_fill, args=(), daemon=False).start()
                selected += f';{round(bot_strength, 2)}'
            elif name in ('-', '+'):
                if name == '-' and round(bot_strength-bot_strength_step, 2) > 0:
                    bot_strength -= bot_strength_step
                elif name == '+' and round(bot_strength+bot_strength_step, 2) <= 1:
                    bot_strength += bot_strength_step
                text_boxes['bot strength'].update_text(f'{' '*(3-len(str(round(bot_strength*100))))}{round(bot_strength*100)}%')

    # piesiu teksto objektus
    for t in text_boxes.values():
        t.blit(main_surface)

    # keiciu kiek yra zaideju prisijungusiu
    text_boxes['joined'].update_text(f'{joined}/{needed_players} '+lang[pref_lang]['joined'])


    # uzrasas palaukti kol prisijungs zaidejai
    font = pygame.font.SysFont('consolas', 50)
    text = font.render(' '+lang[pref_lang]['Waiting for players']+floor(dot_count)*'.'+(4-floor(dot_count))*' ', 1, (0, 0, 0), (153, 153, 153))
    main_surface.blit(text, (win.get_width()/2-text.get_width()/2, win.get_height()/3.5-text.get_height()/2))

    # keiciu taskeliu prie uzraso skaiciu
    dot_count += 5/FPS
    if dot_count >= 3.95:
        dot_count = 0.5


    # piesiu main_surface ant pagrindinio lango
    win.blit(main_surface, (0, 0))


    # grazinu atsakyma
    return selected
