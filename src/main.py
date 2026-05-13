import sys
if getattr(sys, 'frozen', False):
    import pyi_splash
import os
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = 'hide'
import pygame
from objects import Troop, Missile, Explosion, LaunchSite
from threading import Thread
import client
from random import randint
from common import lang, default_lang, WIDTH, HEIGHT, colors, FPS, amplify, sound_slow_rocket, sound_launch_gate_open, sound_taken_over, sound_warning, sound_attack, sound_city_armoured, sound_joined, sound_left, sound_missile_launch, sound_error, sound_explosions, sound_cash, sound_missile_alarm, nuclear_cities, MISSILE_RADIUS, SPLASH_RADIUS, nuclear_city_bound_surfs, MISSILE_PRICE
from all_cities import cities, borders, aux_cities, bridges
import menu
from menu import alter_menu_play_btns
import waiting
import end
from time import sleep

# pasirinkta kalba
pref_lang = default_lang

# lango ir komunikacijos su serveriu inicijavimas
pygame.init()
pygame.key.set_repeat(400, 50)
win = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption(lang[pref_lang]['Conquerors'])
pygame.display.set_icon( pygame.image.load('img/_icon.png') )
pygame.event.set_allowed([pygame.QUIT, pygame.MOUSEBUTTONDOWN, pygame.MOUSEBUTTONUP])
menu.init(win, pref_lang)
waiting.init(win, pref_lang)
end.init(win, pref_lang)

# muzika
pygame.mixer.music.load('audio/menu/theme.mp3')
pygame.mixer.music.set_volume(.05*amplify)
pygame.mixer.music.play(loops=-1)

reticle_angle = 0

# baigiu miestu iniciacija
for c in cities.values():
    c.init_font_image()

def enable_bot_fill(t): # su delay
    sleep(t)
    waiting.bot_fill_enabled = True

def refresh_game():
    global main_surface, main_surface2, not_available_city, gold_icon, gold_change, gold_change_color, reticle, regions_need_updating, troops, missiles, explosions
    global selected_city, pointing_city, targeting_type, my_color, my_color_font, my_gold_font, gold_change_font, winner, cities, player_cols_nicks, player_nick_font, bot_nick_font
    global my_gold, nuclear_launch_sites

    # kariai
    troops = {}
    # raketos
    missiles = {}
    # sprogimai
    explosions = []
    # raketu paleidimo aiksteles
    nuclear_launch_sites = {loc: LaunchSite(coords) for loc, coords in nuclear_cities.items()}

    # mano informacija
    selected_city = 'NOTHING'
    pointing_city = 'NOTHING'
    targeting_type = 'none'
    my_gold = 0
    gold_change = ''
    my_color = ''
    my_color_font = pygame.font.SysFont('consolas', 35)
    my_gold_font = pygame.font.SysFont('consolas', 26)
    gold_change_font = pygame.font.SysFont('consolas', 26, bold=True)
    gold_change_color = 'green'
    Thread(target=enable_bot_fill, args=(5,), daemon=True).start()
    player_cols_nicks = []
    player_nick_font = pygame.font.SysFont('consolas', 23, bold=True)
    bot_nick_font = pygame.font.SysFont('consolas', 23, italic=True)
    # zaidimo informacija
    winner = ''

    # pagrindinis langas
    main_surface = pygame.Surface((WIDTH, HEIGHT))
    main_surface.fill((0, 0, 50))
    # piesiu tiltus
    for connection in bridges:
        c1, c2 = [cities[x] for x in connection.split(',')]
        # pradinis tiltas
        line_coords = [(c1.x, c1.y), (c2.x, c2.y)]
        # randu, ar reikia daugiau nei vienos linijos
        for aux_c in aux_cities:
            if sorted([c1.location, c2.location]) == sorted(aux_c.location.split(',')):
                line_coords = [(c1.x, c1.y), (aux_c.x, aux_c.y), (c2.x, c2.y)]
                break
        # piesiu tiltus
        pygame.draw.lines(main_surface, (0,0,0), False, line_coords, 8)
        pygame.draw.lines(main_surface, (120,60,0), False, line_coords, 4)
    # nupiesti kitas, nenaudojamas zaidimui teritorijas
    main_surface.blit(pygame.transform.scale( pygame.image.load('maps/other-countries.png'), (WIDTH, HEIGHT) ), (0, 0))
    not_available_city = pygame.image.load('img/game/not_available.png')
    reticle = pygame.image.load('img/game/reticle.png')
    gold_icon = pygame.transform.scale(pygame.image.load('img/game/gold.png'), (48, 48))
    for c in cities.values():
        main_surface.blit( c.get_surface(), (0, 0) )
    regions_need_updating = []
    # resetinu miestu armoured lygi
    for c in cities.values():
        c.armoured = False

    # surface objektas troopsams ir miestams piesti
    main_surface2 = pygame.Surface((WIDTH, HEIGHT))
    main_surface2 = main_surface2.convert_alpha()
    main_surface2.fill((0, 0, 0, 0))
