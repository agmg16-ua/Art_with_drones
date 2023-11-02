import time
import threading
from confluent_kafka import Consumer, Producer, KafkaError
import json
from EscucharDrone import EscucharDrone
import os
import socket
import copy
from Map import Map

#Thread para escuchar drones en paralelo
class EscucharDrones(threading.Thread):
    # Contendrá las figuras del fichero
    figuras = []
    def __init__(self, puerto):
        super().__init__()
        self.puerto = puerto
        self.detener_thread = False
        self.socket = None

    def manejar_sigint(signum, frame):
        print("Se ha solicitado detener el servidor.")
        mi_objeto.detener()  # Llama a la función detener() de tu clase

    def detener(self):
        self.detener_thread = True

        sys.exit(0)

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
            while not self.detener_thread:
                print("Esperando drone...")
                conn, addr = s_socket.accept()

                try:
                    escuchar = EscucharDrone(conn)
                    escuchar.start()
                except Exception as e:
                    print("Error para escuchar al drone: ", e)

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
        #Formato de cada drone añadido: [id,[posFinX,posFinY]]
        self.drones = []
        self.figuras = []
        self.dronesActuales = []
        self.detener = False

    def clear_terminal(self):
        os.system('cls' if os.name == 'nt' else 'clear')

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
            'group.id': 'grupo_9',
            'auto.offset.reset': 'latest'  # Comienza desde el inicio del topic
        }

        # Crea una instancia del consumidor
        consumer = Consumer(config)
        return consumer

    #Operaciones en kafka
    def enviar_por_kafka_destinos(self, productor):
        topic = "destino"

        for drone in self.drones:
            pos = drone[1]
            mensaje = f"{str(drone[0])} {str(pos[0])} {str(pos[1])}"
            productor.produce(topic, value=mensaje)
            productor.flush()

    def enviar_mapa(self, productor):
        topic = "mapa"

        mapa = Map()
        mensaje = mapa.to_string(self.drones,self.dronesActuales)
        self.clear_terminal()

        if self.figura_completada():
            mensaje = "*********************************************Figura Completada******************************************************" + "\n" + mensaje

        print(mensaje)
        productor.produce(topic, value=mensaje)
        productor.flush()

        time.sleep(1)

    def escuchar_posicion_drones(self, consumidor):
        topic = "posiciones"
        consumidor.subscribe(topics=[topic])

        while not self.figura_completada():
            mensaje = consumidor.poll(1.0)
            if mensaje is not None:
                if mensaje.error():
                    if mensaje.error().code() == KafkaError._PARTITION_EOF:
                        print('No más mensajes en la partición')
                    else:
                        print('Error al recibir mensaje: {}'.format(mensaje.error()))
                else:
                    # Procesa el mensaje
                    print('Mensaje recibido: {}'.format(mensaje.value()))
                    valores = mensaje.value().decode('utf-8').split()
                    aux = [int(valores[0]),[int(valores[1]),int(valores[2])]]

                    existe = False
                    if len(self.dronesActuales) == 0:
                        self.dronesActuales.append(aux)

                    for dron in self.dronesActuales:
                        if dron[0] == aux[0]:
                            dron[1] = aux[1]
                            existe = True
                    if existe == False:
                        self.dronesActuales.append(aux)
                        self.dronesActuales = sorted(self.dronesActuales, key=lambda x: x[0])

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
                pos = posicion.split(',')
                drones.append([id_drone, [int(pos[0]),int(pos[1])]])
            self.figuras.append([nombre_figura, drones])

        # Eliminar el archivo JSON
        try:
            os.remove('Figuras.json')
            print(f"El archivo {'Figuras.json'} fue eliminado con éxito.")
        except OSError as e:
            print(f"No se pudo eliminar el archivo {'Figuras.json'}: {e}")

        #Si se queda vacío self.figuras devuelvo falso
        if not self.figuras:
            return False

        return True

    #Veo si la figura está completada o no
    def figura_completada(self):
        return self.dronesActuales == self.drones

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

    def stop(self,detener):
        self.detener = detener


    #Función encargada de iniciar el espectaculo, se activa cuando
    def start(self, productor_destinos, productor_mapa, consumidor):
        hay_figura = self.leer_figuras()
        try:
            while hay_figura and self.detener == False:
                if not self.figuras:
                    hay_figura = False
                else:
                    self.drones = self.figuras[0][1]

                    posicionesDrones = threading.Thread(target=self.escuchar_posicion_drones,args=(consumidor,))
                    posicionesDrones.start()

                    while not self.figura_completada() and self.detener == False:
                        self.enviar_por_kafka_destinos(productor_destinos)
                        self.enviar_mapa(productor_mapa)

                    print("*********************************************Figura Completada******************************************************")
                    self.enviar_mapa(productor_mapa) #Envio el mapa una ultima vez porque sale del bucle antes de imprimir y enviar el ultimo mensaje
                    del self.figuras[0]

                    time.sleep(5)

                    if not self.figuras:
                        hay_figura = self.leer_figuras()
                    else:
                        hat_figura = True

            if self.detener == True:
                print("CONDICIONES CLIMATICAS ADVERSAS.ESPECTACULO FINALIZADO")
        except Exception as e:
            print(f"Error en Engine: {e}")

def clima(engine,ip_puerto):
    try:
        skcliente = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        valores = ip_puerto.split(":")

        skcliente.connect((valores[0], int(valores[1])))

        while True:
            cadena = "Alicante"
            skcliente.send(cadena.encode('utf-8'))
            temperatura = skcliente.recv(1024).decode('utf-8')
            if float(temperatura) <= 0.0 and len(temperatura) > 0:
                engine.stop(True)
                break
            time.sleep(1)

    except Exception as e:
        print("Error solicitando clima: " + str(e))
        exit(-1)

    return True

"""
def notificar_Drones(puerto):
    # Obtiene la dirección IP local de la red actual
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    local_ip = s.getsockname()[0]
    s.close()

    # Creo el servidor a la espera de drones que me llamen por ahí
    s_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s_socket.bind((local_ip, puerto))
    s_socket.listen()

    conn, addr = s_socket.accept()
    while True:
"""

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

    controlarClima = threading.Thread(target=clima,args=(engine,ip_puerto_weather))
    controlarClima.start()

    productor_destinos = engine.productor_destinos(ip_puerto_broker)
    productor_mapa = engine.productor_mapa(ip_puerto_broker)
    consumidor_posiciones = engine.consumidor_posiciones(ip_puerto_broker)
    time.sleep(2)

    if engine.detener == False:
        engine.start(productor_destinos, productor_mapa, consumidor_posiciones)

    if escuchar_drones.is_alive() == True:
        escuchar_drones.detener()

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
