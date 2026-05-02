import pandas as pd
import os
from main.python.Services import temporal_save_data

from main.python.Services import temporal_save_data

def calcular_dosis_pacientes(ruta_archivo_limpio):
    """
    Realiza los cálculos de dosimetría utilizando los objetos en memoria.
    Mantiene el nombre original para compatibilidad.
    """
    print(f"--- Iniciando cálculo de dosis desde memoria global ---")
    
    try:
        # 1. Extraemos los datos directamente de los objetos Estudio en memoria
        # Accedemos a los atributos de la clase: id_paciente, lateralidad y dosis_glandular
        datos_estudios = [
            {
                'ID_Paciente': est.id_paciente,
                'Lateralidad': est.lateralidad,
                'Dosis_Glandular': est.dosis_glandular
            }
            for est in temporal_save_data.estudios_memoria
        ]
        
        if not datos_estudios:
            print("Error: No hay datos cargados en memoria.")
            return False, None

        # 2. Creamos el DataFrame para realizar los cálculos estadísticos
        df = pd.DataFrame(datos_estudios)
        
        # 3. Agrupamos por Paciente y Lateralidad, sumando las dosis
        calculos = df.groupby(['ID_Paciente', 'Lateralidad'])['Dosis_Glandular'].sum().unstack(fill_value=0)
        
        # Renombramos columnas para el informe (mapeando posibles valores D/I o Derecha/Izquierda)
        mapeo_columnas = {
            'D': 'Dosis_Mama_Derecha', 
            'I': 'Dosis_Mama_Izquierda',
            'Derecha': 'Dosis_Mama_Derecha',
            'Izquierda': 'Dosis_Mama_Izquierda'
        }
        calculos = calculos.rename(columns=mapeo_columnas)
        
        # Asegurar que ambas columnas existan para evitar errores matemáticos
        for col in ['Dosis_Mama_Derecha', 'Dosis_Mama_Izquierda']:
            if col not in calculos.columns:
                calculos[col] = 0.0
        
        # 4. Cálculo de magnitudes (Punto 3 del TFG)
        calculos['Dosis_Glandular_Total'] = calculos['Dosis_Mama_Derecha'] + calculos['Dosis_Mama_Izquierda']
        
        factor_tisular_mama = 0.12
        calculos['Dosis_Efectiva'] = calculos['Dosis_Glandular_Total'] * factor_tisular_mama
        
        # 5. Preparar resultados finales
        resultados_finales = calculos.reset_index()
        
        # Aunque usamos memoria, mantenemos la lógica de guardado si se desea persistir el cálculo
        # Usamos la ruta proporcionada para saber dónde dejar el reporte
        directorio = os.path.dirname(ruta_archivo_limpio)
        ruta_resultados = os.path.join(directorio, "resultados_dosimetria_pacientes.xlsx")
        
        resultados_finales.to_excel(ruta_resultados, index=False)
        print(f"¡Cálculos terminados! Resultados exportados en: {ruta_resultados}")
        
        return True, ruta_resultados
        
    except Exception as e:
        print(f"Error en los cálculos desde memoria: {e}")
        return False, None