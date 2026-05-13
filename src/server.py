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

import socket
from threading import Thread
from multiprocessing import Process
from random import choice, randint
from objects import Troop, Missile
from time import sleep, asctime
from math import floor
import server_sender
import copy
from common import FORMAT, BUFFER, PORT, colors, FPS, SPLASH_RADIUS, MISSILE_RADIUS
from all_cities import cities, aux_cities, borders
from string import ascii_uppercase
from bot2 import start as start_bot




# auginu visus miestus (vienodu greiciu 1 zmogus per sekunde)
def growing_cities(game_code):
    # nurodau, kurio zaidimo informacija keisti ir tikrinti
    cities = gameplay[game_code][0]
    armoured_cities = gameplay[game_code][4]
    socks = gameplay[game_code][5]

    AUTOMATIC_GROWING_LIMIT = 100
    NEUTRAL_GROWING_LIMIT = 15 #0 testuojant
    GLOBAL_GROWING_RATE = 1
    ARMOURED_CITY_BOOST = 1.1

    while game_code in gameplay.keys() and gameplay[game_code][3] == 'STILL NO WINNER':
        sleep(1) #.1 testuojant
        for city in cities.values():
            if city.owner != 'NOBODY': # auginu zaideju miestus
                increase = GLOBAL_GROWING_RATE*ARMOURED_CITY_BOOST**len(armoured_cities[city.owner])

                if city.inhabitants < AUTOMATIC_GROWING_LIMIT:
                    if city.inhabitants + increase <= AUTOMATIC_GROWING_LIMIT:
                        city.inhabitants += increase
                    else:
                        city.inhabitants = AUTOMATIC_GROWING_LIMIT
            else: # auginu neutralius miestus
                if city.inhabitants + GLOBAL_GROWING_RATE <= NEUTRAL_GROWING_LIMIT:
                    city.inhabitants += GLOBAL_GROWING_RATE
                else:
                    city.inhabitants = NEUTRAL_GROWING_LIMIT

            # tikrinu, ar galima pekelti miesto lygi
            if city.inhabitants >= 300 and city.location not in armoured_cities[city.owner]:
                city.inhabitants -= 300
                armoured_cities[city.owner].append(city.location)
                # pranesu visiems, kad miesto lygis buvo pakeltas
                server_sender.queue.append((socks, f'PATOBULINTAS MIESTAS={city.location}'))


            # siunciu info apie pati miesta
            server_sender.queue.append( (socks, f'MIESTAS={city.location};{city.owner};{floor(city.inhabitants)}') )



# miestai turteja (gauna aukso)
def growing_capital(game_code):
    # nurodau, kurio zaidimo informacija keisti ir tikrinti
    cities = gameplay[game_code][0]
    socks = gameplay[game_code][5]

    GOLD_RATE = 1 # tonomis aukso vienam miestui per 10 sekundziu

    while game_code in gameplay.keys() and gameplay[game_code][3] == 'STILL NO WINNER':
        sleep(10)
        for col in colors.keys():
            addition = len([city.location for city in cities.values() if city.owner == col])*GOLD_RATE
            # siunciu info apie prideta auksa
            if addition != 0:
                server_sender.queue.append( (socks, f'PRIDETI AUKSO={col};{addition}') )








