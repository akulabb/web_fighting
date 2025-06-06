#716 9327 5626

import logging as mainlog
import socket
import threading
import time
import json
import inspect

ERROR = -1

SCREEN_HEIGHT = 600
SCREEN_WIDTH = 800
GROUND_LEVEL = SCREEN_HEIGHT - 150              #716
START_POSITIONS = (int(SCREEN_WIDTH / 5), 
                   int(SCREEN_WIDTH - SCREEN_WIDTH / 5),
                   int(SCREEN_WIDTH / 5 * 2),
                   int(SCREEN_WIDTH / 5 * 3)
                   )

SERVER = 'localhost'
PORT = 55555

FIGHT_TIME = 600
timer = FIGHT_TIME
recent_time = 0

STAY = 0
GO = 1
JUMP = 2
ATTACK = 3
HITTED = 4
DEAD = 5

CONNECTED = 3 #в меню
WAITING = 2   #ждет от остальных игроков
READY = 1
IN_GAME = 0

LOGGING_LEVEL = mainlog.DEBUG
NOT_LOGGING_FUNCTION = ('apply_options', 'send_data', 'recieve', 'update', 'get_self_state', 'sub_func', 'say')

mainlog.basicConfig(level=LOGGING_LEVEL,
                format='%(levelname)s %(message)s')
log = mainlog.getLogger('log_to_file')
fhandler = mainlog.FileHandler(filename='log.txt', mode='a')
formatter = mainlog.Formatter('%(asctime)s, %(levelname)s, %(message)s, %(funcName)s, %(lineno)s, %(filename)s')

fhandler.setFormatter(formatter)
log.addHandler(fhandler)

ATTACK_DELAY = 5
HITTED_DELAY = 5

PLAYER_SIZE = (130, 130)

GRAVITY = 2

start_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
start_socket.bind((SERVER, PORT))
start_socket.listen(2)
log.info('Сервер запущен')

players = {num:None for num in range(20)}

game_started = False

max_players_num = 0
connected_players_num = 0
alive_players_num = 0

def to_log(func):
    def sub_func(*args, **kwargs):
        if not func.__name__ in NOT_LOGGING_FUNCTION:
            log.info(f"** {func.__name__} **")
        result = func(*args, **kwargs)
        return result
    return sub_func

def log_class(class_to_log, ):
    class_name = class_to_log.__name__
    for name, method in inspect.getmembers(class_to_log):
        if inspect.isfunction(method):
            setattr(class_to_log, name, to_log(method))
    return class_to_log


