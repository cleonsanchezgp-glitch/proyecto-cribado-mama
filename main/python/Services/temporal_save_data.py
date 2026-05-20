from typing import List

from main.python.Models.Estudio import Estudio
from main.python.Models.Paciente import Paciente

# Estas listas actuarán como tu "Base de Datos en Memoria"
pacientes_memoria: List['Paciente'] = []
estudios_memoria: List['Estudio'] = []

def limpiar_memoria():
    global pacientes_memoria, estudios_memoria
    pacientes_memoria.clear()
    estudios_memoria.clear()