from typing import List
from main.python.Models.Estudio import Estudio

class Paciente:

    #Representamos a un Paciente en el sistema medico, el cual gestionamos sus datos clínicos 
    # y el historial de los estudios mamográficos realizados.
    def __init__(self, id: str, edad: str, espesor_mama_actual: int):
        self.id = id 
        self.edad = edad 
        self.espesor_mama_actual = int(espesor_mama_actual)
        self.estudios: List[Estudio] = []

    def agregar_estudio(self, estudio: Estudio):
        self.estudios.append(estudio)

    
    def __str__(self):
        return (
            f"Paciente: {self.id} | Edad: {self.edad} | "
            f"Espesor: {self.espesor_mama_actual}mm | "
            f"Dosis Efectiva: {self.calcular_dosis_efectiva():.3f} mGy"
        )