from PySide6.QtWidgets import (
    QFrame, QWidget, QHBoxLayout, QVBoxLayout, QPushButton, QScrollArea, QSizePolicy, QLabel
)
from PySide6.QtCore import Qt
from PySide6.QtGui import (
    QColor, QPainter, QPen, QBrush, QCursor
)

from main.python.Views.colors import COLORS


# ══════════════════════════════════════════════════════════════════════════════
#  FUNCIONES HELPER DE ESTILO
#  Utilidades reutilizables para crear widgets con estilos consistentes.
#  No contienen lógica de negocio — solo presentación.
# ══════════════════════════════════════════════════════════════════════════════

def card_style(bg="#ffffff", radius=12, border=True):
    """Devuelve un string CSS para usar como stylesheet de una tarjeta."""
    b = "border: 0.5px solid rgba(0,0,0,0.10);" if border else ""
    return f"background:{bg}; border-radius:{radius}px; {b}"


def label(text, size=13, color="#1a1a18", weight="normal", wrap=False):
    """
    Crea un QLabel con estilos predefinidos de la interfaz.
    Úsalo en lugar de QLabel() directamente para mantener consistencia visual.
    """
    lbl = QLabel(text)
    lbl.setStyleSheet(
        f"font-size:{size}px; color:{color}; "
        f"font-weight:{'600' if weight=='bold' else '400'}; "
        "background:transparent; border:none;"
    )
    if wrap:
        lbl.setWordWrap(True)
    return lbl


def load_stylesheet(file_path):
    """
    Lee un archivo CSS externo y devuelve su contenido como string.
    Se usa en MainWindow para aplicar el stylesheet global a la aplicación.
    """
    try:
        with open(file_path, "r") as f:
            return f.read()
    except FileNotFoundError:
        print(f"Error: No se encontró el archivo {file_path}")
        return ""


def badge(text, style="blue"):
    """
    Crea una etiqueta pill (pastilla redondeada) de estado o categoría.
    Estilos disponibles: "blue", "green", "amber", "coral", "gray".
    Se usa para indicar estados como "Conectado", "Revisar", "OK", etc.
    """
    styles = {
        "blue":  "background:#E6F1FB; color:#185FA5;",
        "green": "background:#EAF3DE; color:#3B6D11;",
        "amber": "background:#FAEEDA; color:#854F0B;",
        "coral": "background:#FAECE7; color:#993C1D;",
        "gray":  "background:#f0ede8; color:#5f5e5a;",
    }
    lbl = QLabel(text)
    lbl.setStyleSheet(
        f"{styles.get(style, styles['blue'])} "
        "font-size:10px; font-weight:600; padding:2px 8px; "
        "border-radius:99px; border:none;"
    )
    lbl.setFixedHeight(18)
    return lbl


def separator(horizontal=True):
    """
    Crea una línea divisoria fina horizontal o vertical.
    Se usa para separar filas dentro de paneles (p. ej. lista de parámetros EUREF).
    """
    line = QFrame()
    line.setFrameShape(QFrame.HLine if horizontal else QFrame.VLine)
    line.setStyleSheet("color: rgba(0,0,0,0.10); background: rgba(0,0,0,0.10);")
    line.setFixedHeight(1 if horizontal else 0)
    return line


# ══════════════════════════════════════════════════════════════════════════════
#  WIDGET: ProgressBar
#  Barra de progreso personalizada pintada con QPainter.
#  Se usa en ViewResumen (distribución por densidad) y ViewDosis (cumplimiento EUREF).
#
#  PARA RELLENAR CON DATOS REALES:
#      bar.set_value(proporcion_float, color_hex)
#      Ejemplo: bar.set_value(0.94, "#3B6D11")
# ══════════════════════════════════════════════════════════════════════════════

