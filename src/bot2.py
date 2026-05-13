# protingas botas!
from objects import Troop
from threading import Thread
import client
from time import sleep
from random import random
from all_cities import cities, borders
from common import DIAGONAL, colors, MISSILE_PRICE, MISSILE_RADIUS, SPLASH_RADIUS, nuclear_cities, default_bot_strength

actions_happening = []
human_player_cols = []
probability = default_bot_strength # numatytoji reiksme

troops = {}



# boto informacija
my_color = ''
my_gold = 0




def receiver():
    global troops, cities, my_color, my_gold, human_player_cols

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

            elif message.startswith('PRIDETI AUKSO='): # aukso pridejimas
                col, addition = message[14:].split(';')
                if col == my_color:
                    my_gold += int(addition)


            elif message.startswith('PATOBULINTAS MIESTAS='):
                cities[message[21:]].armoured = True


            elif message.startswith('LAIMEJO='):
                client.game_status = 'PABAIGA'


            elif message.startswith('SPALVA='):
                # pridedu nauja is serverio info
                my_color = message[7:]
                client.game_status = 'ZAIDIMAS'
                # nusiunciu serveriui info, jog tokios spalvos yra botas
                client.send(f'BOTAS={my_color}')

            elif message.startswith('NICKAS='):
                # seku, kada nebelieka zmoniu valdomu zaideju
                p_col = message[7:].split(';')[0]
                human_player_cols.append(p_col)

            elif message == 'ZMOGUS UZDARE LANGA':
                # tikrinu, ar tik botai beliko zaidime. Jeigu taip - botas iseina
                distinct_colors = {col: [c.owner for c in cities.values()].count(col) for col in colors}
                if max( [distinct_colors[p_col] for p_col in human_player_cols] ) == 0:
                    client.game_status = 'no humans left'


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
        for direction, secs_left, action in actions_happening:
            if secs_left <= 0:
                actions_happening.remove([direction, secs_left, action])



def is_available(l, action, dir):
    for from_loc, to_loc in [x[0].split('->') for x in [a for a in actions_happening if a[2] == action]]:
        if (dir == 'from' and l == from_loc) or (dir == 'to' and l == to_loc):
            return False
    return True


# BANDZIAU PADARYTI KITOKI NEI ATSTUMO TARP MIESTU MATAVIMO BUDA EFEKTYVIAU PERMESTI KARIUS I FRONTA
# path = ''
# def check_surroundings(loc, iteration, prev_locs):
#     global path
#     print(f'checking {loc} {iteration} {len(prev_locs)}')
#     surrounding = [cities[l] for l in borders[loc].split(',')]
#     my_surrounding = [c for c in surrounding if c.owner == my_color and c.location not in prev_locs] # kad negrizciau atgal ieskodamas
#     enemy_surrounding = [c for c in surrounding if c.owner not in (my_color, 'NOBODY')]

#     if iteration < 10:
#         if len(enemy_surrounding) == 0:
#             # paleidziu sekancia iteracija
#             for c in my_surrounding:
#                 updated_prev_locs = prev_locs
#                 updated_prev_locs.append(loc)
#                 check_surroundings(c.location, iteration+1, updated_prev_locs)
#                 if path != '':
#                     break
#         elif len(enemy_surrounding) > 0:
#             # updatinu
#             path = '->' + enemy_surrounding[0].location + path

# # randa marsruta iki kurios nors prieso teritorijos
# def path_to_enemy(loc):
#     global path
#     path = ''
#     print('pradedu')
#     check_surroundings(loc, 1, [])
#     print('\n\n\n')
#     return path



def do_i_have_nuclear_launch_site():
    for key in nuclear_cities.keys():
        if cities[key].owner == my_color:
            return True
    return False

def average_territory_pos(all_territories):
    # suskaiciuoju vidutines abieju asiu visu priesininko miestu koordinates
    if len(all_territories) == 0:
        return False, -1, -1 # praleisti kariu stumima
    avg_x = sum([t.x for t in all_territories.values()]) / len(all_territories)
    avg_y = sum([t.y for t in all_territories.values()]) / len(all_territories)

    max_inhabs = max(all_territories.values(), key=lambda x:x.inhabitants).inhabitants
    k = .5
    # koreguoju vidutines koordinates pagal miestuose esancius troopus
    for t in all_territories.values():
        if t.x < avg_x:
            avg_x -= t.inhabitants/max_inhabs*t.dist_to(avg_x, avg_y)*k
        elif t.x > avg_x:
            avg_x += t.inhabitants/max_inhabs*t.dist_to(avg_x, avg_y)*k
        if t.y < avg_y:
            avg_y -= t.inhabitants/max_inhabs*t.dist_to(avg_x, avg_y)*k
        elif t.y > avg_y:
            avg_y += t.inhabitants/max_inhabs*t.dist_to(avg_x, avg_y)*k
    
    return True, avg_x, avg_y


