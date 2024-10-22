
import time
import threading
from confluent_kafka import Consumer, Producer, KafkaError
import json
from EscucharDrone import EscucharDrone
import os
import socket
import copy
from Map import Map
import requests
import sqlite3
import ssl

import logging

# Obtener la dirección IP de la máquina
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
import datetime

#Thread para escuchar drones en paralelo a la ejecucion del espectaculo.
@logger_decorator
class RecibirDrones(threading.Thread):
    #Inicializa el tread con el puerto de escucha del servidor.
    def __init__(self, puerto):
        super().__init__()
        self.logger = logger
        self.puerto = puerto

    #Codigo que se ejecutará al hacer .start.
    #Crea el servidor concurrente para escuchar varios drones a la vez
    #Al unirse un nuevo drone lo separo y trabajo con el mediante la clase thread EscucharDrone
    def run(self):
        self.logger.info("Iniciando servidor de drones")
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
            
            #Envuelvo el socket en ssl
            context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
            context.load_cert_chain(certfile='engine_dron/engine_dron.pem', keyfile='engine_dron/key.pem')
            ssock = context.wrap_socket(s_socket, server_side=True)
            
            # Me mantengo en escucha de nuevos drones mientras no quiera detener el Engine
            while True:
                try:
                    print("Esperando drone...")
                    conn, addr = ssock.accept()

                    #Escucho al drone que se acaba de conectar
                    escuchar = EscucharDrone(conn)
                    escuchar.start()

                except Exception as e:
                    logger.error("Error escuchando al drone: ", e)
                    print("Error para escuchar al drone: ", e)
        except Exception as e:
            self.logger.error("Error creando servidor: ", e)
            print("Error creando servidor: ", e)

