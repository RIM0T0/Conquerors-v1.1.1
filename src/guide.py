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
from objects import Button
from common import lang, WIDTH, HEIGHT
import json

step = 1
first_step, last_step = step, 6
finished = False
page_num_font = pygame.font.SysFont('consolas', 25)

def init(window, pref):
    global win, pref_lang, step, done_btn, fwd_btn, end_btn, back_btn, start_btn, surface, first_step, last_step, finished
    
    win = window
    pref_lang = pref
    
    fwd_btn = Button(win, '> ', 40, 'cyan', 'black', 'right', 670)
    end_btn = Button(win, '>>', 40, 'cyan', 'black', 'right', 710)
    back_btn = Button(win, ' <', 40, 'cyan', 'black', 'left', 670)
    start_btn = Button(win, '<<', 40, 'cyan', 'black', 'left', 710)
    done_btn = Button(win, lang[pref_lang]['Done'], 42, 'cyan', 'black', 'center', 690)

    surface = pygame.Surface((WIDTH, HEIGHT))

def show(win, pressed, pref_lang, ip_txt_input_value, nick_txt_input_value):
    global finished, step

    slide = pygame.image.load(f'img/guide/{pref_lang}/{step}.png')
    surface.blit(slide, (0, 0))

    # piesiu mygtukus
    if first_step+1 <= step <= last_step-1:
        fwd_btn.blit(surface)
        end_btn.blit(surface)
        back_btn.blit(surface)
        start_btn.blit(surface)
    elif step == first_step:
        fwd_btn.blit(surface)
        end_btn.blit(surface)
    elif step == last_step:
        back_btn.blit(surface)
        start_btn.blit(surface)
        done_btn.blit(surface)

    # mygtuku veiksmai
    if fwd_btn.is_pressed(pressed) and first_step <= step <= last_step-1:
        step += 1
    elif end_btn.is_pressed(pressed) and first_step <= step <= last_step-1:
        step = last_step
    elif back_btn.is_pressed(pressed) and first_step+1 <= step <= last_step:
        step -= 1
    elif start_btn.is_pressed(pressed) and first_step+1 <= step <= last_step:
        step = first_step
    elif done_btn.is_pressed(pressed) and step == last_step:
        finished = True
        # resetinu gido nustatyma faile
        with open('./settings.json', 'w') as f:
            json.dump({'ip': ip_txt_input_value, 'nickname': nick_txt_input_value, 'showGuideOnLaunch': 0}, f)

    # piesiu puslapio numeri
    page_num = page_num_font.render(f'{step}/{last_step}', 1, (255,255,255))
    surface.blit(page_num, (10, 10))


    # piesiu visa meniu surface ant window
    win.blit(surface, (0, 0))