# spawninu troopus kai papraso zaidejas
def spawn_troops(city_of_origin, target_city, troop_count, game_code):
    # nurodau, kurio zaidimo informacija keisti ir tikrinti
    troops = gameplay[game_code][1]
    used_troop_ids = gameplay[game_code][2]
    original_owner = city_of_origin.owner
    
    for _ in range(troop_count): # siunciu tik tiek troopu, kiek paprase zaidejas
        # saugos mechanizmas, jeigu zmones baigiasi anksciau nei tiketasi
        if city_of_origin.inhabitants <= 0 or city_of_origin.owner != original_owner:
            break
        
        # isrenka nauja id
        new_id = randint(0, 10000)
        while new_id in used_troop_ids:
            new_id = randint(0, 10000)
        used_troop_ids.append(new_id)



        # sukuria nauja objekta ir issiuncia
        setting_final_target_city, setting_target_city = '', target_city

        # ar reikia eiti per papildoma miesta
        for c in aux_cities:
            if city_of_origin.location in c.location.split(',') and target_city.location in c.location.split(','): # tokiu atveju teks eiti per papildoma miesta
                setting_final_target_city, setting_target_city = target_city, c
                break
        
        # surasau tinkama info
        new_tr = Troop(new_id, city_of_origin, setting_target_city)
        new_tr.final_target_city = setting_final_target_city
        
        # prikabinu sukurta troop'a zaidimui
        troops[new_id] = new_tr
        city_of_origin.inhabitants -= 1
        
        # prikabinu sukurta troop'a prie miesto troopu saraso
        city_of_origin.originated_troop_ids.append(new_id)



        sleep(.1)





# karius judinu nuolatos! Jei atsiranda nauju, jie juda ten, kur turetu
def mobilizing_troops(game_code):
    # nurodau, kurio zaidimo informacija keisti ir tikrinti
    cities = gameplay[game_code][0]
    troops = gameplay[game_code][1]
    used_troop_ids = gameplay[game_code][2]
    armoured_cities = gameplay[game_code][4]
    socks = gameplay[game_code][5]

    # judinu karius ir tikrinu, kada jau atejo iki miesto
    while game_code in gameplay.keys() and gameplay[game_code][3] == 'STILL NO WINNER':
        sleep(1/FPS)

        try:
            troops_to_remove = []



            for troop in troops.values():
                # atnaujinu atsitiktinio judejimo krypti
                troop.improvise()

                troop.x += troop.x_vel_per_sec/FPS
                troop.y += troop.y_vel_per_sec/FPS

                if troop.target_city.dist_to(troop.x, troop.y) < troop.target_city.r - troop.r: # jei troopas pasiekia tiksla

                    if troop.final_target_city == '' or troop.final_target_city == troop.target_city: # jeigu pasiektas miestas is tikruju ir yra tikslas, o ne tarpinis miestas
                        # jeigu karys dar nebuvo nustatytas susinaikinti
                        if troop.id not in troops_to_remove:
                            # panaikinu kari is serverio saraso
                            troops_to_remove.append(troop.id) # kitaip meta klaida bandant pasalinti objekta, kuri jau buvo pasaline
                        
                            # papildo/atima gyventoju
                            if troop.target_city.owner == troop.owner:
                                troop.target_city.inhabitants += 1
                            else:
                                troop.target_city.inhabitants -= 1

                            # pakeicia teritorijos spalva pagal nauja valdytoja
                            if troop.target_city.inhabitants < 0:
                                # zaidejas nebetenka patobulinto miesto
                                if troop.target_city.location in armoured_cities[troop.target_city.owner]:
                                    armoured_cities[troop.target_city.owner].remove(troop.target_city.location)
                                    # naujas valdytojas perima patobulinto miesto vadyba
                                    armoured_cities[troop.owner].append(troop.target_city.location)

                                troop.target_city.owner = troop.owner
                                troop.target_city.inhabitants = abs(troop.target_city.inhabitants)
                                # issiunciu pranesima, kad buvo uzimta nauja teritorija
                                server_sender.queue.append( (socks, f'MIESTAS={troop.target_city.location};{troop.target_city.owner};{floor(troop.target_city.inhabitants)}') )
                                server_sender.queue.append( (socks, f'NAUJA TERITORIJOS SPALVA={troop.target_city.location}') )


                    else: # jeigu pasiektas miestas yra tik tarpine stotele, tada nustatau troop'a eiti finaline linkme
                        troop.target_city = troop.final_target_city


                else: # jeigu troopas nepasiekia tikslo, bet galbut susiliete su kitu troopsu
                    
                    # sudarau sarasa troopsu, kurie bent teoriskai galetu susiliesti su tikrinamuoju troop
                    checkable_troops = []

                    for id in cities[troop.starting_location].originated_troop_ids:
                        checkable_troops.append(troops[id])
                    for l in borders[troop.starting_location].split(','):
                        for id in cities[l].originated_troop_ids:
                            checkable_troops.append(troops[id])

                    if ',' not in troop.target_city.location:
                        for id in cities[troop.target_city.location].originated_troop_ids:
                            checkable_troops.append(troops[id])
                        for l in borders[troop.target_city.location].split(','):
                            for id in cities[l].originated_troop_ids:
                                checkable_troops.append(troops[id])

                    # tikrinu ar troopsai susiliecia
                    try:
                        closest_enemy_troop = min([tr2 for tr2 in checkable_troops if tr2.owner != troop.owner], key=lambda var:troop.dist_to(var.x, var.y)) # jeigu isvis imanomas susilietimas (troopsus tikrinu tik is artimiausiu miestu) ir jeigu susiliecia svetimi kariai
                        if closest_enemy_troop.dist_to(troop.x, troop.y) < troop.r:
                            if troop.id not in troops_to_remove and closest_enemy_troop.id not in troops_to_remove: # jeigu abudu kariai dar vis laisvi ir nebuvo nustatyti susinaikinti
                                troops_to_remove.append(troop.id)
                                troops_to_remove.append(closest_enemy_troop.id)
                    except ValueError: # iskyla tokia klaida jeigu min() funkcijoje irasomas tuscias masyvas (siuo atveju - jeigu nera paleista kitu kariu, tik maniskiai)
                        pass

            
            
            # trinu visus pazymetus troopsus (kitaip for loope negaliu istrinti nario, nes meta klaida "dictionary changed size during iteration")
            for t_id in troops_to_remove:
                try:
                    used_troop_ids.remove(t_id)
                    cities[troops[t_id].starting_location].originated_troop_ids.remove(t_id)
                    troops.pop(t_id)
                    server_sender.queue.append( (socks, f'DINGO KARYS={t_id}') )
                except Exception as e:
                    print(type(e), e)

        
        
        except RuntimeError:
            pass