#Clase principal
class AD_Engine:
    #El engine tendrá los dronesFinales que deben haber para que este terminada la figura.
    #Tendrá los dronesActuales en cada momento, todas las figuras leidas del fichero y si debe parar la ejecucion por el clima o por otro problema.
    def __init__(self):
        #Formato de cada drone añadido: [id,[posX,posY]]
        self.figuras = []
        self.dronesFinales = []
        self.detener = False
        self.detener_por_clima = False
        self.en_base_por_clima = False
        self.last_position_received = {} # Diccionario que almacena la última posición recibida de cada drone y el momento de recibirla
        self.logger = logger

    #Limpia la terminal para mejor legibilidad
    def clear_terminal(self):
        os.system('cls' if os.name == 'nt' else 'clear')

    #Me conecto a cada topic con el rol correspondiente
    @logger_decorator
    def productor_destinos(self, broker):
        # Configura las propiedades del productor
        config = {
            'bootstrap.servers': broker,  # Cambia esto a la dirección de tu cluster Kafka
        }
        try:
            self.logger.info("Creando productor de destinos")
            # Crea una instancia del productor
            producer = Producer(config)
        except Exception as e:
            self.logger.error("Error creando productor de destinos: ",e)
            print("Error creando consumidor de posiciones: ",e)

        return producer
    
    @logger_decorator
    def consumidor_posiciones(self, broker):
        # Configura las propiedades del consumidor
        config = {
            'bootstrap.servers': broker,  #El broker es la ip y el puerto
            'group.id': 'grupo_9',  #El grupo es el mismo para todos los consumidores
            'auto.offset.reset': 'latest',  # Comienza desde el inicio del topic
            'enable.auto.commit': False,  # Deshabilita la confirmación automática
        }
        
        try:
            self.logger.info("Creando consumidor de posiciones")
            # Crea una instancia del consumidor
            consumer = Consumer(config)
        except Exception as e:
            self.logger.error("Error creando consumidor de posiciones: ",e)
            print("Error creando consumidor de posiciones: ",e)

        return consumer

    #Operaciones en kafka
    #Envia los destinos Finales a los drones por kafka
    @logger_decorator
    def enviar_por_kafka_destinos(self, productor):
        try:
            self.logger.info("Enviando destinos")
            topic = "destino"
            #Envio los destinos de los que se encuentran aqui

            for drone in self.dronesFinales:
                pos = drone[1]
                mensaje = f"{str(drone[0])} {str(pos[0])} {str(pos[1])}"
                productor.produce(topic, value=mensaje)
                productor.flush()
            self.logger.info("Destinos enviados")
        except Exception as e:
            self.logger.error("Error enviando destinos: ",e)
            print("Error enviando destinos: ",e)

    
    @logger_decorator
    def actualizarPosicionesBD(self, drone):
        try:
            self.logger.info("Actualizando posiciones")
            conn = sqlite3.connect('registry')

            cursor = conn.cursor()

            id = drone[0]
            
            posicion = str(drone[1])

            cursor.execute("UPDATE drones SET posicion = ? WHERE id_virtual = ?", (posicion, id,))

            conn.commit()

            conn.close()
            self.logger.info("Posiciones actualizadas")
        except Exception as e:
            self.logger.info("Error actualizando posiciones: ",e)
            print("Error actualizando posiciones: ",e)
    
    def pintarVerde(self, id_virtual):
        try:
            conn = sqlite3.connect('registry')

            cursor = conn.cursor()

            cursor.execute("UPDATE drones SET fin = ? WHERE id_virtual = ?", ("ok", id_virtual,))

            conn.commit()

            conn.close()

        except Exception as e:
            print("Error pintando de verde: ",e)

    @logger_decorator
    def comprobarFinBD(self):
        try:
            self.logger.info("Comprobando fin")
            conn = sqlite3.connect('registry')

            cursor = conn.cursor()

            cursor.execute("SELECT id_virtual, posicion FROM drones")

            rows = cursor.fetchall()

            if rows is not None:
                for drone in rows:
                    id_virtual, posicion = drone
                    pos = eval(posicion)
                    for droneF in self.dronesFinales:
                        if droneF[0] == id_virtual:
                            if droneF[1] == pos:
                                self.pintarVerde(id_virtual)
                                break

            conn.close()
            self.logger.info("Fin comprobado")
        except Exception as e:
            self.logger.error("Error comprobando fin: ",e)
            print("Error comprobando fin: ",e)
    
    def actualizar_momento(self,id_virtual):
        self.last_position_received[id_virtual] = datetime.datetime.now()
        
    def check_drones(self):
        # Conectar a la base de datos
        conn = sqlite3.connect('registry')
        cur = conn.cursor()
    
        while True:
            now = datetime.datetime.now()
            for id_virtual, last_received in self.last_position_received.items():
                if (now - last_received).total_seconds() > 10:  # Si ha pasado más de 10 segundos
                    print(f"El drone {id_virtual} no está activo")
                    
                    cur.execute("UPDATE drones SET activos = ? WHERE id_virtual = ?", (0, id_virtual,))
                    
                    conn.commit()
                else:
                    cur.execute("UPDATE drones SET activos = ? WHERE id_virtual = ?", (1, id_virtual,))
                    
                    conn.commit()
                    
            time.sleep(10)  # Esperar 10 segundos antes de comprobar de nuevo

        conn.close()
            
    #Escucha las posiciones que le van llegando de los drones.
    @logger_decorator
    def escuchar_posicion_drones(self, consumidor):
        try:
            self.logger.info("Escuchando posiciones")
            topic = "posiciones"
            consumidor.subscribe(topics=[topic])
            
            # Iniciar el hilo de comprobación de los drones activos
            threading.Thread(target=self.check_drones, daemon=True).start()
            
            while not self.figura_completada() and not self.detener and not self.en_base_por_clima:
                
                mensaje = consumidor.poll(0.1)
                if mensaje is not None:
                    if mensaje.error():
                        if mensaje.error().code() == KafkaError._PARTITION_EOF:
                            print('No más mensajes en la partición')
                        else:
                            print('Error al recibir mensaje: {}'.format(mensaje.error()))
                    else:
                        valores = mensaje.value().decode('utf-8').split()
                        aux = [int(valores[0]),[int(valores[1]),int(valores[2])]]
                        
                        self.actualizar_momento(int(valores[0]))
                        
                        self.actualizarPosicionesBD(aux)

                        self.comprobarFinBD()            
        except Exception as e:
            self.logger.error("Error escuchando posiciones: ",e)
            print("Error escuchando posiciones: ", e)

    #Leo las figuras que tenga el archivo Figuras.json y las almaceno en un vector. Despues de ello elimino el fichero de figuras
    @logger_decorator
    def leer_figuras(self):
        self.logger.info("Leyendo figuras")
        inicio = time.time()
        tiempo_transcurrido = 0
        while not self.figuras and not self.detener and not self.detener_por_clima:
            try:
                #Compruebo si he estad escuchando durante mas de 5 segundos
                tiempo_transcurrido = time.time() - inicio
                if tiempo_transcurrido >= 5:
                    return False

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
            except Exception as e:
                self.logger.error("Error leyendo figuras ya que no hay: ",e)
                pass

        # Eliminar el archivo JSON
        if self.detener_por_clima == False:
            try:
                self.logger.info("Eliminando archivo de figuras")
                os.remove('Figuras.json')
                print(f"El archivo {'Figuras.json'} fue eliminado con éxito.")
                self.logger.info("Archivo de figuras eliminado")
            except OSError as e:
                self.logger.error("Error eliminando archivo de figuras: ",e)
                print(f"No se pudo eliminar el archivo {'Figuras.json'}: {e}")

        return True

    #Veo si todos los drones estan en la base por el clima
    @logger_decorator
    def retirada_clima(self):
        self.logger.info("Comprobando si hay una retirada por clima")
        conn = sqlite3.connect('registry')
        cursor = conn.cursor()

        query = "SELECT * FROM drones"
        cursor.execute(query)
        result = cursor.fetchall()

        for row in result:
            if row[3] != [-1, -1]:
                conn.close()
                return False

        conn.close()
        
        return True

    #Veo si la figura está completada o no
    @logger_decorator
    def figura_completada(self):
        self.logger.info("Comprobando si la figura esta completada")
        if self.detener_por_clima == True and self.retirada_clima() == True:
            en_base_por_clima = True
            return True

        conn = sqlite3.connect('registry')
        cursor = conn.cursor()

        query = "SELECT * FROM drones"
        cursor.execute(query)
        result = cursor.fetchall()

        self.dronesActuales = []
        for row in result:
            self.dronesActuales.append([row[1], eval(row[4])])
            
        iguales = True
        for drone in self.dronesFinales:
            if drone not in self.dronesActuales:
                iguales = False
                break
            
        return iguales

    #Operaciones con sockets
    #Leo el socket controladamente
    @logger_decorator
    def lee_socket(self, p_datos):
        self.logger.info("Leyendo del socket")
        try:
            aux = self.drone.recv(1024)
            p_datos = aux.decode()
        except Exception as e:
            self.logger.error("Error leyendo del socket: ",e)
            print(f"Error leyendo del socket: {e}")
        return p_datos

    #Escribe en el socket de forma controlada
    @logger_decorator
    def escribe_socket(self, p_datos):
        self.logger.info("Escribiendo en el socket")
        try:
            self.drone.send(p_datos.encode())
        except Exception as e:
            self.logger.error("Error escribiendo en el socket: ",e)
            print(f"Error escribiendo en el socket: {e}")

    #Motivos para detener la ejecucion
    #Se detiene debido al clima
    @logger_decorator
    def stop_clima(self):
        self.logger.info("Deteniendo por clima")
        self.detener_por_clima = True
        
        for index in range(len(self.dronesFinales)):
            self.dronesFinales[index][1] = [-1,-1]
            
        self.todosRojo()

    #Se detiene por un mal funcionamiento
    @logger_decorator
    def stop(self):
        self.logger.info("Deteniendo por mal funcionamiento")
        self.detener = True

    #Función encargada de iniciar el espectaculo, se activa cuando existe el fichero Figuras.json
    #Recibe por parametros el productor de destinos, de mapa y el consumidor de posiciones de los drones
    #Se ejecuta mientras hayan figuras o se detenga la ejecucion
    @logger_decorator
    def todosRojo(self):
        self.logger.info("Poner todos los drones a rojo")
        try:
            conn = sqlite3.connect('registry')

            cursor = conn.cursor()

            cursor.execute("UPDATE drones SET fin = ?", ("no",))

            conn.commit()

            conn.close()

        except Exception as e:
            self.logger.error("Error poniendolos a rojo: ",e)
            print("Error pintando de rojo: ",e)

    @logger_decorator
    def start(self, productor_destinos, consumidor_posiciones):
        self.logger.info("Iniciando espectaculo")
        hay_figura = self.leer_figuras()    #Lee las figuras del fichero json
        try:
            while hay_figura and self.detener == False and self.en_base_por_clima == False:
                if not self.figuras:
                    hay_figura = False
                else:
                    #Asegurar que todos los drones actuales tienen los mismos finales
                    #dronesActuales_figura_anterior = self.dronesActuales.copy()
                    drones_figura_anterior = self.dronesFinales.copy()
                    #print("")
                    #print("Drones de la figura anterior: " + str(drones_figura_anterior))
                    #print("Figura actual: " + str(self.figuras[0][1]))
                    #print("Drones actuales: " + str(self.dronesActuales))



                    #print("Drones Finales antes")
                    #for drone in drones_figura_anterior:
                    #    print(drone)

                    self.dronesFinales = self.figuras[0][1]  #Asigna a los dronesFinales los valores que tendrá para la figura actual

                    #Comprueba si el drone estaba en la figura de antes y en la de ahora no está.
                    #Si no esta le asigna la posicion [0,0] para que salga de la pantalla
                    for droneA in drones_figura_anterior:
                        existe = False
                        for droneN in self.dronesFinales:
                            if droneA[0] == droneN[0]:
                                existe = True
                                break

                        if existe == False:
                            self.dronesFinales.append([droneA[0], [0, 0]])

                    #print("Drones Finales despues: " + str(self.dronesFinales))

                    #Descomentar para ver los drones que no se utliizan en la figura actual
                    ####################time.sleep(5)

                    #print("Drones Finales despues")
                    #for drone in self.drones:
                    #    print(drone)

                    #time.sleep(5)
                    #Comprueba los drones que esten activos actualmente
                    #Espero a que no exista ya el mismo hilo.

                    #Escucha las posiciones de los drones en todo momento
                    escucharPosiciones = threading.Thread(target=self.escuchar_posicion_drones,args=(consumidor_posiciones,))
                    escucharPosiciones.start()

                    #Mientras que no se haya completado la figura o no se haya detenido por ninguna causa, envia los destinos finales para los drones
                    #y el mapa actual a los drones.
                    while not self.figura_completada() and self.detener == False and not self.en_base_por_clima:
                        self.enviar_por_kafka_destinos(productor_destinos) #Envio los destinos a los drones
                        ##########self.enviar_mapa(productor_mapa) #Envio el mapa una ultima vez porque sale del bucle antes de imprimir y enviar el ultimo mensaje
                        #Espero a que no exista ya el mismo hilo.
                        time.sleep(1)


                    #############self.enviar_mapa(productor_mapa) #Envio el mapa una ultima vez porque sale del bucle antes de imprimir y enviar el ultimo mensaje
                    del self.figuras[0] #Elimina la figura debido a que se ha completado

                    #Si se ha parado por el clima se detiene la ejecucion
                    if self.detener_por_clima == True and self.en_base_por_clima == True:
                        break

                    time.sleep(5)

                    self.todosRojo()
                    #Leo si hay mas figuras y si no hay mas termina el espectaculo.
                    if not self.figuras:
                        hay_figura = self.leer_figuras()
                        if hay_figura == False:

                            for index in range(len(self.dronesFinales)):
                                self.dronesFinales[index][1] = [0,0]

                            escucharPosiciones = threading.Thread(target=self.escuchar_posicion_drones,args=(consumidor_posiciones,))
                            escucharPosiciones.start()

                            while not self.figura_completada():
                                self.enviar_por_kafka_destinos(productor_destinos) #Envio los destinos a los drones
                                #############self.enviar_mapa(productor_mapa) #Envio el mapa una ultima vez porque sale del bucle antes de imprimir y enviar el ultimo mensaje
                                time.sleep(1)

                            self.clear_terminal()
                            print("Espectaculo finalizado")
                            self.stop()
                            return
                    else:
                        hay_figura = True

            #Si la ejecución se ha detenido por el clima sale el mensaje de finalización
            if self.detener_por_clima == True:
                print("CONDICIONES CLIMATICAS ADVERSAS.ESPECTACULO FINALIZADO")

            sys.exit(0)
        except Exception as e:
            self.logger.error("Error durante el espectaculo: ",e)
            print(f"Error en Engine: {e}")

