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

import pygame
from random import choice
from objects import Button, FlagButton
from common import WIDTH, HEIGHT, lang, default_lang
from pygame_textinput import TextInputVisualizer, TextInputManager
import json
from math import sqrt
import guide

# inicijuoju kintamuosius, kuriems reikia window
def init(window, pref):
    global win, sel_buttons, guide_btn, lang_buttons, motivations, motivational_message, motivational_message_growing, font2_size, pref_lang, power_img
    
    win = window
    pref_lang = pref

    guide.init(win, pref_lang)

    # motyvacine zinute
    motivations = [
        'Rule Europe!', 'Expand your empire.', 'Strategy is everything.'
    ]
    motivational_message = lang[pref_lang][choice(motivations)]
    motivational_message_growing = 1
    font2_size = 30

    # mygtukai
    sel_buttons = [
        Button(win, '2 '+lang[pref_lang]['Players'], 52, 'cyan', 'black', 'center', 300),
        Button(win, '3 '+lang[pref_lang]['Players'], 52, 'cyan', 'black', 'center', 370),
        Button(win, '4 '+lang[pref_lang]['Players'], 52, 'cyan', 'black', 'center', 440)
    ]
    guide_btn = Button(win, lang[pref_lang]['How to play?'], 30, 'white', 'black', 'center', 505)
    lang_buttons = [
        FlagButton(win, 'img/menu/flags/lt.png', 0),
        FlagButton(win, 'img/menu/flags/en.png', 1)
    ]
    power_img = pygame.image.load('img/menu/power.png') # mygtukui
    # nustatau defaultini arba pasirinkta kalba
    for b in lang_buttons:
        if b.lang == pref_lang:
            b.selected = True
            break


# teksto ivestis
font = pygame.font.SysFont('consolas', 26)
nick_txt_input = TextInputVisualizer(manager=TextInputManager(validator=lambda inp: len(inp) <= 20), font_object=font, antialias=False)
ip_txt_input = TextInputVisualizer(manager=TextInputManager(validator=lambda inp: len(inp) <= 17), font_object=font, antialias=False)

input_surface = pygame.Surface((280+10, 26+6)) # po 5 plocio ir 3 aukscio paddingo lieka
input_surface.fill((255,255,255))
red_input_surface = pygame.Surface((280+10+4, 26+6+4))
red_input_surface.fill((200, 20, 20))


pref_lang = default_lang
selected_input = '-'
conn_status = 'offline'
# perskaitau IP, gido nustatyma ir nickname is settings.json
with open('./settings.json', 'r') as f:
    settings = json.load(f)
    my_nickname, ip, showGuideOnLaunch = settings['nickname'], settings['ip'], settings['showGuideOnLaunch']
# irasau sias faile rastas reiksmes i atitinkamus laukelius
nick_txt_input.value, ip_txt_input.value = my_nickname, ip
bad_name = True if len(nick_txt_input.value) < 3 else False
# gidas
if showGuideOnLaunch == 0:
    guide.finished = True # nerodau gido jeigu pradzioje nereikalauja



def alter_menu_play_btns(action):
    global sel_buttons, bad_name

    for b in sel_buttons:
        b.clickable = False if action == 'disable' else True
        if len(nick_txt_input.value) < 3:
            b.clickable = False
            bad_name = True
        else:
            bad_name = False