# raketas judinu nuolatos! Jei atsiranda nauju, jos juda ten, kur turetu
def moving_missiles(game_code):
    # nurodau, kurio zaidimo informacija keisti ir tikrinti
    cities = gameplay[game_code][0]
    armoured_cities = gameplay[game_code][4]
    socks = gameplay[game_code][5]
    missiles = gameplay[game_code][6]
    used_missile_ids = gameplay[game_code][7]

    # judinu karius ir tikrinu, kada jau atejo iki miesto
    while game_code in gameplay.keys() and gameplay[game_code][3] == 'STILL NO WINNER':
        sleep(2/FPS)
        try:
            missiles_to_remove = []

            for m in missiles.values():
                m.move()

                # tikrinu susilietima
                if m.target_city.dist_to(m.x, m.y) <= m.target_city.r + m.imgs[0].get_height()/7:

                    # sunaikintas miestas
                    m.target_city.inhabitants = 0
                    if m.target_city.location in armoured_cities[m.target_city.owner]:
                        armoured_cities[m.target_city.owner].remove(m.target_city.location)
                    server_sender.queue.append( (socks, f'MIESTAS={m.target_city.location};{m.target_city.owner};{floor(m.target_city.inhabitants)}') ) # atnaujinu gyventojus
                    server_sender.queue.append( (socks, f'SUNAIKINTAS RAKETOS={m.target_city.location};{m.id}') ) # animacija

                    # zala aplinkiniams
                    affected = [c for c in cities.values() if m.target_city.dist_to(c.x, c.y) <= SPLASH_RADIUS and m.target_city.location != c.location] # visi paveikti miestai aplink
                    for c in affected:
                        c.inhabitants /= 2 # sumazeja perpus
                        server_sender.queue.append( (socks, f'MIESTAS={c.location};{c.owner};{floor(c.inhabitants)}') ) # atnaujinu gyventojus
                    
                    # salinu raketa
                    missiles_to_remove.append(m.id)



            # trinu pazymetas raketas (jos pasieke tiksla)
            for m_id in missiles_to_remove:
                try:
                    used_missile_ids.remove(m_id)
                    missiles.pop(m_id)
                except Exception as e:
                    print(type(e), e)

        except RuntimeError:
            pass





