import time
import threading
from confluent_kafka import Consumer, Producer, KafkaError
import json
from EscucharDrone import EscucharDrone
import os
import socket
import copy
from Map import Map

#Thread para escuchar drones en paralelo a la ejecucion del espectaculo.
class RecibirDrones(threading.Thread):
    #Inicializa el tread con el puerto de escucha del servidor.
    def __init__(self, puerto):
        super().__init__()
        self.puerto = puerto

    #Codigo que se ejecutará al hacer .start.
    #Crea el servidor concurrente para escuchar varios drones a la vez
    #Al unirse un nuevo drone lo separo y trabajo con el mediante la clase thread EscucharDrone
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
            while True:
                try:
                    print("Esperando drone...")
                    conn, addr = s_socket.accept()

                    #Escucho al drone que se acaba de conectar
                    escuchar = EscucharDrone(conn)
                    escuchar.start()

                except Exception as e:
                    print("Error para escuchar al drone: ", e)
        except Exception as e:
            print("Error creando servidor: ", e)

#Clase principal
class AD_Engine:

    #El engine tendrá los dronesFinales que deben haber para que este terminada la figura.
    #Tendrá los dronesActuales en cada momento, todas las figuras leidas del fichero y si debe parar la ejecucion por el clima o por otro problema.
    def __init__(self):
        #Formato de cada drone añadido: [id,[posX,posY]]
        self.figuras = []
        self.dronesFinales = []
        self.dronesActuales = []
        self.dronesDesactivados = []
        self.detener = False
        self.detener_por_clima = False

    #Limpia la terminal para mejor legibilidad
    def clear_terminal(self):
        os.system('cls' if os.name == 'nt' else 'clear')

    #Me conecto a cada topic con el rol correspondiente
    def productor_destinos(self, broker):
        # Configura las propiedades del productor
        config = {
            'bootstrap.servers': broker,  # Cambia esto a la dirección de tu cluster Kafka
        }
        try:
            # Crea una instancia del productor
            producer = Producer(config)
        except Exception as e:
            print("Error creando consumidor de posiciones: ",e)

        return producer

    def productor_mapa(self, broker):
        # Configura las propiedades del productor
        config = {
            'bootstrap.servers': broker,  # Cambia esto a la dirección de tu cluster Kafka
        }
        try:
            # Crea una instancia del productor
            producer = Producer(config)
        except Exception as e:
            print("Error creando productor de mapas: ",e)

        return producer

    def consumidor_posiciones(self, broker):
        # Configura las propiedades del consumidor
        config = {
            'bootstrap.servers': broker,  # Cambia esto a la dirección de tu cluster Kafka
            'group.id': 'grupo_9',
            'auto.offset.reset': 'latest',  # Comienza desde el inicio del topic
            'enable.auto.commit': False  # Deshabilita la confirmación automática
        }
        try:
            # Crea una instancia del consumidor
            consumer = Consumer(config)
        except Exception as e:
            print("Error creando consumidor de posiciones: ",e)

        return consumer

    def consumidor_activos(self,broker):
        # Configura las propiedades del consumidor
        config = {
            'bootstrap.servers': broker,  # Cambia esto a la dirección de tu cluster Kafka
            'group.id': 'grupo_9',
            'auto.offset.reset': 'latest',  # Comienza desde el inicio del topic
            'enable.auto.commit': False  # Deshabilita la confirmación automática
        }
        try:
            # Crea una instancia del consumidor
            consumer = Consumer(config)
        except Exception as e:
            print("Error creando consumidor de posiciones: ",e)

        return consumer

    #Operaciones en kafka
    #Comprueba los drones que están activos realmente y los compara con los dronesActuales
    def comprueba_activos(self,consumidor):
        try:
            topic = "activos"
            consumidor.subscribe(topics=[topic])
            activos = []

            inicio = time.time()

            #Escucha las posiciones de los drones mientras la figura no este completada o no se haya detenido el programa
            while not self.figura_completada() and not self.detener and not self.detener_por_clima:
                mensaje = consumidor.poll(1.0)
                if mensaje is not None:
                    if mensaje.error():
                        if mensaje.error().code() == KafkaError._PARTITION_EOF:
                            print('No más mensajes en la partición')
                        else:
                            print('Error al recibir mensaje: {}'.format(mensaje.error()))
                    else:
                        #Si el drone que envio su id se encuentra entre los desactivados lo vuelvo a incluir a la accion
                        if len(self.dronesDesactivados) != 0:
                            for drone in self.dronesDesactivados:
                                if int(mensaje.value().decode('utf-8')) == drone[0][0]:
                                    self.dronesActuales.append(drone[0])
                                    self.dronesActuales = sorted(self.dronesActuales, key=lambda x: x[0])
                                    self.dronesFinales.append(drone[1])
                                    self.dronesFinales = sorted(self.dronesFinales, key=lambda x: x[0])
                                    self.dronesDesactivados.remove(drone)

                        #Crea un vector que contendra para cada posicion del vector de dronesActuales si está activo o no
                        for i in range(len(self.dronesActuales)):
                            activos.append(False)

                        if len(self.dronesActuales) != 0:
                            #Compruebo las ids que me han mandado en el intervalo de tiempo de 5 segundos
                            index = 0
                            for drone in self.dronesActuales:
                                if int(mensaje.value().decode('utf-8')) == drone[0]:
                                    activos[index] = True
                                    break
                                index += 1
                #Si he leido durante 5 segundos salgo del bucle
                final = time.time() - inicio
                if final >= 3:
                    break


            try:
                #Si alguno no está activo tengo que añadirlo a desactivados
                if len(activos) != 0 and all(activos) == False:
                    #Ahora compruebo los que estan activos y los que no
                    indice = 0
                    for activo in activos:
                        if activo == False:
                            self.dronesDesactivados.append([self.dronesActuales[indice],self.dronesFinales[indice]])
                            del self.dronesActuales[indice]
                            del self.dronesFinales[indice]
                        indice+=1
            except Exception as e:
                print("Es aqui")

        except Exception as e:
            print("Error escuchando activos: ", e)

    #Envia los destinos Finales a los drones por kafka
    def enviar_por_kafka_destinos(self, productor):
        try:
            topic = "destino"
            while  not self.figura_completada() and self.detener == False and self.detener_por_clima == False:
            
                #Envio los destinos de los que se encuentran aqui
                for drone in self.dronesFinales:
                    pos = drone[1]
                    mensaje = f"{str(drone[0])} {str(pos[0])} {str(pos[1])}"
                    productor.produce(topic, value=mensaje)
                    productor.flush()

        except Exception as e:
            print("Error enviando destinos: ",e)

    #Envia el mapa como un string a los drones. Si la figura está completada tambien se añade el mensaje de finalizacion.
    #Para el mapa utilizamos una clase mapa que genera el mapa y tiene una opcion .to_string.
    def enviar_mapa(self, productor):
        try:
            topic = "mapa"
            while not self.figura_completada() and self.detener == False and self.detener_por_clima == False:

                mapa = Map()
                mensaje = ""
                mensaje = mapa.to_string(self.dronesFinales,self.dronesActuales)
                self.clear_terminal()

                if self.figura_completada():
                    mensaje = "*********************************************Figura Completada******************************************************" + "\n" + mensaje

                print(mensaje)
                print(self.dronesActuales)
                print(self.dronesFinales)
                print(self.dronesDesactivados)
                productor.produce(topic, value=mensaje)
                productor.flush()

        except Exception as e:
            print("Error enviando mapa: ",e)

    #Escucha las posiciones que le van llegando de los drones.
    def escuchar_posicion_drones(self, consumidor):
        try:
            topic = "posiciones"
            consumidor.subscribe(topics=[topic])

            #Escucha las posiciones de los drones mientras la figura no este completada o no se haya detenido el programa
            while not self.figura_completada() and not self.detener and not self.detener_por_clima:
                mensaje = consumidor.poll(1.0)
                if mensaje is not None:
                    if mensaje.error():
                        if mensaje.error().code() == KafkaError._PARTITION_EOF:
                            print('No más mensajes en la partición')
                        else:
                            print('Error al recibir mensaje: {}'.format(mensaje.error()))
                    else:
                        valores = mensaje.value().decode('utf-8').split()
                        aux = [int(valores[0]),[int(valores[1]),int(valores[2])]]

                        existe = False


                        #Si el drone esta desactivado no deberian llegarme mensajes de el
                        esta_desactivado = False
                        if len(self.dronesDesactivados) != 0:
                            for drone in self.dronesDesactivados:
                                if aux[0] == drone[0][0]:
                                    esta_desactivado = True

                        if esta_desactivado == False:
                            #Si no hay drones añadidos a mi vector de drones actuales añado al nuevo
                            if len(self.dronesActuales) == 0:
                                self.dronesActuales.append(aux)

                            #Compruebo si el drone ya lo tengo guardado.
                            for dron in self.dronesActuales:
                                if dron[0] == aux[0]:
                                    dron[1] = aux[1]
                                    existe = True
                                    break

                            #Si el drone no existe entre los guardados en actuales lo añado al vector
                            if existe == False:
                                    self.dronesActuales.append(aux)
                                    self.dronesActuales = sorted(self.dronesActuales, key=lambda x: x[0])

        except Exception as e:
            print("Error escuchando posiciones: ", e)

    #Leo las figuras que tenga el archivo Figuras.json y las almaceno en un vector. Despues de ello elimino el fichero de figuras
    def leer_figuras(self):
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
                pass

        # Eliminar el archivo JSON
        try:
            os.remove('Figuras.json')
            print(f"El archivo {'Figuras.json'} fue eliminado con éxito.")
        except OSError as e:
            print(f"No se pudo eliminar el archivo {'Figuras.json'}: {e}")

        return True

    #Veo si la figura está completada o no
    def figura_completada(self):
        return self.dronesActuales == self.dronesFinales

    #Operaciones con sockets
    #Leo el socket controladamente
    def lee_socket(self, p_datos):
        try:
            aux = self.drone.recv(1024)
            p_datos = aux.decode()
        except Exception as e:
            print(f"Error leyendo del socket: {e}")
        return p_datos

    #Escribe en el socket de forma controlada
    def escribe_socket(self, p_datos):
        try:
            self.drone.send(p_datos.encode())
        except Exception as e:
            print(f"Error escribiendo en el socket: {e}")

    #Motivos para detener la ejecucion
    #Se detiene debido al clima
    def stop_clima(self):
        self.detener_por_clima = True

    #Se detiene por un mal funcionamiento
    def stop(self):
        self.detener = True

    #Función encargada de iniciar el espectaculo, se activa cuando existe el fichero Figuras.json
    #Recibe por parametros el productor de destinos, de mapa y el consumidor de posiciones de los drones
    #Se ejecuta mientras hayan figuras o se detenga la ejecucion
    def start(self, productor_destinos, productor_mapa, consumidor_posiciones, consumidor_activos):
        hay_figura = self.leer_figuras()    #Lee las figuras del fichero json
        try:
            while hay_figura and self.detener == False and self.detener_por_clima == False:
                if not self.figuras:
                    hay_figura = False
                else:
                    #Asegurar que todos los drones actuales tienen los mismos finales
                    dronesActuales_figura_anterior = self.dronesActuales.copy()
                    drones_figura_anterior = self.dronesFinales.copy()

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

                    #print("Drones Finales despues")
                    #for drone in self.drones:
                    #    print(drone)

                    #time.sleep(5)

                    #Ejecuta el hilo para mantenerme a la escucha de las posiciones de los drones.
                    posicionesDrones = threading.Thread(target=self.escuchar_posicion_drones,args=(consumidor_posiciones,))
                    posicionesDrones.start()

                    #Comprueba los drones que esten activos actualmente
                    dronesActivos = threading.Thread(target=self.comprueba_activos,args=(consumidor_activos,))
                    dronesActivos.start()

                    #Envio los destinos paralelamente
                    enviarDestinos = threading.Thread(target=self.enviar_por_kafka_destinos,args=(productor_destinos,))
                    enviarDestinos.start()

                    #Envio el mapa paralelamente
                    enviarDestinos = threading.Thread(target=self.enviar_mapa,args=(productor_mapa,))
                    enviarDestinos.start()


                    #Mientras que no se haya completado la figura o no se haya detenido por ninguna causa, envia los destinos finales para los drones
                    #y el mapa actual a los drones.
                    while not self.figura_completada() and self.detener == False and not self.detener_por_clima:
                        #Espero a que no exista ya el mismo hilo.
                        if dronesActivos.is_alive() == False:
                            #Comprueba los drones que esten activos actualmente
                            dronesActivos = threading.Thread(target=self.comprueba_activos,args=(consumidor_activos,))
                            dronesActivos.start()
                        time.sleep(1)


                    self.enviar_mapa(productor_mapa) #Envio el mapa una ultima vez porque sale del bucle antes de imprimir y enviar el ultimo mensaje
                    del self.figuras[0] #Elimina la figura debido a que se ha completado

                    #Espero a que no exista ya el mismo hilo.
                    if dronesActivos.is_alive() == False:
                        #Comprueba los drones que esten activos actualmente
                        dronesActivos = threading.Thread(target=self.comprueba_activos,args=(consumidor_activos,))
                        dronesActivos.start()

                    time.sleep(5)

                    #Leo si hay mas figuras y si no hay mas termina el espectaculo.
                    if not self.figuras:
                        hay_figura = self.leer_figuras()
                        if hay_figura == False:

                            for index in range(len(self.dronesFinales)):
                                self.dronesFinales[index][1] = [0,0]

                            while not self.figura_completada():

                                #Espero a que no exista ya el mismo hilo.
                                if dronesActivos.is_alive() == False:
                                    #Comprueba los drones que esten activos actualmente
                                    dronesActivos = threading.Thread(target=self.comprueba_activos,args=(consumidor_activos,))
                                    dronesActivos.start()

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
                if posicionesDrones.is_alive():
                    posicionesDrones.detener()

            sys.exit(0)
        except Exception as e:
            print(f"Error en Engine: {e}")

