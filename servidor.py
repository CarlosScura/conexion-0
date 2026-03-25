import socket, selectors
from datetime import datetime
from conexion import HOST, PORT

class server():
    def __init__(self, host, port):
        self.host = host
        self.port = port
        # AF_INET = IPv4 // SOCK_STREAM = TCP
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.selector = selectors.DefaultSelector()
        self.clientes = {}
    
    def establecer_conexion(self):
        # si el servidor se cayó y el puerto quedó en un estado intermedio.
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        
        # configuramos el socket para que controle si el programa ya se esta ejecutando o si otro server usa el puerto.
        try: 
            self.server_socket.bind((self.host, self.port))
        except:
            raise SystemExit(f"El puerto {self.port} ya se esta utilizando por otro programa, se procede a cerrar la aplicacion")
        
        # El selector necesita que los sockets sean no bloqueantes para poder monitorear varios a la vez
        self.server_socket.setblocking(False)
        
        self.server_socket.listen()
        
        # Le estás diciendo "monitoreá este socket y avisame cuando haya algo para leer"
        self.selector.register(self.server_socket, selectors.EVENT_READ)

    def aceptar_conexion(self):
        # aceptamos la conexión
        cliente_socket, direccion = self.server_socket.accept()
        
        # la hacemos no bloqueante y la registramos en el selector
        cliente_socket.setblocking(False)
        self.selector.register(cliente_socket, selectors.EVENT_READ)
        
        # pedimos el nombre y lo guardamos, convertimos texto a bytes y viceversa
        cliente_socket.send("Ingresa tu nombre: ".encode())
        nombre = cliente_socket.recv(1024).decode()
        self.clientes[cliente_socket] = nombre
        
        # notificamos a todos que llegó alguien
        self.broadcast(f"{nombre} se unió al chat!", None)

    def broadcast(self, mensaje, socket_emisor):
        # si modificamos el diccionario va a causar error 
        # asi que creamos una lista solo de los sockets
        for cliente_socket in list(self.clientes):
            if cliente_socket != socket_emisor:
                try:
                    cliente_socket.send(mensaje.encode())
                except:
                    self.desconectar_cliente(cliente_socket)

    def revisar_selectores(self):
        while True:
            # Lista de selectores que tuvieron actividad
            eventos = self.selector.select()
            for evento in eventos:
                # evento[0].fileobj nos da el socket que tuvo actividad
                socket_evento = evento[0].fileobj
                if socket_evento == self.server_socket:
                    # es una conexión nueva
                    self.aceptar_conexion()
                else:
                    # es un mensaje de cliente existente
                    self.recibir_mensaje(socket_evento)

    def recibir_mensaje(self, cliente_socket):
        try:
            mensaje = cliente_socket.recv(1024).decode()
            if mensaje:
                nombre = self.clientes[cliente_socket]
                timestamp = datetime.now().strftime("%H:%M")
                mensaje_completo = f"[{timestamp}] {nombre}: {mensaje}"
                self.broadcast(mensaje_completo, cliente_socket)
                self.guardar_log(mensaje_completo)
            else:
                # si el mensaje esta vacio lo desconectamos
                self.desconectar_cliente(cliente_socket)
        except:
            self.desconectar_cliente(cliente_socket)

    def desconectar_cliente(self, cliente_socket):
        nombre = self.clientes[cliente_socket]
        
        # notificamos a todos que se fue
        self.broadcast(f"{nombre} abandonó el chat.", None)
        self.guardar_log(f"{nombre} abandonó el chat.")
        
        # le decimos al selector que deje de monitorear ese socket
        self.selector.unregister(cliente_socket)
        # lo borramos del diccionario y cerramos el socket
        del self.clientes[cliente_socket]
        cliente_socket.close()

    def guardar_log(self, mensaje):
        with open("log.txt", "a") as log:
            log.write(f"{mensaje}\n")

    def iniciar(self):
        self.establecer_conexion()
        print(f"Servidor iniciado en {self.host}:{self.port}")
        
        try:
            self.revisar_selectores()
        except KeyboardInterrupt:
            print("Servidor cerrado.")
        finally:
            # cerramos todo
            self.selector.close()
            self.server_socket.close()

if __name__ == "__main__":
    servidor = server(HOST, PORT)
    servidor.iniciar()