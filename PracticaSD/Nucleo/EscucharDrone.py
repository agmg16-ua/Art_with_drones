import socket
import threading
import sqlite3
#Libreria para auditoria

import logging

# Obtiene la dirección IP local de la red actual
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.connect(("8.8.8.8", 80))
ip_address = s.getsockname()[0]
s.close()

# Configurar el sistema de registro
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

handler = logging.FileHandler('auditoria.log')
handler.setLevel(logging.INFO)

formatter = logging.Formatter('%(asctime)s - %(levelname)s - Acción: %(funcName)s - IP: ' + ip_address + ' - Descripción: %(message)s')
handler.setFormatter(formatter)

logger.addHandler(handler)

# Decorador para asignar un Logger con IP a la función
def logger_decorator(func):
    def wrapper(*args, **kwargs):
        func.logger = logger
        return func(*args, **kwargs)
    return wrapper

#Realiza todas las operaciones posibles para autenticar a un drone
class EscucharDrone(threading.Thread):
    #Obtiene la coneccion del soket y la guarda.
    def __init__(self, skDrone):
        super().__init__()
        self.logger = logger
        self.drone = skDrone

    #Lee del socket de forma controlada
    @logger_decorator
    def lee_socket(self, p_datos):
        self.logger.info("Leyendo socket")
        try:
            aux = self.drone.recv(1024)
            p_datos = aux.decode()
        except Exception as e:
            self.logger.error(f"Error leyendo socket: {e}")
            print(f"Error leyendo socket: {e}")
        return p_datos

    #Escribe en el socket de forma controlada
    @logger_decorator
    def escribe_socket(self, p_datos):
        self.logger.info("Escribiendo socket")
        try:
            self.drone.send(p_datos.encode())
        except Exception as e:
            self.logger.error(f"Error escribiendo socket: {e}")
            print(f"Error escribiendo socket: {e}")

    #Autentica al drone conectado en el espectaculo.
    #Comprueba que el token y la id del drone son las correctas en mi base de datos.
    #Devuelve un booleano diciendo si se ha autenticado y un string que tendrá la id
    #para que el drone se vea en el espectaculo. En caso de que no se una obtiene un string vacio
    @logger_decorator
    def autenticar(self, token, id):
        self.logger.info("Autenticando drone")
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

            cursor.execute("SELECT id, id_virtual, token FROM drones WHERE id = ?", (id,))

            rows = cursor.fetchall()

            if rows is not None:
                id_drone, id_virtual_drone, token_drone = rows[0]
                if token_drone == token:
                    return True, id_virtual_drone

        except Exception as e:
            self.logger.error(f"Error autenticando al drone: {e}")   
            print(f"Error autenticando al drone: {e}")
            return False,""
        return False,""

    #Codigo que se ejecutará al hacer .start
    #Devuelve al drone si ha sido aceptado o denegado
    @logger_decorator
    def run(self):
        self.logger.info("Contactando drone")
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
            self.logger.error(f"Error en escucharDrone: {e}")
            print(f"Error en escucharDrone: {e}")
        finally:
            self.logger.info("Cerrando socket")
            self.drone.close()