class ProgressBar(QWidget):
    """Barra de progreso horizontal pintada a mano."""

    def __init__(self, value=0.0, color="#185FA5", height=8, parent=None):
        super().__init__(parent)
        self._value = max(0.0, min(1.0, value))   # Proporción entre 0.0 y 1.0
        self._color = color
        self.setFixedHeight(height)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

    def set_value(self, value: float, color: str = None):
        """
        ── PUNTO DE ENTRADA DE DATOS ──────────────────────────────────────
        Actualiza la barra con un nuevo valor y color opcionales.

        Llamar desde el controller tras calcular el porcentaje:
            bar.set_value(agd_cumplimiento / 100.0, "#3B6D11")
        """
        self._value = max(0.0, min(1.0, value))
        if color:
            self._color = color
        self.update()   # Fuerza repintado

    def paintEvent(self, event):
        # Dibuja el fondo gris y el relleno coloreado proporcionalmente
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        r = self.rect()

        # Fondo gris claro
        p.setBrush(QBrush(QColor("#f0ede8")))
        p.setPen(Qt.NoPen)
        p.drawRoundedRect(r, 4, 4)

        # Relleno coloreado según el valor
        fill_w = int(r.width() * self._value)
        if fill_w > 0:
            fr = r.adjusted(0, 0, -(r.width() - fill_w), 0)
            p.setBrush(QBrush(QColor(self._color)))
            p.drawRoundedRect(fr, 4, 4)


# ══════════════════════════════════════════════════════════════════════════════
#  WIDGET: BarChart
#  Gráfico de barras agrupadas (año anterior / año actual) para dosis AGD.
#  Se usa en ViewResumen, panel "Dosis media AGD por grupo de densidad".
#
#  PARA RELLENAR CON DATOS REALES:
#      chart.set_data([
#          ("Tipo A", valor_anterior, valor_actual, color_claro, color_oscuro),
#          ...
#      ])
# ══════════════════════════════════════════════════════════════════════════════

class BarChart(QWidget):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumHeight(220)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self._data = []   # Lista vacía hasta que se inyecten datos reales

    def set_data(self, data: list):
        """
        ── PUNTO DE ENTRADA DE DATOS ──────────────────────────────────────
        Inyecta los datos del gráfico de barras.

        Formato esperado:
            [("Tipo A", val_año_anterior, val_año_actual, color_claro, color_oscuro), ...]

        Llamar desde ViewResumen.populate_chart() con datos del controller:
            chart.set_data(resumen_controller.get_agd_por_tipo())
        """
        self._data = data
        self.update()   # Fuerza repintado con los nuevos datos

    def paintEvent(self, event):
        if not self._data:
            return   # Sin datos → no dibuja nada

        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        w, h = self.width(), self.height()
        margin_l, margin_b, margin_t = 38, 28, 10

        chart_h = h - margin_b - margin_t
        chart_w = w - margin_l - 12

        # ── Líneas de cuadrícula horizontal (eje Y) ───────────────────────
        for y_val in [0, 1.0, 2.0, 3.0]:
            y = h - margin_b - int(chart_h * y_val / 3.5)
            p.setPen(QPen(QColor(0, 0, 0, 25), 1, Qt.DashLine))
            p.drawLine(margin_l, y, w - 12, y)
            # Etiqueta numérica del eje Y
            p.setPen(QColor("#9a9890"))
            font = p.font()
            font.setPointSize(7)
            p.setFont(font)
            p.drawText(0, y + 4, 34, 14, Qt.AlignRight, f"{y_val:.1f}")

        # ── Barras agrupadas por tipo de densidad ─────────────────────────
        group_w = chart_w / len(self._data)
        bar_w = group_w * 0.22
        gap = bar_w * 0.3

        for idx, (label_txt, h1, h2, c1, c2) in enumerate(self._data):
            gx = margin_l + idx * group_w + group_w * 0.15
            max_h = 180   # Altura máxima de referencia para escalar las barras

            # Barra año anterior (color claro)
            bh1 = int(chart_h * h1 / max_h)
            x1 = int(gx)
            p.setPen(Qt.NoPen)
            p.setBrush(QBrush(QColor(c1)))
            p.drawRoundedRect(x1, h - margin_b - bh1, int(bar_w), bh1, 2, 2)

            # Barra año actual (color oscuro)
            bh2 = int(chart_h * h2 / max_h)
            x2 = int(gx + bar_w + gap)
            p.setBrush(QBrush(QColor(c2)))
            p.drawRoundedRect(x2, h - margin_b - bh2, int(bar_w), bh2, 2, 2)

            # Etiqueta del grupo en el eje X (p. ej. "Tipo A")
            p.setPen(QColor("#9a9890"))
            font2 = p.font()
            font2.setPointSize(7)
            p.setFont(font2)
            center_x = int(gx + bar_w + gap / 2)
            p.drawText(center_x - 22, h - margin_b + 6, 44, 14, Qt.AlignCenter, label_txt)


