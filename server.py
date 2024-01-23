import socket
import threading
import time
import json


SCREEN_HEIGHT = 970
SCREEN_WIDTH = 1280
GROUND_LEVEL = SCREEN_HEIGHT - 254
START_POSITIONS = (int(SCREEN_WIDTH / 5), 
                   int(SCREEN_WIDTH - SCREEN_WIDTH / 5),
                   int(SCREEN_WIDTH / 5 * 2),
                   int(SCREEN_WIDTH / 5 * 3)
                   )

SERVER = 'localhost'
PORT = 5555

PLAYER_SIZE = (280, 180)

GRAVITY = 2

start_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
start_socket.bind((SERVER, PORT))
start_socket.listen(2)
print('Сервер запущен')

players = {0 : None,
		   1 : None,
		   2 : None,
		   3 : None,
		   }


class Player:
    def __init__(self, id, socket, gravity):
        self.id = id
        self.health = 100
        self.y_pos = GROUND_LEVEL - PLAYER_SIZE[1] / 2
        self.rect = Rect(PLAYER_SIZE, 
                         START_POSITIONS[self.id], 
                         self.y_pos
                         )
        self.socket = socket
        self.fall_speed = 0
        self.jumping = False
        self.gravity = gravity
        
    def apply_options(self, options):
    
        dx = 0
        dy = 0
        # controling
        if options.get('jump') == True and not self.jumping:
            self.fall_speed = -30
            self.jumping = True
#        if options.get('hit') == True:
 #           self.attack()
        dx += options.get('move')
#        self.flip_skins(options.get('direction'))
        #print(options.get('direction'))
        
        # gravitation
        self.fall_speed += self.gravity
        dy = self.fall_speed
        
        # удержание спрайта в пределах экрана
        if self.rect.left + dx < 0:
            dx = -self.rect.left
        elif self.rect.right + dx > SCREEN_WIDTH:
            dx = SCREEN_WIDTH - self.rect.right
        if self.rect.bottom + dy > GROUND_LEVEL:
            dy -= self.rect.bottom + dy - GROUND_LEVEL
            self.fall_speed = 0
            self.jumping = False
        
        pos_x = self.rect.center_x + dx
        pos_y = self.rect.center_y + dy
        self.rect.update(pos_x, pos_y)
        return {'coords' : (pos_x, pos_y),
                'health' : self.health_bar.value,
                } 
        
    def get_self_state(self):
        return (self.rect.center_x, self.rect.center_y, self.health)
    

class Rect:
    def __init__(self, size, center_x, center_y, ):
        self.wigth, self.height = size
        self.center_x = center_x
        self.center_y = center_y
        self.update(center_x, center_y)
    
    def update(self, center_x, center_y):
        self.top = center_x + self.height / 2
        self.bottom = center_x - self.height / 2
        self.right = center_y + self.wigth / 2
        self.left = center_y - self.wigth / 2
        self.center_x = center_x
        self.center_y = center_y    

def remove_player(id):
	players[id].socket.close()
	players[id] = None
	print('игрок закончился с id : ', id)


def fighter(current_player):
    print('Игрок создан с id : ', current_player.id)
    start_state = {'current_player_id' : current_player.id}
    for id, player in players.items():
        if player:
            start_state[id] = (player.rect.center_x, 
                               player.rect.center_y, 
                               player.rect.wigth, 
                               player.rect.height,
                               )
    str_start_state = json.dumps(start_state)
    current_player.socket.send(str_start_state.encode())
    while True:                                                 #главный цикл игры
        try:
            raw_options = current_player.socket.recv(1024)
            str_options = raw_options.decode()
            options = json.loads(str_options)
            #print('options:', options)   # TODO: получить game_state от всех игроков и отправить в клиент
        except Exception as err:
            print('Потерянно соеденение с : ', current_player.id, 'игрок отключился')
            break
        current_player.apply_options(options)
        players_state = {}
        for id, player in players.items():
            players_state[id] = player.get_self_state()
 #       players_state
        try:
            str_players_state = json.dumps(data)
            byte_players_state = str_players_state.encode()
            self.socket.send(byte_players_state)
        except Exception as err:
            print('connection error : ', err)
    remove_player(current_player.id)


while True:
    player_socket, adress = start_socket.accept()
    print('Подключился игрок с адресом : ', adress)
    for id, player_in_slot in players.items():
        if not player_in_slot:
            player = Player(id, player_socket, GRAVITY)
            players[id] = player
            threading.Thread(target=fighter, args=(player,)).start()
            break
    else:
        print('Максимальное кичество игроков')
        player_socket.close()