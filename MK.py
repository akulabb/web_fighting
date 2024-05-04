import easy_pygame as epg
from easy_pygame import UP, DOWN, LEFT, RIGHT
import pygame as pg
from fighter import Fighter
import connection
import os

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

SERVER = 'localhost'
PORT = 5555

def update():
    epg.update()
    if epg.close_window():
        exit()
    epg.tick(FPS)
    

screen = epg.Screen(EARTH_IMAGE_PATH, width=SCREEN_WIDTH, height=SCREEN_HEIGHT)

server = connection.Conection(SERVER, PORT)

ground_level = SCREEN_HEIGHT - 254

start_game_state = server.get_start()
current_fighter_id = start_game_state.pop('current_player_id')

fighters = []

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


def main():
    print('файтеры', len(fighters))
    while len(fighters) > 1:
        for fighter in fighters:
            if fighter.id == current_fighter_id:
                options = fighter.check_options()
                game_state = server.get_game_state(options)
                break
        for fighter in fighters:
            fighter.apply_game_state(game_state.get(str(fighter.id)))
        update()
       
       
main()