def check_for_winner(game_code):
    # nurodau, kurio zaidimo informacija keisti ir tikrinti
    cities = gameplay[game_code][0]
    troops = gameplay[game_code][1]
    socks = gameplay[game_code][5]

    while game_code in gameplay.keys() and gameplay[game_code][3] == 'STILL NO WINNER':
        sleep(1.23)

        # tikrinu ar visi troopsai priklauso vienam zaidejui
        diversity = False
        try:
            own = troops[list(troops)[0]].owner # pirmas sarase troopas
            for t in troops.values():
                if t.owner != own:
                    diversity = True
                    break
        except:
            pass


        if not diversity:
            ownership = {
                'NOBODY': 0,
            }
            ownership_t = {
                'NOBODY': 0,
            }

            # pridedu visas spalvas
            for color in color_options:
                ownership[color] = 0
                ownership_t[color] = 0

            # skaiciuoju
            for c in cities.values():
                ownership[c.owner] += 1
            for t in troops.values():
                ownership_t[t.owner] += 1

            # tikrinu
            for color in color_options:
                if ownership[color] == len(cities) - ownership['NOBODY'] and ownership_t[color] == len(troops) - ownership_t['NOBODY']:
                    gameplay[game_code][3] = color
                    break

    # pranesu
    server_sender.queue.append( (socks, f'LAIMEJO={gameplay[game_code][3]}') )

    # isvalau visus jau baigtus zaidimus
    gameplay.pop(game_code)








# zaidimo ciklas
def game(game_code):
    # nurodau, kurio zaidimo informacija keisti ir tikrinti
    cities = gameplay[game_code][0]
    troops = gameplay[game_code][1]
    socks = gameplay[game_code][5]
    missiles = gameplay[game_code][6]

    # atnaujinu visu neutraliu teritoriju pradine spalva
    for cc in cities.values():
        server_sender.queue.append( (socks, f'MIESTAS={cc.location};{cc.owner};{floor(cc.inhabitants)}') )

    # pradines teritorijos ir spalvos isrinkimas zaidejams
    color_options_copy = copy.deepcopy(color_options)
    city_options = [city_loc for city_loc, c in cities.items()]
    forbidden = []

    for s in socks:
        # spalvos isrinkimas zaidejui
        col = choice(color_options_copy)
        color_options_copy.remove(col)
        server_sender.queue.append( ((s,), f'SPALVA={col}') )

        # pradines teritorijos isrinkimas zaidejui
        city_loc = choice(city_options)
        while city_loc in forbidden:
            city_loc = choice(city_options)
        # surasau, kad zaidejai negaletu atsirasti prie pat viens kito
        forbidden.append(city_loc)
        for c in borders[city_loc].split(','):
            forbidden.append(c)
        # padarau realius pakeitimus pagal random isrinkima
        cities[city_loc].owner = col
        # istrinu jau uzimta miesta
        city_options.remove(city_loc)

        # pirmuju teritoriju issiuntimui
        server_sender.queue.append( (socks, f'MIESTAS={city_loc};{col};{floor(cities[city_loc].inhabitants)}') )
        server_sender.queue.append( (socks, f'NAUJA TERITORIJOS SPALVA={city_loc}') )



    # duomenu atnaujinimo loopas
    while game_code in gameplay.keys() and gameplay[game_code][3] == 'STILL NO WINNER':
        sleep(2/FPS) # siunciu dvigubai leciau nei zaidimas gali refreshinti - kitaip susidaro didele eile neissiustu kariu

        # siuncia informacija apie esamus troopus
        try:
            for troop in troops.values():
                server_sender.queue.append( (socks, f'KARYS={troop.id};{troop.starting_location};{troop.target_city.location};{troop.x};{troop.y}') )
        except RuntimeError:
            pass

        # siuncia informacija apie esamas raketas
        try:
            for missile in missiles.values():
                server_sender.queue.append( (socks, f'RAKETA={missile.id};{missile.x};{missile.y};{missile.angle}') )
        except RuntimeError:
            pass



