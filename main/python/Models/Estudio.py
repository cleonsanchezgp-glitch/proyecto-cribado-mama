from datetime import datetime

class Estudio:
    def __init__(self, id_paciente: str, tipo_actividad: str, prestacion_realizada: str, 
                 hora_adquisicion: datetime, fecha_realizacion: datetime, lateralidad: str, 
                 proyeccion: str, fuerza_compresion: str, tension_tubo: int, 
                 espesor_mama_estudio: int, corriente_tubo: int, carga: float, 
                 tiempo_exposicion: float, filtro: str, kerma_entrada: float, 
                 dosis_glandular: float, distancia_foco_paciente: str, 
                 distancia_foco_mama: str, factor_magnificacion: float, 
                 rejilla: str, temperatura: float):
        
        self.id_paciente = id_paciente # FK
        self.tipo_actividad = tipo_actividad
        self.prestacion_realizada = prestacion_realizada
        self.hora_adquisicion = hora_adquisicion
        self.fecha_realizacion = fecha_realizacion
        self.lateralidad = lateralidad
        self.proyeccion = proyeccion
        self.fuerza_compresion = fuerza_compresion
        self.tension_tubo = int(tension_tubo)
        self.espesor_mama_estudio = int(espesor_mama_estudio)
        self.corriente_tubo = int(corriente_tubo)
        self.carga = float(carga)
        self.tiempo_exposicion = float(tiempo_exposicion)
        self.filtro = filtro
        self.kerma_entrada = float(kerma_entrada)
        self.dosis_glandular = float(dosis_glandular)
        self.distancia_foco_paciente = distancia_foco_paciente
        self.distancia_foco_mama = distancia_foco_mama
        self.factor_magnificacion = float(factor_magnificacion)
        self.rejilla = rejilla
        self.temperatura = float(temperatura)

    def __repr__(self):
        return (
            f"Estudio(id_paciente={self.id_paciente}, tipo={self.tipo_actividad}, "
            f"prestacion={self.prestacion_realizada}, fecha={self.fecha_realizacion}, "
            f"lat={self.lateralidad}, proy={self.proyeccion}, kVp={self.tension_tubo}, "
            f"espesor_estudio={self.espesor_mama_estudio}, mAs={self.carga})"
        )