refresh_game()



# atnaujinu miestu spalvas (juodos atspalvi pagal zmoniu skaiciu)
def update_city_color(loc):
    global cities
        
    # nustatau reikiama spalva dabartiniam gyventoju skaiciui
    desired_col = 0
    if cities[loc].inhabitants <= 100:
        desired_col = 255 - cities[loc].inhabitants/100 * 255

    if cities[loc].city_col != desired_col:
        # jeigu dabartine spalva netinkama, pakeiciu
        cities[loc].city_col = desired_col
        cities[loc].text_col = 0
        if cities[loc].inhabitants > 60:
            cities[loc].text_col = 255 - desired_col


def show_gold_change(addition):
    global gold_change, gold_change_color
    
    if isinstance(addition, int):
        gold_change_color = 'red' if addition < 0 else 'green'
        gold_change = f'{'-' if addition < 0 else '+'}{abs(addition)}'
    elif isinstance(addition, str):
        gold_change_color = 'red'
        gold_change = f' {lang[pref_lang]['Insufficient gold reserve']} ({lang[pref_lang]['lacking']} {MISSILE_PRICE-my_gold}t)'
    my_message = gold_change
    
    sleep(2)
    if gold_change == my_message: # jeigu kita funkcijos show_gold_change instancija nepakeite uzraso
        gold_change = ''


