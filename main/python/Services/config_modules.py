import os
import json

def get_config():
    """Lee el archivo de configuración central."""
    # Localizamos el JSON (subiendo desde main/python/Views/ a la raíz del proyecto)
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
    json_path = os.path.join(base_dir, "main", "resources", "paths.json")
    
    try:
        with open(json_path, "r", encoding="utf-8") as f:
            config = json.load(f)
            # Convertimos la ruta relativa del JSON en una ruta absoluta real
            config["stylesheet_path"] = os.path.join(base_dir, config["stylesheet_path"])
            return config
    except Exception as e:
        print(f"Error cargando config: {e}")
        return {}

def load_stylesheet():
    """Carga el CSS usando la ruta definida en el fichero de configuración."""
    config = get_config()
    css_path = config.get("stylesheet_path")
    
    if css_path and os.path.exists(css_path):
        with open(css_path, "r", encoding="utf-8") as f:
            return f.read()
    return "" # Devuelve vacío si no encuentra el archivo