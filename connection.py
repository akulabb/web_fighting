import socket
import json


class Conection :
    def __init__(self, server, port):
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.connect((server, port))

    def get_start(self):
        try:
            response = self.server.recv(1024)
            coord = response.decode()
            coord = json.loads(coord)
        except Exception as err:
            print('connection error : ', err)
        return coord
    
    