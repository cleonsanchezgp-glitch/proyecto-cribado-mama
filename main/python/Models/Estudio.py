from datetime import time

class Estudio:
    def __init__(self, id_paciente: str, tipo_actividad: str, prestacion_realizada: str, 
                 hora_adquisicion: time, fecha_realizacion: time, lateralidad: str, 
                 proyeccion: str, fuerza_compresion: str, tension_tubo: int, 
                 espesor_mama_estudio: int, corriente_tubo: int, carga: float, 
                 tiempo_exposicion: float, filtro: str, kerma_entrada: float, 
                 dosis_glandular: float, distancia_foco_paciente: float, 
                 distancia_foco_mama: str, factor_magnificacion: float, 
                 rejilla: str, temperatura: float, grupo_espesor: str = ""):
        
        # Identificadores
        self.id_paciente = id_paciente 
        self.tipo_actividad = tipo_actividad
        self.prestacion_realizada = prestacion_realizada
        self.hora_adquisicion = hora_adquisicion
        self.fecha_realizacion = fecha_realizacion
        
        # Lateralidad normalizada
        self.lateralidad = str(lateralidad).strip().upper()
        self.proyeccion = proyeccion
        
        # Datos Técnicos
        self.fuerza_compresion = fuerza_compresion
        self.tension_tubo = tension_tubo
        self.espesor_mama_estudio = int(espesor_mama_estudio) 
        self.corriente_tubo = corriente_tubo
        self.carga = float(carga)
        self.tiempo_exposicion = float(tiempo_exposicion)
        self.filtro = filtro
        
        # Dosis y Física
        self.kerma_entrada = float(kerma_entrada)
        self.dosis_glandular = float(dosis_glandular)
        self.distancia_foco_paciente = float(str(distancia_foco_paciente).replace(',', '.'))
        self.distancia_foco_mama = str(distancia_foco_mama).strip()
        self.factor_magnificacion = float(factor_magnificacion)
        self.rejilla = rejilla
        self.temperatura = float(temperatura)
        self.grupo_espesor = grupo_espesor

        # --- ATRIBUTOS DISCRIMINADOS POR MAMA ---
        # Se calculan automáticamente al instanciar el objeto
        self.dosis_der, self.dosis_izq = self.calcular_dosis_por_mama()
        self.espesor_der, self.espesor_izq = self.calcular_espesor_por_mama()

    # --- MÉTODOS DE CÁLCULO ---

    def calcular_dosis_por_mama(self):
        """Asigna la dosis glandular al lado correspondiente."""
        d_der = 0.0
        d_izq = 0.0
        if 'D' in self.lateralidad or 'R' in self.lateralidad:
            d_der = self.dosis_glandular
        elif 'I' in self.lateralidad or 'L' in self.lateralidad:
            d_izq = self.dosis_glandular
        return d_der, d_izq

    def calcular_espesor_por_mama(self):
        """Asigna el espesor de la mama al lado correspondiente."""
        e_der = 0
        e_izq = 0
        if 'D' in self.lateralidad or 'R' in self.lateralidad:
            e_der = self.espesor_mama_estudio
        elif 'I' in self.lateralidad or 'L' in self.lateralidad:
            e_izq = self.espesor_mama_estudio
        return e_der, e_izq

    def calcular_dosis_glandular_total(self) -> float:
        return self.dosis_glandular

    def calcular_dosis_efectiva(self) -> float:
        return self.dosis_glandular * 0.12

    def __repr__(self):
        return (
            f"Estudio(ID={self.id_paciente}, Lat={self.lateralidad}, "
            f"Espesor_D={self.espesor_der}, Espesor_I={self.espesor_izq}, "
            f"Dosis={self.dosis_glandular})"
        )