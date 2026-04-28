import sys
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QHBoxLayout, QVBoxLayout,
    QScrollArea, QStackedWidget
)
from PySide6.QtWidgets import QMessageBox
from main.python.Services.data_cleaner import limpiar_datos_ris
from main.python.Services.data_calculator import calcular_dosis_pacientes
from main.python.Services.data_analyzer import obtener_metricas_dashboard, obtener_datos_graficos, obtener_datos_historial

from main.python.Services.config_modules import load_stylesheet
from main.python.Views.colors import COLORS
from main.python.Views.utils import Sidebar, Topbar
from main.python.Views.view_cargar import ViewCargar
from main.python.Views.view_config import ViewConfig
from main.python.Views.view_dosis import ViewDosis
from main.python.Views.view_hisotrial import ViewHistorial
from main.python.Views.view_resumen import ViewResumen


# ══════════════════════════════════════════════════════════════════════════════
#  VENTANA PRINCIPAL
#  Orquesta todos los componentes: Sidebar, Topbar y las 5 vistas.
#  Es el punto central donde se instancian y conectan los controllers.
#
#  ESTRUCTURA VISUAL:
#    ┌──────────┬──────────────────────────────────────┐
#    │          │  Topbar (título + botones acción)    │
#    │ Sidebar  ├──────────────────────────────────────┤
#    │  (nav)   │  QStackedWidget con las 5 vistas     │
#    │          │  (solo una visible a la vez)         │
#    └──────────┴──────────────────────────────────────┘
#
#  PARA AÑADIR LÓGICA REAL:
#    1. Importa tus controllers arriba
#    2. Descomenta y rellena _init_controllers()
#    3. Descomenta y rellena _load_initial_data()
#    4. Conecta los botones de la topbar en _init_controllers()
# ══════════════════════════════════════════════════════════════════════════════

