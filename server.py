import socket
import threading
import time
import json


SERVER = 'localhost'
PORT = 5555

start_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
start_socket.bind((SERVER, PORT))
start_socket.listen(2)
print('Сервер запущен')

players = {0 : None,
		   1 : None,
		   2 : None,
		   3 : None,
		   }

def remove_player(id):
	players[id].close()
	players[id] = None
	print('игрок закончился с id : ', id)


def fighter(id):
	fighter_socket = players[id]
	print('Игрок создан с id : ', id)
	x_pos = 0
	y_pos = 716
	start_pos = json.dumps((x_pos, y_pos))
	fighter_socket.send(start_pos.encode())
	time.sleep(3)
	remove_player(id)


while True:
	player_socket, adress = start_socket.accept()
	print('Подключился игрок с адресом : ', adress)
	for id, player in players.items():
		if not player:
			players[id] = player_socket
			threading.Thread(target=fighter, args=(id,)).start()
			break
	else:
		print('Максимальное кичество игроков')
		player_socket.close()