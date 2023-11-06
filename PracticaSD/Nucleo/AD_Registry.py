import socket
import uuid

token = "Puedes entrar"
id_nueva = 1
token_dron_actual = ""

def leer_socket(sock, datos):
    try:
        datos = sock.recv(1024).decode('utf-8')
    except Exception as e:
        print("Error:", e)
    return datos

def enviar_socket(sock, token):
    try:
        sock.send(token.encode('utf-8'))
    except Exception as e:
        print("Error:", e)

def existe_en_bd(id, alias):
    existe = False
    try:
        with open("drones.txt", "r") as archivo:
            for linea in archivo:
                palabras = linea.split()
                if palabras[1] == id:
                    existe = True
                    token_dron_actual = palabras[0]
    except Exception as e:
        print("Error al leer drones:", e)
    return existe

def escribir_bd(id, alias):
    global id_nueva
    global token_dron_actual
    with open("drones.txt", "a") as archivo:
        if not existe_en_bd(id, alias):
            token_dron_actual = generar_token()
            archivo.write(f"{token_dron_actual} {id} {id_nueva} {alias}\n")
            id_nueva += 1

def generar_token():
    token = str(uuid.uuid4())
    return token

def borrar_fichero():
    try:
        with open("drones.txt", "w") as archivo:
            archivo.truncate(0)
        print("El fichero ha sido vaciado con éxito.")
    except Exception as e:
        print("Error al vaciar el fichero:", e)

if __name__ == "__main__":
    import sys

    try:
        if len(sys.argv) < 2:
            print("Faltan argumentos: <Puerto de escucha>")
            sys.exit(-1)

        puerto = int(sys.argv[1])

        borrar_fichero()
        Ssocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        Ssocket.bind(('', puerto))
        Ssocket.listen()

        while True:
            print("Esperando solicitud...")
            socket, _ = Ssocket.accept()
            print("Recibida solicitud...")
            peticion = leer_socket(socket, "")
            print(peticion)
            palabras = peticion.split()

            escribir_bd(palabras[0], palabras[1])

            enviar_socket(socket, token_dron_actual)

        Ssocket.close()
    except Exception as e:
        print("Error:", e)
