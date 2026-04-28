import pandas as pd
import os

def limpiar_datos_ris(ruta_archivo):
    print(f"Iniciando limpieza del archivo: {ruta_archivo}")
    
    try:
        # 1. Detectar si es CSV o Excel y leerlo
        if ruta_archivo.lower().endswith('.csv'):
            try:
                df = pd.read_csv(ruta_archivo)
            except:
                df = pd.read_csv(ruta_archivo, sep=';')
        else:
            df = pd.read_excel(ruta_archivo)
            
        print(f"Archivo cargado. Filas iniciales: {len(df)}")
        
        # 2. Eliminar duplicados y filas vacías
        df.drop_duplicates(inplace=True)
        df.dropna(inplace=True)
        # 3. Guardar el archivo limpio (Lo guardamos siempre como Excel para que sea más fácil de abrir)
        directorio = os.path.dirname(ruta_archivo)
        ruta_salida = os.path.join(directorio, "datos_ris_limpios.xlsx")
        
        df.to_excel(ruta_salida, index=False)
        print(f"¡Éxito! Archivo limpio guardado en: {ruta_salida}")
        return True
        
    except Exception as e:
        print(f"Error al limpiar los datos: {e}")
        return False