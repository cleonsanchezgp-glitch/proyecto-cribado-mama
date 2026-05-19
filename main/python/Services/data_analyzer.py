import numpy as np
from datetime import datetime
# Importamos el almacén para que los métodos puedan ser llamados sin parámetros si se desea,
# aunque en tu MainWindow los pasas como argumento.
from main.python.Services import temporal_save_data

def deducir_densidad(espesor):
    """Lógica de clasificación basada en el espesor (mm)."""
    if espesor < 45: return 'A'
    elif espesor < 55: return 'B'
    elif espesor < 65: return 'C'
    else: return 'D'

def obtener_metricas_dashboard(pacientes):
    """Calcula las métricas principales para los cuadros superiores del dashboard."""
    if not pacientes: return []

    # Calculamos las dosis totales usando la función local
    dosis_totales = [calcular_dosis_total_paciente(p) for p in pacientes]
    
    total_estudios = sum(len(p.estudios) for p in pacientes)
    dosis_media = np.mean(dosis_totales) if dosis_totales else 0
    desviacion_std = np.std(dosis_totales) if len(dosis_totales) > 1 else 0.0

    return [
        {"value": str(len(pacientes)), "subtitle": "Pacientes únicos", "badge_text": "Agrupados", "badge_style": "blue"},
        {"value": f"{dosis_media:.2f}".replace('.', ','), "subtitle": "Dosis Glandular Media", "badge_text": "mGy", "badge_style": "green"},
        {"value": str(total_estudios), "subtitle": "Exploraciones", "badge_text": "Procesadas", "badge_style": "blue"},
        {"value": f"{desviacion_std:.2f}".replace('.', ','), "subtitle": "Dispersión", "badge_text": "± mGy", "badge_style": "amber"}
    ]

def obtener_datos_graficos(pacientes):
    """Agrupa dosis por densidad mamaria para los gráficos del dashboard."""
    if not pacientes: return [], []
    
    datos_por_densidad = {'A': [], 'B': [], 'C': [], 'D': []}
    
    for p in pacientes:
        # Usamos el atributo espesor_mama_actual del objeto Paciente
        tipo = deducir_densidad(p.espesor_mama_actual)
        dosis = p.calcular_dosis_glandular_total()
        datos_por_densidad[tipo].append(dosis)
        
    total_pacientes = len(pacientes)
    datos_densidad = []
    datos_grafico = []
    
    for letra in ['A', 'B', 'C', 'D']:
        lista_dosis = datos_por_densidad[letra]
        n = len(lista_dosis)
        prop = n / total_pacientes if total_pacientes > 0 else 0
        
        # Formato para los "Density Progress Bars" de la UI
        datos_densidad.append({
            "proportion": float(prop), 
            "pct_text": f"{int(prop * 100)}%", 
            "n": str(n)
        })
        
        # Formato para el gráfico de barras/líneas
        dosis_media = np.mean(lista_dosis) if n > 0 else 0.0
        datos_grafico.append({
            "label": f"Tipo {letra}", 
            "value1": float(dosis_media * 0.85), # Referencia (ej. límite EUREF)
            "value2": float(dosis_media)          # Valor real obtenido
        })
        
    return datos_densidad, datos_grafico

def obtener_datos_historial(pacientes):
    """Transforma la lista de objetos en una lista plana para la tabla de la UI."""
    filas_historial = []
    
    for p in pacientes:
        dosis_total = calcular_dosis_total_paciente(p)
        
        # Lógica de estado según espesor
        limite_seguridad = 3.0 if p.espesor_mama_actual > 50 else 2.0
        estado = "revisar" if dosis_total > limite_seguridad else "ok"
        
        # Obtenemos la fecha del primer estudio disponible
        fecha_str = "Desconocida"
        if p.estudios:
            f = p.estudios[0].fecha_realizacion
            fecha_str = f.isoformat() if hasattr(f, 'isoformat') else str(f)
        
        filas_historial.append({
            "id": p.id,
            "age": str(p.edad),
            "density": deducir_densidad(p.espesor_mama_actual),
            "agd": float(round(dosis_total, 3)),
            "date": fecha_str, 
            "status": estado
        })
        
    return filas_historial


def deducir_densidad(espesor):
    """Lógica de clasificación basada en el espesor (mm)."""
    try:
        esp = float(espesor)
    except (ValueError, TypeError):
        return 'D'
    
    if esp < 45: return 'A'
    elif esp < 55: return 'B'
    elif esp < 65: return 'C'
    else: return 'D'
def calcular_dosis_total_paciente(paciente):
    """
    Suma la dosis de todos los estudios del objeto paciente.
    Sustituye la llamada al método inexistente en la clase Paciente.
    """
    if not hasattr(paciente, 'estudios') or not paciente.estudios:
        return 0.0
    return sum(estudio.dosis_glandular for estudio in paciente.estudios)

def obtener_datos_graficos(pacientes):
    """Agrupa dosis por densidad mamaria para los gráficos del dashboard."""
    if not pacientes: return [], []
    
    # Referencias EUREF aproximadas
    referencias = {'A': 1.5, 'B': 2.0, 'C': 2.5, 'D': 3.0}
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
        
        #Datos para barras de progreso
        datos_densidad.append({
            "proportion": float(prop), 
            "pct_text": f"{int(prop * 100)}%", 
            "n": str(n)
        })
        
        #Datos para el gráfico comparativo (EUREF vs Real)
        dosis_media = np.mean(lista_dosis) if n > 0 else 0.0
        datos_grafico.append({
            "label": f"Tipo {letra}", 
            "value1": referencias[letra], # Valor de referencia
            "value2": float(dosis_media)   # Valor real calculado
        })
        
    return datos_densidad, datos_grafico