def receiver():
    global troops, missiles, regions_need_updating, my_color, winner, player_cols_nicks, my_gold, selected_city, targeting_type

    while 1:
        try:
            # priima
            message = client.recv()

            # atskiriu zinutes pobudi ir koreguoju objektus
            if message.startswith('KARYS='):
                id, start_loc, targ_loc, x, y = message[6:].split(';')
                id, x, y = int(id), float(x), float(y)

                # koreguoju reikiama troop objekta. Jeigu nerandu, sukuriu nauja
                if id in troops.keys():
                    troops[id].x = x
                    troops[id].y = y
                else:
                    # sukuriu nauja troop objekta
                    if targ_loc in cities.keys():
                        new_troop = Troop(id, cities[start_loc], cities[targ_loc], win)
                    else:
                        new_troop = Troop(id, cities[start_loc], 'tarpinis miestas', win)
                    new_troop.x = x
                    new_troop.y = y
                    troops[id] = new_troop


            elif message.startswith('DINGO KARYS='):
                try:
                    troops.pop(int(message[12:]))
                except KeyError: # jeigu serveris taip greitai sukure kari bei ji istryne, kad net nespejo perduoti sukurimo informacijos klientui, gaunasi, kad cia bandoma istrinti neegzistuojanti kari
                    pass


            elif message.startswith('RAKETA='):
                id, x, y, angle = message[7:].split(';')
                id, x, y, angle = int(id), float(x), float(y), float(angle)
                # sukuriu nauja raketa, jei dar nebuvo
                if id not in missiles.keys():
                    new_m = Missile(id)
                    new_m.x, new_m.y, new_m.angle = x, y, angle
                    missiles[id] = new_m
                else:
                    missiles[id].x = x
                    missiles[id].y = y
                    missiles[id].angle = angle


            elif message.startswith('SIRENA='):
                launch_loc, target_loc, alarm_length, launch_delay, missile_id = message[7:].split(';')
                if my_color == cities[target_loc].owner:
                    sound_missile_alarm.play(maxtime=(int(alarm_length)+int(launch_delay))*1000)
                # visiems pradedama rodyti raketos paleidimo animacija su garsu
                Thread(target=missile_launch, args=(int(launch_delay), launch_loc, int(missile_id)), daemon=True).start()


            elif message.startswith('MIESTAS='):
                loc, owner, inhab = message[8:].split(';')
                inhab = int(inhab)

                # koreguoju
                cities[loc].owner = owner
                cities[loc].inhabitants = inhab
                update_city_color(loc) # atnaujinu spalva


            elif message.startswith('NAUJA TERITORIJOS SPALVA='): # du kartus atnaujinu is eiles, nes atnaujinus tik viena karta pasirodo paveiksleliai atsinaujina vienu uzemimu per velai
                regions_need_updating.append(message[25:])
                #regions_need_updating.append(message[25:])
                sound_taken_over.play()

                # jeigu tai buvo mano teritorija ir as jau buvau ja pazymejes, tai atzymiu
                if selected_city != 'NOTHING':
                    if message[25:] == selected_city.location:
                        selected_city.r = selected_city.normal_r # grizta i iprasta dydi
                        selected_city.init_font_image()
                        selected_city = 'NOTHING'
                        targeting_type = 'none'

                # tikrinu, ar dar turiu teritoriju
                my_territory_count = len([c for c in cities.values() if c.owner == my_color])
                if my_territory_count == 0:
                    client.send('VISKAS PRARASTA')

            elif message.startswith('PRIDETI AUKSO='): # aukso pridejimas
                col, addition = message[14:].split(';')
                if col == my_color:
                    my_gold += int(addition)
                    sound_cash.play()
                    Thread(target=show_gold_change, args=(int(addition),), daemon=True).start() # trumpam parodau, kiek buvo prideta aukso


            elif message.startswith('ISPEJIMAS='):
                if randint(0, 2) == 0: # mazdaug kas trecias uzpuolimas tures garsa, nes uzkniso jau
                    if message[10:] == my_color:
                        sound_warning.play()

            elif message.startswith('PATOBULINTAS MIESTAS='):
                cities[message[21:]].armoured = True
                sound_city_armoured.play()


            elif message.startswith('SUNAIKINTAS RAKETOS='):
                loc, m_id = message[20:].split(';')
                cities[loc].armoured = False
                # animacija
                affected = [c for c in cities.values() if cities[loc].dist_to(c.x, c.y) <= SPLASH_RADIUS and loc != c.location] # visi paveikti miestai aplink
                explosions.append(Explosion(cities[loc], affected))
                # sprogimo garsas
                sound_explosions[randint(0, 1)].play()
                # salinu raketa is dictonary
                try:
                    missiles.pop(int(m_id))
                except KeyError as e:
                    print(e)


            elif message.startswith('LAIMEJO='):
                client.game_status = 'PABAIGA'
                end.timer = 0
                winner = message[8:]
                # muzika
                pygame.mixer.music.stop()
                pygame.mixer.music.unload()
                if winner == my_color:
                    pygame.mixer.music.load('audio/end/clapping.mp3')
                else:
                    pygame.mixer.music.load('audio/end/lost.mp3')
                pygame.mixer.music.set_volume(.07*amplify)
                pygame.mixer.music.play()


            elif message.startswith('SPALVA='):
                # refreshinu zaidimo surfaces
                refresh_game()
                # pridedu nauja is serverio info
                my_color = message[7:]
                client.game_status = 'ZAIDIMAS'
                # nusiunciu kitiems zaidejams savo nickname (t.y. serveriui, kuris perforwardins toliau)
                client.send(f'NICKAS={my_color};{menu.nick_txt_input.value}')
                # muzika
                pygame.mixer.music.stop()
                pygame.mixer.music.unload()
                pygame.mixer.music.load('audio/game/drums.mp3')
                pygame.mixer.music.set_volume(.06*amplify)
                pygame.mixer.music.play(loops=-1)

            elif message.startswith('NICKAS='):
                p_col, p_nickname = message[7:].split(';')
                # priskiriu, kad iskart rodyciau zaidime
                player_cols_nicks.append((p_col, p_nickname, 'human')) # (spalva, nickname'as, player_type)

            elif message.startswith('BOTAS='):
                b_col = message[6:]
                player_cols_nicks.append((b_col, lang[pref_lang]['Bot'], 'bot'))


            elif message.startswith('PRISIJUNGE='):
                past_joined = waiting.joined
                waiting.joined, waiting.needed_players = message[11:].split('/')
                if int(past_joined) < int(waiting.joined):
                    sound_joined.play()
                else:
                    sound_left.play()
                

            elif message.startswith('INDEKSAS EILEJE='):
                if message[16:] == '0':
                    waiting.bot_fill_enabled = True
                    client.send(f'BOT STRENGTH={round(waiting.bot_strength, 2)}')
                else:
                    waiting.bot_fill_enabled = False

            
            elif message.startswith('BOT STRENGTH='):
                waiting.bot_strength = float(message[13:])
                waiting.text_boxes['bot strength'].update_text(f'{' '*(3-len(str(round(waiting.bot_strength*100))))}{round(waiting.bot_strength*100)}%')


        except ConnectionAbortedError: # atsijungta nuo serverio tycia (paspaudus mygtuka)
            break
        except ConnectionResetError: # buvo isjungtas pats serveris
            attempt_disconnect()
            client.game_status = 'PABAIGA'
            end.timer = 0
            winner = 'server disconnected'
            pygame.mixer.music.stop()
            pygame.mixer.music.unload()
            break
        except Exception as e:
            print(type(e), e)




