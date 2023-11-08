import socket
import uuid

#Variables globales.
id_nueva = 1                #Id nueva para el drone que se quiera registrar
token_dron_actual = ""      #Token de acceso

#Lee el sokcet con el drone de forma controlada
def leer_socket(sock, datos):
    try:
        datos = sock.recv(1024).decode('utf-8')
    except Exception as e:
        print("Error leyendo el socket: ", e)
    return datos

#Escribe en el socket de forma controlada
def enviar_socket(sock, token):
    try:
        sock.send(token.encode('utf-8'))
    except Exception as e:
        print("Error escribiendo en el socket: ", e)

#Compruebo si el drone ya se ha registrado anteriormente
def existe_en_bd(id, alias):
    global token_dron_actual
    existe = False
    try:
        with open("drones.txt", "r") as archivo:
            for linea in archivo:
                palabras = linea.split()
                if palabras[1] == id:
                    existe = True
                    token_dron_actual = palabras[0]
    except Exception as e:
        print("Error al comprobar drones:", e)
    return existe

#Escribe en el fichero el token,la id real del drone, la id virtual del drone y el alias.
def escribir_bd(id, alias):
    global id_nueva
    global token_dron_actual
    with open("drones.txt", "a") as archivo:
        if not existe_en_bd(id, alias):
            token_dron_actual = generar_token()
            archivo.write(f"{token_dron_actual} {id} {id_nueva} {alias}\n")
            id_nueva += 1

#Genera un token de acceso
def generar_token():
    token = str(uuid.uuid4())
    return token

#Vacia el fichero antiguo de drones antes de empezar a registrar
def borrar_fichero():
    try:
        with open("drones.txt", "w") as archivo:
            archivo.truncate(0)
        print("El fichero ha sido vaciado con éxito.")
    except Exception as e:
        print("Error al vaciar el fichero:", e)

#Programa principal. NO ES CONCURRENTE AUN
if __name__ == "__main__":
    import sys

    try:
        #Comprueba los argumentos
        if len(sys.argv) < 2:
            print("Faltan argumentos: <Puerto de escucha>")
            sys.exit(-1)

        #Los asigna
        puerto = int(sys.argv[1])

        #Vacia el fichero y crea el servidor a la espera de nuevos drones
        borrar_fichero()
        Ssocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        Ssocket.bind(('', puerto))
        Ssocket.listen()

        #Realiza el registro del drone
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
