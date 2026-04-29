import pandas as pd
import os

def calcular_dosis_pacientes(ruta_archivo_limpio):
    print(f"--- Iniciando cálculo de dosis para: {ruta_archivo_limpio} ---")
    
    try:
        df = pd.read_excel(ruta_archivo_limpio)

        # ✅ FIX 1: Limpiar espacios de Lateralidad y filtrar filas sin lateralidad
        df['Lateralidad'] = df['Lateralidad'].str.strip()
        df = df[df['Lateralidad'].isin(['R', 'L'])]

        # ✅ FIX 2: Convertir Dosis Glandular de string español a float
        df['Dosis Glandular (mGy)'] = (
            df['Dosis Glandular (mGy)']
            .astype(str)
            .str.strip()
            .str.replace('.', '', regex=False)   # quitar separador de miles
            .str.replace(',', '.', regex=False)  # coma decimal → punto
            .astype(float)
        )

        # 2. Agrupar y pivotar
        calculos = df.groupby(
            ['Nº de Estudio', 'Lateralidad']
        )['Dosis Glandular (mGy)'].sum().unstack(fill_value=0.0)

        calculos.columns = [str(c) for c in calculos.columns]

        calculos = calculos.rename(columns={
            'R': 'Dosis_Mama_Derecha',
            'L': 'Dosis_Mama_Izquierda'
        })

        if 'Dosis_Mama_Derecha' not in calculos.columns:
            calculos['Dosis_Mama_Derecha'] = 0.0
        if 'Dosis_Mama_Izquierda' not in calculos.columns:
            calculos['Dosis_Mama_Izquierda'] = 0.0

        calculos['Dosis_Glandular_Total'] = (
            calculos['Dosis_Mama_Derecha'] + calculos['Dosis_Mama_Izquierda']
        )
        calculos['Dosis_Efectiva'] = calculos['Dosis_Glandular_Total'] * 0.12

        resultados_finales = calculos.reset_index()
        directorio = os.path.dirname(ruta_archivo_limpio)
        ruta_resultados = os.path.join(directorio, "resultados_dosimetria_pacientes.xlsx")
        resultados_finales.to_excel(ruta_resultados, index=False)

        print(f"¡Cálculos terminados! Resultados guardados en: {ruta_resultados}")
        return True, ruta_resultados
        
    except Exception as e:
        print(f"Error en los cálculos: {e}")
        return False, None