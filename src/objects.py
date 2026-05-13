import os
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = 'hide'
from math import floor, sqrt, atan, sin, cos, pi
from random import random
import pygame
from common import WIDTH, HEIGHT, colors, sound_click, FPS, nuclear_cities, nuclear_city_exception_routes

explosion_final_stage = 13
cracks_imgs = [pygame.transform.scale(pygame.transform.scale(pygame.image.load(f'img/game/cracks/{i}.png'), (20, 20)), (20+i/explosion_final_stage*10, 20+i/explosion_final_stage*10)) for i in range(1, explosion_final_stage+1)]
explosion_imgs = [pygame.transform.scale(pygame.transform.scale(pygame.image.load(f'img/game/explosion/{i}.png'), (20, 20)), (80, 80)) for i in range(1, explosion_final_stage+1)]
class Explosion:
    def __init__(self, city, affected_cities):
        self.stage = 1 # 1 is 13
        self.final_stage = explosion_final_stage
        self.city = city
        self.affected_cities = affected_cities
    def draw(self, surf):
        stage = self.final_stage if self.stage >= self.final_stage+1 else self.stage
        # aplinkiniu miestu zemes drebejimas
        for city in self.affected_cities:
            pygame.draw.circle(surf, (60, 60, 60), (city.x, city.y), 10+stage/self.final_stage*5)
            img = cracks_imgs[floor(stage)-1]
            surf.blit(img, (city.x-img.get_width()/2, city.y-img.get_height()/2))
        # sprogimas, kur nukrito raketa
        pygame.draw.circle(surf, (30, 30, 30), (self.city.x, self.city.y), 20+stage/self.final_stage*10)
        img = explosion_imgs[floor(stage)-1]
        surf.blit(img, (self.city.x-img.get_width()/2, self.city.y-img.get_height()+5))
        


class City:
    def __init__(self, location, x, y):
        self.location = location
        self.x = x
        self.y = y
        self.r = 14
        self.normal_r = self.r
        self.owner = 'NOBODY'
        self.inhabitants = 15
        self.city_col = 255 - self.inhabitants/100 * 255
        self.text_col = 0
        self.armoured = False
        self.originated_troop_ids = []
    def init_font_image(self, font_size=14): # atskirai inicijuoju, nes pvz. botams ir serveriui grafines sasajos nereikia
        self.font = pygame.font.SysFont('consolas', font_size, bold=True)
    def draw_armour(self, main_surface):
        # sarvuotas miestas
        pygame.draw.circle(main_surface, (255, 213, 0), (self.x, self.y), self.r+3, 0)
        pygame.draw.circle(main_surface, (0 ,0, 0), (self.x, self.y), self.r+3, 1)
    def draw_city(self, main_surface):
        # piesti miesto sarva
        if self.armoured:
            self.draw_armour(main_surface)
        # miestas-tvirtove
        if (0 <= self.city_col <= 255):
            pygame.draw.circle(main_surface, (self.city_col, self.city_col, self.city_col), (self.x, self.y), self.r, 0)
            pygame.draw.circle(main_surface, (0, 0, 0), (self.x, self.y), self.r, 1)
        # gyventojai
        text = self.font.render(str(floor(self.inhabitants)), 1, (self.text_col, self.text_col, self.text_col))
        main_surface.blit(text, (self.x - text.get_width()/2, self.y - text.get_height()/2))
    def dist_to(self, x2, y2):
        return sqrt( pow(self.x-x2, 2) + pow(self.y-y2, 2) )
    def get_surface(self):
        return pygame.transform.scale( pygame.image.load(f'maps/{self.location}/{self.owner}.png'), (WIDTH, HEIGHT) )




class Troop:
    def __init__(self, id, city_of_origin, target_city, window=''):
        self.x = city_of_origin.x
        self.y = city_of_origin.y
        self.owner = city_of_origin.owner
        self.color = colors[self.owner]
        self.target_city = target_city
        self.final_target_city = '' # tarpiniams miestams
        self.starting_location = city_of_origin.location
        self.id = id
        
        self.r = 7.5
        self.vel = 160
        self.improviser_counter = 0

        self.x_vel_per_sec = 0
        self.y_vel_per_sec = 0

        self.win = window

    def draw(self, main_surface):
        pygame.draw.circle(main_surface, self.color, (self.x, self.y), self.r, 0)
        pygame.draw.circle(main_surface, (0,0,0), (self.x, self.y), self.r, 1)
    def dist_to(self, x2, y2):
        return sqrt( pow(self.x-x2, 2) + pow(self.y-y2, 2) )
    def improvise(self):
        # reciau atnaujinu kryptis
        self.improviser_counter += 1
        if not self.improviser_counter == 5:
            return
        self.improviser_counter = 0


        # angle
        if self.target_city.x-self.x != 0:
            angle = atan(abs((self.target_city.y-self.y)/(self.target_city.x-self.x)))
        else:
            angle = pi/2


        # deviate the angle
        deviation = 30 # laipsniais i viena puse
        angle += (-deviation + random()*2*deviation) * pi/180
        
        self.y_vel_per_sec = self.vel * sin(angle)
        self.x_vel_per_sec = self.vel * cos(angle)

        if self.target_city.x < self.x:
            self.x_vel_per_sec = -self.x_vel_per_sec
        if self.target_city.y < self.y:
            self.y_vel_per_sec = -self.y_vel_per_sec



