import pandas as pd
import os

def calcular_dosis_pacientes(ruta_archivo_limpio):
    print(f"--- Iniciando cálculo de dosis para: {ruta_archivo_limpio} ---")
    
    try:
        # 1. Cargamos el archivo que acabamos de limpiar
        df = pd.read_excel(ruta_archivo_limpio)
        
        # 2. Agrupamos por Paciente y Lateralidad (Derecha/Izquierda), y sumamos las dosis
        # unstack() hace la magia de poner la 'D' y la 'I' en columnas separadas
        calculos = df.groupby(['ID_Paciente', 'Lateralidad'])['Dosis_Glandular'].sum().unstack(fill_value=0)
        
        # Renombramos las columnas para que quede profesional
        # Si en tu CSV la lateralidad tiene otras letras, ponlas aquí (ej: 'R' y 'L' en inglés)
        calculos = calculos.rename(columns={'D': 'Dosis_Mama_Derecha', 'I': 'Dosis_Mama_Izquierda'})
        
        # 3. Cálculo de magnitudes derivadas (Lo que pide el Punto 3 del TFG)
        # Sumamos ambas mamas
        calculos['Dosis_Glandular_Total'] = calculos.get('Dosis_Mama_Derecha', 0) + calculos.get('Dosis_Mama_Izquierda', 0)
        
        # Multiplicamos por el factor tisular de la mama (0.12)
        factor_tisular_mama = 0.12
        calculos['Dosis_Efectiva'] = calculos['Dosis_Glandular_Total'] * factor_tisular_mama
        
        # 4. Restaurar el ID_Paciente como columna y guardar
        resultados_finales = calculos.reset_index()
        
        directorio = os.path.dirname(ruta_archivo_limpio)
        ruta_resultados = os.path.join(directorio, "resultados_dosimetria_pacientes.xlsx")
        
        resultados_finales.to_excel(ruta_resultados, index=False)
        print(f"¡Cálculos terminados! Resultados guardados en: {ruta_resultados}")
        
        return True, ruta_resultados
        
    except Exception as e:
        print(f"Error en los cálculos: {e}")
        return False, None