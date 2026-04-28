from typing import List

from main.python.Models.Estudio import Estudio
# Asegúrate de que la ruta de importación sea correcta según tu estructura de carpetas
# from main.python.Models.Estudio import Estudio 

class Paciente:
    def __init__(self, id: str, edad: str, espesor_mama_actual: int):
        self.id = id # DNI (String)
        self.edad = edad # String según tu especificación
        self.espesor_mama_actual = int(espesor_mama_actual)
        self.estudios: List[Estudio] = []

    def agregar_estudio(self, estudio: Estudio):
        """Añade un objeto de tipo Estudio a la lista del paciente."""
        self.estudios.append(estudio)

    def __str__(self):
        return (
            f"Paciente: {self.id} | Edad: {self.edad} | "
            f"Espesor Actual: {self.espesor_mama_actual}mm | "
            f"Total Estudios: {len(self.estudios)}"
        )