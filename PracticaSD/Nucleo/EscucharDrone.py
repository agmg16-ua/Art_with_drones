import socket
import threading

class EscucharDrone(threading.Thread):
    def __init__(self, skDrone):
        super().__init__()
        self.drone = skDrone

    def lee_socket(self, p_datos):
        try:
            aux = self.drone.recv(1024)
            p_datos = aux.decode()
        except Exception as e:
            print(f"Error: {e}")
        return p_datos

    def escribe_socket(self, p_datos):
        try:
            self.drone.send(p_datos.encode())
        except Exception as e:
            print(f"Error: {e}")

    def autenticar(self, token):
        try:
            with open("drones.txt", "r") as archivo:
                for linea in archivo:
                    palabras = linea.split(" ")
                    token_aux = palabras[0]
                    if token_aux == token:
                        return True
        except Exception as e:
            print(f"Error: {e}")
            return False
        return False

    def run(self):
        print("Contactando drone...")
        token_id = ""
        existe = False

        try:
            token_id = self.lee_socket(token_id)
            palabras = token_id.split(" ")
            existe = self.autenticar(palabras[0])

            if existe:
                self.escribe_socket("aceptado")
            else:
                self.escribe_socket("denegado")

            self.drone.close()
        except Exception as e:
            print(f"Error en escucharDrone: {e}")
        finally:
            self.drone.close()

# El código restante debe ir en tu programa principal para iniciar la ejecución.