@log_class
class Player(threading.Thread):
    def __init__(self, id, socket, gravity):
        super().__init__(daemon=True)
        self.attack_delay = 0
        self.hitted_delay = 0
        self.action = STAY     # 0 = stay, 1 = go, 2 = jump, 3 = attack, 4 hitted, 5 = dead
        self.id = id
        self.dir = bool(self.id % 2) or False            # True влево, False вправо
        self.health = 100
        self.y_pos = int(GROUND_LEVEL - PLAYER_SIZE[1] / 2)
        self.rect = Rect(PLAYER_SIZE, 
                         START_POSITIONS[self.id], 
                         self.y_pos
                        )
        self.socket = socket
        self.fall_speed = 0
        self.jumping = False
        self.gravity = gravity
        self.mode = READY
        self.extra_socket = None
        self.update_timer_value = 0
        self.immortal = True
    
    def add_extra_socket(self, extra_socket):
        self.extra_socket=extra_socket
        log.debug(f'added extra socket')
    
    def set_start(self,):
        self.rect.update(START_POSITIONS[self.id], self.y_pos)
        self.health = 100
        self.action = STAY
        self.mode = READY
    
    def attack(self,):
        self.attack_delay = ATTACK_DELAY
        attack_dist = self.rect.width
        if self.dir:
            hit_x = self.rect.center_x - attack_dist / 2
        else:
            hit_x = self.rect.center_x + attack_dist / 2
        
        hit = Rect(PLAYER_SIZE,
                     hit_x,
                     self.y_pos,
                     )
        
   #     print('starting apply hitted')
        for hitted_enemy in hit.get_hitted(self.id): 
            hitted_enemy.hitted()
         #   print('attack:enemy id', hitted_enemy.id)
    
    def hitted(self):
        global alive_players_num
        self.hitted_delay = HITTED_DELAY
        if self.mode == IN_GAME:
            if self.health > 0 and not self.immortal:
                self.health -= 5
                self.action = HITTED
            if self.health < 1 and self.action != DEAD:
                self.action = DEAD
                alive_players_num -= 1
                print(f'player: {self.id} dead, alive_players_num: {alive_players_num}')
    #    print('hitted:health', self.health)
    
    def apply_options(self, options):
        dx = 0
        dy = 0
        # gravitation
        self.fall_speed += self.gravity
        dy = self.fall_speed
        
        # удержание спрайта в пределах экрана
        if (self.rect.left + dx) < 0:       #левая граница экрана
            dx = -self.rect.left
        elif self.rect.right + dx > SCREEN_WIDTH:   #правая граница
            dx = SCREEN_WIDTH - self.rect.right
        if (self.rect.bottom + dy) > GROUND_LEVEL:
            dy = (GROUND_LEVEL - self.rect.bottom)
            self.fall_speed = 0
            self.jumping = False
        
        # controling
        if self.action != DEAD:
            if self.hitted_delay:
                self.action = HITTED
                self.hitted_delay -= 1
            else:
                self.action = STAY
                if options.get('move'):
                    self.action = GO
                if options.get('jump') and not self.jumping:
                    self.fall_speed = -30
                    self.jumping = True
                    self.action = JUMP
                if options.get('hit') and not self.attack_delay:
             #       print('call attack')
                    self.action = ATTACK
                    self.attack()
                dx += options.get('move')
                self.dir = options.get('direction')

        pos_x = self.rect.center_x + dx
        pos_y = self.rect.center_y + dy
        if self.attack_delay:
            self.attack_delay -= 1
        self.rect.update(pos_x, pos_y)
        
    def get_self_state(self):
        return (self.rect.center_x, self.rect.center_y, self.health, self.action, self.dir, self.mode)
      
    def say(self, message):
        log.info(f'player {self.id} : {message}')
    
    def wait_for_extra_socket(self):
        self.say('waiting for extra socket')
        while not self.extra_socket:
            time.sleep(0.25)
    
    def watch_rings(self, ):
        self.say(f'watch rings started')
        prev_rings_states = []
        while self.mode == READY:
            #self.say(f'self.mode == READY')
            rings_states = [ring.fight for ring in rings.values()]
            if prev_rings_states != rings_states:
                prev_rings_states = rings_states
                send(rings_states, self.extra_socket)
            time.sleep(0.1)
    
    def run(self): 
        self.say(f'Игрок создан')
        player_connected = True
        self.set_start()
        start_state = {'current_player_id' : self.id,
                       'rings' : tuple(rings.keys()),
                       }
        start_config =(self.dir,
                       self.rect.center_x, 
                       self.rect.center_y, 
                       self.rect.width,
                       self.rect.height,
                       )
        start_state = (self.id,
                       start_config,
                       tuple(rings.keys()),
                       )
        send(start_state, self.socket)
        self.wait_for_extra_socket()
        self.say(f'start state: {start_state}')
        while player_connected:
            threading.Thread(target=self.watch_rings, args=(), daemon=True).start()
            try:
                ring_number = recieve(self.socket)
                ring = rings[ring_number]
            except Exception as err:
                self.say(f"Wrong ring number : {ring_number}, Disconnecting player")
                player_connected = false
                continue
            self.say(f' выбрал ринг на {ring_number} игрока')
            ring.add_player(self)
            self.say(f'start main cycle.')
            self.mode = IN_GAME
            while True:                                                    #главный цикл игры
                options = recieve(self.socket)
                self.mode = IN_GAME
                if options == ERROR:
                    self.say(f'Потерянно соеденение, player disconnected')
                    player_connected = False
                    break
                self.apply_options(options)
                gm_state = ring.get_game_state(self.update_timer_value)
                #print(gm_state)
                send(gm_state, self.socket)
                #send(ring.get_game_state(self.update_timer_value), self.socket)
                if ring.game_over():
                    self.say('GAME OVER')
                    self.socket.recv(1024)
                    self.say('sending finish')
                    send('finish', self.socket)
                    self.say('recieving finish confirmation')
                    confirm = self.socket.recv(1024)
                    self.say(f'confirm : {confirm}')
                    self.mode = READY
                    break
        remove_player(self.id)

class Rect:
    def __init__(self, size, center_x, center_y, ):
        self.width, self.height = size
        self.center_x = center_x
        self.center_y = center_y
        self.update(center_x, center_y)
    
    def update(self, center_x, center_y):
        self.top = int(center_y - self.height / 2)
        self.bottom = int(center_y + self.height / 2)
        self.right = int(center_x + self.width / 2)
        self.left = int(center_x - self.width / 2)
        self.center_x = center_x
        self.center_y = center_y    
    
    def get_hitted(self, my_player_id):
        enemies = []
        for id, player in players.items():
            if player and not id == my_player_id:
                if (player.rect.right >= self.left and
                        player.rect.left <= self.right and
                        player.rect.top <= self.bottom and
                        player.rect.bottom >= self.top):
         #           print('enemys append')
                    enemies.append(player)
        return enemies


