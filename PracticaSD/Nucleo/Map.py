class Drone:
    def __init__(self, _id):
        self.id = _id
        self.coord_x = 0
        self.coord_y = 0
        self.pos_final = False

    def set_coordenada(self, x, y):
        self.coord_x = x
        self.coord_y = y

    def set_pos_final(self, pos_final):
        self.pos_final = pos_final


class Map:
    def __init__(self):
        self.filas = 19
        self.columnas = 19
        self.mapa = ""

    def get_filas(self):
        return self.filas

    def get_columnas(self):
        return self.columnas

    def print_mapa(self, drones):
        rojo = "\u001B[91m"
        verde = "\u001B[32m"
        reset = "\u001B[0m"
        for i in range(0, 21):
            for j in range(0, 21):
                if i == 0:
                    if j == 0:
                        self.mapa += "     1   2   3   4   5   6   7   8   9  10  11  12  13  14  15  16  17  18  19  20 "
                elif j == 0:
                    if i < 10:
                        self.mapa += f" {i} "
                    else:
                        self.mapa += f"{i} "
                else:
                    existe = False
                    for drone in drones:
                        if drone.coord_y == i and drone.coord_x == j:
                            existe = True
                            if drone.id < 10:
                                if drone.pos_final:
                                    self.mapa += f"{verde} {drone.id} {reset} "
                                else:
                                    self.mapa += f"{rojo} {drone.id} {reset} "
                            else:
                                if drone.pos_final:
                                    self.mapa += f"{verde} {drone.id} {reset} "
                                else:
                                    self.mapa += f"{rojo} {drone.id} {reset} "
                    if not existe:
                        self.mapa += "   "
                self.mapa += " "
            self.mapa += "\n\n"

    def to_string(self, drones):
        self.mapa = ""
        self.mapa += "\r"
        self.print_mapa(drones)
        return self.mapa

