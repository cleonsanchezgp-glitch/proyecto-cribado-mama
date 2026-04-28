import pandas as pd
from main.python.Models.Paciente import Paciente
from main.python.Models.Estudio import Estudio

# --- NOMBRES EXACTOS CONFIRMADOS ---
ALIASES = {
    'edad': ['Edad'],
    'espesor': ['Espesor de Mama Comprimida (mm)'],
    'dosis': ['Dosis Glandular (mGy)'],
    'fecha': ['Fecha de Realización', 'Fecha'],
    'hora': ['Hora de Adquisición', 'Hora'],
    'lat': ['Lateralidad'],
    'proy': ['Proyección', 'Proyeccion'],
    'fuerza': ['Fuerza de Compresión (N)'],
    'kvp': ['Tensión del Tubo (kVp)'],
    'ma': ['Corriente del Tubo (mA)'],
    'mas': ['Carga (mAs)'],
    'tiempo': ['Tiempo Exposición Solicit (ms)', 'Tiempo Exposición Solicit(ms)', 'Tiempo'],
    'filtro': ['Filtro'],
    'kerma': ['Kerma a la Entrada (mGy)'],
    'dist_fp': ['Distancia Foco a Paciente'],
    'dist_fm': ['Distancia Foco Entrada de la Mama (mm)'],
    'mag': ['Factor de magnificación'],
    'rejilla': ['Rejilla'],
    'tipo_act': ['Tipo de Actividad'],
    'prestacion': ['Presta Prestación Realizada'],
    'temperatura': ['Temperatura Detector (ºC)']
}

def encontrar_cabecera(ruta_archivo):
    """Busca en qué fila empiezan realmente los datos."""
    if ruta_archivo.lower().endswith('.csv'):
        df_temp = pd.read_csv(ruta_archivo, sep=None, engine='python', header=None, nrows=15)
    else:
        df_temp = pd.read_excel(ruta_archivo, header=None, nrows=15)
        
    for i, fila in df_temp.iterrows():
        texto_fila = " ".join([str(val).lower() for val in fila.values if pd.notna(val)])
        if "edad" in texto_fila and "actividad" in texto_fila:
            return i
    return 0

def procesar_archivo_a_objetos(ruta_archivo):
    print(f"--- Iniciando carga por Agrupación de Fecha: {ruta_archivo} ---")
    
    try:
        fila_cabecera = encontrar_cabecera(ruta_archivo)
        
        if ruta_archivo.lower().endswith('.csv'):
            df = pd.read_csv(ruta_archivo, sep=None, engine='python', header=fila_cabecera) 
        elif ruta_archivo.lower().endswith(('.xls', '.xlsx')):
            df = pd.read_excel(ruta_archivo, header=fila_cabecera)
        else:
            return []

        # LIMPIEZA: Quitamos saltos de línea de las cabeceras
        df.columns = [str(col).replace('\n', ' ').replace('\r', ' ').replace('  ', ' ').strip() for col in df.columns]

        def buscar_valor(fila_datos, lista_nombres, tipo_dato):
            """Busca el valor en la fila tolerando diferencias de mayúsculas/espacios."""
            for nombre_col in lista_nombres:
                for col_real in df.columns:
                    if nombre_col.lower() in col_real.lower():
                        val = fila_datos[col_real]
                        if pd.notna(val):
                            try:
                                # TRUCO: Si queremos un decimal (float) y viene como texto con coma ("1,45")
                                if tipo_dato == float and isinstance(val, str):
                                    val = val.replace(',', '.')
                                return tipo_dato(val)
                            except:
                                pass
            return tipo_dato() if tipo_dato != str else ""

        # --- LÓGICA DE AGRUPACIÓN SECUENCIAL ---
        pacientes_creados = []
        paciente_actual = None
        ultima_clave_tiempo = None

        for _, fila in df.iterrows():
            fecha_val = str(buscar_valor(fila, ALIASES['fecha'], str)).strip()
            hora_val = str(buscar_valor(fila, ALIASES['hora'], str)).strip()
            
            # Combinamos fecha y hora para tener la marca temporal exacta
            clave_tiempo = f"{fecha_val} {hora_val}".strip()
            
            # Si la celda viene vacía (por celdas combinadas en Excel), heredamos la de la fila anterior
            if not clave_tiempo or clave_tiempo == 'nan' or clave_tiempo == 'nan nan':
                clave_tiempo = ultima_clave_tiempo
                
            # Si sigue vacía y no hay anterior, es una fila basura, la saltamos
            if not clave_tiempo:
                continue
                
            # Si la marca de tiempo CAMBIA respecto a la anterior, significa que es un PACIENTE NUEVO
            if clave_tiempo != ultima_clave_tiempo:
                # Generamos un ID automático consecutivo (PAC-0001, PAC-0002...)
                nuevo_id = f"PAC-{len(pacientes_creados) + 1:04d}"
                edad = str(buscar_valor(fila, ALIASES['edad'], str))
                espesor = buscar_valor(fila, ALIASES['espesor'], int)
                
                # Creamos el objeto paciente y lo guardamos
                paciente_actual = Paciente(id=nuevo_id, edad=edad, espesor_mama_actual=espesor)
                pacientes_creados.append(paciente_actual)
                
                # Actualizamos la memoria temporal
                ultima_clave_tiempo = clave_tiempo
            
            # Independientemente de si es nuevo o el mismo, creamos su Estudio (la fila actual)
            estudio = Estudio(
                id_paciente=paciente_actual.id,  # Le asignamos el ID autogenerado
                tipo_actividad=buscar_valor(fila, ALIASES['tipo_act'], str),
                prestacion_realizada=buscar_valor(fila, ALIASES['prestacion'], str),
                hora_adquisicion=buscar_valor(fila, ALIASES['hora'], str), 
                fecha_realizacion=buscar_valor(fila, ALIASES['fecha'], str), 
                lateralidad=buscar_valor(fila, ALIASES['lat'], str),
                proyeccion=buscar_valor(fila, ALIASES['proy'], str),
                fuerza_compresion=buscar_valor(fila, ALIASES['fuerza'], str),
                tension_tubo=buscar_valor(fila, ALIASES['kvp'], int),
                espesor_mama_estudio=buscar_valor(fila, ALIASES['espesor'], int),
                corriente_tubo=buscar_valor(fila, ALIASES['ma'], int),
                carga=buscar_valor(fila, ALIASES['mas'], float),
                tiempo_exposicion=buscar_valor(fila, ALIASES['tiempo'], float),
                filtro=buscar_valor(fila, ALIASES['filtro'], str),
                kerma_entrada=buscar_valor(fila, ALIASES['kerma'], float),
                dosis_glandular=buscar_valor(fila, ALIASES['dosis'], float),
                distancia_foco_paciente=buscar_valor(fila, ALIASES['dist_fp'], str),
                distancia_foco_mama=buscar_valor(fila, ALIASES['dist_fm'], str),
                factor_magnificacion=buscar_valor(fila, ALIASES['mag'], float),
                rejilla=buscar_valor(fila, ALIASES['rejilla'], str),
                temperatura=buscar_valor(fila, ALIASES['temperatura'], float)
            )
            
            # Añadimos el estudio a la "mochila" del paciente actual
            paciente_actual.agregar_estudio(estudio)

        print(f"¡Éxito! Se han creado {len(pacientes_creados)} pacientes a partir de los grupos de fecha.")
        return pacientes_creados

    except Exception as e:
        import traceback
        print(f"Error procesando el archivo:\n{traceback.format_exc()}")
        return []