def leerApiKeyOpenWeather(archivoApiKey):
    apiKey = ""

    with open(archivoApiKey, "r") as archivo:
        apiKey = archivo.readline().strip()

    return apiKey

#Controlador del clima. Es un hilo. Recibe por parametros el engine, la ip y el puerto del weather y la ciudad donde tendrá ligar el espectaculo.
#Esta función solicita el clima de la ciudad constantemente. Si la temperatura es <= a cero detiene al engine.
@logger_decorator
def clima(engine, archivoApiKey):
    logger.info("Controlando el clima")
    try:
        ciudad_antigua = ""
        while True:
            with open('ciudad.txt', 'r') as archivo_ciudad:
                ciudad = archivo_ciudad.read().strip()
            
            if ciudad_antigua == "":
                print("Solicitando clima de: " + ciudad)

            if ciudad != ciudad_antigua and ciudad_antigua != "":
                print("Cambiando de ciudad... Nueva ciudad: " + ciudad)
            
            ciudad_antigua = ciudad
            
            apiKey = leerApiKeyOpenWeather(archivoApiKey)

            url = f'https://api.openweathermap.org/data/2.5/weather?q={ciudad}&appid={apiKey}&units=metric'
            
            response = requests.get(url)
            data = response.json()
            
            if response.status_code == 200:
                temperatura = data['main']['temp']
                print("Temperatura actual: " + str(temperatura))

                if temperatura <= 0.0:
                    engine.stop_clima()
                    break

                time.sleep(5)
            
            else:
                print(f'Error en la solicitud: {data["message"]}')
                engine.stop_clima()
                break

        sys.exit(0)
    except FileNotFoundError as fileE:
        logger.error("Error solicitando clima de la ciudad en: ",fileE)
        print("El archivo ciudades.txt no existe")
        engine.stop_clima()

    except Exception as e:
        logger.error("Error durante la solicitud del clima: ",e)
        print("Error solicitando clima: " + str(e))
        print("No se puede realizar el espectaculo")
        engine.stop_clima()


