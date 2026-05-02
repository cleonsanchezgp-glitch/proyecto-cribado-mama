import pandas as pd
import oracledb

def generate_csv_doc(pacientes, filename):
    data = []
    for paciente in pacientes:
        for estudio in paciente.estudios:  
            row = {
                'paciente_id': paciente.id,
                'edad': paciente.edad,
                'espesor_mama': paciente.espesor_mama,
                'tipo_actividad': estudio.tipo_actividad,
                'prestacion_realizada': estudio.prestacion_realizada,
                'hora_adquisicion': estudio.hora_adquisicion.isoformat() if estudio.hora_adquisicion else None,
                'fecha_realizacion': estudio.fecha_realizacion.isoformat() if estudio.fecha_realizacion else None,
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
            }
            data.append(row)
    df = pd.DataFrame(data)
    df.to_csv(filename, index=False)


def insert_data_DB(pacientes):
    # Assuming connection details; adjust as needed
    dsn = oracledb.makedsn('localhost', 1521, service_name='FREE')
    connection = oracledb.connect(user='your_username', password='your_password', dsn=dsn)
    cursor = connection.cursor()
    
    for paciente in pacientes:
        cursor.execute("""
            INSERT INTO pacientes (id, edad, espesor_mama)
            VALUES (:id, :edad, :espesor_mama)
        """, {
            'id': paciente.id,
            'edad': paciente.edad,
            'espesor_mama': paciente.espesor_mama
        })
        
        for estudio in paciente.estudios:  
            cursor.execute("""
                INSERT INTO estudios (paciente_id, tipo_actividad, prestacion_realizada, hora_adquisicion, fecha_realizacion, lateralidad, proyeccion, fuerza_compresion, tension_tubo, corriente_tubo, carga, tiempo_exposicion, filtro, kerma_entrada, dosis_glandular, distancia_foco_paciente, distancia_foco_mama, factor_magnificacion, rejilla, temperatura, grupo_espesor)
                VALUES (:paciente_id, :tipo_actividad, :prestacion_realizada, :hora_adquisicion, :fecha_realizacion, :lateralidad, :proyeccion, :fuerza_compresion, :tension_tubo, :corriente_tubo, :carga, :tiempo_exposicion, :filtro, :kerma_entrada, :dosis_glandular, :distancia_foco_paciente, :distancia_foco_mama, :factor_magnificacion, :rejilla, :temperatura, :grupo_espesor)
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
    cursor.close()
    connection.close()