def attempt_connection():
    menu.conn_status = 'hold'
    alter_menu_play_btns('disable')
    state = client.connect(menu.ip_txt_input.value) # jungiuosi prie serverio

    if state == 'success':
        Thread(target=receiver, args=(), daemon=True).start() # klausau serverio
        menu.conn_status = 'online'
        alter_menu_play_btns('enable')
    else:
        menu.conn_status = 'offline'
        alter_menu_play_btns('disable')

def attempt_disconnect():
    menu.conn_status = 'hold'
    client.disconnect() # receiver() automatiskai issijungs
    menu.conn_status = 'offline'
    alter_menu_play_btns('disable')


def missile_launch(launch_delay, launch_loc, missile_id):
    global nuclear_launch_sites, missiles

    # islindimas is duobes
    cycle_time = (launch_delay+.2)/nuclear_launch_sites[launch_loc].final_stage
    sound_launch_gate_open.play()
    sound_slow_rocket.play()

    for i in range(1, nuclear_launch_sites[launch_loc].final_stage+1):
        sleep(cycle_time)
        nuclear_launch_sites[launch_loc].stage = i
        if i == 53:
            sound_launch_gate_open.play() # uzdarymas
    nuclear_launch_sites[launch_loc].stage = 1
    
    sound_missile_launch.play()

    # raketos greicio pakeitimas
    missiles[missile_id].change_to_fast()


def ground_attack():
    # pernesti karius
    if pointing_city != 'NOTHING' and pointing_city.location != selected_city.location:
        # jeigu prasoma perkelti karius ne i salia esancia teritorija, prasymas ignoruojamas
        if pointing_city.location in borders[selected_city.location].split(','):
            client.send(f'ATAKA={selected_city.location};{pointing_city.location};{selected_city.inhabitants}')
            # muzika
            if randint(0, 9) == 0: # mazdaug kas desimtas uzpuolimas tures garsa, nes uzkniso jau
                sound_attack.play()

def air_attack():
    global my_gold
    if pointing_city != 'NOTHING' and pointing_city.location != selected_city.location:
        if pointing_city.dist_to(nuclear_cities[selected_city.location][0], nuclear_cities[selected_city.location][1]) <= MISSILE_RADIUS:
            if my_gold >= MISSILE_PRICE:
                client.send(f'NAUJA RAKETA={selected_city.location};{pointing_city.location}')
                ### cia anksciau buvo Thread(target=missile_launch...
                my_gold -= MISSILE_PRICE
                Thread(target=show_gold_change, args=(-MISSILE_PRICE,), daemon=True).start() # trumpam parodau, kiek buvo atimta aukso
            else:
                sound_error.play()
                Thread(target=show_gold_change, args=('-',), daemon=True).start() # pasako, kad truksta aukso