# ══════════════════════════════════════════════════════════════════════════════
#  WIDGET: ScatterPlot
#  Gráfico de dispersión Espesor (mm) vs. AGD (mGy) coloreado por densidad.
#  Se usa en ViewDosis, panel "Dispersión Espesor vs. AGD".
#  Incluye línea de referencia EUREF a 2,5 mGy.
#
#  PARA RELLENAR CON DATOS REALES:
#      scatter.set_data([
#          (espesor_mm, agd_mGy, densidad_idx),   # densidad: 0=A, 1=B, 2=C, 3=D
#          ...
#      ])
# ══════════════════════════════════════════════════════════════════════════════

class ScatterPlot(QWidget):

    # Colores por tipo de densidad: A=verde, B=azul, C=naranja, D=rojo
    DENSITY_COLORS = ["#97C459", "#378ADD", "#EF9F27", "#D85A30"]

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumHeight(240)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self._points = []   # Lista vacía hasta que se inyecten datos reales

    def set_data(self, points: list):
        """
        ── PUNTO DE ENTRADA DE DATOS ──────────────────────────────────────
        Inyecta los puntos del scatter plot.

        Formato esperado:
            [(espesor_mm: float, agd_mGy: float, densidad_idx: int), ...]
            densidad_idx → 0=Tipo A, 1=Tipo B, 2=Tipo C, 3=Tipo D

        Llamar desde ViewDosis.populate_scatter() con datos del controller:
            scatter.set_data(dosis_controller.get_scatter_points())
        """
        self._points = points
        self.update()   # Fuerza repintado

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        w, h = self.width(), self.height()
        ml, mb, mt, mr = 36, 28, 10, 12

        chart_w = w - ml - mr
        chart_h = h - mb - mt

        # ── Ejes X e Y ────────────────────────────────────────────────────
        p.setPen(QPen(QColor(0, 0, 0, 50), 1))
        p.drawLine(ml, mt, ml, h - mb)       # Eje Y (vertical)
        p.drawLine(ml, h - mb, w - mr, h - mb)  # Eje X (horizontal)

        # ── Línea de referencia EUREF a 2,5 mGy ──────────────────────────
        # TODO: hacer configurable desde ViewConfig (parámetro "Límite AGD tipo B")
        ref_y = mt + int(chart_h * (1 - 2.5 / 4.5))
        p.setPen(QPen(QColor("#D85A30"), 1, Qt.DashLine))
        p.drawLine(ml, ref_y, w - mr, ref_y)
        p.setPen(QColor("#D85A30"))
        font = p.font()
        font.setPointSize(7)
        p.setFont(font)
        p.drawText(w - mr - 50, ref_y - -2, 50, 12, Qt.AlignRight, "Ref. EUREF")

        # ── Etiquetas del eje X (espesor en mm) ───────────────────────────
        p.setPen(QColor("#9a9890"))
        font2 = p.font()
        font2.setPointSize(7)
        p.setFont(font2)
        for val, txt in [(0, "30mm"), (0.5, "60mm"), (1.0, "90mm")]:
            x = ml + int(chart_w * val)
            p.drawText(x - 15, h - mb + 6, 30, 12, Qt.AlignCenter, txt)

        # ── Puntos del scatter (un punto por paciente) ────────────────────
        for thickness, agd, d in self._points:
            # Mapear espesor (30–90mm) al ancho del gráfico
            xp = ml + int(chart_w * (thickness - 30) / 60)
            # Mapear AGD (0–4,5 mGy) a la altura del gráfico (invertido: 0 abajo)
            yp = mt + int(chart_h * (1 - agd / 4.5))
            color = QColor(self.DENSITY_COLORS[d % len(self.DENSITY_COLORS)])
            color.setAlpha(180)   # Semi-transparente para ver solapamientos
            p.setPen(Qt.NoPen)
            p.setBrush(QBrush(color))
            p.drawEllipse(xp - 3, yp - 3, 7, 7)