#Controlador del clima. Es un hilo. Recibe por parametros el engine, la ip y el puerto del weather y la ciudad donde tendrá ligar el espectaculo.
#Esta función solicita el clima de la ciudad constantemente. Si la temperatura es <= a cero detiene al engine.
def clima(engine,ip_puerto,ciudad):
    try:
        skcliente = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        valores = ip_puerto.split(":")

        skcliente.connect((valores[0], int(valores[1])))

        while True:
            skcliente.send(ciudad.encode('utf-8'))
            temperatura = skcliente.recv(1024).decode('utf-8')
            if float(temperatura) <= 0.0 and len(temperatura) > 0:
                engine.stop_clima()
                break
            time.sleep(2)

        sys.exit(0)
    except Exception as e:
        print("Error solicitando clima: " + str(e))
        print("No se puede realizar el espectaculo")
        engine.stop_clima()

#Programa principal
if __name__ == "__main__":
    import sys
    #Comprobación de parametros
    if len(sys.argv) != 6:
        print(len(sys.argv))
        print("ERROR: Los parámetros no son correctos")
        sys.exit(1)
    #Asignacion de parametros
    puerto = sys.argv[1]
    max_drones = int(sys.argv[2])
    ip_puerto_broker = sys.argv[3]
    ip_puerto_weather = sys.argv[4]
    ciudad = sys.argv[5]

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
    controlarClima = threading.Thread(target=clima,args=(engine,ip_puerto_weather,ciudad))
    controlarClima.start()

    #Creo los productores de mapa y destino y el consumidor de posiciones.
    productor_destinos = engine.productor_destinos(ip_puerto_broker)
    productor_mapa = engine.productor_mapa(ip_puerto_broker)
    consumidor_posiciones = engine.consumidor_posiciones(ip_puerto_broker)
    consumidor_activos = engine.consumidor_activos(ip_puerto_broker)

    time.sleep(2)

    #Si el clima no es malo comienzo el espectaculo.
    if engine.detener_por_clima == False:
        engine.start(productor_destinos, productor_mapa, consumidor_posiciones, consumidor_activos)
    else:
        print("CONDICIONES CLIMATICAS ADVERSAS.ESPECTACULO FINALIZADO")
    sys.exit(0)
