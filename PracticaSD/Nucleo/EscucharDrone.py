import socket
import threading
import sqlite3

#Realiza todas las operaciones posibles para autenticar a un drone
class EscucharDrone(threading.Thread):
    #Obtiene la coneccion del soket y la guarda.
    def __init__(self, skDrone):
        super().__init__()
        self.drone = skDrone

    #Lee del socket de forma controlada
    def lee_socket(self, p_datos):
        try:
            aux = self.drone.recv(1024)
            p_datos = aux.decode()
        except Exception as e:
            print(f"Error leyendo socket: {e}")
        return p_datos

    #Escribe en el socket de forma controlada
    def escribe_socket(self, p_datos):
        try:
            self.drone.send(p_datos.encode())
        except Exception as e:
            print(f"Error escribiendo socket: {e}")

    #Autentica al drone conectado en el espectaculo.
    #Comprueba que el token y la id del drone son las correctas en mi base de datos.
    #Devuelve un booleano diciendo si se ha autenticado y un string que tendrá la id
    #para que el drone se vea en el espectaculo. En caso de que no se una obtiene un string vacio
    def autenticar(self, token, id):
        try:
            """
            with open("drones.txt", "r") as archivo:
                for linea in archivo:
                    palabras = linea.split(" ")
                    token_aux = palabras[0]
                    id_aux = palabras[1]
                    if token_aux == token and id_aux == id:
                        return True,palabras[2]
            """
            conn = sqlite3.connect('registry')

            cursor = conn.cursor()

            cursor.execute("SELECT id, token FROM drones WHERE id = ?", (id,))

            rows = cursor.fetchall()

            if rows is not None:
                id_drone, token_drone = rows[0]
                if token_drone == token:
                    return True, id_drone

        except Exception as e:
            print(f"Error autenticando al drone: {e}")
            return False,""
        return False,""

    #Codigo que se ejecutará al hacer .start
    #Devuelve al drone si ha sido aceptado o denegado
    def run(self):
        print("Contactando drone...")
        token_id = ""
        existe = False

        try:
            token_id = self.lee_socket(token_id)
            palabras = token_id.split(" ")
            existe,id = self.autenticar(palabras[0],palabras[1])
            if existe:
                self.escribe_socket("aceptado " + str(id))
            else:
                self.escribe_socket("denegado")

        except Exception as e:
            print(f"Error en escucharDrone: {e}")
        finally:
            self.drone.close()
