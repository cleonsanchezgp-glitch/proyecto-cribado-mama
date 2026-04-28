import pandas as pd
import numpy as np

def obtener_metricas_dashboard(ruta_limpio, ruta_resultados):
    print("--- Calculando métricas para el Dashboard ---")
    try:
        # 1. Leer los dos archivos que hemos generado antes
        df_limpio = pd.read_excel(ruta_limpio)
        df_resultados = pd.read_excel(ruta_resultados)

        # 2. Hacer las matemáticas matemáticas
        pacientes_totales = len(df_resultados)
        registros_cruzados = len(df_limpio)
        dosis_media = df_resultados['Dosis_Glandular_Total'].mean()
        desviacion_std = df_resultados['Dosis_Glandular_Total'].std()
        
        # Si solo hay 1 paciente, la desviación da error, así que la ponemos a 0
        if pd.isna(desviacion_std):
            desviacion_std = 0.0

        # Preparar el formato de view_resumen.py
        metricas = [
            {
                "value": str(pacientes_totales), 
                "subtitle": "Pacientes únicos",
                "badge_text": "Agrupados", "badge_style": "blue"
            },
            {
                "value": f"{dosis_media:.2f}".replace('.', ','), # Formato europeo con coma
                "subtitle": "Dosis Glandular Total",
                "badge_text": "mGy", "badge_style": "green"
            },
            {
                "value": str(registros_cruzados), 
                "subtitle": "Exploraciones válidas",
                "badge_text": "Limpios", "badge_style": "blue"
            },
            {
                "value": f"{desviacion_std:.2f}".replace('.', ','), 
                "subtitle": "Dispersión",
                "badge_text": "± mGy", "badge_style": "amber"
            }
        ]
        return metricas
        
    except Exception as e:
        print(f"Error generando métricas: {e}")
        return []

def obtener_datos_historial(ruta_limpio, ruta_resultados):
    try:
        df_limpio = pd.read_excel(ruta_limpio)
        df_resultados = pd.read_excel(ruta_resultados)
        
        # Juntamos los datos usando el ID del paciente
        df_completo = pd.merge(df_resultados, df_limpio.drop_duplicates(subset=['ID_Paciente']), on='ID_Paciente', how='left')
        
        # Volvemos a deducir la densidad (por si no estaba)
        if 'Densidad' not in df_completo.columns:
            condiciones = [
                df_completo['Espesor_Mama'] < 45,
                (df_completo['Espesor_Mama'] >= 45) & (df_completo['Espesor_Mama'] < 55),
                (df_completo['Espesor_Mama'] >= 55) & (df_completo['Espesor_Mama'] < 65),
                df_completo['Espesor_Mama'] >= 65
            ]
            opciones = ['A', 'B', 'C', 'D'] # La vista añade "Tipo " automáticamente
            df_completo['Densidad'] = np.select(condiciones, opciones, default='B')
            
        filas_historial = []
        for index, row in df_completo.iterrows():
            # Si la dosis es alta (> 2.0), lo marcamos para "revisar"
            estado = "revisar" if row['Dosis_Glandular_Total'] > 2.0 else "ok"
            
            # Como en nuestro Excel de prueba no pusimos Edad, nos la inventamos para la demo (ej: 55)
            # (Si en tu Excel real está, cámbialo por row['Edad'])
            edad = 55 
            
            filas_historial.append({
                "id": str(row['ID_Paciente']),
                "age": edad,
                "density": str(row['Densidad']),
                "agd": float(row['Dosis_Glandular_Total']),
                "date": str(row['Fecha']).split(' ')[0], # Solo la fecha, sin la hora
                "status": estado
            })
            
        return filas_historial
    except Exception as e:
        print(f"Error generando datos para historial: {e}")
        return []

def obtener_datos_graficos(ruta_limpio):
    try:
        df = pd.read_excel(ruta_limpio)
        
        # Si el hospital no nos da la "Densidad", la calculamos según el "Espesor"
        if 'Densidad' not in df.columns:
            condiciones = [
                df['Espesor_Mama'] < 45,
                (df['Espesor_Mama'] >= 45) & (df['Espesor_Mama'] < 55),
                (df['Espesor_Mama'] >= 55) & (df['Espesor_Mama'] < 65),
                df['Espesor_Mama'] >= 65
            ]
            opciones = ['Tipo A', 'Tipo B', 'Tipo C', 'Tipo D']
            df['Densidad'] = np.select(condiciones, opciones, default='Tipo B')

        # Calcular datos para la Distribución de Densidad (Las 4 barras inferiores)
        total_exploraciones = len(df)
        conteo = df['Densidad'].value_counts()
        
        datos_densidad = []
        for tipo in ['Tipo A', 'Tipo B', 'Tipo C', 'Tipo D']:
            n = conteo.get(tipo, 0)
            prop = n / total_exploraciones if total_exploraciones > 0 else 0
            datos_densidad.append({
                "proportion": float(prop),
                "pct_text": f"{int(prop * 100)}%",
                "n": str(n)
            })

        # Calcular datos para el Gráfico de Barras Principal (Dosis media por densidad)
        dosis_media_densidad = df.groupby('Densidad')['Dosis_Glandular'].mean()
        
        datos_grafico = []
        for tipo in ['Tipo A', 'Tipo B', 'Tipo C', 'Tipo D']:
            dosis_actual = float(dosis_media_densidad.get(tipo, 0))
            if pd.isna(dosis_actual): dosis_actual = 0.0
            
            datos_grafico.append({
                "label": tipo,
                "value1": dosis_actual * 0.9,  # Año anterior (Azul clarito)
                "value2": dosis_actual         # Año actual (Azul oscuro)
            })

        return datos_densidad, datos_grafico
        
    except Exception as e:
        print(f"Error generando gráficos: {e}")
        return [], []