def send_queue_info(queue, queue_i):
    # nusiunciu, kad visi zinotu, kas turi teise uzpildyti zaidima botais
    for i, s in enumerate(queues[queue][queue_i]):
        if s != 'rezervuota botui':
            server_sender.queue.append(((s,), f'INDEKSAS EILEJE={i}'))
    
    # suskaiciuoju, kiek prisijungusiu (ne rezervuotu vietu)
    joined = len(queues[queue][queue_i]) - queues[queue][queue_i].count('rezervuota botui')
    # nusiunciu, kiek jau prisijungusiu (i rezervuotas vietas nesiunciu, nes nera kur siusti)
    server_sender.queue.append(([ s for s in queues[queue][queue_i] if s != 'rezervuota botui' ], f'PRISIJUNGE={joined}/{queue}'))








def handle_queues(sock, queue, player_type):
    global gameplay, queues

    updated_queue_i = ''

    # tikrinu, ar zmogus, ar botas prisijunge
    if player_type == 'human':
        # ieskau, ar yra nepilnu eiliu (truksta zmogaus zaidejo)
        found = False
        for i, q in enumerate(queues[queue]):
            if len(q) < queue:
                queues[queue][i].append(sock) # pridedu nauja
                updated_queue_i = i
                found = True
                break
        # jeigu nerandu, sukuriu nauja eile
        if not found:
            queues[queue].append([sock,])
            updated_queue_i = len(queues[queue])-1 # paskutinis, nes ka tik sukuriau

    elif player_type == 'bot':
        # randu rezervuota vieta
        for i, q in enumerate(queues[queue]):
            if 'rezervuota botui' in q:
                # dedu i rezervuota
                queues[queue][i].remove('rezervuota botui')
                queues[queue][i].append(sock)
                updated_queue_i = i
                break

    
    # nusiunciu, kad zinotu, kas turi teise uzpildyti zaidima botais ir kiek zmoniu/botu siuo metu prisijungusiu laukia
    send_queue_info(queue, updated_queue_i)
    

    # tikrinu, ar jau galima pradeti zaidima is ka tik surinktu zaideju (t.y. ar uzpildytos visos vietos ir ar daugiau nelaukiama jokiu botu)
    if len(queues[queue][updated_queue_i]) == queue and 'rezervuota botui' not in queues[queue][updated_queue_i]:
        socks = queues[queue][updated_queue_i]
        queues[queue].pop(updated_queue_i) # pasalinu i zaidima dedamus zaidejus (dabar jie nebelaukia eileje)


        ### PRADEDU ZAIDIMA ###

        # sukuriu zaidimo erdve
        new_code = f'{choice(list(ascii_uppercase))}{choice(list(ascii_uppercase))}{choice(list(ascii_uppercase))}'
        while new_code in gameplay.keys():
            new_code = f'{choice(list(ascii_uppercase))}{choice(list(ascii_uppercase))}{choice(list(ascii_uppercase))}'
        # gameplay[new_code] = [cities, troops, used_troop_ids, winner, armoured_cities, socks, missiles, used_missile_ids]
        gameplay[new_code] = [copy.deepcopy(cities), {}, [], 'STILL NO WINNER', copy.deepcopy(armoured_cities), socks, {}, []]

        # paleidziu reikalingas funkcijas
        Thread(target=growing_cities, args=(new_code,), daemon=True).start()
        Thread(target=growing_capital, args=(new_code,), daemon=True).start()
        Thread(target=moving_missiles, args=(new_code,), daemon=True).start()
        Thread(target=mobilizing_troops, args=(new_code,), daemon=True).start()
        Thread(target=check_for_winner, args=(new_code,), daemon=True).start()
        Thread(target=game, args=(new_code,), daemon=True).start()



