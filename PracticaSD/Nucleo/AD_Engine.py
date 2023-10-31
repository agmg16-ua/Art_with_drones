import time
import threading
from confluent_kafka import Consumer, Producer, KafkaError

import EscucharDrone

import socket

class EscucharDrones(threading.Thread):
    def __init__(self, puerto):
        super().__init__()
        self.puerto = puerto
        self.detener = False

    def detener(self):
        self.detener = True

    def run(self):
        try:
            # Creo el servidor a la espera de drones que me llamen por ahí
            s_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s_socket.bind(('localhost', self.puerto))
            s_socket.listen()

            # Me mantengo en escucha de nuevos drones mientras no quiera detener el Engine
            while not self.detener:
                print("Esperando drone...")
                conn, addr = s_socket.accept()

                try:
                    escuchar = EscucharDrone(conn)
                    escuchar.start()
                except Exception as e:
                    print("Error:", e)

            # Cierro el servidor
            s_socket.close()

        except Exception as e:
            print("Error:", e)


class Drone:
    def __init__(self, id):
        self.id = id
        self.coordenada = (0, 0)

    def set_coordenada(self, x, y):
        self.coordenada = (x, y)

class AD_Engine:
    def __init__(self):
        self.drones = []

    def productor_destinos(self, broker):
        return KafkaProducer(bootstrap_servers=broker, value_serializer=str)

    def productor_mapa(self, broker):
        return KafkaProducer(bootstrap_servers=broker, value_serializer=str)

    def consumidor_posiciones(self, broker):
        grupo = "grupo_9"
        return KafkaConsumer(bootstrap_servers=broker, auto_offset_reset='earliest',
                             group_id=grupo, value_deserializer=str)

    def enviar_por_kafka_destinos(self, productor, palabras):
        topic = "destino"
        mensaje = f"{palabras[1]} {palabras[2]} {palabras[3]}"
        productor.send(topic, value=mensaje)

    def leer_figura(self, productor):
        archivo = open("figuras.txt", "r")
        hay_figura = True
        while hay_figura:
            linea = archivo.readline()
            if "</figura>" in linea:
                hay_figura = False
            else:
                palabras = [p.strip('<>') for p in linea.split('<') if p]
                self.enviar_por_kafka_destinos(productor, palabras)
        archivo.close()

    def enviar_mapa(self, productor):
        topic = "mapa"
        mensaje = "El mapita"
        productor.send(topic, value=mensaje)

    def escuchar_posicion_drones(self, consumidor):
        topic = "posiciones"
        consumidor.subscribe([topic])
        for mensaje in consumidor:
            palabras = mensaje.value.split()
            id_dron = int(palabras[1])
            coordenada_x = int(palabras[2])
            coordenada_y = int(palabras[3])

            # Compruebo si el mensaje recibido es de un dron que ya existe en mi lista de drones
            ya_existe = False
            for dron in self.drones:
                if dron.id == id_dron:
                    ya_existe = True
                    dron.set_coordenada(coordenada_x, coordenada_y)
                    break

            if not ya_existe:
                dron = Drone(id_dron)
                dron.set_coordenada(coordenada_x, coordenada_y)
                self.drones.append(dron)

    def start(self, productor_destinos, productor_mapa, consumidor):
        hay_figura = True
        while hay_figura:
            self.leer_figura(productor_destinos)
            self.escuchar_posicion_drones(consumidor)
            self.enviar_mapa(productor_mapa)

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

    escuchar_drones = EscucharDrone(target=run)  # No se ha proporcionado el código para esta parte
    escuchar_drones.start()

    figuras = open('figuras.txt', 'r')  # No se ha proporcionado el código para esta parte
    while not figuras.exists():
        time.sleep(1)

    engine = AD_Engine()
    productor_destinos = engine.productor_destinos(ip_puerto_broker)
    productor_mapa = engine.productor_mapa(ip_puerto_broker)
    consumidor_posiciones = engine.consumidor_posiciones(ip_puerto_broker)

    engine.start(productor_destinos, productor_mapa, consumidor_posiciones)
    try:
        while hay_figura:
            self.leer_figura(productor_destinos)
            self.escuchar_posicion_drones(consumidor_posiciones)
            self.enviar_mapa(productor_mapa)
    except Exception as e:
        print(f"Error en Engine: {e}")

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