# ══════════════════════════════════════════════════════════════════════════════
#  COMPONENTE: Sidebar
#  Panel de navegación lateral izquierdo.
#  Contiene: logo, menú de navegación por secciones, y footer de estado de conexión.
#
#  PARA ACTUALIZAR EL ESTADO DE CONEXIÓN DESDE UN CONTROLLER:
#      sidebar.set_connection_status(True, "Conectado a PACS")
# ══════════════════════════════════════════════════════════════════════════════

class Sidebar(QWidget):

    # Estructura del menú: (sección, [(id_vista, nombre, icono), ...])
    # Para añadir una nueva vista: agregar una tupla aquí y registrarla en MainWindow.views
    NAV_ITEMS = [
        ("Análisis", [
            ("resumen",   "Resumen",          "◈"),
            ("dosis",     "Análisis de dosis", "◉"),
            ("historial", "Historial",         "≡"),
        ]),
        ("Datos", [
            ("cargar",   "Cargar archivos",    "⊞"),
            ("exportar", "Exportar resultados","↓"),
        ]),
        ("Sistema", [
            ("config",   "Configuración",      "⚙"),
        ]),
    ]

    def __init__(self, on_nav, parent=None):
        """
        on_nav: callable(view_id: str) — función de MainWindow que cambia la vista activa.
        Se pasa como callback para desacoplar Sidebar de MainWindow.
        """
        super().__init__(parent)
        self.setFixedWidth(220)
        # ObjectName necesario para que el selector CSS #Sidebar tenga alta especificidad
        # y no sea sobreescrito por el stylesheet global de QWidget
        self.setObjectName("Sidebar")
        self.setStyleSheet(
            "#Sidebar, #Sidebar QWidget, #Sidebar QScrollArea {"
            f"  background:{COLORS['bg_primary']};"
            "  color:#1a1a18;"
            "}"
            "#Sidebar {"
            "  border-right:1px solid rgba(0,0,0,0.08);"
            "}"
        )
        self._on_nav = on_nav
        self._buttons = {}   # Mapa { view_id: QPushButton } para gestionar el estado activo
        self._build()

    def _build(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # ── Cabecera / Logo ───────────────────────────────────────────────
        # Zona fija superior con icono, nombre de la app y nombre del hospital
        logo_w = QWidget()
        logo_w.setObjectName("SidebarLogo")
        logo_w.setFixedHeight(72)
        logo_w.setStyleSheet(
            f"#SidebarLogo {{ background:{COLORS['bg_primary']}; "
            "border-bottom:1px solid rgba(0,0,0,0.08); }}"
        )
        ll = QVBoxLayout(logo_w)
        ll.setContentsMargins(16, 16, 16, 12)
        ll.setSpacing(3)

        # Icono de la aplicación (emoji de estetoscopio sobre fondo azul)
        icon_lbl = QLabel("🩺")
        icon_lbl.setStyleSheet(
            f"background:{COLORS['blue']}; border-radius:8px; font-size:16px; padding:4px; border:none;"
        )
        icon_lbl.setFixedSize(32, 32)
        icon_lbl.setAlignment(Qt.AlignCenter)

        title_lbl = label("Cribado Mamá", 13, COLORS["text_primary"], "bold")
        title_lbl.setStyleSheet(title_lbl.styleSheet() + "padding-left: 40px;")
        sub_lbl = label("H.U. Miguel Servet", 11, COLORS["text_secondary"])
        sub_lbl.setStyleSheet(sub_lbl.styleSheet() + "padding-left: 40px;")

        ll.addWidget(icon_lbl)
        ll.addWidget(title_lbl)
        ll.addWidget(sub_lbl)
        layout.addWidget(logo_w)

        # ── Menú de navegación (scrollable) ──────────────────────────────
        # Cada ítem es un QPushButton checkable que activa la vista correspondiente
        nav_scroll = QScrollArea()
        nav_scroll.setWidgetResizable(True)
        nav_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        nav_scroll.setStyleSheet("background:transparent; border:none;")

        nav_container = QWidget()
        nav_container.setStyleSheet(f"background:{COLORS['bg_primary']};")
        nav_layout = QVBoxLayout(nav_container)
        nav_layout.setContentsMargins(8, 12, 8, 12)
        nav_layout.setSpacing(0)

        first_btn = None
        for section_name, items in self.NAV_ITEMS:
            # Etiqueta de sección (ANÁLISIS, DATOS, SISTEMA)
            sec_lbl = label(section_name.upper(), 10, COLORS["text_tertiary"])
            sec_lbl.setStyleSheet(
                f"font-size:10px; color:{COLORS['text_tertiary']}; font-weight:600; "
                "letter-spacing:0.06em; padding:0 8px; background:transparent; border:none;"
            )
            nav_layout.addSpacing(12)
            nav_layout.addWidget(sec_lbl)
            nav_layout.addSpacing(4)

            for view_id, name, icon in items:
                # Botón de navegación — al hacer clic llama a _nav_click(view_id)
                btn = QPushButton(f"  {icon}  {name}")
                btn.setCheckable(True)
                btn.setCursor(QCursor(Qt.PointingHandCursor))
                btn.setFixedHeight(34)
                btn.setStyleSheet(
                    f"QPushButton {{ background:transparent; color:{COLORS['text_secondary']}; "
                    "text-align:left; padding:0 8px; border-radius:8px; border:none; font-size:13px; }}"
                    f"QPushButton:hover {{ background:{COLORS['bg_secondary']}; color:{COLORS['text_primary']}; }}"
                    f"QPushButton:checked {{ background:{COLORS['blue_light']}; color:{COLORS['blue']}; font-weight:600; }}"
                )
                btn.clicked.connect(lambda _, vid=view_id, b=btn: self._nav_click(vid, b))
                self._buttons[view_id] = btn
                nav_layout.addWidget(btn)
                nav_layout.addSpacing(2)
                if first_btn is None:
                    first_btn = btn   # Guardamos el primero para activarlo por defecto

        nav_layout.addStretch()
        nav_scroll.setWidget(nav_container)
        layout.addWidget(nav_scroll, 1)

        # ── Footer de estado de conexión ──────────────────────────────────
        # Muestra si la aplicación está conectada a PACS/RIS o en modo offline
        # Para actualizar: sidebar.set_connection_status(True/False, "texto")
        footer = QWidget()
        footer.setObjectName("SidebarFooter")
        footer.setFixedHeight(40)
        footer.setStyleSheet(
            f"#SidebarFooter {{ background:{COLORS['bg_primary']}; "
            "border-top:1px solid rgba(0,0,0,0.08); }}"
        )
        fl = QHBoxLayout(footer)
        fl.setContentsMargins(16, 0, 16, 0)

        self._status_dot = QLabel("●")
        self._status_dot.setStyleSheet(
            f"color:{COLORS['status_green']}; font-size:8px; background:transparent; border:none;"
        )
        self._status_label = label("Modo offline", 11, COLORS["text_tertiary"])
        fl.addWidget(self._status_dot)
        fl.addWidget(self._status_label)
        fl.addStretch()
        layout.addWidget(footer)

        # Activar el primer ítem del menú al arrancar
        if first_btn:
            first_btn.setChecked(True)

    def _nav_click(self, view_id, clicked_btn):
        """Desactiva todos los botones y activa solo el clicado. Llama al callback de navegación."""
        for btn in self._buttons.values():
            btn.setChecked(False)
        clicked_btn.setChecked(True)
        self._on_nav(view_id)

    def activate(self, view_id):
        """
        Activa programáticamente un botón del menú sin disparar la navegación.
        Útil para sincronizar la sidebar cuando se cambia de vista desde código.
        """
        for vid, btn in self._buttons.items():
            btn.setChecked(vid == view_id)

    def set_connection_status(self, online: bool, text: str = None):
        """
        ── PUNTO DE ENTRADA DE ESTADO ─────────────────────────────────────
        Actualiza el indicador de conexión del footer.

        Llamar desde el controller de conexión PACS/RIS:
            sidebar.set_connection_status(True, "Conectado a PACS")
            sidebar.set_connection_status(False, "Sin conexión")
        """
        color = COLORS["status_green"] if online else COLORS["text_tertiary"]
        self._status_dot.setStyleSheet(
            f"color:{color}; font-size:8px; background:transparent; border:none;"
        )
        if text:
            self._status_label.setText(text)


# ══════════════════════════════════════════════════════════════════════════════
#  COMPONENTE: Topbar
#  Barra superior horizontal con título de la vista activa y botones de acción.
#  Contiene: título dinámico, botón "Exportar" y botón "Nuevo análisis".
#
#  PARA CONECTAR LOS BOTONES DESDE MainWindow:
#      topbar.export_btn.clicked.connect(ctrl.on_export)
#      topbar.new_analysis_btn.clicked.connect(ctrl.on_new_analysis)
# ══════════════════════════════════════════════════════════════════════════════

class Topbar(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedHeight(52)
        self.setStyleSheet(
            f"background:{COLORS['bg_primary']}; border-bottom:1px solid rgba(0,0,0,0.08);"
        )
        layout = QHBoxLayout(self)
        layout.setContentsMargins(20, 0, 20, 0)
        layout.setSpacing(10)

        # Título dinámico — se actualiza con set_title() al cambiar de vista
        self.title = QLabel("")
        self.title.setStyleSheet(
            f"font-size:15px; font-weight:600; color:{COLORS['text_primary']}; "
            "background:transparent; border:none;"
        )
        layout.addWidget(self.title, 1)

        # Botón secundario: exportar resultados del análisis actual
        # Conectar en MainWindow: self.topbar.export_btn.clicked.connect(...)
        self.export_btn = QPushButton("↓  Exportar")
        self.export_btn.setCursor(QCursor(Qt.PointingHandCursor))
        self.export_btn.setFixedHeight(30)
        self.export_btn.setStyleSheet(
            f"QPushButton {{ background:transparent; color:{COLORS['text_secondary']}; "
            f"border:0.5px solid rgba(0,0,0,0.18); border-radius:8px; "
            "padding:0 12px; font-size:12px; }}"
            f"QPushButton:hover {{ background:{COLORS['bg_secondary']}; }}"
        )
        layout.addWidget(self.export_btn)

        # Botón primario: iniciar un nuevo ciclo de análisis
        # Conectar en MainWindow: self.topbar.new_analysis_btn.clicked.connect(...)
        self.new_analysis_btn = QPushButton("→  Nuevo análisis")
        self.new_analysis_btn.setCursor(QCursor(Qt.PointingHandCursor))
        self.new_analysis_btn.setFixedHeight(30)
        self.new_analysis_btn.setStyleSheet(
            f"QPushButton {{ background:{COLORS['blue']}; color:#ffffff; "
            "border:none; border-radius:8px; padding:0 14px; font-size:12px; font-weight:600; }}"
            "QPushButton:hover { background:#0C447C; }"
        )
        layout.addWidget(self.new_analysis_btn)

    def set_title(self, text: str):
        """Actualiza el título mostrado en la topbar. Lo llama MainWindow._on_nav()."""
        self.title.setText(text)


# ══════════════════════════════════════════════════════════════════════════════
#  COMPONENTE: Panel
#  Contenedor con cabecera de título y cuerpo de contenido.
#  Es el bloque visual base de todas las vistas (tarjetas blancas con borde).
#  Uso: panel = Panel("Título"); panel.body().addWidget(mi_widget)
# ══════════════════════════════════════════════════════════════════════════════

class Panel(QWidget):

    def __init__(self, title="", parent=None):
        super().__init__(parent)
        self.setStyleSheet(
            f"background:{COLORS['bg_primary']}; border-radius:12px; "
            "border:0.5px solid rgba(0,0,0,0.10);"
        )
        self._layout = QVBoxLayout(self)
        self._layout.setContentsMargins(0, 0, 0, 0)
        self._layout.setSpacing(0)

        # Cabecera con título (opcional — si title="" no se muestra)
        if title:
            header = QWidget()
            header.setFixedHeight(44)
            header.setStyleSheet(
                "background:transparent; border-bottom:0.5px solid rgba(0,0,0,0.08);"
            )
            hl = QHBoxLayout(header)
            hl.setContentsMargins(16, 0, 16, 0)
            hl.addWidget(label(title, 13, COLORS["text_primary"], "bold"))
            hl.addStretch()
            self._layout.addWidget(header)

        # Cuerpo del panel — aquí se añaden los widgets hijos
        self._body = QWidget()
        self._body.setStyleSheet("background:transparent;")
        self._body_layout = QVBoxLayout(self._body)
        self._body_layout.setContentsMargins(16, 14, 16, 16)
        self._body_layout.setSpacing(10)
        self._layout.addWidget(self._body)

    def body(self):
        """Devuelve el QVBoxLayout del cuerpo para añadir widgets hijos."""
        return self._body_layout


# ══════════════════════════════════════════════════════════════════════════════
#  COMPONENTE: MetricCard
#  Tarjeta KPI con título, valor numérico grande, subtítulo y badge de estado.
#  Se usa en ViewResumen (fila superior de 4 tarjetas).
#
#  PARA ACTUALIZAR CON DATOS REALES:
#      card.set_values("8.342", "Exploración 2023–2024", "+312 nuevo lote", "blue")
# ══════════════════════════════════════════════════════════════════════════════

class MetricCard(QWidget):

    def __init__(self, title, value="—", subtitle="", badge_text="", badge_style="blue", parent=None):
        super().__init__(parent)
        self.setStyleSheet(f"background:{COLORS['bg_secondary']}; border-radius:8px; border:none;")
        layout = QVBoxLayout(self)
        layout.setContentsMargins(14, 12, 14, 14)
        layout.setSpacing(4)

        # Título de la métrica en mayúsculas pequeñas (p. ej. "PACIENTES TOTALES")
        lbl_title = QLabel(title.upper())
        lbl_title.setStyleSheet(
            f"font-size:10px; font-weight:600; color:{COLORS['text_tertiary']}; "
            "letter-spacing:0.05em; background:transparent; border:none;"
        )
        layout.addWidget(lbl_title)

        # Valor principal — número grande que se actualiza con set_values()
        self._lbl_val = QLabel(value)
        self._lbl_val.setStyleSheet(
            f"font-size:22px; font-weight:500; color:{COLORS['text_primary']}; "
            "background:transparent; border:none;"
        )
        layout.addWidget(self._lbl_val)

        # Subtítulo descriptivo (p. ej. "Media ponderada")
        self._lbl_sub = QLabel(subtitle)
        self._lbl_sub.setStyleSheet(
            f"font-size:11px; color:{COLORS['text_tertiary']}; background:transparent; border:none;"
        )
        layout.addWidget(self._lbl_sub)

        # Badge de estado (p. ej. "Dentro EUREF" en verde)
        self._badge = badge(badge_text, badge_style)
        layout.addWidget(self._badge)
        layout.addStretch()

    def set_values(self, value: str, subtitle: str = None, badge_text: str = None, badge_style: str = None):
        """
        ── PUNTO DE ENTRADA DE DATOS ──────────────────────────────────────
        Actualiza todos los campos visuales de la tarjeta.

        Llamar desde ViewResumen.populate_metrics() con datos del controller:
            card.set_values("8.342", "Exploración 2023–2024", "+312 nuevo lote", "blue")
        """
        self._lbl_val.setText(value)
        if subtitle is not None:
            self._lbl_sub.setText(subtitle)
        if badge_text is not None:
            self._badge.setText(badge_text)
        if badge_style is not None:
            styles = {
                "blue":  "background:#E6F1FB; color:#185FA5;",
                "green": "background:#EAF3DE; color:#3B6D11;",
                "amber": "background:#FAEEDA; color:#854F0B;",
                "coral": "background:#FAECE7; color:#993C1D;",
                "gray":  "background:#f0ede8; color:#5f5e5a;",
            }
            self._badge.setStyleSheet(
                f"{styles.get(badge_style, styles['blue'])} "
                "font-size:10px; font-weight:600; padding:2px 8px; "
                "border-radius:99px; border:none;"
            )