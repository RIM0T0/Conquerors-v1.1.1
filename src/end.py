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
from common import WIDTH, HEIGHT, lang, FPS, colors, default_lang
from objects import Button


pref_lang = default_lang
# inicijuoju kintamuosius, kuriems reikia window
def init(window, pref):
    global win, button, pref_lang

    pref_lang = pref
    win = window
    button = Button(win, lang[pref_lang]['Back'], 35, 'white', 'black', 'center', 500)


timer = 0
def show(my_color, winner, pressed, latest_game_surf):
    global timer

    # laimetojo spalvos fonas
    surface = pygame.Surface((WIDTH, HEIGHT))
    if winner in ('player left', 'server disconnected'):
        surface.fill( (0, 0, 0) )
    else:
        surface.fill( (colors[winner][0], colors[winner][1], colors[winner][2]) )
    
    # permatomumas
    if timer < 4:
        surface.set_alpha(1)
        latest_game_surf.blit(surface, (0, 0))
        win.blit(latest_game_surf, (0, 0))
    # timer'is - kiek laiko praejo nuo pabaigos lango rodymo pradzios
    timer += 1/FPS



    # laimejai/pralaimejai uzrasas
    font = pygame.font.SysFont('consolas', 40, bold=True)
    notice = lang[pref_lang]['YOU WON'] if (winner == my_color) else lang[pref_lang]['YOU LOST']
    if winner == 'player left':
        notice = lang[pref_lang]['Someone has left the game']
    elif winner == 'server disconnected':
        notice = lang[pref_lang]['Server is offline']
    text = font.render( notice, 1, (255,255,255) )
    win.blit(text, (win.get_width()/2-text.get_width()/2, win.get_height()/2-text.get_height()/2))

    # mygtukas grizti
    selected = ''
    button.blit(win)
    if button.is_pressed(pressed):
        selected = button.text


    # atsakymas
    return selected