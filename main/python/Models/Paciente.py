from typing import List
from main.python.Models.Estudio import Estudio

class Paciente:
    #tengo que agregar un id paciente 
    def __init__(self, id: str, edad: str, espesor_mama_actual: int):
        self.id = id 
        self.edad = edad 
        self.espesor_mama_actual = int(espesor_mama_actual)
        self.estudios: List[Estudio] = []

    def agregar_estudio(self, estudio: Estudio):
        self.estudios.append(estudio)

    # --- NUEVOS MÉTODOS MATEMÁTICOS ---
    
    def calcular_dosis_glandular_total(self) -> float:
        """Suma la dosis de absolutamente todas las fotos (estudios) de este paciente."""
        return sum(estudio.dosis_glandular for estudio in self.estudios)

    def calcular_dosis_efectiva(self) -> float:
        """Dosis Total * Factor de ponderación de la mama (0.12) = Riesgo real"""
        dosis_total = self.calcular_dosis_glandular_total()
        return dosis_total * 0.12

    def calcular_dosis_por_mama(self):
        """Devuelve una tupla (dosis_derecha, dosis_izquierda) para el informe EUREF"""
        dosis_der = 0.0
        dosis_izq = 0.0
        
        for estudio in self.estudios:
            # Buscamos 'D' (Derecha/Right) o 'I' (Izquierda/Left)
            lat = str(estudio.lateralidad).strip().upper()
            if 'D' in lat or 'R' in lat:
                dosis_der += estudio.dosis_glandular
            elif 'I' in lat or 'L' in lat:
                dosis_izq += estudio.dosis_glandular
                
        return dosis_der, dosis_izq

    def __str__(self):
        return (
            f"Paciente: {self.id} | Edad: {self.edad} | "
            f"Espesor: {self.espesor_mama_actual}mm | "
            f"Dosis Efectiva: {self.calcular_dosis_efectiva():.3f} mGy"
        )