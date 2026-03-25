### SERVIDOR

Se crea el socket 
Se establecen los puntos de conexión 
MIENTRAS servidor activo:
   Revisar selectores
   SI hay actividad en el socket principal:
      → nueva conexión
      Acepta la conexion, 
      Se le registra el selector,
      Se pregunta el nombre
      Se guarda el nombre que recibe
   SI hay actividad en un socket de cliente:
      → mensaje o desconexión
      SI Recibe un mensajes:
         Lo anexa a la hora
         Lo envia a todos con el timestamp y el nombre del usuario
         Lo guarda en log
      SI se desconecta el cliente:
         Cierra el socket
         Se quita del selector
         Se le saca del diccionario de clientes activos
         Se notifica al chat y al log que se desconecto
AL cerrar el servidor:
    Cerrar todos los sockets de clientes
    Cerrar el socket principal


### CLIENTE

Se conecta al servidor
Ingresa su nombre

THREAD 1 - Escucha:
    MIENTRAS conectado:
        Recibir mensaje del servidor
        Mostrar mensaje
    SI se pierde conexión:
    Intentar reconectar X veces
    SI no reconecta en X intentos:
        Mostrar "conexión perdida"
        Cerrar cliente

THREAD 2 - Envío:
    MIENTRAS conectado:
        Esperar input del usuario
        SI input es "/exit":
            Desconectarse
            Terminar ambos threads
        SINO:
            Enviar mensaje al servidor

