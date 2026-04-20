import sys
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QHBoxLayout, QVBoxLayout,
    QScrollArea, QStackedWidget
)
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

        # ── PUNTO DE CONEXIÓN DE CONTROLLERS ─────────────────────────────
        # Descomenta estas líneas cuando tengas los controllers implementados:
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