def push_to_front():
    global actions_happening
    while 1:
        sleep(5+random())

        # ar botas turi bent viena raketu paleidimo aikstele
        if not do_i_have_nuclear_launch_site():
            # randu artimiausia aikstele ir pasiimu

            # mano teritoriju vidutine koordinate
            all_territories = {loc: city for loc, city in cities.items() if city.owner == my_color}
            push, avg_x, avg_y = average_territory_pos(all_territories)

            # artimiausia aikstele
            closest_nucl_site = min([cities[loc] for loc in nuclear_cities.keys()], key=lambda x:x.dist_to(avg_x, avg_y))
            avg_x, avg_y = closest_nucl_site.x, closest_nucl_site.y
        else:
            # surandu pranasiausio priesininko teritoriju geografini centra

            # surandu visu priesininku visas teritorijas
            enemies = {}
            for enemy_col in [c for c in colors.keys() if c != my_color]:
                enemy_cities = {loc: city for loc, city in cities.items() if city.owner == enemy_col}
                enemies[enemy_col] = enemy_cities
            # atrenku daugiausia teritoriju turincio zaidejo teritorijas
            all_territories = max(enemies.values(), key=lambda x:len(x.values()))
            push, avg_x, avg_y = average_territory_pos(all_territories)


        # stumiu visus karius link ten
        if push:
            my_cities = {loc: city for loc, city in cities.items() if city.owner == my_color}
            for loc, city in my_cities.items():
                try:
                    # randu arciau tikslo esancia besilieciancia teritorija
                    closest = min([cities[l] for l in borders[loc].split(',') if cities[l].owner == my_color], key=lambda x:x.dist_to(avg_x, avg_y))
                    if closest.dist_to(avg_x, avg_y) < city.dist_to(avg_x, avg_y) and is_available(loc, 'kariu siuntimas', 'from') and is_available(loc, 'kariu siuntimas', 'to') and is_available(closest.location, 'kariu siuntimas', 'from'):
                        # perstumiu
                        # laiko cooldown neskaiciuoju tam, kad visus visus karius galetu siusti toliau
                        if random() <= probability:
                            client.send(f'ATAKA={loc};{closest.location};{city.inhabitants}')

                except ValueError: # empty list in function min()
                    pass



