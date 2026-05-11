import socket
import threading
import sys

recibiendo = True

def recibir_mensajes(cliente_socket):
    """Hilo para escuchar mensajes del servidor."""
    global recibiendo
    while recibiendo:
        try:
            mensaje = cliente_socket.recv(1024).decode('utf-8')
            if not mensaje:
                break
            print(mensaje)
        except (ConnectionResetError, BrokenPipeError, OSError):
            print("\n[!] Desconectado del servidor.")
            break
    recibiendo = False
    try:
        cliente_socket.close()
    except:
        pass

def iniciar_cliente(host='localhost', puerto=12345):
    cliente_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        cliente_socket.connect((host, puerto))
        print("Conectado al chat. Escribe '/salir' para terminar.")
    except ConnectionRefusedError:
        print("No se pudo conectar al servidor.")
        sys.exit(1)

    # Hilo de recepción
    hilo_lectura = threading.Thread(target=recibir_mensajes, args=(cliente_socket,))
    hilo_lectura.daemon = True
    hilo_lectura.start()

    # Hilo principal: enviar mensajes
    global recibiendo
    while recibiendo:
        try:
            mensaje = input()
            if mensaje.lower() == "/salir":
                recibiendo = False
                break
            cliente_socket.send(mensaje.encode('utf-8'))
        except (BrokenPipeError, OSError):
            print("Conexión perdida.")
            break
        except KeyboardInterrupt:
            break

    print("Cerrando conexión...")
    cliente_socket.close()
    sys.exit(0)

if __name__ == "__main__":
    iniciar_cliente()
    