#Programa principal
if __name__ == "__main__":
    import sys
    #Comprobación de parametros
    if len(sys.argv) != 5:
        print(len(sys.argv))
        print("ERROR: Los parámetros no son correctos")
        sys.exit(1)
    #Asignacion de parametros
    puerto = sys.argv[1]
    max_drones = int(sys.argv[2])
    ip_puerto_broker = sys.argv[3]
    archivoApiKey = sys.argv[4]

    print(f"Escuchando puerto {puerto}")
    print(f"Maximo de drones establecido en {max_drones} drones")

    #Ejecuta el hilo para recibir a los drones
    recibir_drones = RecibirDrones(int(puerto))
    recibir_drones.start()

    #Mientras no exista el fichero Figuras.json no hago nada
    while not os.path.exists("Figuras.json"):
        time.sleep(1)

    engine = AD_Engine()

    

    #Al iniciar el espectaculo creo el controlador del clima
    controlarClima = threading.Thread(target=clima,args=(engine, archivoApiKey,))
    controlarClima.start()

    #Creo los productores de mapa y destino y el consumidor de posiciones.
    productor_destinos = engine.productor_destinos(ip_puerto_broker)
    #########productor_mapa = engine.productor_mapa(ip_puerto_broker)
    consumidor_posiciones = engine.consumidor_posiciones(ip_puerto_broker)

    time.sleep(2)

    #Si el clima no es malo comienzo el espectaculo.
    if engine.detener_por_clima == False:
        engine.start(productor_destinos, consumidor_posiciones) #productor_mapa
    else:
        print("CONDICIONES CLIMATICAS ADVERSAS.ESPECTACULO FINALIZADO")
    sys.exit(0)
