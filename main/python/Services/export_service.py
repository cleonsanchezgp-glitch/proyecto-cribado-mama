import pandas as pd
import oracledb
from main.python.Services import temporal_save_data

import pandas as pd
import oracledb
from main.python.Services import temporal_save_data

def generate_csv_doc(filename):
    """
    Genera un archivo CSV o Excel (.xlsx) leyendo desde la memoria global.
    """
    data = []
    for paciente in temporal_save_data.pacientes_memoria:
        for estudio in paciente.estudios:  
            
            # Obtención segura del espesor (comprueba si existe en el objeto)
            espesor_valor = getattr(paciente, 'espesor_mama_actual', getattr(paciente, 'espesor_mama', 'N/A'))
            
            # Manejo seguro para evitar llamar a isoformat() si el objeto ya es un string
            hora_val = (estudio.hora_adquisicion.isoformat() 
                        if hasattr(estudio.hora_adquisicion, 'isoformat') 
                        else estudio.hora_adquisicion)
            
            fecha_val = (estudio.fecha_realizacion.isoformat() 
                         if hasattr(estudio.fecha_realizacion, 'isoformat') 
                         else estudio.fecha_realizacion)
            
            row = {
                'paciente_id': paciente.id,
                'edad': paciente.edad,
                'espesor_mama': espesor_valor,
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
                'distancia_foco_paciente': estudio.distancia_foco_paciente,
                'distancia_foco_mama': estudio.distancia_foco_mama,
                'factor_magnificacion': estudio.factor_magnificacion,
                'rejilla': estudio.rejilla,
                'temperatura': estudio.temperatura,
            }
            data.append(row)
            
    df = pd.DataFrame(data)
    
    # Exporta a Excel o CSV según la extensión
    if filename.endswith('.xlsx'):
        df.to_excel(filename, index=False)
    else:
        # Se añade sep=';' para que Excel separe correctamente las columnas con la configuración regional en español
        df.to_csv(filename, index=False, sep=';') 
        
    print(f"Archivo exportado correctamente en: {filename}")


def insert_data_DB():
    """
    Inserta los datos de la memoria global en la base de datos Oracle.
    """
    dsn = oracledb.makedsn('localhost', 1521, service_name='FREE')
    connection = oracledb.connect(user='your_username', password='your_password', dsn=dsn)
    cursor = connection.cursor()
    
    try:
        for paciente in temporal_save_data.pacientes_memoria:
            
            espesor_valor = getattr(paciente, 'espesor_mama_actual', getattr(paciente, 'espesor_mama', 0.0))
            
            cursor.execute("""
                INSERT INTO pacientes (id, edad, espesor_mama)
                VALUES (:id, :edad, :espesor_mama)
            """, {
                'id': paciente.id,
                'edad': paciente.edad,
                'espesor_mama': espesor_valor
            })
            
            for estudio in paciente.estudios:  
                cursor.execute("""
                    INSERT INTO estudios (paciente_id, tipo_actividad, prestacion_realizada, 
                    hora_adquisicion, fecha_realizacion, lateralidad, proyeccion, fuerza_compresion, 
                    tension_tubo, corriente_tubo, carga, tiempo_exposicion, filtro, kerma_entrada, 
                    dosis_glandular, distancia_foco_paciente, distancia_foco_mama, factor_magnificacion, 
                    rejilla, temperatura, grupo_espesor)
                    VALUES (:paciente_id, :tipo_actividad, :prestacion_realizada, :hora_adquisicion, 
                    :fecha_realizacion, :lateralidad, :proyeccion, :fuerza_compresion, :tension_tubo, 
                    :corriente_tubo, :carga, :tiempo_exposicion, :filtro, :kerma_entrada, :dosis_glandular, 
                    :distancia_foco_paciente, :distancia_foco_mama, :factor_magnificacion, :rejilla, 
                    :temperatura, :grupo_espesor)
                """, {
                    'paciente_id': paciente.id,
                    'tipo_actividad': estudio.tipo_actividad,
                    'prestacion_realizada': estudio.prestacion_realizada,
                    'hora_adquisicion': estudio.hora_adquisicion,
                    'fecha_realizacion': estudio.fecha_realizacion,
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
                    'distancia_foco_paciente': estudio.distancia_foco_paciente,
                    'distancia_foco_mama': estudio.distancia_foco_mama,
                    'factor_magnificacion': estudio.factor_magnificacion,
                    'rejilla': estudio.rejilla,
                    'temperatura': estudio.temperatura,
                    'grupo_espesor': estudio.grupo_espesor
                })
        
        connection.commit()
        print("Datos insertados correctamente en Oracle.")
        
    except Exception as e:
        connection.rollback()
        print(f"Error en la inserción: {e}")
        raise e
        
    finally:
        cursor.close()
        connection.close()


def insert_data_DB():
    """
    Inserta los datos de la memoria global en la base de datos Oracle.
    """
    dsn = oracledb.makedsn('localhost', 1521, service_name='FREE')
    connection = oracledb.connect(user='your_username', password='your_password', dsn=dsn)
    cursor = connection.cursor()
    
    try:
        for paciente in temporal_save_data.pacientes_memoria:
            
            espesor_valor = getattr(paciente, 'espesor_mama_actual', getattr(paciente, 'espesor_mama', 0.0))
            
            cursor.execute("""
                INSERT INTO pacientes (id, edad, espesor_mama)
                VALUES (:id, :edad, :espesor_mama)
            """, {
                'id': paciente.id,
                'edad': paciente.edad,
                'espesor_mama': espesor_valor
            })
            
            for estudio in paciente.estudios:  
                cursor.execute("""
                    INSERT INTO estudios (paciente_id, tipo_actividad, prestacion_realizada, 
                    hora_adquisicion, fecha_realizacion, lateralidad, proyeccion, fuerza_compresion, 
                    tension_tubo, corriente_tubo, carga, tiempo_exposicion, filtro, kerma_entrada, 
                    dosis_glandular, distancia_foco_paciente, distancia_foco_mama, factor_magnificacion, 
                    rejilla, temperatura, grupo_espesor)
                    VALUES (:paciente_id, :tipo_actividad, :prestacion_realizada, :hora_adquisicion, 
                    :fecha_realizacion, :lateralidad, :proyeccion, :fuerza_compresion, :tension_tubo, 
                    :corriente_tubo, :carga, :tiempo_exposicion, :filtro, :kerma_entrada, :dosis_glandular, 
                    :distancia_foco_paciente, :distancia_foco_mama, :factor_magnificacion, :rejilla, 
                    :temperatura, :grupo_espesor)
                """, {
                    'paciente_id': paciente.id,
                    'tipo_actividad': estudio.tipo_actividad,
                    'prestacion_realizada': estudio.prestacion_realizada,
                    'hora_adquisicion': estudio.hora_adquisicion,
                    'fecha_realizacion': estudio.fecha_realizacion,
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
                    'distancia_foco_paciente': estudio.distancia_foco_paciente,
                    'distancia_foco_mama': estudio.distancia_foco_mama,
                    'factor_magnificacion': estudio.factor_magnificacion,
                    'rejilla': estudio.rejilla,
                    'temperatura': estudio.temperatura,
                    'grupo_espesor': estudio.grupo_espesor
                })
        
        connection.commit()
        print("Datos insertados correctamente en Oracle.")
        
    except Exception as e:
        connection.rollback()
        print(f"Error en la inserción: {e}")
        raise e
        
    finally:
        cursor.close()
        connection.close()