# uzdarau loading langa (pyinstaller splash screen)
if getattr(sys, 'frozen', False):
    pyi_splash.close()

# pradinis jungimasis prie serverio
Thread(target=attempt_connection, args=(), daemon=True).start()

# zaidimo loopas
run = True
clock = pygame.time.Clock()
while run:
    clock.tick(FPS)


    mouse_x, mouse_y = pygame.mouse.get_pos()
    # tikrinu ar paspausta
    pressed = False


    # tikrinu lango ivykius
    events = pygame.event.get()
    for event in events:
        if event.type == pygame.QUIT:
            run = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            pressed = True
        if client.game_status == 'ZAIDIMAS':
            if event.type == pygame.MOUSEBUTTONDOWN:
                # nunulina padeti
                pointing_city = 'NOTHING'
                if selected_city != 'NOTHING':
                    # pointinamas miestas
                    pointing_city = min(cities.values(), key=lambda x:x.dist_to(mouse_x, mouse_y))
                    if event.button == 1 and targeting_type == 'ground': # LMB
                        ground_attack()
                    elif event.button == 3 and targeting_type == 'air':
                        air_attack()
                    selected_city.r = selected_city.normal_r # grizta i iprasta dydi
                    selected_city.init_font_image()
                    selected_city = 'NOTHING'
                    targeting_type = 'none'
                else:
                    if event.button == 1:
                        # pasirenka
                        closest_city = min(cities.values(), key=lambda x:x.dist_to(mouse_x, mouse_y))
                        if closest_city.owner == my_color:
                            selected_city = closest_city
                            # padideja miesto apskritimas
                            selected_city.r = selected_city.normal_r + 4
                            selected_city.init_font_image(17)
                            targeting_type = 'ground'
                    elif event.button == 3:
                        # pasirenka
                        closest_city = min(cities.values(), key=lambda x:x.dist_to(mouse_x, mouse_y))
                        if closest_city.owner == my_color and closest_city.location in nuclear_cities.keys():
                            selected_city = closest_city
                            # padideja miesto apskritimas
                            selected_city.r = selected_city.normal_r + 4
                            selected_city.init_font_image(17)
                            targeting_type = 'air'


            elif event.type == pygame.MOUSEBUTTONUP:
                if selected_city != 'NOTHING':
                    # ieskau artimiausio pelei miesto
                    pointing_city = min(cities.values(), key=lambda x:x.dist_to(mouse_x, mouse_y))
                    if pointing_city.location != selected_city.location:
                        if event.button == 1 and targeting_type == 'ground':
                            ground_attack()
                        elif event.button == 3 and targeting_type == 'air':
                            air_attack()
                        if selected_city.dist_to(mouse_x, mouse_y) > selected_city.r: # atzymiu miesta jeigu reikia
                            selected_city.r = selected_city.normal_r # grizta i iprasta dydi
                            selected_city.init_font_image()
                            selected_city = 'NOTHING'
                        targeting_type = 'none'



    # zaidimo statusai
    # zaidimo procesai
    if client.game_status == 'ZAIDIMAS':        
        # atnaujinu teritorijas
        if len(regions_need_updating) > 0:
            main_surface.blit(cities[regions_need_updating[0]].get_surface(), (0, 0))
            regions_need_updating.pop(0)
        # piesiu teritorijas
        win.blit(main_surface, (0, 0))
            

        
        # piesiu atomines aiksteles
        try:
            for loc, site in nuclear_launch_sites.items():
                site.draw(main_surface2)
        except RuntimeError:
            pass


        # randu artimiausia pointinama miesta
        pointing_city = cities[min(cities, key=lambda x: cities[x].dist_to(mouse_x, mouse_y))]
        
        # piesiu kelia, kuriuo eis troopai
        if targeting_type == 'ground':
            if selected_city not in ('NOTHING', pointing_city):
                if pointing_city.location in borders[selected_city.location]:
                    # pradinis kelias
                    line_coords = [(selected_city.x, selected_city.y), (pointing_city.x, pointing_city.y)]
                    # randu, ar reikia daugiau nei vienos linijos
                    for aux_c in aux_cities:
                        if sorted([selected_city.location, pointing_city.location]) == sorted(aux_c.location.split(',')):
                            line_coords = [(selected_city.x, selected_city.y), (aux_c.x, aux_c.y), (pointing_city.x, pointing_city.y)]
                            break
                    # piesiu kelia
                    pygame.draw.lines(main_surface2, (0,0,0), False, line_coords, 12)
                    pygame.draw.lines(main_surface2, (255,255,255), False, line_coords, 4)



        # piesiu troopsus
        try:
            for troop in troops.values():
                # drawing
                troop.draw(main_surface2)
        except RuntimeError:
            pass


        # piesiu miestus
        try:
            for city in cities.values():
                # drawing
                city.draw_city(main_surface2)
        except RuntimeError:
            pass


        # piesiu miestu sprogimus ir zemes drebejimus nuo raketu
        try:
            for expl in explosions:
                # drawing
                expl.draw(main_surface2)
                expl.stage += 13/FPS
                if expl.stage >= 25:
                    explosions.remove(expl)
        except RuntimeError:
            pass


        # piesiu raketas
        try:
            for missile in missiles.values():
                # drawing
                missile.draw(main_surface2)
        except RuntimeError:
            pass


        # piesiu raketos veiksmingumo zonas ir raudona teritorija
        if targeting_type == 'air':
            # raudona teritorija
            main_surface2.blit(nuclear_city_bound_surfs[selected_city.location], (0, 0))
            pygame.draw.circle(main_surface2, (200, 0, 0), nuclear_cities[selected_city.location], MISSILE_RADIUS+2, 2)
            if pointing_city != selected_city and pointing_city.dist_to(nuclear_cities[selected_city.location][0], nuclear_cities[selected_city.location][1]) <= MISSILE_RADIUS:
                # linija nurodau paveikiamus miestus
                for cit in [cit for cit in cities.values() if cit.dist_to(pointing_city.x, pointing_city.y) <= SPLASH_RADIUS]:
                    pygame.draw.line(main_surface2, (220, 220, 72), (cit.x, cit.y), (pointing_city.x, pointing_city.y), 5)
                # splash spindulys
                pygame.draw.circle(main_surface2, (150, 0, 0), (pointing_city.x, pointing_city.y), SPLASH_RADIUS, 3)

        # jeigu bandoma pointinti i neleistina teritorija, uzdedu 'x' zenkla ant miesto
        if selected_city not in ('NOTHING', pointing_city):
            if (targeting_type == 'ground' and pointing_city.location not in borders[selected_city.location]) or (targeting_type == 'air' and pointing_city.dist_to(nuclear_cities[selected_city.location][0], nuclear_cities[selected_city.location][1]) > MISSILE_RADIUS):
                pygame.draw.circle(main_surface2, (0, 0, 0), (pointing_city.x, pointing_city.y), pointing_city.r+1) # tamsus fonas raudonam kryziui
                main_surface2.blit(not_available_city, (pointing_city.x-not_available_city.get_width()/2, pointing_city.y-not_available_city.get_height()/2))
            
            # piesiu taikikli ant pointing city
            if (targeting_type == 'ground' and pointing_city.location in borders[selected_city.location]) or (targeting_type == 'air' and pointing_city.dist_to(nuclear_cities[selected_city.location][0], nuclear_cities[selected_city.location][1]) <= MISSILE_RADIUS):
                rotated = pygame.transform.rotate(reticle, reticle_angle)
                main_surface2.blit(rotated, rotated.get_rect(center=(pointing_city.x-.5, pointing_city.y-1)))
                reticle_angle += 90/FPS
                if reticle_angle == 360: reticle_angle = 0



        # piesia miestus ir troopsus
        win.blit(main_surface2, (0, 0))
        main_surface2.fill((0, 0, 0, 0)) # uzpiesiu transparent backgrounda per nauja




        # mano spalvos uzrasas
        text = my_color_font.render(lang[pref_lang][f'You are {my_color}'], 1, colors[my_color])

        surface = pygame.Surface( (text.get_width() , text.get_height()) )
        surface.fill((0, 0, 0))

        win.blit(surface, ( WIDTH-surface.get_width(), HEIGHT-surface.get_height() ))
        win.blit(text, ( WIDTH-surface.get_width(), HEIGHT-surface.get_height() ))


        # mano turimas auksas
        win.blit(gold_icon, (10, 0))

        text = my_gold_font.render(f'{my_gold}t', 1, colors['yellow'])
        win.blit(text, (10+gold_icon.get_width()+10, gold_icon.get_height()/2-text.get_height()/2))

        text2 = gold_change_font.render(' '+gold_change, 1, colors[gold_change_color])
        win.blit(text2, (10+gold_icon.get_width()+10+text.get_width(), gold_icon.get_height()/2-text.get_height()/2))


        # surasau, kokie zaideju vardai ir spalvos
        for i, (p_col, p_nick, player_type) in enumerate(player_cols_nicks):
            correct_font = player_nick_font if player_type == 'human' else bot_nick_font # parenku fonta pagal tai, ar rasomas zaidejo, ar boto vardas
            text = correct_font.render(' '*(len( max(player_cols_nicks, key=lambda x:len(x[1]))[1] ) - len(p_nick)) + p_nick, 1, colors[p_col])

            surface = pygame.Surface( (text.get_width()+12, text.get_height()+4) )
            surface.fill((0, 0, 0))


            win.blit(surface, ( WIDTH-surface.get_width(), 0+surface.get_height()*i ))
            win.blit(text, ( WIDTH-surface.get_width()+12/2, 0+surface.get_height()*i+4/2 ))




    elif client.game_status == 'MENIU':
        # rodau meniu
        next_move = menu.show(pressed, events)
        
        if next_move != -1:
            if next_move.startswith('kalba='):
                pref_lang = next_move[6:]
                # atnaujinu kalbas visur
                pygame.display.set_caption(lang[pref_lang]['Conquerors'])
                menu.init(win, pref_lang)
                waiting.init(win, pref_lang)
                end.init(win, pref_lang)
                alter_menu_play_btns('disable') if menu.conn_status in ('offline', 'hold') else alter_menu_play_btns('enable')
            elif next_move.startswith('zaisti='):
                if client.is_connected(): # tikrinu, ar serveris vis dar pasiekiamas
                    client.send(f'NORIU ZAISTI={next_move[7:]};human') # pranesu, kad noriu zaisti
                    client.game_status = 'LAUKIMAS'
                else: # tinkamai pakeiciu interface i neprijungta serveri (disablinu zaidimo pradzios mygtukus ir serverio connection mygtuka)
                    menu.conn_status = 'offline'
                    alter_menu_play_btns('disable')
            elif next_move == 'jungtis':
                Thread(target=attempt_connection, args=(), daemon=True).start()
            elif next_move == 'atsijungti':
                Thread(target=attempt_disconnect, args=(), daemon=True).start()



    elif client.game_status == 'LAUKIMAS':
        # rodau laukimo ekrana
        next_move = waiting.show(pressed)
        # jeigu paspaudziu viena is dvieju mygtuku - atsaukiu laukima arba pakvieciu botu
        if next_move != '':
            if len(next_move.split(';')) == 2 and next_move.split(';')[0] == 'fill with bots':
                client.send(f'FILL WITH BOTS;{next_move.split(';')[1]}')
            elif next_move in ('-', '+'):
                client.send(f'BOT STRENGTH={round(waiting.bot_strength, 2)}')
            elif next_move == 'cancel':
                client.send('CANCEL')
                client.game_status = 'MENIU' # grazinu i meniu
                waiting.joined = 0


    elif client.game_status == 'PABAIGA':
        # rodau pabaigos ekrana
        next_move = end.show(my_color, winner, pressed, main_surface)
        
        if next_move == lang[pref_lang]['Back']:
            client.game_status = 'MENIU' # grazinu i meniu
            waiting.joined = 0
            # muzika per nauja
            pygame.mixer.music.stop()
            pygame.mixer.music.unload()
            pygame.mixer.music.load('audio/menu/theme.mp3')
            pygame.mixer.music.set_volume(.05*amplify)
            pygame.mixer.music.play(loops=-1)

    #print(mouse_x,mouse_y)
    
    pygame.display.flip()
client.disconnect()
pygame.quit()