import sys
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QHBoxLayout, QVBoxLayout,QScrollArea,
    QStackedWidget
)
from PySide6.QtWidgets import QMessageBox
from main.python.Services.data_cleaner import limpiar_datos_ris
from main.python.Services.data_calculator import calcular_dosis_pacientes
from main.python.Services.data_analyzer import obtener_metricas_dashboard, obtener_datos_graficos

from main.python.Services.config_modules import load_stylesheet
from main.python.Views.colors import COLORS
from main.python.Views.utils import Sidebar, Topbar
from main.python.Views.view_cargar import ViewCargar
from main.python.Views.view_config import ViewConfig
from main.python.Views.view_dosis import ViewDosis
from main.python.Views.view_hisotrial import ViewHistorial
from main.python.Views.view_resumen import ViewResumen

class MainWindow(QMainWindow):
    """
    Ventana principal. Orquesta Sidebar, Topbar y las vistas.

    CÓMO CONECTAR CONTROLLERS
    ───────────────────────────────────────────────────────────────────────
    1. Importa tus controllers aquí arriba.
    2. En __init__, instancíalos pasándoles la sesión de BD o los repos:

        self.resumen_ctrl   = ResumenController(db)
        self.dosis_ctrl     = DosisController(db)
        self.historial_ctrl = HistorialController(db)
        self.config_ctrl    = ConfigController(config_path)

    3. Llama a _load_initial_data() al final de __init__.

    4. Conecta botones de la topbar:

        self.topbar.export_btn.clicked.connect(self._on_export)
        self.topbar.new_analysis_btn.clicked.connect(self._on_new_analysis)

    5. Conecta el botón de procesar de ViewCargar:

        self.views["cargar"].process_btn.clicked.connect(
            lambda: self.cargar_ctrl.on_process(self.views["cargar"].selected_files)
        )

    6. Conecta búsqueda e historial:

        v = self.views["historial"]
        v.search_input.textChanged.connect(self.historial_ctrl.on_search)
        for key, chip in v.filter_chips.items():
            chip.toggled.connect(lambda checked, k=key: self.historial_ctrl.on_filter(k, checked))
    """

    TITLES = {
        "resumen":   "Resumen del análisis",
        "dosis":     "Análisis de dosis",
        "historial": "Historial de exploraciones",
        "cargar":    "Cargar archivos",
        "config":    "Configuración",
    }

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Cribado Mamá — H.U. Miguel Servet")
        self.resize(1200, 780)
        self.setMinimumSize(900, 600)
        STYLESHEET = load_stylesheet()
        self.setStyleSheet(STYLESHEET)

        central = QWidget()
        self.setCentralWidget(central)
        root = QHBoxLayout(central)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        self.sidebar = Sidebar(self._on_nav)
        root.addWidget(self.sidebar)

        main_area = QWidget()
        main_area.setStyleSheet(f"background:{COLORS['bg_tertiary']};")
        mv = QVBoxLayout(main_area)
        mv.setContentsMargins(0, 0, 0, 0)
        mv.setSpacing(0)

        self.topbar = Topbar()
        mv.addWidget(self.topbar)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("background:transparent; border:none;")

        self.stack = QStackedWidget()
        self.stack.setStyleSheet("background:transparent;")

        self.views = {
            "resumen":   ViewResumen(),
            "dosis":     ViewDosis(),
            "historial": ViewHistorial(),
            "cargar":    ViewCargar(),
            "config":    ViewConfig(),
        }
        for view in self.views.values():
            self.stack.addWidget(view)

        scroll.setWidget(self.stack)
        mv.addWidget(scroll, 1)
        root.addWidget(main_area, 1)

        # Título inicial
        self.topbar.set_title(self.TITLES["resumen"])

        # ── PUNTO DE CONEXIÓN: Añade aquí tus controllers e inicialización ──
        self.views["cargar"].process_btn.clicked.connect(self._ejecutar_limpieza)
        # self._init_controllers()
        # self._load_initial_data()

    def _on_nav(self, view_id):
        view = self.views.get(view_id)
        if view:
            self.stack.setCurrentWidget(view)
        self.topbar.set_title(self.TITLES.get(view_id, ""))


    def _ejecutar_limpieza(self):
        archivos = self.views["cargar"].selected_files
        
        if "ris" not in archivos:
            QMessageBox.warning(self, "Falta archivo", "Por favor, carga primero el archivo en 'Informe RIS / CSV'.")
            return
            
        ruta_ris = archivos["ris"]
        
        # 3. script de Pandas para limpiar
        exito = limpiar_datos_ris(ruta_ris)
        
        # 4. Si se ha limpiado, hacemos los cálculos
        if exito:
            import os
            # Buscamos el archivo limpio que acaba de crear el paso anterior
            directorio = os.path.dirname(ruta_ris)
            ruta_limpio = os.path.join(directorio, "datos_ris_limpios.xlsx")
            
            exito_calculo, ruta_final = calcular_dosis_pacientes(ruta_limpio)
            
            if exito_calculo:
                # Generamos las métricas
                metricas = obtener_metricas_dashboard(ruta_limpio, ruta_final)
                
                self.views["resumen"].populate_metrics(metricas)
                
                pasos = [
                    {"state": "done",   "detail": "CSV cargado y verificado"},
                    {"state": "done",   "detail": f"{metricas[2]['value']} registros limpios"},
                    {"state": "done",   "detail": "Dosis AGD y Efectiva calculada"},
                    {"state": "active", "detail": "Listo para generar gráficos"},
                    {"state": "",       "detail": "Exportación pendiente"}
                ]
                self.views["resumen"].populate_steps(pasos)

                # ALERTA DE ÉXITO
                alertas = [
                    {
                        "style": "blue", 
                        "title": "Análisis Completado", 
                        "subtitle": f"Se han procesado {metricas[0]['value']} pacientes con éxito."
                    }
                ]
                # Si la dosis media es alta (ej. mayor a 2.0), lanzamos un aviso amarillo
                if float(metricas[1]['value'].replace(',', '.')) > 2.0:
                    alertas.append({
                        "style": "amber", 
                        "title": "Aviso de Dosis", 
                        "subtitle": "La dosis media de este lote es superior a 2.0 mGy"
                    })

                self.views["resumen"].populate_alerts(alertas)
                
                datos_densidad, datos_grafico = obtener_datos_graficos(ruta_limpio)
                self.views["resumen"].populate_density(datos_densidad)
                self.views["resumen"].populate_chart(datos_grafico)
                
                # Cambiamos automáticamente a la pestaña de "Resumen"
                self._on_nav("resumen")
                
                QMessageBox.information(self, "Proceso Completado", "¡Datos procesados y dashboard actualizado!")
                
                # Se las pasamos a la pantalla de resumen
                self.views["resumen"].populate_metrics(metricas)
                
                # Cambiamos automáticamente a la pestaña de "Resumen"
                self._on_nav("resumen")
                
                QMessageBox.information(self, "Proceso Completado", "¡Datos procesados y dashboard actualizado!")
            else:
                QMessageBox.critical(self, "Error", "Fallo al calcular las dosis. Revisa la consola.")
        else:
            QMessageBox.critical(self, "Error", "Hubo un problema al procesar el archivo. Revisa la consola.")

    # ── MÉTODOS A IMPLEMENTAR ──────────────────────────────────────────────

    # def _init_controllers(self):
    #     """Instancia controllers y conecta señales de botones."""
    #     pass

    # def _load_initial_data(self):
    #     """Carga datos iniciales en todas las vistas al arrancar."""
    #     pass


# ════════════════════════════════════════════════════════════════════════════
#  PUNTO DE ENTRADA
# ════════════════════════════════════════════════════════════════════════════

def main():
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()