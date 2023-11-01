import time
import threading
from confluent_kafka import Consumer, Producer, KafkaError
import json
from EscucharDrone import EscucharDrone
import os
import socket
import copy

#Thread para escuchar drones en paralelo
class EscucharDrones(threading.Thread):
    # Contendrá las figuras del fichero
    figuras = []
    def __init__(self, puerto):
        super().__init__()
        self.puerto = puerto
        self.detener = False

    def detener(self):
        self.detener = True

    def run(self):
        try:
            # Obtiene la dirección IP local de la red actual
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            local_ip = s.getsockname()[0]
            s.close()

            # Creo el servidor a la espera de drones que me llamen por ahí
            s_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s_socket.bind((local_ip, self.puerto))
            s_socket.listen()

            # Me mantengo en escucha de nuevos drones mientras no quiera detener el Engine
            while not self.detener:
                print("Esperando drone...")
                conn, addr = s_socket.accept()

                try:
                    escuchar = EscucharDrone(conn)
                    escuchar.start()
                except Exception as e:
                    print("Error para escuchar al drone: ", e)

            # Cierro el servidor
            s_socket.close()

        except Exception as e:
            print("Error:", e)

#Clase para almacenar los drones con su coordenada actual
class Drone:
    def __init__(self, id):
        self.id = id
        self.coordenada = (0, 0)

    def set_coordenada(self, x, y):
        self.coordenada = (x, y)

#Clase principal
class AD_Engine:

    def __init__(self):
        self.drones = []
        self.figuras = []

    #Me conecto a cada topic con el rol correspondiente
    def productor_destinos(self, broker):
        # Configura las propiedades del productor
        config = {
            'bootstrap.servers': broker,  # Cambia esto a la dirección de tu cluster Kafka
        }

        # Crea una instancia del productor
        producer = Producer(config)
        return producer

    def productor_mapa(self, broker):
        # Configura las propiedades del productor
        config = {
            'bootstrap.servers': broker,  # Cambia esto a la dirección de tu cluster Kafka
        }

        # Crea una instancia del productor
        producer = Producer(config)
        return producer

    def consumidor_posiciones(self, broker):
        # Configura las propiedades del consumidor
        config = {
            'bootstrap.servers': broker,  # Cambia esto a la dirección de tu cluster Kafka
            'group.id': 'grupo_2',
            'auto.offset.reset': 'latest'  # Comienza desde el inicio del topic
        }

        # Crea una instancia del consumidor
        consumer = Consumer(config)
        return consumer

    #Operaciones en kafka
    def enviar_por_kafka_destinos(self, productor):
        topic = "destino"
        #Selecciono la primera figura y la elimino del vector
        figura = self.figuras[0]
        del self.figuras[0]

        #Envio el mensaje con la id de cada drone y con sus posiciones destino
        print(figura)
        for drone in figura[1]:
            pos = drone[1].split(',')
            mensaje = f"{str(drone[0])} {str(pos[0])} {str(pos[1])}"
            productor.produce(topic, value=mensaje)
            print(mensaje)

        # Espera a que el mensaje se envíe
        productor.flush()
        time.sleep(3)

    def enviar_mapa(self, productor): #FALTA AÑADIR EL MAPA
        topic = "mapa"
        mensaje = "El mapita"
        productor.produce(topic, value=mensaje)

        # Espera a que el mensaje se envíe
        productor.flush()
        time.sleep(3)

    def escuchar_posicion_drones(self, consumidor):
        topic = "posiciones"
        consumidor.subscribe(topics=[topic])
        
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

        time.sleep(3)

    #Leo las figuras que tenga el archivo Figuras.json y las almaceno en un vector
    def leer_figuras(self):
        # Abre el archivo JSON en modo lectura
        with open('Figuras.json', 'r') as archivo:
            data = json.load(archivo)

        # Itera a través de las figuras en el archivo JSON
        for figura in data['figuras']:
            nombre_figura = figura['Nombre']
            drones = []

            # Itera a través de los drones en la figura actual
            for drone in figura['Drones']:
                id_drone = drone['ID']
                posicion = drone['POS']
                drones.append([id_drone, posicion])

            self.figuras.append([nombre_figura, drones])

        # Ahora, 'resultados' contendrá los datos en el formato deseado
        print(self.figuras)
        return True

    #Función encargada de iniciar el espectaculo, se activa cuando
    def start(self, productor_destinos, productor_mapa, consumidor): #FALTA VOVLER A COMPROBAR FIGURAS
        hay_figura = self.leer_figuras()
        try:
            while hay_figura:
                if not self.figuras:
                    hay_figura = False
                else:
                    hay_figura = True
                    self.enviar_por_kafka_destinos(productor_destinos)
                    self.escuchar_posicion_drones(consumidor_posiciones)
                    self.enviar_mapa(productor_mapa)
        except Exception as e:
            print(f"Error en Engine: {e}")

if __name__ == "__main__":
    import sys

    if len(sys.argv) != 5:
        print(len(sys.argv))
        print("ERROR: Los parámetros no son correctos")
        sys.exit(1)

    puerto = sys.argv[1]
    max_drones = int(sys.argv[2])
    ip_puerto_broker = sys.argv[3]
    ip_puerto_weather = sys.argv[4]

    print(f"Escuchando puerto {puerto}")
    print(f"Maximo de drones establecido en {max_drones} drones")

    escuchar_drones = EscucharDrones(int(puerto))  # No se ha proporcionado el código para esta parte
    escuchar_drones.start()

    while not os.path.exists("Figuras.json"):
        time.sleep(1)

    engine = AD_Engine()
    productor_destinos = engine.productor_destinos(ip_puerto_broker)
    productor_mapa = engine.productor_mapa(ip_puerto_broker)
    consumidor_posiciones = engine.consumidor_posiciones(ip_puerto_broker)

    engine.start(productor_destinos, productor_mapa, consumidor_posiciones)

# La parte que falta en el archivo main se debe completar según tus necesidades.
# if __name__ == "__main__":
#    import sys
#
#    if len(sys.argv) != 4:
#        print("ERROR: Los parámetros no son correctos")
#        sys.exit(1)
#
##    puerto = sys.argv[1]
#    max_drones = int(sys.argv[2])
 #   ip_puerto_broker = sys.argv[3]
 #   ip_puerto_weather = sys.argv[4]
##
 #   print(f"Escuchando puerto {puerto}")
#    print(f"Maximo de drones establecido en {max_drones} drones")
#
 #   escuchar_drones = None  # Debes completar esta parte con la lógica de inicio de hilos o procesos
 #   escuchar_drones.start()  # Inicia el hilo para escuchar drones

#    figuras = None  # Debes completar esta parte con la lógica de comprobación de existencia del archivo
 #   while not figuras.exists():
 #       time.sleep(1)

#    engine = AD_Engine()
 #   productor_destinos = engine.productor_destinos(ip_puerto_broker)
  #  productor_mapa = engine.productor_mapa(ip_puerto_broker)
 #   consumidor_posiciones = engine.consumidor_posiciones(ip_puerto_broker)

 #   engine.start(productor_destinos, productor_mapa, consumidor_posiciones)
