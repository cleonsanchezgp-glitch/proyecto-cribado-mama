
import pandas as pd
import oracledb
from main.python.Services import temporal_save_data

def generate_csv_doc(filename):
    """
    Genera un archivo CSV o Excel (.xlsx) leyendo desde la memoria global.
    Incluye cálculos de dosis por mama, total, efectiva y espesores discriminados.
    """
    data = []
    for paciente in temporal_save_data.pacientes_memoria:
        for estudio in paciente.estudios:  
            
            # Obtención segura del espesor del paciente
            espesor_valor = getattr(paciente, 'espesor_mama_actual', getattr(paciente, 'espesor_mama', 'N/A'))
            
            # Manejo de formatos de fecha/hora
            hora_val = (estudio.hora_adquisicion.isoformat() 
                        if hasattr(estudio.hora_adquisicion, 'isoformat') 
                        else estudio.hora_adquisicion)
            
            fecha_val = (estudio.fecha_realizacion.isoformat() 
                         if hasattr(estudio.fecha_realizacion, 'isoformat') 
                         else estudio.fecha_realizacion)
            
            # --- NUEVOS CÁLCULOS EXTRAÍDOS DEL OBJETO ESTUDIO ---
            dosis_der, dosis_izq = estudio.calcular_dosis_por_mama()
            esp_der, esp_izq = estudio.calcular_espesor_por_mama()
            dosis_efectiva = estudio.calcular_dosis_efectiva()
            if estudio.lateralidad == 'R':
                row = {
                    'paciente_id': paciente.id,
                    'edad': paciente.edad,
                    'espesor_mama_paciente': espesor_valor,
                    'tipo_actividad': estudio.tipo_actividad,
                    'prestacion_realizada': estudio.prestacion_realizada,
                    'hora_adquisicion': hora_val,
                    'fecha_realizacion': fecha_val,
                    'lateralidad': estudio.lateralidad,
                    'proyeccion': estudio.proyeccion,
                    'fuerza_compresion': estudio.fuerza_compresion,
                    'tension_tubo': estudio.tension_tubo,
                    'corriente_tubo': estudio.corriente_tubo,
                    'carga': estudio.carga,
                    'tiempo_exposicion': estudio.tiempo_exposicion,
                    'filtro': estudio.filtro,
                    'kerma_entrada': estudio.kerma_entrada,
                    'dosis_glandular': estudio.dosis_glandular,
                    # --- NUEVAS COLUMNAS EN EL EXPORT ---
                    'dosis_mama_izquierda': "N/A",
                    'espesor_mama_izquierda': "N/A",
                    'dosis_mama_derecha': dosis_der,
                    'espesor_mama_derecha': esp_der,
                    'dosis_efectiva': dosis_efectiva,
                    'grupo_espesor': getattr(estudio, 'grupo_espesor', ''),
                    # ------------------------------------
                    'distancia_foco_paciente': estudio.distancia_foco_paciente,
                    'distancia_foco_mama': estudio.distancia_foco_mama,
                    'factor_magnificacion': estudio.factor_magnificacion,
                    'rejilla': estudio.rejilla,
                    'temperatura': estudio.temperatura,
                }
                data.append(row)
            
            if estudio.lateralidad == 'L':
                row = {
                    'paciente_id': paciente.id,
                    'edad': paciente.edad,
                    'espesor_mama_paciente': espesor_valor,
                    'tipo_actividad': estudio.tipo_actividad,
                    'prestacion_realizada': estudio.prestacion_realizada,
                    'hora_adquisicion': hora_val,
                    'fecha_realizacion': fecha_val,
                    'lateralidad': estudio.lateralidad,
                    'proyeccion': estudio.proyeccion,
                    'fuerza_compresion': estudio.fuerza_compresion,
                    'tension_tubo': estudio.tension_tubo,
                    'corriente_tubo': estudio.corriente_tubo,
                    'carga': estudio.carga,
                    'tiempo_exposicion': estudio.tiempo_exposicion,
                    'filtro': estudio.filtro,
                    'kerma_entrada': estudio.kerma_entrada,
                    'dosis_glandular': estudio.dosis_glandular,
                    # --- NUEVAS COLUMNAS EN EL EXPORT ---
                    'dosis_mama_izquierda': dosis_izq,
                    'espesor_mama_izquierda': esp_izq,
                    'dosis_mama_derecha': "N/A",
                    'espesor_mama_derecha': "N/A",
                    'dosis_efectiva': dosis_efectiva,
                    'grupo_espesor': getattr(estudio, 'grupo_espesor', ''),
                    # ------------------------------------
                    'distancia_foco_paciente': estudio.distancia_foco_paciente,
                    'distancia_foco_mama': estudio.distancia_foco_mama,
                    'factor_magnificacion': estudio.factor_magnificacion,
                    'rejilla': estudio.rejilla,
                    'temperatura': estudio.temperatura,
                }
                data.append(row)
    if not data:
        print("No hay datos para exportar.")
        return

    df = pd.DataFrame(data)
    
    # Exporta a Excel o CSV según la extensión
    if filename.lower().endswith('.xlsx'):
        df.to_excel(filename, index=False)
    else:
        # Se añade sep=';' para compatibilidad con Excel en español
        df.to_csv(filename, index=False, sep=';', encoding='utf-8-sig') 
        
    print(f"Archivo exportado correctamente en: {filename}")


