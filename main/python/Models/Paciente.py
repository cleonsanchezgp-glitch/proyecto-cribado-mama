from datetime import date
from typing import List

from Estudio import Estudio


class Paciente:
    #tengo que agregar un id paciente 
    def __init__(self, id: str, edad: int, espesor_mama: int):
        self.id = id
        self.edad = edad
        self.espesor_mama = espesor_mama
        # Lista para agrupar todas las exposiciones/proyecciones
        self.estudios: List[Estudio] = [] #

    def agregar_estudio(self, estudio: Estudio):
        #.append es lo mismo que el .add en java
        self.estudios.append(estudio)

    def __str__(self):
        return (f"Paciente: {self.id} ({self.edad} años) | "
                f"Espesor de la Mama: {self.espesor_mama} | "
                f"Exposiciones: {len(self.estudios)}")