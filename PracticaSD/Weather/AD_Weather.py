import socket
import sys
import time
import threading

#Thread para escuchar drones en paralelo a la ejecucion del espectaculo.
class AD_Weather(threading.Thread):
    #Inicializa el thread con el socket del drone y los vectores de los datos vacios.
    def __init__(self, skEngine):
        super().__init__()
        self.engine = skEngine
        self.ciudades = []
        self.temperaturas = []

    #Lee del socket de forma controlada
    def leer_socket(self, sock):
        try:
            datos = sock.recv(1024).decode('utf-8')
            return datos
        except Exception as e:
            print("Error al leer datos del socket:", e)
        return ""

    #Escribe en el socket de forma controlada
    def escribe_socket(self, sock, p_datos):
        try:
            sock.send(p_datos.encode('utf-8'))
        except Exception as e:
            print("Error al enviar datos socket: ", e)

    #Actualiza los vectores de ciudades y temperaturas con los datos del archivo climas.txt
    def actualizar_temperaturas(self):
        ciudades_aux = []
        temperaturas_aux = []

        try:
            with open("climas.txt", "r") as archivo:
                for linea in archivo:
                    partes = linea.split(" ")
                    #Si la linea tiene dos partes se añade a los vectores
                    if len(partes) == 2:
                        ciudad = partes[0]
                        temperatura = float(partes[1])
                        ciudades_aux.append(ciudad)
                        temperaturas_aux.append(temperatura)

        except Exception as e:
            print("Error al abrir la base de datos de climas: ", e)
        else:
            self.ciudades = ciudades_aux
            self.temperaturas = temperaturas_aux

    #Devuelve la temperatura actual de la ciudad pasada por parametro y si no existe devuelve -1.0
    def clima_actual(self, ciudad):
        for i in range(len(self.ciudades)):
            if self.ciudades[i] == ciudad:
                return self.temperaturas[i]
        return -1.0

    #Codigo que se ejecutará al hacer .start
    def run(self):
        while True:
            self.actualizar_temperaturas()

            print("Esperando petición...")

            peticion = self.leer_socket(conn)
            print(peticion)

            if len(peticion) > 0:
                temperatura = self.clima_actual(peticion)

                print("Enviando temperatura en " + peticion + ": " + str(temperatura))
                self.escribe_socket(conn, str(temperatura))

                #Si la temperatura es menor o igual a 0.0 se finaliza el espectaculo
                if float(temperatura) <= 0.0:
                    print("CONDICIONES CLIMATICAS ADVERSAS. NOTIFICANDO CANCELACIÓN DE ESPECTÁCULO\n")

            time.sleep(1)
        self.engine.close()

#Programa principal
if __name__ == "__main__":
    try:
        #Comprueba que se ha introducido el puerto de escucha como argumento
        if len(sys.argv) < 2:
            print("Especifica el puerto de escucha")
            sys.exit(1)

        puerto = int(sys.argv[1])

        # Obtiene la dirección IP local de la red actual
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
        s.close()

        # Creo el servidor a la espera de drones que me llamen por ahí
        s_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s_socket.bind((local_ip, puerto))
        s_socket.listen()
        while True:
            conn, addr = s_socket.accept()
            try:
                # Creo un hilo para escuchar al drone
                escuchar = AD_Weather(conn)
                escuchar.start()
            except Exception as e:
                print("Error para escuchar al engine: ", e)

    except Exception as e:
        print("Error al crear el servidor del clima:", e)