import oracledb

def insert_data_DB():
    """
    Inserta los datos de la memoria global en la base de datos Oracle CMAMA_DB.
    Maneja la relación jerárquica entre Paciente y Estudio.
    """


    # Configuración de conexión (Ajusta con tus credenciales reales)
    # Recomiendo usar variables de entorno para user y password
    dsn = oracledb.makedsn('localhost', 1521, service_name='FREEPDB1')
    
    try:
        connection = oracledb.connect(
            user='CMAMA_DB_USR', 
            password='root', 
            dsn=dsn
        )
        cursor = connection.cursor()
        
        for paciente in temporal_save_data.pacientes_memoria:
            # 1. INSERTAR O ACTUALIZAR PACIENTE
            # Usamos MERGE para evitar errores de clave primaria duplicada
            cursor.execute("""
                MERGE INTO PACIENTE p
                USING (SELECT :id as id_paciente FROM dual) src
                ON (p.id_paciente = src.id_paciente)
                WHEN MATCHED THEN
                    UPDATE SET edad = :edad, espesor_mama_actual = :esp
                WHEN NOT MATCHED THEN
                    INSERT (id_paciente, edad, espesor_mama_actual)
                    VALUES (:id, :edad, :esp)
            """, {
                'id': paciente.id,
                'edad': paciente.edad,
                'esp': paciente.espesor_mama_actual
            })

            # 2. INSERTAR CADA ESTUDIO DEL PACIENTE
            for estudio in paciente.estudios:
                # 1. Normalización de Hora (a String HH:MM:SS)
                if hasattr(estudio.hora_adquisicion, 'strftime'):
                    hora_str = estudio.hora_adquisicion.strftime('%H:%M:%S')
                else:
                    hora_str = str(estudio.hora_adquisicion)[:8] # Cortamos si es muy largo

                # 2. Normalización de Fecha (Evita el ORA-01830)
                fecha_val = estudio.fecha_realizacion
                if hasattr(fecha_val, 'date'): 
                    # Si es un datetime de Python, extraemos solo la fecha
                    fecha_val = fecha_val.date()
                elif isinstance(fecha_val, str):
                    # Si es un string, nos aseguramos de que Oracle no reciba basura extra
                    # Tomamos solo los primeros 10 caracteres (YYYY-MM-DD)
                    from datetime import datetime
                    try:
                        fecha_val = datetime.strptime(fecha_val[:10], '%Y-%m-%d').date()
                    except:
                        fecha_val = None # O manejar el error de formato

                cursor.execute("""
                    INSERT INTO ESTUDIO (
                        id_paciente, tipo_actividad, prestacion_realizada, hora_adquisicion, 
                        fecha_realizacion, lateralidad, proyeccion, fuerza_compresion, 
                        tension_tubo, espesor_mama_estudio, corriente_tubo, carga, 
                        tiempo_exposicion, filtro, kerma_entrada, dosis_glandular,
                        dosis_der, dosis_izq, espesor_der, espesor_izq, dosis_efectiva,
                        distancia_foco_paciente, distancia_foco_mama, factor_magnificacion, 
                        rejilla, temperatura, grupo_espesor
                    ) VALUES (
                        :id_p, :tipo, :prest, :hora, :fecha, :lat, :proy, :fuerza,
                        :kvp, :esp_est, :ma, :mas, :time, :filt, :kerma, :dosis,
                        :d_der, :d_izq, :e_der, :e_izq, :d_efec,
                        :dfp, :dfm, :mag, :rej, :temp, :grupo
                    )
                """, {
                    'id_p': estudio.id_paciente,
                    'tipo': estudio.tipo_actividad,
                    'prest': estudio.prestacion_realizada,
                    'hora': hora_str,
                    'fecha': fecha_val, # Ahora es un objeto date puro
                    'lat': estudio.lateralidad,
                    'proy': estudio.proyeccion,
                    'fuerza': estudio.fuerza_compresion,
                    'kvp': estudio.tension_tubo,
                    'esp_est': estudio.espesor_mama_estudio,
                    'ma': estudio.corriente_tubo,
                    'mas': estudio.carga,
                    'time': estudio.tiempo_exposicion,
                    'filt': estudio.filtro,
                    'kerma': estudio.kerma_entrada,
                    'dosis': estudio.dosis_glandular,
                    'd_der': estudio.dosis_der,
                    'd_izq': estudio.dosis_izq,
                    'e_der': estudio.espesor_der,
                    'e_izq': estudio.espesor_izq,
                    'd_efec': estudio.calcular_dosis_efectiva(),
                    'dfp': estudio.distancia_foco_paciente,
                    'dfm': estudio.distancia_foco_mama,
                    'mag': estudio.factor_magnificacion,
                    'rej': estudio.rejilla,
                    'temp': estudio.temperatura,
                    'grupo': estudio.grupo_espesor
                })
        
        connection.commit()
        print(f"Éxito: Se han persistido {len(temporal_save_data.pacientes_memoria)} pacientes y sus estudios.")
        
    except oracledb.Error as e:
        if 'connection' in locals():
            connection.rollback()
        print(f"Error crítico de Oracle: {e}")
        raise e
        
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'connection' in locals():
            connection.close()
