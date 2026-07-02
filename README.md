# conexion-0
Segundo Challenge en The Huddle, Chat en tiempo real con sockets ("como si fuera 1995").

## Descripción

Chat multicliente en terminal implementado desde cero con la librería estándar de Python, sin frameworks. El servidor acepta múltiples conexiones concurrentes usando selectores, distribuye los mensajes por broadcast y maneja desconexiones (voluntarias e inesperadas) sin caer. El cliente corre en dos hilos para poder hablar y escuchar al mismo tiempo, y reintenta reconectarse si pierde la conexión con el servidor.

---

## Tecnologías utilizadas

- Python
- socket
- selectors
- threading

---

## Estructura del proyecto
```
conexion-0
├── servidor.py
├── cliente.py
├── conexion.py     → host, puerto y constantes compartidas
├── log.txt         → historial de mensajes (se genera en runtime)
├── pseudocodigos.md
└── README.md
```
---

## Cómo correr el proyecto

1. Tener Python 3 instalado (no requiere librerías externas).
2. Configurar host y puerto en `conexion.py` si hace falta.
3. Levantar el servidor:
```bash
   python servidor.py
```
4. En otra terminal (una por cada usuario), levantar el cliente:
```bash
   python cliente.py
```
5. Ingresar un nombre de usuario cuando se solicite y empezar a chatear. Escribir `/exit` para salir del chat.

---

## Decisiones técnicas

**Selectores en el servidor, threads en el cliente.**
El servidor puede tener N clientes simultáneos — usar un thread por cliente escalaría mal en memoria y CPU. Con `selectors` un solo hilo monitorea todos los sockets y reacciona solo cuando hay actividad. El cliente en cambio solo tiene 2 tareas fijas (escuchar y enviar), así que 2 threads simples alcanzan sin la complejidad de un selector.

**`SO_REUSEADDR`.**
Si el servidor se cae y se reinicia rápido, el sistema operativo deja el puerto en estado de espera por varios minutos. Esta opción permite reutilizar el puerto sin esperar ese tiempo.

**Orden de borrado en `desconectar_cliente`: primero eliminar del diccionario, luego notificar.**
Al notificar al resto que un cliente se fue, `broadcast` puede fallarle el envío a otro socket ya muerto y volver a invocar `desconectar_cliente` sobre él. Si primero se borra el cliente del diccionario de conexiones activas y recién después se llama a `broadcast`, cualquier llamada recursiva sobre el mismo socket corta de inmediato (ya no está en el diccionario), evitando una recursión infinita entre `broadcast` y `desconectar_cliente`.

**Reintentos de reconexión en el cliente.**
Si el cliente pierde la conexión (por caída del servidor o error de red), intenta reconectar 3 veces con una espera entre intentos antes de cerrar definitivamente, en vez de crashear al primer fallo.

**Manejo de desconexión voluntaria vs. inesperada.**
Un mensaje vacío o una excepción en `recv` se interpreta como desconexión (voluntaria con `/exit` o inesperada por caída de red). En ambos casos el servidor limpia el socket del selector y del diccionario de clientes activos.

---

## Requisitos del challenge cumplidos

- Servidor con selectores, acepta múltiples conexiones concurrentes.
- Broadcast de mensajes a todos los clientes conectados.
- Lista activa de conexiones, con limpieza al desconectarse un cliente.
- Cliente por terminal, sin interfaz gráfica, hablando y escuchando en simultáneo (2 threads).
- Manejo de desconexiones inesperadas sin crashear el servidor.
- Reintentos de reconexión en el cliente ante fallos de red.
- Log de mensajes en `log.txt`.

---

## Autor

**Fede Alarcón Scura** — Estudiante de Penguin Academy
Challenge desarrollado como parte del programa de formación.