class Ring(threading.Thread):
    def __init__(self, players_num, playing_time=100):
        super().__init__()
        self.playing_time = playing_time
        self.timer = self.playing_time
        self.players_num = players_num
        self.max_players_num = 0
        self.alive_players_num = 0
        self.ring_enable = False
        self.fight = False
        self.players = []
        self.winners = []
    
    def add_player(self, player):
        self.enable()
        self.players.append(player)
        self.say(f'It is new player on our ring! His name is {self.name}')
    
    def _remove_player_from(self, id, container):
        index = None
        for player in container:
           if player.id == id:
                index = container.index(player)
        if index != None:
            container.pop(index)
        return index
    
    def remove_player(self, id):
        remove = False
        if self._remove_player_from(id, self.players):
            self.say(f'player {id} was removed from players')
            remove = True
        if self._remove_player_from(id, self.winners):
            self.say(f'player {id} was removed from winners')
            remove = True
        return remove
    
    def enable(self, enable=True):
        self.ring_enable = enable
    
    def enable_players_immortal(self, enable=True):
        for player in self.players:
            player.immortal = enable
    
    def run(self, ):
        self.say("referee started!")
        while True:
            self.waiting_for_players()
            self.enable_players_immortal(False)
            self.say('game started!')
            self.fight = True
            self.timer = self.playing_time
            alive_players = self.players_num
            while self.timer > 0 and alive_players > 1:              #TODO разобраться с waiting_players()
                alive_players = self.players_num
                time.sleep(1)
                self.timer -= 1
                self.update_timer_value = True
                for player in self.players:
                    player.update_timer_value = True
                    if player.action == DEAD:
                        alive_players -= 1
            self.winners = self.get_winners()
            if alive_players > 1:                                                    #timer is over
                new_winners = []
                max_health = self.winners[0].health
                for winner in self.winners:
                    if winner.health > max_health:
                        new_winners = [winner]
                    elif winner.health == max_health:
                        new_winners.append(winner)
                self.winners = new_winners
                print(f"new_winners : {new_winners}")
            self.enable(False)
            self.alive_players_num = 0
            self.max_players_num = 0
            self.say('game over!')
            self.enable_players_immortal()
            self.players.clear()
            self.fight = False
            print("ring clear")
            print()
    
    def get_winners(self, ): 
        self.winners = [player for player in self.players if player.action != DEAD]
        return self.winners
    
    def get_game_state(self, update_timer=False):
        game_state = {"timer" : None}
        for player in self.players:
            game_state[player.id] = player.get_self_state()
        if update_timer:
            game_state['timer'] = self.timer
            recent_time = self.timer
        return game_state
    
    def waiting_for_players(self, ):
        while len(self.players) < self.players_num:
            time.sleep(0.25)
    
    def say(self, message):
        log.info(f'ring on {self.players_num} players : {message}')
    
    def game_over(self):                                #TODO is game over 
        if not self.ring_enable:
            return self.winners

def waiting_players():
    result = True
    for player in players.values():
        if player:
            result = result and bool(player.mode)
    return result

@to_log
def remove_player(id):                                              #TODO найти на каком ринге игрок и удалить его оттуда(если есть)
    global connected_players_num, rings
    for ring in rings.values():
        ring.remove_player(id)
    players[id].socket.close()
    players[id] = None
    log.debug(f'игрок закончился с id : {id}')
    connected_players_num -= 1

def send(data, client_socket):
    try:
        str_data = json.dumps(data)
        byte_data = str_data.encode()
        client_socket.send(byte_data)
    except Exception as err:
        log.error(f'connection error : {err}')

def recieve(client_socket,):
    try:
        raw_data = client_socket.recv(1024)
        str_data = raw_data.decode()
        data = json.loads(str_data)
    except Exception as err:
        log.error(f'{err}')
        data = ERROR
    finally:
        return data

@to_log
def choice_waiting(player):
    send('connected', player.socket)
    ring_num = recieve(player.socket)
    log.info(f'player {player.id} chose to {ring_name}')        #TODO обработать ошибку соединения
    if ring_name in ring.keys():
        rings(ring_name).add_player(player)

ring2 = Ring(2)
ring3 = Ring(3)
ring4 = Ring(4)

ring2.start()
ring3.start()
ring4.start()
#создать объект ринга и админа

rings = {'2' : ring2,
         '3' : ring3,
         '4' : ring4,
        }

while True:
    new_socket, adress = start_socket.accept()
    socket_type = recieve(new_socket)
    log.info(f'Новое подключение с адресом : {adress}, тип подключения {socket_type}')
    if socket_type == 'main':
        for id, player_in_slot in players.items():
            if not player_in_slot:
                player = Player(id, new_socket, GRAVITY)
                player.start()
                players[id] = player
                connected_players_num += 1
                break
        else:
            print('Максимальное количество игроков')
            new_socket.close()
    elif type(socket_type) == int and socket_type >= 0:
        players[socket_type].add_extra_socket(new_socket)
    else:
        print('Неправильный тип подключения!')
            


