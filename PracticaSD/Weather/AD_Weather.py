import socket
import sys

class AD_Weather:
    def __init__(self):
        self.ciudades = []
        self.temperaturas = []

    def leer_socket(self, sock):
        try:
            datos = sock.recv(1024).decode('utf-8')
            return datos
        except Exception as e:
            print("Error:", e)
        return ""

    def escribe_socket(self, sock, p_datos):
        try:
            sock.send(p_datos.encode('utf-8'))
        except Exception as e:
            print("Error:", e)

    def actualizar_temperaturas(self):
        ciudades_aux = []
        temperaturas_aux = []

        try:
            with open("climas.txt", "r") as archivo:
                for linea in archivo:
                    partes = linea.split()
                    if len(partes) == 2:
                        ciudad = partes[0]
                        temperatura = float(partes[1])
                        ciudades_aux.append(ciudad)
                        temperaturas_aux.append(temperatura)

        except Exception as e:
            print(e)
        else:
            self.ciudades = ciudades_aux
            self.temperaturas = temperaturas_aux

    def clima_actual(self, ciudad):
        for i in range(len(self.ciudades)):
            if self.ciudades[i] == ciudad:
                return self.temperaturas[i]
        return -1.0

if __name__ == "__main__":
    try:
        if len(sys.argv) < 2:
            print("Especifica el puerto de escucha")
            sys.exit(1)

        puerto = int(sys.argv[1])

        s_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s_socket.bind(('localhost', puerto))
        s_socket.listen(1)

        while True:
            clima = AD_Weather()
            clima.actualizar_temperaturas()

            print("Esperando petición...")
            conn, addr = s_socket.accept()

            peticion = clima.leer_socket(conn)
            print(peticion)

            temperatura = clima.clima_actual(peticion)

            print("Enviando temperatura en " + peticion + ": " + str(temperatura))
            clima.escribe_socket(conn, str(temperatura))
            conn.close()

    except Exception as e:
        print("Error:", e)
