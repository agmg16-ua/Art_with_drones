import socket
import random
import threading

class AD_Drone:
    def __init__(self, alias):
        self.estado = "Rojo"
        self.posicionActual = [0, 0]
        self.posicionFin = [0, 0]
        self.alias = alias
        self.id = random.randint(1, 10000)
        self.token = ""

    def get_id(self):
        return self.id

    def mover(self):
        if self.estado == "Verde":
            return

        if self.posicionFin[0] > self.posicionActual[0]:
            self.posicionActual[0] += 1
        elif self.posicionFin[0] < self.posicionActual[0]:
            self.posicionActual[0] -= 1

        if self.posicionFin[1] > self.posicionActual[1]:
            self.posicionActual[1] += 1
        elif self.posicionFin[1] < self.posicionActual[1]:
            self.posicionActual[1] -= 1

        if self.posicionFin[0] == self.posicionActual[0] and self.posicionFin[1] == self.posicionActual[1]:
            self.estado = "Verde"

    def registrarse(self, ip, puerto):
        try:
            cadena = f"{self.id} {self.alias}"

            skcliente = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            skcliente.connect((ip, int(puerto)))

            skcliente.send(cadena.encode('utf-8'))

            token = skcliente.recv(1024).decode('utf-8')
            self.token = token

            print("---Drone registrado de manera satisfactoria---\n")
            skcliente.close()

        except Exception as e:
            print(e)
            exit(-1)

    def escribe_socket(self, sock, datos):
        try:
            sock.send(datos.encode('utf-8'))
        except Exception as e:
            print("Error:", e)

    def lee_socket(self, sock):
        try:
            p_datos = sock.recv(1024).decode('utf-8')
            return p_datos
        except Exception as e:
            print("Error:", e)
            return ""

    def solicitar_inclusion(self, ip, puerto):
        aceptado = False

        try:
            cadena = f"{self.token} {self.id}"

            skcliente = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            skcliente.connect((ip, int(puerto)))

            self.escribe_socket(skcliente, cadena)

            inclusion = self.lee_socket(skcliente)
            if inclusion == "aceptado":
                print("---Drone registrado de manera satisfactoria---\n")
                aceptado = True
            else:
                print("---No se ha podido registrar---\n")

            skcliente.close()
        except Exception as e:
            print(e)
            exit(-1)

        return aceptado

class EscucharDestino(threading.Thread):
    def __init__(self, ip_kafka, id_drone):
        threading.Thread.__init__(self)
        self.ip_kafka = ip_kafka
        self.id_drone = id_drone

    def run(self):
        print(f"Escuchando destino para el Drone {self.id_drone} en {self.ip_kafka}")

if __name__ == "__main__":
    import sys

    if len(sys.argv) < 7:
        print("ERROR: No hay suficientes argumentos")
        print("$ ./AD_Drone.py alias ip_Engine puerto_Engine ip_Kafka puerto_Kafka ip_Registry puerto_Registry")
        exit(-1)

    drone = AD_Drone(sys.argv[1])
    ip_Engine = sys.argv[2]
    puerto_Engine = sys.argv[3]
    ip_Kafka = sys.argv[4]
    puerto_Kafka = sys.argv[5]
    ip_Registry = sys.argv[6]
    puerto_Registry = sys.argv[7]

    opcion = -1

    while opcion != 3:
        print("[1] Registrar drone en el sistema")
        print("[2] Entrar al espectáculo")
        print("[3] Salir")

        opcion = int(input())

        if opcion == 1:
            drone.registrarse(ip_Registry, puerto_Registry)
        elif opcion == 2:
            aceptado = drone.solicitar_inclusion(ip_Engine, puerto_Engine)
            if aceptado:
                escuchar_destino = EscucharDestino(f"{ip_Kafka}:{puerto_Kafka}", drone.get_id())
                escuchar_destino.start()
        else:
            exit(0)
