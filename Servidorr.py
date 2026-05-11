# -*- coding: latin-1 -*-
import socket
import threading
import signal
import sys

clientes = []
clientes_lock = threading.Lock()   # Protege el acceso a la lista
servidor_ejecutandose = True

def broadcast(mensaje, emisor_socket=None):
    """Envía un mensaje a todos los clientes conectados (excepto al emisor si se indica)."""
    with clientes_lock:
        for c in clientes[:]:   # Iteramos sobre copia para poder eliminar dentro
            if emisor_socket and c == emisor_socket:
                continue
            try:
                c.send(mensaje.encode('utf-8'))
            except (BrokenPipeError, ConnectionResetError, OSError):
                # Cliente muerto: lo eliminamos de la lista
                clientes.remove(c)

def manejar_cliente(cliente_socket, direccion):
    """Hilo para recibir mensajes de un cliente."""
    with clientes_lock:
        clientes.append(cliente_socket)
    print(f"[INFO] Cliente {direccion} conectado. Total: {len(clientes)}")

    try:
        while servidor_ejecutandose:
            try:
                mensaje = cliente_socket.recv(1024).decode('utf-8')
                if not mensaje:
                    break
                print(f"\n[CLIENTE {direccion}] dice: {mensaje}")
                # Reenvía a todos los demás
                broadcast(f"Mensaje de {direccion}: {mensaje}", emisor_socket=cliente_socket)
            except (ConnectionResetError, BrokenPipeError):
                break
    finally:
        with clientes_lock:
            if cliente_socket in clientes:
                clientes.remove(cliente_socket)
        cliente_socket.close()
        print(f"[INFO] Cliente {direccion} desconectado. Quedan: {len(clientes)}")

def entrada_servidor():
    """Hilo para mensajes del administrador."""
    while servidor_ejecutandose:
        try:
            mensaje_admin = input("Servidor > ")
            if mensaje_admin.lower() == "/salir":
                print("Apagando servidor...")
                sys.exit(0)   # O podemos detener el bucle principal
            broadcast(f"AVISO DEL SERVIDOR: {mensaje_admin}")
        except EOFError:
            break

def cerrar_servidor(signal, frame):
    """Captura Ctrl+C para cerrar el servidor limpiamente."""
    global servidor_ejecutandose
    print("\n[INFO] Cerrando servidor...")
    servidor_ejecutandose = False
    with clientes_lock:
        for c in clientes:
            try:
                c.close()
            except:
                pass
        clientes.clear()
    sys.exit(0)

def iniciar_servidor(host='localhost', puerto=12345):
    servidor = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    servidor.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)  # Reutilizar puerto
    servidor.bind((host, puerto))
    servidor.listen()
    print(f"Servidor iniciado en {host}:{puerto} - Escribe '/salir' para terminar")

    # Hilo del administrador
    hilo_admin = threading.Thread(target=entrada_servidor, daemon=True)
    hilo_admin.start()

    # Capturar Ctrl+C
    signal.signal(signal.SIGINT, cerrar_servidor)

    global servidor_ejecutandose
    while servidor_ejecutandose:
        try:
            cliente_socket, direccion = servidor.accept()
            hilo = threading.Thread(target=manejar_cliente, args=(cliente_socket, direccion))
            hilo.daemon = True
            hilo.start()
        except OSError:
            break   # servidor cerrado
    print("Servidor detenido.")

if __name__ == "__main__":
    iniciar_servidor()
    
