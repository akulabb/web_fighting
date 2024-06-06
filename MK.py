import easy_pygame as epg
from easy_pygame import UP, DOWN, LEFT, RIGHT
import pygame as pg
from fighter import Fighter
import connection
import os
import time
import threading

epg.AUTO_UPDATE = False
SCREEN_HEIGHT = epg.HEIGHT = 600
SCREEN_WIDTH = epg.WIDTH = 800
FPS = 30
BALL_IMAGE_PATH = 'photos/ball.png'
EARTH_IMAGE_PATH = 'photos/earth.png'
BACK_IMAGE_PATH = 'photos/back.png'

HEIGHT_HALF = int(SCREEN_HEIGHT/2)
WIDTH_HALF = int(SCREEN_WIDTH/2)
epg.AUTO_UPDATE = False

GRAVITY = 2
#EARTH = 716

PROJECT_DIR = os.getcwd()
FIGHTER_IMAGE_PATHES = (os.path.join(PROJECT_DIR, 'photos\\stay.png'),
                        os.path.join(PROJECT_DIR, 'photos\\go.png'),
                        os.path.join(PROJECT_DIR, 'photos\\jump.png'),
                        os.path.join(PROJECT_DIR, 'photos\\attack.png'),
                        os.path.join(PROJECT_DIR, 'photos\\hitted.png'),
                        os.path.join(PROJECT_DIR, 'photos\\dead.png'),
                        )

BUTTON_RELEASED_IMAGE_PATH = 'photos/released.jpeg'
BUTTON_PRESSED_IMAGE_PATH = 'photos/pressed.jpeg'
BUTTON_DISABLED_IMAGE_PATH = 'photos/disabled.jpeg'

SERVER = 'localhost'
PORT = 5555


class Menu():
    def __init__(self, screen,
                 menu_background_img_path, 
                 button_titles, 
                 button_img_paths, 
                 button_size, 
                 button_order='v', 
                 button_margin=100,
                ):
        self.background_path = menu_background_img_path
        self.screen = screen
        if button_order == 'v':
            button_x = int(SCREEN_WIDTH / 2)
            button_y = button_margin + int(button_size[1] / 2)
        else:
            button_x = button_margin + int(button_size[0] / 2)
            button_y = int(SCREEN_HEIGHT / 2)
        self.buttons = []
        for title in button_titles:
            button_pos = (button_x, button_y)
            self.buttons.append(Button(button_img_paths, 
                                       title,
                                       button_pos,
                                       w=button_size[0],
                                       h=button_size[1],
                                       ))
            if button_order == 'v':
                button_y += button_size[1] + button_margin
            else:
                button_x += button_size[0] + button_margin
                
    def get_choice (self, labels=[]):
        choice = ''
        self.screen.set_background(self.background_path)
        if labels:
            label_y = SCREEN_HEIGHT / (len(labels) + 1)
            label_height = label_y
            for label in labels:
                label.place_to((CENTER_X, label_y), center=True)
                label.show()
                label_y += label_height
        for button in self.buttons:
            button.show()
        menu = True
        while menu:
            update()
            for button in self.buttons:
                if button.get_pressed():
                    choice = button.text
                    update()
                    time.sleep(0.5)
                    menu = False
                    button.set_skin(button.RELEASED)
        for button in self.buttons:
            button.hide()
        for label in labels:
            label.hide()
        return choice
        
    def enable_button(self, button_name, enable=True):
        for button in self.buttons:
            if button.text == button_name:
                button.enable(enable)


class Button(epg.Sprite, epg.Label):
    RELEASED = 0
    PRESSED = 1
    DISABLED = 2
    def __init__(self, button_image_paths, text, pos, w=50, h=50, savescale=False):
        epg.Sprite.__init__(self, button_image_paths[0], pos, w=w, h=h, savescale=savescale)
        epg.Label.__init__(self, text=text, x=pos[0], y=pos[1], center=True)
        self.skin_index = self.RELEASED
        self.animation_list = []
        self.animation_list.append(self.load_img(img=button_image_paths[self.RELEASED]))
        self.animation_list.append(self.load_img(img=button_image_paths[self.PRESSED]))
        self.animation_list.append(self.load_img(img=button_image_paths[self.DISABLED]))

    
    def set_skin(self, skin_index):
        self.image = self.orig_image = self.animation_list[skin_index]
        self.skin_index = skin_index
    
    def get_pressed(self,):
        if not self.skin_index == self.DISABLED:
            if self.taped(epg.MOUSE) and pg.mouse.get_pressed()[0]:
                self.set_skin(self.PRESSED)
                return True
     #   else:
      #      self.set_skin(self.RELEASED)
      #      return False
    
    def hide(self):
        epg.Sprite.hide(self)
        epg.Label.hide(self)
    
    def show(self):
        epg.Sprite.show(self)
        epg.Label.show(self)
        
    def enable(self, enable=True):
        if enable:
            self.set_skin(self.RELEASED)
        else:
            self.set_skin(self.DISABLED)


def update():
    epg.update()
    if epg.close_window():
        exit()
    epg.tick(FPS)
    

screen = epg.Screen(EARTH_IMAGE_PATH, width=SCREEN_WIDTH, height=SCREEN_HEIGHT)

server = connection.Conection(SERVER, PORT)

fighters = []

current_fighter_id = 0

ground_level = SCREEN_HEIGHT - 254

def start_game():
    start_game_state = server.get_start()
    global current_fighter_id
    current_fighter_id = start_game_state.pop('current_player_id')
    for id, player_pos in start_game_state.items():
        print(f'fighter {id} created')
        dir, x_pos, y_pos, wigth, height = player_pos
        fighters.append(Fighter(animation_pathes=FIGHTER_IMAGE_PATHES,
                        x_pos=x_pos,
                        y_pos=y_pos,
                        flip = dir,
                        wigth=wigth, 
                        height=height,
                        ground_level=ground_level,
                        gravity=GRAVITY,
                        id=int(id)
                        ))
    menu.enable_button('играть')


def fight():
    print('файтеры', len(fighters))
    while len(fighters) > 1:                              #TODO вместо количества должно быть здоровье
        for fighter in fighters:
            if fighter.id == current_fighter_id:
                options = fighter.check_options()
                game_state = server.get_game_state(options)
                break
        for fighter in fighters:
            fighter.apply_game_state(game_state.get(str(fighter.id)))
        update()
    print('end')
       
menu = Menu(screen,
            BACK_IMAGE_PATH, 
            ('играть', 'выйти'),
            (BUTTON_RELEASED_IMAGE_PATH, BUTTON_PRESSED_IMAGE_PATH, BUTTON_DISABLED_IMAGE_PATH),
            (110, 110),
            button_order='h',
            button_margin=205,
            )

menu.enable_button('играть', False)

threading.Thread(target=start_game).start()

choice = menu.get_choice()

if choice == 'выйти':
    exit()

if choice == 'играть':
    screen.set_background(EARTH_IMAGE_PATH)
    fight()
