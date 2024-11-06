import easy_pygame as epg
from easy_pygame import UP, DOWN, LEFT, RIGHT, BORDER
import pygame


SCREEN_HEIGHT = 600
SCREEN_WIDTH = 800
RIGHT = False
LEFT = True

STAY = 0
GO = 1
JUMP = 2
ATTACK = 3
HITTED = 4
DEAD = 5

class Fighter(epg.Sprite):
    def __init__(self, animation_pathes, x_pos, y_pos, flip, wigth, height, ground_level, gravity, id, img=epg.GREEN, show=True):
        pos = (x_pos, y_pos)
        super().__init__(img=animation_pathes[0], pos=pos, w=wigth, h=height, savescale=False, show=show)
        self.gravity = gravity
        self.fall_speed = 0
        self.ground_level = ground_level
        self.skins_dir = False
        self.knife = None
        self.direction = flip
        self.enemy = None
        self.id = id
        health_bar_width = epg.WIDTH / 4 - 20
        health_bar_x = int(x_pos - health_bar_width / 2)
        self.health_bar = HealthBar(id=self.id, health=100, pos=(health_bar_x, 10), width=health_bar_width)
        self.speed = 10
        self.skin_index = 0
        self.animation_list = []
        for img_path in animation_pathes:
            self.animation_list.append(self.load_img(img=img_path, colorkey=(43, 205, 27)))
        self.stay()
        self.actions = (self.stay,
                        self.go,
                        self.jump,
                        self.attack,
                        self.hitted,
                        self.dead
                       )
        # 0 = stay, 1 = go, 2 = jump, 3 = attack, 4 = hitted, 5 = dead

    def check_options(self, ):
        options = {'move' : 0,
                   'direction' : self.skins_dir,
                   'jump' : False,
                   'hit' : False,
                    }
                    
        keystate = pygame.key.get_pressed()
                    
        if keystate[pygame.K_a]:
            options['direction'] = LEFT
            options['move'] = -self.speed
        if keystate[pygame.K_d]:
            options['direction'] = RIGHT
            options['move'] = self.speed
        if keystate[pygame.K_SPACE]:
            options['jump'] = True
        if keystate[pygame.K_e]:
            options['hit'] = True
#        print(options)
        return options

        
    def update_health(self, health):
        self.health_bar.set_value(self.health_bar.value + health)    
        
    def stay(self,):
        self.set_skin(STAY)
        
    def go(self,):
        self.set_skin(GO)
        
    def jump(self,):
        self.set_skin(JUMP)
        
    def attack(self, ):
        self.set_skin(ATTACK)
        
    def hitted(self,):
        self.set_skin(HITTED)
    
    def dead(self,):
        self.set_skin(DEAD)
    
    def apply_game_state(self, state):
        x_pos, y_pos, health, action, self.direction, hide = state
        self.move_to((x_pos, y_pos))
        self.health_bar.set_value(health)
        self.actions[action]()
        if hide:
            self.hide()
        else:
            self.show()
    
    def set_skin(self, skin_index):
        if self.skins_dir != self.direction:
            for index, skin in enumerate(self.animation_list):
                self.animation_list[index] = pygame.transform.flip(skin, flip_x=True, flip_y=False)             #TODO посмотреть как работает flip и доделать разворот картинки
            self.skins_dir = self.direction
        self.image = self.orig_image = self.animation_list[skin_index]
        self.skin_index = skin_index


class HealthBar(epg.Label):
    HEIGHT = 40
    def __init__(self, id, pos, width, health=100):
        self.width = width
        x, y = pos
        super().__init__(text=id, x=x, y=y, val=health)
        
    
    def _get_surf(self, ):
        raito = self.width/100
        surface = pygame.Surface((self.width+4, self.HEIGHT+4))
        pygame.draw.rect(surface, epg.BLACK, (0, 0, self.width, self.HEIGHT))
        pygame.draw.rect(surface, epg.RED, (2, 2, self.width, self.HEIGHT))
        pygame.draw.rect(surface, epg.YELLOW, (2, 2, self.value * raito, self.HEIGHT))
        return surface
    