# pridedu raketa i zaidima po tam tikro laiko
def add_missile_after(game_code, missile, delay):
    missiles = gameplay[game_code][6]
    sleep(delay)
    missiles[missile.id] = missile


# gauta info is zaideju bet kurios zaidimo stadijos metu
def receiver(sock):
    global queues, gameplay
    player_has_lost_everything = False

    while 1:
        try:
            # gaunu zinute
            received = str(sock.recv(BUFFER).decode(FORMAT).strip())
            game_status, message = received.split('#')

            # atpazistu, koks zaidimo statusas pas ta zaideja ir atitinkamai darau ka reikia
            if game_status == 'ZAIDIMAS':
                # surandu, kuriame zaidime zaidejas zaidzia
                for code, g in gameplay.items():
                    if sock in g[5]:
                        game_code = code
                        break
                cities = gameplay[game_code][0]
                troops = gameplay[game_code][1]
                socks = gameplay[game_code][5]
                missiles = gameplay[game_code][6]
                used_missile_ids = gameplay[game_code][7]

                # zaidejas nori siusti karius
                if message.startswith('ATAKA='):
                    sel_city_loc, targ_city_loc, troop_count = message[6:].split(';')
                    troop_count, sel_city, targ_city = int(troop_count), cities[sel_city_loc], cities[targ_city_loc]

                    # taisau spraga, kad negaletu zaidejas belekiek siusti kariu
                    repeated_action = False
                    for t in troops.values():
                        if t.starting_location == sel_city_loc and t.target_city.location == targ_city_loc:
                            repeated_action = True
                            break

                    if not repeated_action:
                        # ispeju zaideja, i kurio miesta keliauja kariai
                        if sel_city.owner != targ_city.owner:
                            server_sender.queue.append( (socks, f'ISPEJIMAS={targ_city.owner}'))
                        # spawninu troopsus (idetas Thread'e tam, kad kol visi troopsai neisejo is miesto, galetu eiti kiti tos spalvos)
                        Thread(target=spawn_troops, args=(sel_city, targ_city, troop_count, game_code), daemon=True).start()
                
                elif message.startswith('NAUJA RAKETA='):
                    origin_city_loc, target_city_loc = message[13:].split(';')
                    # isrenka nauja id
                    new_id = randint(0, 1000)
                    while new_id in used_missile_ids:
                        new_id = randint(0, 1000)
                    used_missile_ids.append(new_id)

                    new_m = Missile(new_id, cities[origin_city_loc], cities[target_city_loc])

                    # ispejimas zaidejui, link kurio skrenda
                    alarm_length = new_m.d*3.3 / (new_m.v*FPS)
                    launch_delay = 2
                    server_sender.queue.append( (socks, f'SIRENA={origin_city_loc};{target_city_loc};{round(alarm_length)};{launch_delay};{new_id}') )

                    # po 3 sekundziu idedu i zaidima
                    Thread(target=add_missile_after, args=(game_code, new_m, launch_delay,), daemon=True).start()


                elif message == 'VISKAS PRARASTA':
                    player_has_lost_everything = True

                elif message.startswith('NICKAS=') or message.startswith('BOTAS='):
                    # persiunciu kitiems spalvos ir vardo sarysi
                    server_sender.queue.append( (socks, message) )

            



            elif game_status == 'MENIU':
                player_has_lost_everything = False # resetinu
                if message.startswith('NORIU ZAISTI='):
                    queue, player_type = message[13:].split(';')
                    handle_queues(sock, int(queue), player_type) # pradedu zaidima



            elif game_status == 'LAUKIMAS':
                if message == 'CANCEL':
                    # ismetu is laukianciuju eiles
                    for queue, q_shared in queues.items():
                        for i, q in enumerate(q_shared):
                            if sock in q:
                                queues[queue][i].remove(sock)
                                send_queue_info(queue, i)
                                break

                elif message.startswith('FILL WITH BOTS'):
                    # boto stiprumas turetu priklausyti intervalui (0; 1]
                    bot_strength = float(message.split(';')[1])
                    # issiaiskinu, kiek botu truksta ir atspawninu, kiek reikia
                    for players, q_shared in queues.items():
                        for q in q_shared:
                            if sock in q:
                                # paleidziu botu tiek, kiek reikia bei uzrezervuoju jiems vietas
                                bot_count = players - len(q)
                                for _ in range(bot_count):
                                    q.append('rezervuota botui')
                                    Process(target=start_bot, args=(players, determined_server_ip, bot_strength), daemon=False).start()
                                break
                
                elif message.startswith('BOT STRENGTH='):
                    for q_shared in queues.values():
                        for q in q_shared:
                            if sock in q:
                                # radau tinkama eile
                                server_sender.queue.append(([s for s in q if s != sock and type(s) != str], message))



            elif game_status == 'PABAIGA':
                pass




        # jeigu zaidejas netiketai uzdaro zaidimo langa
        except (ConnectionError, ValueError):
            # surandu, kuriame zaidime zaidejas zaidzia (jeigu toks zaidimas isvis egzistavo) ir ar tas zaidejas isejimo momentu turejo kokiu nors teritoriju
            for code, g in gameplay.items():
                if sock in g[5]:
                    if not player_has_lost_everything:
                        gameplay[code][3] = 'player left'
                    # issiunciu visiems zinute (bet sureaguoja tik botai), kad zmogus zaidejas paliko zaidima
                    server_sender.queue.append((socks, 'ZMOGUS UZDARE LANGA'))
                    return


            # ismetu is laukianciuju eiles (jeigu laukimo ekrane)
            for queue, q_shared in queues.items():
                for i, q in enumerate(q_shared):
                    if sock in q:
                        queues[queue][i].remove(sock)
                        send_queue_info(queue, i)
                        return
            return







