import numpy as np

def calcular_dosis_total_paciente(paciente):
    return sum(estudio.dosis_glandular for estudio in paciente.estudios)

def deducir_densidad(espesor):
    if espesor < 45: return 'A'
    elif espesor < 55: return 'B'
    elif espesor < 65: return 'C'
    else: return 'D'

def obtener_metricas_dashboard(pacientes):
    if not pacientes: return []
    dosis_totales = [calcular_dosis_total_paciente(p) for p in pacientes]
    registros_cruzados = sum(len(p.estudios) for p in pacientes)
    dosis_media = np.mean(dosis_totales) if dosis_totales else 0
    desviacion_std = np.std(dosis_totales) if len(dosis_totales) > 1 else 0.0

    return [
        {"value": str(len(pacientes)), "subtitle": "Pacientes únicos", "badge_text": "Agrupados", "badge_style": "blue"},
        {"value": f"{dosis_media:.2f}".replace('.', ','), "subtitle": "Dosis Glandular Media", "badge_text": "mGy", "badge_style": "green"},
        {"value": str(registros_cruzados), "subtitle": "Exploraciones", "badge_text": "Limpias", "badge_style": "blue"},
        {"value": f"{desviacion_std:.2f}".replace('.', ','), "subtitle": "Dispersión", "badge_text": "± mGy", "badge_style": "amber"}
    ]

def obtener_datos_graficos(pacientes):
    if not pacientes: return [], []
    datos_por_densidad = {'A': [], 'B': [], 'C': [], 'D': []}
    
    for p in pacientes:
        tipo = deducir_densidad(p.espesor_mama_actual)
        dosis = calcular_dosis_total_paciente(p)
        datos_por_densidad[tipo].append(dosis)
        
    total_pacientes = len(pacientes)
    datos_densidad = []
    datos_grafico = []
    
    for letra in ['A', 'B', 'C', 'D']:
        lista_dosis = datos_por_densidad[letra]
        n = len(lista_dosis)
        prop = n / total_pacientes if total_pacientes > 0 else 0
        
        datos_densidad.append({"proportion": float(prop), "pct_text": f"{int(prop * 100)}%", "n": str(n)})
        
        dosis_media = np.mean(lista_dosis) if n > 0 else 0.0
        datos_grafico.append({"label": f"Tipo {letra}", "value1": float(dosis_media * 0.9), "value2": float(dosis_media)})
        
    return datos_densidad, datos_grafico

def obtener_datos_historial(pacientes):
    filas_historial = []
    for p in pacientes:
        dosis_total = calcular_dosis_total_paciente(p)
        estado = "revisar" if dosis_total > 2.0 else "ok"
        fecha_str = p.estudios[0].fecha_realizacion if p.estudios else "Desconocida"
        
        filas_historial.append({
            "id": p.id,
            "age": str(p.edad),
            "density": deducir_densidad(p.espesor_mama_actual),
            "agd": float(dosis_total),
            "date": str(fecha_str).split(' ')[0], 
            "status": estado
        })
    return filas_historial