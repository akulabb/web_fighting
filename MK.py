import easy_pygame as epg
from easy_pygame import UP, DOWN, LEFT, RIGHT
import pygame as pg
from fighter import Fighter
import connection

epg.AUTO_UPDATE = False
SCREEN_HEIGHT = epg.HEIGHT = 970
SCREEN_WIDTH = epg.WIDTH = 1280
FPS = 30
BALL_IMAGE_PATH = 'photos/ball.png'
EARTH_IMAGE_PATH = 'photos/earth.png'

HEIGHT_HALF = int(SCREEN_HEIGHT/2)
WIDTH_HALF = int(SCREEN_WIDTH/2)
epg.AUTO_UPDATE = False

GRAVITY = 2
#EARTH = 716

FIGHTER_IMAGE_PATH = 'C:\\Users\\Akula\\Desktop\\pytho\\Pygame\\wed_fighting\\photos\\fighter.png'

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
    x_pos, y_pos, wigth, height = player_pos
    fighters.append(Fighter(img=FIGHTER_IMAGE_PATH,
                    x_pos=x_pos,
                    y_pos=y_pos,
                    flip = False,
                    wigth=player_wigth, 
                    height=player_height,
                    ground_level=ground_level,
                    gravity=GRAVITY,
                    id=id
                    ))



    






fall_speed = 0
horiz_speed = 0

#fighter1.fights(fighter2)


def main():
    while len(fighters) > 1:
        for fighter in fighters:
            if fighter.id == current_fighter_id:
                options = fighter.check_options()
                game_state = server.get_game_state(options)
                #server.send(options)
            fighter.moving(game_state.get(fighter.id))
        fighter1.moving(game_state)
        update()
        

        

main()

