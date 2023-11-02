import time
import threading
from confluent_kafka import Consumer, Producer, KafkaError

class EscucharDestino(threading.Thread):
    def __init__(self, broker, id):
        super().__init__()
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

            self.escucharEstadoMapa(consumidorMapa, productorPosicion)

        except Exception as e:
            print("Error:", e)
