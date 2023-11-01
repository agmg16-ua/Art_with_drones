import socket
import random
import threading
import time
from confluent_kafka import Consumer, Producer, KafkaError

class EscucharDestino:
    def __init__(self, broker, id):
        self.broker = broker
        self.id = id
        self.posicionFin = [None, None]
        self.posicionActual = [None, None]
        self.estado = "Rojo"  # En movimiento "Rojo" y en la posición final "Verde"

    #Me uno a los topics con los roles correspondientes a Drone
    def consumidorDestino(self):
        # Configura las propiedades del consumidor
        config = {
            'bootstrap.servers': self.broker,  # Cambia esto a la dirección de tu cluster Kafka
            'group.id': 'grupo_2',
            'auto.offset.reset': 'latest'  # Comienza desde el inicio del topic
        }

        # Crea una instancia del consumidor
        consumidor = Consumer(config)

        return consumidor

    def consumidorMapa(self):
        # Configura las propiedades del consumidor
        config = {
            'bootstrap.servers': self.broker,  # Cambia esto a la dirección de tu cluster Kafka
            'group.id': 'grupo_2',
            'auto.offset.reset': 'latest'  # Comienza desde el inicio del topic
        }

        # Crea una instancia del consumidor
        consumidor = Consumer(config)

        return consumidor

    def productorPosiciones(self):
        # Configura las propiedades del productor
        config = {
            'bootstrap.servers': self.broker,  # Cambia esto a la dirección de tu cluster Kafka
        }

        # Crea una instancia del productor
        productor = Producer(config)

        return productor

    #Operaciones en kafka
    def escucharPorKafkaDestino(self, consumidor):
        topic = "destino"
        consumidor.subscribe(topics=[topic])

        while True:
            mensaje = consumidor.poll(1.0)
            if mensaje is not None:
                if mensaje.error():
                    if mensaje.error().code() == KafkaError._PARTITION_EOF:
                        print('No más mensajes en la partición')
                        break
                    else:
                        print('Error al recibir mensaje: {}'.format(mensaje.error()))

                else:
                    # Procesa el mensaje
                    print('Mensaje recibido: {}'.format(mensaje.value()))

    def escucharEstadoMapa(self, consumidor, productor):
        topic = "mapa"
        consumidor.subscribe(topics=[topic])

        while self.posicionActual[0] != self.posicionFin[0] and self.posicionActual[1] != self.posicionFin[1]:
            mensaje = consumidor.poll(1.0)
            while mensaje is not None:
                if mensaje.error():
                    if mensaje.error().code() == KafkaError._PARTITION_EOF:
                        print('No más mensajes en la partición')
                    else:
                        print('Error al recibir mensaje: {}'.format(mensaje.error()))
                else:
                    # Procesa el mensaje
                    print('Mensaje recibido: {}'.format(mensaje.value()))
                mensaje = consumidor.poll(1.0)

            self.mover()
            self.enviarPosicion(productor)
            time.sleep(3)

    def enviarPosicion(self, productor):
        topic = "posiciones"

        productor.produce(topic, value=f"{self.posicionActual[0]} {self.posicionActual[1]}")
        time.sleep(3)

    #Operaciones con el mapa
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

    def run(self):
        try:
            consumidorDestino = self.consumidorDestino()
            consumidorMapa = self.consumidorMapa()
            productorPosicion = self.productorPosiciones()

            destino = self.escucharPorKafkaDestino(consumidorDestino)

            while not destino:
                pass

            opcionAux = -1
            while opcionAux != 2:
                print("[1] Imprimir Mapa")
                print("[2] Salir del espectaculo")

                opcionAux = int(input())
                if opcionAux == 1:
                    self.escucharEstadoMapa(consumidorMapa, productorPosicion)

        except Exception as e:
            print("Error:", e)

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
            dron = inclusion.split(" ")
            print(dron)
            if dron[0] == "aceptado":
                print("---Drone unido de manera satisfactoria---\n")
                self.id = int(dron[1])
                print(dron)
                aceptado = True
            else:
                print("---No se ha podido unir---\n")

            skcliente.close()
        except Exception as e:
            print("Error solicitando inclusion: " + str(e))
            exit(-1)

        return aceptado

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

    broker = ip_Kafka + ":" + puerto_Kafka
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
                escuchar_destino = EscucharDestino(broker,drone.id)
                escuchar_destino.run()

        else:
            exit(0)
