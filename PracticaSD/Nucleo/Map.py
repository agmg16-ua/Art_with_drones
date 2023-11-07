import time
import sys
import os
import copy

"""
class Drone:
    def _init_(self, _id):
        self.id = _id
        self.coord_x = 0
        self.coord_y = 0
        self.pos_final = False

    def set_coordenada(self, x, y):
        self.coord_x = x
        self.coord_y = y

    def set_pos_final(self, pos_final):
        self.pos_final = pos_final
"""

#Clase para generar el mapa
class Map:
    #Inicia el tamaño del mapa y el string que contiene el mapa a vacio
    def _init_(self):
        self.filas = 19
        self.columnas = 19
        self.mapa = ""

    #Devuelve las filas del mapa
    def get_filas(self):
        return self.filas

    #Devuelve las columnas del mapa
    def get_columnas(self):
        return self.columnas

    #Método principal para generar el mapa
    #Recibe las posiciones finales de los drones (drones) y los drones que hay en el sistema (dronesActuales)
    def print_mapa(self, drones, dronesActuales):
        rojo = "\u001B[91m"
        verde = "\u001B[32m"
        reset = "\u001B[0m"

        #Recorre el mapa
        for i in range(0, 21):
            for j in range(0, 21):

                #Si es la primera fila escribe los numeros de las columnas
                if i == 0:
                    if j == 0:
                        self.mapa += "     1   2   3   4   5   6   7   8   9  10  11  12  13  14  15  16  17  18  19  20 "

                #Si es la primera columna escribe los numeros de las filas
                elif j == 0:
                    if i < 10:
                        self.mapa += f" {i} "
                    else:
                        self.mapa += f"{i} "
                
                #Si no escribe el mapa
                else:
                    existe = False #Variable para saber si en esa posición hay un drone
                    for droneActual in dronesActuales:
                        droneFinal = []

                        #Encontrar posicion final del drone y se guarda para acceder más fácilmente
                        for drone in drones:
                            if drone[0] == droneActual[0]:
                                droneFinal = drone

                        #Si hay un drone en esa posición se escribe en el mapa
                        if droneActual[1][1] == i and droneActual[1][0] == j:
                            existe = True
                            if droneActual[0] < 10:
                                if droneActual[1][0] == droneFinal[1][0] and droneActual[1][1] == droneFinal[1][1]:
                                    self.mapa += f" {verde}{droneActual[0]}{reset} "
                                else:
                                    self.mapa += f" {rojo}{droneActual[0]}{reset} "
                            else:
                                if droneActual[1][0] == droneFinal[1][0] and droneActual[1][1] == droneFinal[1][1]:
                                    self.mapa += f"{verde}{droneActual[0]}{reset} "
                                else:
                                    self.mapa += f"{rojo}{droneActual[0]}{reset} "
                            break
                    
                    #Si no hay un drone en esa posición se escribe un espacio vacio
                    if existe == False:
                        self.mapa += "   "

                #Se deja un espacio entre las columnas
                self.mapa += " "
            
            #Se deja un espacio entre las filas
            self.mapa += "\n\n"

    #Método para convertir los drones en un mapa en formato string
    def to_string(self, drones, dronesActuales):
        dronesAux = drones.copy() #Copia las posiciones finales para no modificar el original

        if len(dronesActuales) == 0:
            dronesAux = [[0, [0, 0]]]
        
        #Si no existe el drone en la figura (posiciones finales) actual se añade la posicion de la base
        for actual in dronesActuales:
            existe = False
            for buscando in dronesAux:
                if actual[0] == buscando[0]:
                    existe = True
            
            if existe == False:
                dronesAux.append([actual[0], [0, 0]])

        #print(dronesAux)
        #print(dronesActuales)

        #Se llama al método para generar el mapa
        self.mapa = ""
        sys.stdout.write("\b")
        self.print_mapa(dronesAux, dronesActuales)
        return self.mapa

#Método para limpiar la terminal
def clear_terminal():
    os.system('cls' if os.name == 'nt' else 'clear')

"""
if _name_ == "_main_":

    dronesActuales = [[1, [1, 2]], [2, [5, 6]], [3, [4, 4]], [4, [1, 2]]]

    drones = [[1, [1, 1]], [2, [5, 5]], [3, [4, 2]], [4, [1, 2]]]

    mapa = Map()

    clear_terminal()
    print(mapa.to_string(drones, dronesActuales))

    time.sleep(3)
    clear_terminal()

    dronesActuales[0][1][1] = 5


    print(mapa.to_string(drones, dronesActuales))
"""
