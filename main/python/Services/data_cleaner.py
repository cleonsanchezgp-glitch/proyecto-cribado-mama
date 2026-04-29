import pandas as pd
import os
from main.python.Services import temporal_save_data

def calcular_dosis_pacientes(ruta_archivo_limpio):
    """
    Realiza los cálculos de dosimetría utilizando los objetos almacenados en la 
    memoria global (temporal_save_data).
    """
    print(f"--- Iniciando cálculo de dosis desde memoria global ---")
    
    try:
        # 1. Extraemos los datos de los objetos Estudio en la memoria global
        # Usamos los nombres de atributos de tu clase Estudio
        datos_estudios = [
            {
                'ID_Paciente': est.id_paciente,
                'Lateralidad': est.lateralidad,
                'Dosis_Glandular': est.dosis_glandular
            }
            for est in temporal_save_data.estudios_memoria
        ]
        
        if not datos_estudios:
            print("Error: No hay datos cargados en la memoria global.")
            return False, None

        # 2. Creamos el DataFrame para cálculos
        df = pd.DataFrame(datos_estudios)
        
        # 3. Agrupamos y sumamos
        calculos = df.groupby(['ID_Paciente', 'Lateralidad'])['Dosis_Glandular'].sum().unstack(fill_value=0)
        
        # Mapeo de columnas según los valores que guardes en el objeto (D/I o Derecha/Izquierda)
        mapeo_columnas = {
            'D': 'Dosis_Mama_Derecha', 
            'I': 'Dosis_Mama_Izquierda',
            'Derecha': 'Dosis_Mama_Derecha',
            'Izquierda': 'Dosis_Mama_Izquierda'
        }
        calculos = calculos.rename(columns=mapeo_columnas)
        
        # Aseguramos existencia de columnas para la suma total
        for col in ['Dosis_Mama_Derecha', 'Dosis_Mama_Izquierda']:
            if col not in calculos.columns:
                calculos[col] = 0.0
        
        # 4. Cálculo de magnitudes derivadas
        calculos['Dosis_Glandular_Total'] = calculos['Dosis_Mama_Derecha'] + calculos['Dosis_Mama_Izquierda']
        
        factor_tisular_mama = 0.12
        calculos['Dosis_Efectiva'] = calculos['Dosis_Glandular_Total'] * factor_tisular_mama
        
        # 5. Exportación y retorno
        resultados_finales = calculos.reset_index()
        
        directorio = os.path.dirname(ruta_archivo_limpio)
        ruta_resultados = os.path.join(directorio, "resultados_dosimetria_pacientes.xlsx")
        
        resultados_finales.to_excel(ruta_resultados, index=False)
        print(f"¡Cálculos terminados! Resultados exportados en: {ruta_resultados}")
        
        return True, ruta_resultados
        
    except Exception as e:
        print(f"Error en los cálculos desde memoria: {e}")
        return False, None