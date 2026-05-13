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
from math import sqrt

# langas
WIDTH = 1000
HEIGHT = 750
DIAGONAL = sqrt(WIDTH**2 + HEIGHT**2)
FPS = 50


# serverio/kliento komunikacija
FORMAT = 'ascii'
BUFFER = 150
PORT = 443



# imanomos troopu/zaideju spalvos, taip pat pabaigos ekrano laimetojo spalva nudazomas ekranas
colors = {
    'green': (54, 161, 9),
    'red': (175, 17, 17),
    'blue': (32, 50, 162),
    'yellow': (228, 221, 42)
}


# muzika ir garsai
amplify = 1.5 # visus garsus padidina, bet ju paciu proporcijos islieka

pygame.mixer.init()
sound_taken_over = pygame.mixer.Sound('audio/game/taken_over.wav')
sound_taken_over.set_volume(.03*amplify)
sound_warning = pygame.mixer.Sound('audio/game/warning.mp3')
sound_warning.set_volume(.06*amplify)
sound_attack = pygame.mixer.Sound('audio/game/attack.mp3')
sound_attack.set_volume(.09*amplify)
sound_city_armoured = pygame.mixer.Sound('audio/game/city_armoured.wav')
sound_city_armoured.set_volume(.06*amplify)
sound_joined = pygame.mixer.Sound('audio/waiting/joined.wav')
sound_joined.set_volume(.06*amplify)
sound_left = pygame.mixer.Sound('audio/waiting/left.wav')
sound_left.set_volume(.05*amplify)
sound_click = pygame.mixer.Sound('audio/menu/click.wav')
sound_click.set_volume(.2*amplify)
sound_error = pygame.mixer.Sound('audio/game/error.mp3')
sound_error.set_volume(.5*amplify)
sound_explosions = [pygame.mixer.Sound(f'audio/game/explosion1.mp3'), pygame.mixer.Sound(f'audio/game/explosion2.mp3')]
for e in sound_explosions:
    e.set_volume(.2*amplify)
sound_missile_launch = pygame.mixer.Sound('audio/game/missile_launch.mp3')
sound_missile_launch.set_volume(.2*amplify)
sound_cash = pygame.mixer.Sound('audio/game/cash.mp3')
sound_cash.set_volume(.15*amplify)
sound_missile_alarm = pygame.mixer.Sound('audio/game/eas.mp3')
sound_missile_alarm.set_volume(.25*amplify)
sound_launch_gate_open = pygame.mixer.Sound('audio/game/launch_gate_open.mp3')
sound_launch_gate_open.set_volume(.1*amplify)
sound_slow_rocket = pygame.mixer.Sound('audio/game/slow_rocket.mp3')
sound_slow_rocket.set_volume(.66*amplify)



# kalba
lang = {
    'en': {
        'Conquerors': 'Conquerors',
        'CONQUERORS': 'CONQUERORS',

        'Players': 'Players',
        'Fill with bots': 'Fill with bots',
        'Bot strength': 'Bot strength',
        'Cancel': 'Cancel',
        'joined': 'joined',
        'Waiting for players': 'Waiting for players',
        'Nickname': 'Nickname',
        'Server IP': 'Server IP',
        'How to play?': 'How to play?',

        'YOU WON': 'YOU WON',
        'YOU LOST': 'YOU LOST',
        'Back': 'Back',
        'Someone has left the game': 'Someone has left the game',
        'Server is offline': 'Server is offline',

        'You are green': 'You are green',
        'You are red': 'You are red',
        'You are blue': 'You are blue',
        'You are yellow': 'You are yellow',
        'Bot': 'Bot',
        'Insufficient gold reserve': 'Insufficient gold reserve',
        'lacking': 'lacking',

        'Rule Europe!': 'Rule Europe!',
        'Expand your empire.': 'Expand your empire.',
        'Strategy is everything.': 'Strategy is everything.',
        'Done': 'Done',
    },
    'lt': {
        'Conquerors': 'Užkariautojai',
        'CONQUERORS': 'UŽKARIAUTOJAI',

        'Players': 'Žaidėjai',
        'Fill with bots': 'Žaisti prieš kompiuterį',
        'Bot strength': 'Komp. žaidėjų stiprumas',
        'Cancel': 'Atšaukti',
        'joined': 'prisijungė',
        'Waiting for players': 'Laukiama žaidėjų',
        'Nickname': 'Vardas',
        'Server IP': 'Serverio IP',
        'How to play?': 'Kaip žaisti?',

        'YOU WON': 'LAIMĖJAI',
        'YOU LOST': 'NEPASISEKĖ',
        'Back': 'Atgal',
        'Someone has left the game': 'Priešininkas paliko žaidimą',
        'Server is offline': 'Serveris išjungtas',

        'You are green': 'Tu žaliasis',
        'You are red': 'Tu raudonasis',
        'You are blue': 'Tu mėlynasis',
        'You are yellow': 'Tu geltonasis',
        'Bot': 'Kompiuteris',
        'Insufficient gold reserve': 'Nepakanka aukso',
        'lacking': 'trūksta',

        'Rule Europe!': 'Užvaldyk Europą!',
        'Expand your empire.': 'Plėsk imperiją!',
        'Strategy is everything.': 'Svarbiausia čia - strategija.',
        'Done': 'Baigti',
    }
}
default_lang = 'lt'
default_bot_strength = .35





# miestai, is kuriu galima leisti branduolini ginkla ir paleidimo aiksteles koordinates
nuclear_cities = {
    'ispanijos-pietus': (123, 648),
    'azerbaidzanas': (905, 599),
    'islandija': (168, 107)
}
MISSILE_PRICE = 50
MISSILE_RADIUS = 600 # kokius atstumu galima leisti branduolines raketas
SPLASH_RADIUS = 100 # poveikis aplinkiniams miestams

# sukuriu visus pygame surfaces, kurias rodysiu, kai taikysiuosi su raketomis
def bound_surf(coords):
    surf = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    for x in range(WIDTH):
        for y in range(HEIGHT):
            x_hole, y_hole = coords
            if sqrt((x-x_hole)**2 + (y-y_hole)**2) >= MISSILE_RADIUS:
                surf.set_at((x, y), (200, 0, 0, 100))
    return surf

nuclear_city_bound_surfs = {loc:bound_surf(coords) for loc, coords in nuclear_cities.items()}

nuclear_city_exception_routes = [
    'islandija--norvegijos-siaure',
    'islandija--svedijos-siaure',
    'islandija--svedijos-pietus',
    'islandija--ispanijos-siaure',
    'islandija--ispanijos-pietus',
    'islandija--portugalija',
    'islandija--rusijos-vakarai',
    'islandija--lietuva',
    'islandija--karaliaucius',
    'islandija--baltarusija',
    'islandija--ukrainos-vakarai',
    'islandija--lenkija'
]