def show(pressed, events):
    global motivational_message_growing, font2_size, lang_buttons, selected_input, conn_status, bad_name
    
    selected = -1
    if guide.finished: # jeigu nereikia rodyti gido
        # fonas
        menu_image = pygame.image.load('img/menu/theme.jpeg').convert() # realus dydis 900 x 643
        k = HEIGHT/643
        surface = pygame.transform.scale(menu_image, (900*k, 643*k))

        # zaidimo versija
        font = pygame.font.SysFont('consolas', 30)
        text = font.render('v1.1.1', 1, (255, 255, 255))
        surface.blit(text, (10, win.get_height()-text.get_height()-10))


        # zaidimo pavadinimas
        font = pygame.font.SysFont('bahnschrift', 80)
        text = font.render(lang[pref_lang]['CONQUERORS'], 1, (0, 0, 0))
        surface.blit(text, (win.get_width()/2-text.get_width()/2, win.get_height()/9-text.get_height()/2))

        # motyvacine zinute
        font2 = pygame.font.SysFont('bookmanoldstyle', round(font2_size))
        text2 = font2.render(motivational_message, 1, (0, 0, 0))
        surface.blit(text2, (win.get_width()/2-text2.get_width()/2, win.get_height()/9-text.get_height()/2 + text.get_height()))

        # motyvacinio uzraso svyravimai
        if motivational_message_growing == 1:
            if font2_size > 32:
                motivational_message_growing = -1
        else:
            if font2_size < 27:
                motivational_message_growing = 1
        font2_size += .8*motivational_message_growing


        # piesiu pasirinkimo mygtukus
        for b in sel_buttons:
            if b.is_pressed(pressed):
                selected = 'zaisti=' + b.text.split()[0]
                # atnaujinu json faila (nustatymus)
                with open('./settings.json', 'w') as f:
                    json.dump({'ip': ip_txt_input.value, 'nickname': nick_txt_input.value, 'showGuideOnLaunch': 0}, f)
            b.blit(surface)

        # gido mygtukas
        if guide_btn.is_pressed(pressed):
            guide.step = guide.first_step
            guide.finished = False
        guide_btn.blit(surface)




        # tikrinu, kuris inputas pasirinktas, kad rasyciau teksta
        mouse_x, mouse_y = pygame.mouse.get_pos()
        if pressed:
            if sqrt((WIDTH-12-14 - mouse_x)**2 + (HEIGHT-input_surface.get_height()*.5-5 - mouse_y)**2) <= 14: # jeigu paspaudziu mygtuka
                selected_input = '-'
                # siunciu komanda main.py
                if conn_status == 'offline':
                    selected = 'jungtis'
                elif conn_status == 'online':
                    selected = 'atsijungti'
            elif mouse_x in range(WIDTH-input_surface.get_width()-5 , WIDTH-5): # jeigu renkuosi viena is ivesties laukeliu
                # nick
                if mouse_y in range(HEIGHT-input_surface.get_height()*2-10 , HEIGHT-input_surface.get_height()-10):
                    selected_input = 'nick'
                elif mouse_y in range(HEIGHT-input_surface.get_height()-5 , HEIGHT-5):
                    selected_input = 'ip'
                else:
                    selected_input = '-'
            else:
                selected_input = '-'


        # atnaujinu tekstinius inputus
        if selected_input == 'nick':
            nick_txt_input.update(events)
            # mygtukus disablinu jeigu per mazai vardo raidziu
            if len(nick_txt_input.value) < 3:
                bad_name = True
                alter_menu_play_btns('disable')
            elif conn_status == 'online':
                bad_name = False
                alter_menu_play_btns('enable')
        elif selected_input == 'ip':
            ip_txt_input.update(events)
            # atsijungiu nuo serverio, jeigu koreguoju adresa
            if conn_status == 'online':
                selected = 'atsijungti'


        # piesiu raudona surface (indikacija, kad vardas per trumpas)
        if bad_name:
            surface.blit(red_input_surface, ((WIDTH-input_surface.get_width()-5-2, HEIGHT-input_surface.get_height()*2-10-2)))


        # uzrasai tekstiniams inputams
        font = pygame.font.SysFont('consolas', 26, bold=True)
        text = font.render(lang[pref_lang]['Nickname']+': ', 1, (255, 255, 255))
        surface.blit(text, (WIDTH-input_surface.get_width()-5-text.get_width(), HEIGHT-input_surface.get_height()*2-8))

        text = font.render(lang[pref_lang]['Server IP']+': ', 1, (255, 255, 255))
        surface.blit(text, (WIDTH-input_surface.get_width()-5-text.get_width(), HEIGHT-input_surface.get_height()-3))

        # piesiu tekstinius inputus vardui ir IP adresui
        surface.blit(input_surface, (WIDTH-input_surface.get_width()-5, HEIGHT-input_surface.get_height()*2-10))
        surface.blit(nick_txt_input.surface, (WIDTH-input_surface.get_width()+5-5, HEIGHT-input_surface.get_height()*2+3-10))

        surface.blit(input_surface, (WIDTH-input_surface.get_width()-5, HEIGHT-input_surface.get_height()-5))
        surface.blit(ip_txt_input.surface, (WIDTH-input_surface.get_width()+5-5, HEIGHT-input_surface.get_height()+3-5))


        # piesiu jungimosi prie serverio mygtuka
        if conn_status == 'online':
            connection_col = (20, 200, 20)
        elif conn_status == 'offline':
            connection_col = (200, 20, 20)
        elif conn_status == 'hold':
            connection_col = (240, 240, 20)
        pygame.draw.circle(surface, connection_col, (WIDTH-12-14, HEIGHT-input_surface.get_height()*.5-5), 14)
        surface.blit(power_img, (WIDTH-12-14-power_img.get_width()*.5, HEIGHT-input_surface.get_height()*.5-power_img.get_height()*.5-5))


        # piesiu visa meniu surface ant window
        win.blit(surface, (0, 0))




    else:
        # piesiu gida atskirai ant window
        guide.show(win, pressed, pref_lang, ip_txt_input.value, nick_txt_input.value) # paskutiniai du argumentai skirti settings.json atnaujinimui (showGuideOnLaunch parametro pakeitimui kai paspaudziu "Baigti")


    # piesiu kalbos pasirinkimo mygtukus atskirai ant window
    for b in lang_buttons:
        if b.is_pressed(pressed):
            selected = 'kalba=' + b.lang
            # visus kitus atzymiu
            for b1 in lang_buttons:
                if b1.img_path != b.img_path:
                    b1.selected = False
        b.blit(win)

    # grazinu atsakyma
    return selected