if __name__ == '__main__':
    color_options = list(colors)

    IP = '0.0.0.0'
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((IP, PORT))
    server.listen()



    # # seku, kiek koks zaidejas turi patobulintu miestu
    armoured_cities = {
        'NOBODY': [],
    }
    for c in color_options:
        armoured_cities[c] = []


    # visu siuo metu vykstanciu zaidimu kontrole
    '''
    gameplay = {
        code: [cities, troops, used_troop_ids, winner, armoured_cities, socks],
        ...
    }
    '''
    gameplay = {}

    '''
    queues = {
        2: [[], [], ...], <-- viduje queues[n] listo yra atskiros eiles pvz. dvieju zaideju zaidimui
        3: [[], [], ...],
        4: [[], [], ...],
    }
    '''
    queues = {
        2: [],
        3: [],
        4: []
    }


    # pradedu
    Thread(target=server_sender.start_sending, args=(), daemon=True).start()
    try:
        determined_server_ip = socket.gethostbyname(socket.getfqdn())
        print(f'[{asctime()}] server up on address {determined_server_ip}')
    except Exception as err:
        print(f'[{asctime()}] server up, but failed to retrieve host address ({type(err)})')
        determined_server_ip = input(f'[{asctime()}] Enter address manually: ') # naudojamas tik tinkamai paleisti bota
    
    while 1:
        sock, addr = server.accept()
        Thread(target=receiver, args=(sock,), daemon=True).start()
