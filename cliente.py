import socket
from conexion import HOST, PORT

class cliente():
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.conectado = False
    
    def conectarse():
        pass