LAUNCH_SITE_SCALE = 2.66
fast_missile_imgs = [pygame.transform.scale(pygame.image.load(f'img/game/missile/missile_fast{i}.png'), (10*LAUNCH_SITE_SCALE, 48*LAUNCH_SITE_SCALE)) for i in range(1, 2+1)]
slow_missile_imgs = [pygame.transform.scale(pygame.image.load(f'img/game/missile/missile_slow{i}.png'), (10*LAUNCH_SITE_SCALE, 48*LAUNCH_SITE_SCALE)) for i in range(1, 2+1)]
class Missile:
    def __init__(self, id, city_of_origin='', target_city=''):
        self.imgs = slow_missile_imgs
        self.id = id
        self.city_of_origin = city_of_origin
        self.target_city = target_city
        self.angle = pi/2
        if city_of_origin != '' and target_city != '':
            self.x, self.y = nuclear_cities[city_of_origin.location]
            self.y -= 23*LAUNCH_SITE_SCALE
            self.v = 70*2/FPS # greitis pikseliais (pvz.: 140/FPS = 70px/s)
            self.d = sqrt((self.x - self.target_city.x)**2 + (self.y - self.target_city.y)**2) # tiesus atstumas iki taikinio
            self.angle_dev = 90*pi/180
            self.dev_v = self.angle_dev / (self.d*1.5 / self.v)
            self.k = 1 if self.x < self.target_city.x else -1 # naudoju nustatyti, i kuria puse lenksis trajektorija
            #self.k = -self.k if (f'{city_of_origin.location}--{target_city.location}' in nuclear_city_exception_routes or f'{target_city.location}--{city_of_origin.location}' in nuclear_city_exception_routes) else self.k
            self.starting_angle_settled = False
        else:
            self.x, self.y = 0, 0 # siuos dydzius klientas is karto perraso
            self.img_n = 0
    def draw(self, surf):
        rotated = pygame.transform.rotate(self.imgs[floor(self.img_n)], self.angle*180/pi - 90)
        surf.blit(rotated, rotated.get_rect(center=(self.x, self.y)))
        if self.img_n + 8/FPS < 2:
            self.img_n += 8/FPS
        else:
            self.img_n = 0
    def change_to_fast(self):
        self.imgs = fast_missile_imgs

    def calc_angle(self):
        dx = abs(self.x - self.target_city.x)
        dy = abs(self.y - self.target_city.y)
        if dx != 0:
            return atan(dy/dx)
        else:
            if self.y > self.target_city.y:
                return pi/2
            else:
                return 3/2*pi
    def move(self):
        # kampai
        direct_angle = self.calc_angle()
        if self.angle_dev - self.dev_v >= 0:
            self.angle_dev -= self.dev_v

        # judejimas
        if self.x <= self.target_city.x and self.y >= self.target_city.y: # i desine ir virsu
            needed_angle = direct_angle + self.k*self.angle_dev
        elif self.x <= self.target_city.x and self.y <= self.target_city.y: # i desine ir apacia
            needed_angle = -direct_angle + self.k*self.angle_dev
        elif self.x >= self.target_city.x and self.y >= self.target_city.y: # i kaire ir virsu
            needed_angle = pi-direct_angle + self.k*self.angle_dev
        elif self.x >= self.target_city.x and self.y <= self.target_city.y: # i kaire ir apacia
            needed_angle = pi+direct_angle + self.k*self.angle_dev
        
        # letas pasisukimas reikiama kryptimi pradzioje judejimo
        if not self.starting_angle_settled:
            if needed_angle < 0:
                needed_angle += 2*pi
            elif needed_angle > 2*pi:
                needed_angle -= 2*pi
            if self.angle < 0:
                self.angle += 2*pi
            elif self.angle > 2*pi:
                self.angle -= 2*pi
            if abs(self.angle-needed_angle) > pi/30:
                if 0 < needed_angle - self.angle <= pi:
                    self.angle += pi/(FPS/2)
                elif 0 < self.angle - needed_angle <= pi:
                    self.angle -= pi/(FPS/2)
                return
            else:
                self.starting_angle_settled = True

        # veiksmas
        self.angle = needed_angle
        self.x += self.v*cos(self.angle)
        self.y -= self.v*sin(self.angle)


