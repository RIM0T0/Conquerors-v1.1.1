# pirmoji 1.1 zaidimo boto versija (antroji is viso, skaiciuojant nuo zaidimo 1.0 versijos) - ne itin protingas
from objects import Troop
from threading import Thread
import client
from time import sleep
from random import random
from all_cities import cities, borders

actions_happening = []
GLOBAL_GROWING_RATE = 1


troops = {}



# mano informacija
my_color = ''




def receiver():
    global troops, cities, my_color

    while 1:
        try:
            # priima
            message = client.recv()

            # atskiriu zinutes pobudi ir koreguoju objektus
            if message.startswith('KARYS='):
                id, start_loc, targ_loc, x, y = message[6:].split(';')
                id, x, y = int(id), float(x), float(y)

                # koreguoju reikiama troopa. Jeigu nerandu, sukuriu nauja
                if id in troops.keys():
                    troops[id].x = x
                    troops[id].y = y
                else:
                    # sukuriu nauja troopa
                    if targ_loc in cities.keys():
                        new_troop = Troop(id, cities[start_loc], cities[targ_loc])
                    else:
                        new_troop = Troop(id, cities[start_loc], 'tarpinis miestas')
                    new_troop.x = x
                    new_troop.y = y
                    troops[id] = new_troop


            elif message.startswith('DINGO KARYS='):
                troops.pop(int(message[12:]))


            elif message.startswith('MIESTAS='):
                loc, owner, inhab = message[8:].split(';')
                inhab = int(inhab)

                # koreguoju
                cities[loc].owner = owner
                cities[loc].inhabitants = inhab


            elif message.startswith('PATOBULINTAS MIESTAS='):
                cities[message[21:]].armoured = True


            elif message.startswith('LAIMEJO='):
                client.game_status = 'PABAIGA'


            elif message.startswith('SPALVA='):
                # pridedu nauja is serverio info
                my_color = message[7:]
                client.game_status = 'ZAIDIMAS'

        except:
            pass


def cooldown():
    global actions_happening

    while True:
        sleep(1)

        # working cooldowning process
        for i in range(len(actions_happening)):
            actions_happening[i][1] -= 1

        # removing expired cooldowns
        for direction, secs_left in actions_happening:
            if secs_left <= 0:
                actions_happening.remove([direction, secs_left])





def start(players, server_ip):
    client.connect(server_ip)

    
    # pradedu funkcijas
    Thread(target=receiver, args=(), daemon=True).start()

    Thread(target=cooldown, args=(), daemon=True).start()





    # prisijungiu i zaidima, kuriame zmogus paprase boto
    client.send(f'NORIU ZAISTI={players};bot')
    # laukiu, kol receiver Thread'as gaus is serverio spalva
    while my_color == '':
        sleep(.05)





    # zaidimo loopas
    while client.game_status == 'ZAIDIMAS':
        sleep(random()+1)

        for c in cities.values():
            if c.owner == my_color:

                nearby_cities_locs = borders[c.location].split(',')
                for nearby_city_loc in nearby_cities_locs:
                    nearby_city = cities[nearby_city_loc]


                    # suskaiciuoju, kiek zaideju bus atvykus
                    if nearby_city.owner == my_color:
                        multiplier = 1
                    else:
                        multiplier = -1
                    inhabitants_when_arrives = multiplier*(nearby_city.inhabitants + (c.dist_to(nearby_city.x, nearby_city.y) / (80) + .1*c.inhabitants)*GLOBAL_GROWING_RATE) + c.inhabitants
                    

                    # skaiciuoju kiek ir kokiu aplinkiniu zonu bus
                    friendly_zones = 0
                    free_zones = 0
                    enemy_zones = 0
                    enemy_inhabs_total = 0
                    for cc in nearby_cities_locs:
                        if cities[cc].owner == my_color:
                            friendly_zones += 1
                        elif cities[cc].owner == 'NOBODY':
                            free_zones += 1
                        else:
                            enemy_zones += 1
                            enemy_inhabs_total += cities[cc].inhabitants




                    # sprendimai
                    unavailable = False
                    for direction, secs_left in actions_happening:
                        if direction.split('->')[0] == c.location or direction.split('->')[1] == c.location:
                            unavailable = True
                            break
                    
                    if not unavailable:
                        if nearby_city.owner == my_color:
                            if nearby_city.inhabitants < enemy_inhabs_total and inhabitants_when_arrives > enemy_inhabs_total:
                                client.send(f'ATAKA={c.location};{nearby_city_loc};{c.inhabitants}')
                                actions_happening.append( [f'{c.location}->{nearby_city_loc}', 5] )
                        elif nearby_city.owner != 'NOBODY': # priesas
                            if inhabitants_when_arrives >= 5:
                                client.send(f'ATAKA={c.location};{nearby_city_loc};{c.inhabitants}')
                                actions_happening.append( [f'{c.location}->{nearby_city_loc}', 5] )
                        elif nearby_city.owner == 'NOBODY':
                            if enemy_zones == 0 and inhabitants_when_arrives >= 5:
                                client.send(f'ATAKA={c.location};{nearby_city_loc};{c.inhabitants}')
                                actions_happening.append( [f'{c.location}->{nearby_city_loc}', 5] )

    client.disconnect()