def start(players, server_ip, strength):
    global my_gold, probability
    
    # nustatomas boto stiprumas pagal kliento nora. Jeigu pateikiama netinkama reiksme, paliekama numatytoji.
    if 0 < strength <= 1:
        probability = strength
    else:
        print(f'Wrong bot strength value ({strength}), using default ({probability})')

    client.connect(server_ip)

    
    # pradedu funkcijas
    Thread(target=receiver, args=(), daemon=True).start()
    Thread(target=cooldown, args=(), daemon=True).start()





    # prisijungiu i zaidima, kuriame zmogus paprase boto
    client.send(f'NORIU ZAISTI={players};bot')
    # laukiu, kol receiver Thread'as gaus is serverio spalva
    while my_color == '':
        sleep(.05)




    # laikas nuo laiko pastumiu visus karius fronto linijos link
    Thread(target=push_to_front, args=(), daemon=True).start()
    # zaidimo loopas
    while client.game_status == 'ZAIDIMAS':
        sleep(random())

        bigger_goals = {
            'upgrading cities': [], # liste yra imanomi veiksmai bei taskais ivertintas sprendimo gerumas, pvz. [['azerbaidzanas->rusija,estija->rusija', 100], [], ...]
            'mass attacks': [],
            'missile launch': []
        }

        my_cities = {loc: city for loc, city in cities.items() if city.owner == my_color}
        bordering_enemy_cities = {loc: city for loc, city in cities.items() if city.owner != my_color and my_color in [cities[l].owner for l in borders[loc].split(',')]}
        
        # upgrading cities
        for loc, city in my_cities.items():
            if not city.armoured:
                my_troops_around = sum([cities[l].inhabitants for l in borders[loc].split(',') if cities[l].owner == my_color and is_available(l, 'kariu siuntimas', 'from') and is_available(loc, 'kariu siuntimas', 'from')])
                enemies_around = sum([cities[l].inhabitants for l in borders[loc].split(',') if cities[l].owner not in (my_color, 'NOBODY')])
                
                if enemies_around == 0:
                    if my_troops_around+city.inhabitants >= 300:
                        my_cities_of_action = [cities[l] for l in borders[loc].split(',') if cities[l].owner == my_color and is_available(l, 'kariu siuntimas', 'from') and is_available(loc, 'kariu siuntimas', 'from')]
                        action_str = ','.join([f'{x.location}->{loc}' for x in my_cities_of_action])
                        bigger_goals['upgrading cities'].append( (action_str, city.inhabitants) )
        
        # mass attacks
        for loc, city in bordering_enemy_cities.items():
            my_troops_around = sum([cities[l].inhabitants for l in borders[loc].split(',') if cities[l].owner == my_color and is_available(l, 'kariu siuntimas', 'from') and is_available(loc, 'kariu siuntimas', 'from')])
            enemies_around = sum([cities[l].inhabitants for l in borders[loc].split(',') if cities[l].owner not in (my_color, 'NOBODY')])
            
            if my_troops_around >= city.inhabitants*1.1 and my_troops_around - city.inhabitants > enemies_around: # jeigu gyventoju skaicius puolama miesta virsija dvigubai ir priesas negales perimti teritorijos
                my_cities_of_action = [cities[l] for l in borders[loc].split(',') if cities[l].owner == my_color and is_available(l, 'kariu siuntimas', 'from') and is_available(loc, 'kariu siuntimas', 'from')]
                action_str = ','.join([f'{x.location}->{loc}' for x in my_cities_of_action])
                bigger_goals['mass attacks'].append( (action_str, my_troops_around - city.inhabitants - enemies_around) )

        # missile launch
        if my_gold >= MISSILE_PRICE:
            my_nuclear_cities = [cities[loc] for loc in nuclear_cities.keys() if cities[loc].owner == my_color]
            for nuclear_city in my_nuclear_cities:
                reachable_enemy_cities = [city for city in cities.values() if city.owner not in (my_color, 'NOBODY') and city.dist_to(nuclear_city.x, nuclear_city.y) <= MISSILE_RADIUS]
                for reachable_city in reachable_enemy_cities:
                    reachable_city_affected_cities = [ c for c in cities.values() if c.dist_to(reachable_city.x, reachable_city.y) <= SPLASH_RADIUS ]
                    my_people = sum( [c.inhabitants for c in reachable_city_affected_cities if c.owner == my_color] )
                    all_people = sum( [c.inhabitants for c in reachable_city_affected_cities] )
                    enemy_people = all_people - my_people

                    if ((my_people*3 < enemy_people+reachable_city.inhabitants and reachable_city.inhabitants >= 100) or reachable_city.armoured) and is_available(f'{reachable_city.location}', 'raketos paleidimas', 'to'): # kad neprarasciau didelio kiekio gyventoju
                        score = (enemy_people/2 + reachable_city.inhabitants) + (100 * reachable_city.dist_to(nuclear_city.x, nuclear_city.y) / DIAGONAL) # iskaiciuoju ir miestu tarpusavio atstuma
                        score *= 3 if reachable_city.armoured else 1 # jei patobulintas prieso miestas, score padidinti 3x
                        bigger_goals['missile launch'].append( (f'{nuclear_city.location}->{reachable_city.location}', score) )


        # randu geriausius kiekvienos strategijos variantus
        best_goal_options = {}
        for goal, option in bigger_goals.items():
            if len(option) != 0:
                best_goal_options[goal] = max(option, key=lambda x: x[1])

        missile_launch = False
        # issirenku strategija
        if 'mass attacks' in best_goal_options.keys():
            best_actions = best_goal_options['mass attacks'][0].split(',')
        elif 'upgrading cities' in best_goal_options.keys():
            best_actions = best_goal_options['upgrading cities'][0].split(',')
        elif 'missile launch' in best_goal_options.keys():
            missile_launch = True
            best_actions = best_goal_options['missile launch'][0].split('->')
        else:
            best_actions = []



        # atlieku veiksmus
        if random() <= probability:
            if missile_launch:
                start_loc, targ_loc = best_actions
                client.send(f'NAUJA RAKETA={start_loc};{targ_loc}')
                flight_time = cities[start_loc].dist_to( cities[targ_loc].x, cities[targ_loc].y ) * 3.3 / 140 + 2 # skaiciuojama sekundemis. Paimta is serverio skaiciavimu sirenos trukmei
                actions_happening.append( ['->'.join(best_actions), flight_time, 'raketos paleidimas'] )
                my_gold -= MISSILE_PRICE
            else:
                for a in best_actions:
                    start_loc, targ_loc = a.split('->')
                    client.send(f'ATAKA={start_loc};{targ_loc};{cities[start_loc].inhabitants}')
                    actions_happening.append( [a, cities[start_loc].inhabitants*.1, 'kariu siuntimas'] ) # per tiek laiko bus issiusti visi kariai is teritorijos


    client.disconnect()