class MainWindow(QMainWindow):

    # Títulos mostrados en la Topbar al navegar a cada vista
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

        # Stylesheet global — aplicado a toda la aplicación desde archivo CSS externo
        STYLESHEET = load_stylesheet()
        self.setStyleSheet(STYLESHEET)

        # ── Layout raíz: Sidebar + Área principal ─────────────────────────
        central = QWidget()
        self.setCentralWidget(central)
        root = QHBoxLayout(central)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # Sidebar — panel de navegación lateral
        # Recibe _on_nav como callback para cambiar de vista al hacer clic
        self.sidebar = Sidebar(self._on_nav)
        root.addWidget(self.sidebar)

        # ── Área principal (derecha): Topbar + Contenido scrollable ───────
        main_area = QWidget()
        main_area.setStyleSheet(f"background:{COLORS['bg_tertiary']};")
        mv = QVBoxLayout(main_area)
        mv.setContentsMargins(0, 0, 0, 0)
        mv.setSpacing(0)

        # Topbar — barra superior con título y botones de acción
        # Conectar botones desde _init_controllers():
        #   self.topbar.export_btn.clicked.connect(ctrl.on_export)
        #   self.topbar.new_analysis_btn.clicked.connect(ctrl.on_new_analysis)
        self.topbar = Topbar()
        mv.addWidget(self.topbar)

        # Área de scroll que envuelve el QStackedWidget
        # Permite hacer scroll vertical en vistas con mucho contenido
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("background:transparent; border:none;")

        # QStackedWidget — contiene todas las vistas, muestra solo una a la vez
        # Se cambia de vista con self.stack.setCurrentWidget(view)
        self.stack = QStackedWidget()
        self.stack.setStyleSheet("background:transparent;")

        # Registro de vistas — añadir aquí si se crean nuevas vistas
        # La clave debe coincidir con el view_id de Sidebar.NAV_ITEMS
        self.views = {
            "resumen":   ViewResumen(),    # Vista de resumen global del lote
            "dosis":     ViewDosis(),      # Vista de análisis de dosis AGD
            "historial": ViewHistorial(),  # Vista de tabla de pacientes
            "cargar":    ViewCargar(),     # Vista de carga de archivos
            "config":    ViewConfig(),     # Vista de configuración y parámetros
        }
        for view in self.views.values():
            self.stack.addWidget(view)

        scroll.setWidget(self.stack)
        mv.addWidget(scroll, 1)
        root.addWidget(main_area, 1)

        # Activar la vista inicial (Resumen) al arrancar
        self.topbar.set_title(self.TITLES["resumen"])

        # ── PUNTO DE CONEXIÓN: Añade aquí tus controllers e inicialización ──
        self.views["cargar"].process_btn.clicked.connect(self._ejecutar_limpieza)
        # Conectar el buscador del historial a la nueva función maestra
        self.views["historial"].search_input.textChanged.connect(self._actualizar_tabla_historial)
        
        # Conectar los botones de densidad (Chips)
        for nombre, chip in self.views["historial"].filter_chips.items():
            chip.clicked.connect(lambda checked=False, n=nombre: self._al_pulsar_chip(n))

        # self._init_controllers()
        # self._load_initial_data()

    def _on_nav(self, view_id: str):
        """
        Callback de navegación llamado por Sidebar al hacer clic en un ítem del menú.
        Cambia la vista visible en el QStackedWidget y actualiza el título de la Topbar.
        """
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

                # Enviar datos a la pestaña Historial
                self.datos_tabla = obtener_datos_historial(ruta_limpio, ruta_final)
                self.views["historial"].populate_table(self.datos_tabla)
                
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

    def _al_pulsar_chip(self, nombre_pulsado):
        # 1. Hacemos que se comporten como "Radio Buttons" (solo se queda encendido el que pulsas)
        for nombre, chip in self.views["historial"].filter_chips.items():
            chip.setChecked(nombre == nombre_pulsado)
            
        # 2. Le decimos a la tabla que se actualice con el nuevo filtro
        self._actualizar_tabla_historial()

    def _actualizar_tabla_historial(self, *args):
        # Si aún no hay datos cargados, no hacemos nada
        if not hasattr(self, 'datos_tabla'):
            return
            
        # Qué texto hay en el buscador
        texto = self.views["historial"].search_input.text().lower()
        
        # Averiguar qué chip está encendido ahora mismo
        filtro_activo = "Todos"
        for nombre, chip in self.views["historial"].filter_chips.items():
            if chip.isChecked():
                filtro_activo = nombre
                break
                
        # Filtramos la lista maestra
        filas_filtradas = []
        for fila in self.datos_tabla:
            # Condición 1: El texto del buscador encaja con el ID
            pasa_texto = texto in fila['id'].lower()
            
            # Condición 2: La densidad del paciente encaja con el botón pulsado
            if filtro_activo == "Todos":
                pasa_densidad = True
            else:
                # Si pulsaste "Tipo A", le quitamos el "Tipo " para compararlo con la "A" de la fila
                letra_densidad = filtro_activo.replace("Tipo ", "")
                pasa_densidad = (fila['density'] == letra_densidad)
                
            # Si el paciente cumple ambas cosas, se muestra en la tabla
            if pasa_texto and pasa_densidad:
                filas_filtradas.append(fila)
                
        self.views["historial"].populate_table(filas_filtradas)

    # ── MÉTODOS A IMPLEMENTAR ──────────────────────────────────────────────

    # def _init_controllers(self):
    #     """
    #     Instancia los controllers y conecta las señales de los botones.
    #
    #     Ejemplo:
    #         self.resumen_ctrl   = ResumenController(db_session)
    #         self.dosis_ctrl     = DosisController(db_session)
    #         self.historial_ctrl = HistorialController(db_session)
    #         self.config_ctrl    = ConfigController(config_path)
    #
    #         # Conectar botones de la Topbar
    #         self.topbar.export_btn.clicked.connect(self.resumen_ctrl.on_export)
    #         self.topbar.new_analysis_btn.clicked.connect(self.resumen_ctrl.on_new_analysis)
    #
    #         # Conectar botón de procesado de la vista Cargar
    #         self.views["cargar"].process_btn.clicked.connect(
    #             lambda: self.cargar_ctrl.on_process(self.views["cargar"].selected_files)
    #         )
    #
    #         # Conectar búsqueda y filtros del Historial
    #         v = self.views["historial"]
    #         v.search_input.textChanged.connect(self.historial_ctrl.on_search)
    #         for key, chip in v.filter_chips.items():
    #             chip.toggled.connect(lambda checked, k=key: self.historial_ctrl.on_filter(k, checked))
    #     """
    #     pass

    # def _load_initial_data(self):
    #     """
    #     Carga los datos iniciales en todas las vistas al arrancar la aplicación.
    #     Se llama una sola vez después de _init_controllers().
    #
    #     Ejemplo:
    #         self.views["resumen"].populate_metrics(self.resumen_ctrl.get_metrics())
    #         self.views["resumen"].populate_chart(self.resumen_ctrl.get_chart_data())
    #         self.views["resumen"].populate_density(self.resumen_ctrl.get_density_distribution())
    #         self.views["resumen"].populate_steps(self.resumen_ctrl.get_pipeline_steps())
    #         self.views["resumen"].populate_alerts(self.resumen_ctrl.get_alerts())
    #
    #         self.views["dosis"].populate_stats(self.dosis_ctrl.get_stats())
    #         self.views["dosis"].populate_scatter(self.dosis_ctrl.get_scatter_points())
    #         self.views["dosis"].populate_compliance(self.dosis_ctrl.get_compliance())
    #
    #         self.views["historial"].populate_table(self.historial_ctrl.get_all())
    #
    #         self.views["config"].populate_euref_params(self.config_ctrl.get_euref_params())
    #         self.views["config"].populate_integrations(self.config_ctrl.get_integration_status())
    #
    #         self.sidebar.set_connection_status(self.config_ctrl.is_pacs_connected(), "Conectado a PACS")
    #     """
    #     pass


# ══════════════════════════════════════════════════════════════════════════════
#  PUNTO DE ENTRADA
# ══════════════════════════════════════════════════════════════════════════════

def main():
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()