# raketu paleidimo aiksteles
launch_site_imgs = [pygame.transform.scale( pygame.image.load(f'img/game/launch/{i}.png'), (12*LAUNCH_SITE_SCALE, 48*LAUNCH_SITE_SCALE) ) for i in range(1, 59+1)] # uzkrauna is karto
class LaunchSite:
    def __init__(self, coords):
        self.final_stage = 59
        self.stage = 1
        self.x, self.y = coords
    def draw(self, surf):
        img = launch_site_imgs[self.stage-1]
        surf.blit(img, (self.x-img.get_width()/2, self.y-img.get_height()+4*LAUNCH_SITE_SCALE))




# mygtuku spalvos
but_col = {
    'white': (153, 153, 153),
    'cyan': (0, 153, 153),
    'black': (0, 0, 0),
    'green': (0, 150, 0),
    'red': (150, 0, 0),
    'blue': (0, 0, 150),
    'yellow': (150, 150, 0),
    'player left': (0, 0, 0)
}

class Text:
    def __init__(self, text, font_size, col1, col2, center_x, center_y):
        self.col1 = col1
        self.col2 = col2
        self.text = text
        self.font = pygame.font.SysFont('consolas', font_size)
        self.text_obj = self.font.render(self.text, 1, but_col[self.col1], but_col[self.col2] if self.col2 != None else None)
        self.center_x = center_x
        self.center_y = center_y
        self.x = center_x - self.text_obj.get_width()/2
        self.y = center_y - self.text_obj.get_height()/2
        self.greyed_out = False
    def blit(self, surf):
        self.text_obj.set_alpha(127 if self.greyed_out else 255)
        surf.blit(self.text_obj, (self.x, self.y))
    def update_text(self, new_text):
        self.text = new_text
        self.text_obj = self.font.render(self.text, 1, but_col[self.col1], but_col[self.col2] if self.col2 != None else None)
        self.x = self.center_x - self.text_obj.get_width()/2
        self.y = self.center_y - self.text_obj.get_height()/2


class Button:
    def __init__(self, screen, text, font_size, col1, col2, center_x, center_y):
        self.screen = screen
        self.text = text
        self.font = pygame.font.SysFont('consolas', font_size)
        self.col1 = col1
        self.col2 = col2
        self.center_x = center_x
        self.center_y = center_y
        self.text_obj = self.font.render(self.text, 1, but_col[self.col1], but_col[self.col2])
        if self.center_x == 'center':
            self.x = self.screen.get_width()/2 - self.text_obj.get_width()/2
        elif self.center_x == 'left':
            self.x = 5
        elif self.center_x == 'right':
            self.x = self.screen.get_width() - self.text_obj.get_width() - 5
        else:
            self.x = self.center_x - self.text_obj.get_width()/2
        self.y = self.center_y - self.text_obj.get_height()/2
        self.clickable = True
    def blit(self, surf):
        surf.blit(self.text_obj, (self.x, self.y))
    def is_pressed(self, pressed):
        if self.clickable:
            mouse_x, mouse_y = pygame.mouse.get_pos()
            if mouse_x in range(round(self.x), round(self.x+self.text_obj.get_width())) and mouse_y in range(round(self.y), round(self.y+self.text_obj.get_height())):
                self.text_obj = self.font.render(self.text, 1, but_col[self.col2], but_col[self.col1])
                if pressed:
                    sound_click.play()
                    return True
            else:
                self.text_obj = self.font.render(self.text, 1, but_col[self.col1], but_col[self.col2])
        else:
            self.text_obj.set_alpha(127) # atrodo tarsi disabled mygtukas
        return False



class FlagButton:
    def __init__(self, screen, img_path, i): # i = kiek i apacia pasislinkes mygtukas
        self.screen = screen
        self.img_path = img_path
        self.lang = self.img_path.split('/')[-1].split('.')[0]
        self.img_obj = pygame.transform.scale(pygame.image.load(self.img_path), (64, 64))
        self.sel_icon = pygame.transform.scale(pygame.image.load('img/menu/right-arrow.png'), (52, 52))
        self.x = self.screen.get_width() - self.img_obj.get_width() - 10
        self.y = 5 + i * (self.img_obj.get_height() - 10)
        self.selected = False
    def blit(self, surf):
        surf.blit(self.img_obj, (self.x, self.y))
        if self.selected:
            surf.blit(self.sel_icon, (self.x - self.sel_icon.get_width() - 2, self.y + (self.img_obj.get_height()-self.sel_icon.get_height()) / 2))
    def is_pressed(self, pressed):
        mouse_x, mouse_y = pygame.mouse.get_pos()
        if mouse_x in range(round(self.x), round(self.x+self.img_obj.get_width())) and mouse_y in range(round(self.y), round(self.y+self.img_obj.get_height())):
            if pressed:
                self.selected = True
                sound_click.play()
                return True
        return False
