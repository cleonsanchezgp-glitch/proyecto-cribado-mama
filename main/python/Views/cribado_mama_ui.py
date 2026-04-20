"""
╔══════════════════════════════════════════════════════════════════════════════╗
║            Cribado Mamá — H.U. Miguel Servet                                ║
║            Interfaz PySide6  ·  Versión modular sin datos hardcoded         ║
║                                                                              ║
║  ESTRUCTURA DE ARCHIVOS RECOMENDADA                                          ║
║  ─────────────────────────────────────────────────────────────────────────  ║
║  cribado_mama_ui.py       ← Este archivo (UI pura, sin datos)               ║
║  main_window.py           ← Clase MainWindow + punto de entrada main()      ║
║  view_resumen.py          ← Clase ViewResumen                               ║
║  view_dosis.py            ← Clase ViewDosis                                 ║
║  view_historial.py        ← Clase ViewHistorial                             ║
║  view_cargar.py           ← Clase ViewCargar                                ║
║  view_config.py           ← Clase ViewConfig                                ║
║  controllers/             ← Lógica de negocio desacoplada de la UI          ║
║      resumen_controller.py                                                   ║
║      dosis_controller.py                                                     ║
║      historial_controller.py                                                 ║
║  models/                  ← Clases de datos (dataclasses / Pydantic)        ║
║      paciente.py                                                             ║
║      agd_result.py                                                           ║
║                                                                              ║
║  CÓMO CONECTAR LÓGICA A LA UI                                                ║
║  ─────────────────────────────────────────────────────────────────────────  ║
║  1. Cada ventana expone métodos públicos  populate_*(data)                   ║
║     Búscalos marcados con  # ── MÉTODO PÚBLICO ──                           ║
║  2. Instancia tu controller en MainWindow.__init__                           ║
║  3. Llama a view.populate_*(controller.get_data())  después de cargar        ║
║  4. Para refresco en caliente conecta señales Qt o usa un QTimer             ║
║                                                                              ║
║  Requiere: pip install PySide6                                               ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

import sys
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QHBoxLayout, QVBoxLayout,
    QLabel, QPushButton, QScrollArea, QFrame, QGridLayout,
    QStackedWidget, QLineEdit, QSizePolicy, QSpacerItem,
    QTableWidget, QTableWidgetItem, QHeaderView, QFileDialog,
    QButtonGroup
)
from PySide6.QtCore import Qt, QSize, QPropertyAnimation, QEasingCurve, QPoint
from PySide6.QtGui import (
    QColor, QPainter, QPen, QBrush, QFont, QFontDatabase,
    QPainterPath, QLinearGradient, QIcon, QPixmap, QCursor
)


# ══════════════════════════════════════════════════════════════════════════════
#  PALETA Y ESTILOS GLOBALES
# ══════════════════════════════════════════════════════════════════════════════

COLORS = {
    "bg_primary":    "#ffffff",
    "bg_secondary":  "#f5f5f4",
    "bg_tertiary":   "#eeece6",
    "text_primary":  "#1a1a18",
    "text_secondary":"#5f5e5a",
    "text_tertiary": "#9a9890",
    "border":        "rgba(0,0,0,0.10)",
    "blue":          "#185FA5",
    "blue_light":    "#E6F1FB",
    "green":         "#3B6D11",
    "green_light":   "#EAF3DE",
    "amber":         "#854F0B",
    "amber_light":   "#FAEEDA",
    "coral":         "#993C1D",
    "coral_light":   "#FAECE7",
    "status_green":  "#639922",
    "density_a":     "#97C459",
    "density_b":     "#378ADD",
    "density_c":     "#EF9F27",
    "density_d":     "#D85A30"
}

STYLESHEET = """
QWidget {
    background-color: #eeece6;
    color: #1a1a18;
    font-family: 'Segoe UI', sans-serif;
    font-size: 13px;
}
QScrollArea { border: none; background: transparent; }
QScrollBar:vertical { width: 6px; background: transparent; }
QScrollBar::handle:vertical {
    background: #c8c6c0; border-radius: 3px; min-height: 20px;
}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0px; }
QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical { background: transparent; }
"""


# ══════════════════════════════════════════════════════════════════════════════
#  HELPERS DE ESTILO
# ══════════════════════════════════════════════════════════════════════════════

def card_style(bg="#ffffff", radius=12, border=True):
    b = "border: 0.5px solid rgba(0,0,0,0.10);" if border else ""
    return f"background:{bg}; border-radius:{radius}px; {b}"


def label(text, size=13, color="#1a1a18", weight="normal", wrap=False):
    lbl = QLabel(text)
    lbl.setStyleSheet(
        f"font-size:{size}px; color:{color}; "
        f"font-weight:{'600' if weight=='bold' else '400'}; "
        "background:transparent; border:none;"
    )
    if wrap:
        lbl.setWordWrap(True)
    return lbl


def badge(text, style="blue"):
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
    line = QFrame()
    line.setFrameShape(QFrame.HLine if horizontal else QFrame.VLine)
    line.setStyleSheet("color: rgba(0,0,0,0.10); background: rgba(0,0,0,0.10);")
    line.setFixedHeight(1 if horizontal else 0)
    return line


# ══════════════════════════════════════════════════════════════════════════════
#  WIDGETS REUTILIZABLES
# ══════════════════════════════════════════════════════════════════════════════

class ProgressBar(QWidget):
    """Barra de progreso horizontal pintada a mano."""

    def __init__(self, value=0.0, color="#185FA5", height=8, parent=None):
        super().__init__(parent)
        self._value = max(0.0, min(1.0, value))
        self._color = color
        self.setFixedHeight(height)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

    # ── MÉTODO PÚBLICO ─────────────────────────────────────────────────────
    def set_value(self, value: float, color: str = None):
        """
        Actualiza el valor de la barra.

        Parámetros
        ----------
        value : float  — proporción entre 0.0 y 1.0
        color : str    — color hex opcional (p. ej. "#378ADD")

        Uso desde controller:
            bar.set_value(agd_cumplimiento / 100.0, "#3B6D11")
        """
        self._value = max(0.0, min(1.0, value))
        if color:
            self._color = color
        self.update()

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        r = self.rect()
        p.setBrush(QBrush(QColor("#f0ede8")))
        p.setPen(Qt.NoPen)
        p.drawRoundedRect(r, 4, 4)
        fill_w = int(r.width() * self._value)
        if fill_w > 0:
            fr = r.adjusted(0, 0, -(r.width() - fill_w), 0)
            p.setBrush(QBrush(QColor(self._color)))
            p.drawRoundedRect(fr, 4, 4)


class BarChart(QWidget):
    """
    Gráfico de barras agrupadas para dosis AGD.

    Los datos se inyectan con set_data(); mientras no se llame,
    el gráfico aparece vacío (sin barras hardcodeadas).
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumHeight(220)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self._data = []      # Se rellena con set_data()

    # ── MÉTODO PÚBLICO ─────────────────────────────────────────────────────
    def set_data(self, data: list):
        """
        Define las barras del gráfico.

        Parámetros
        ----------
        data : list de tuplas
            Formato: [("Tipo A", valor_2023, valor_2024, color_claro, color_oscuro), ...]

            Ejemplo:
                chart.set_data([
                    ("Tipo A", 82,  78,  "#B5D4F4", "#378ADD"),
                    ("Tipo B", 112, 108, "#B5D4F4", "#378ADD"),
                    ("Tipo C", 145, 149, "#B5D4F4", "#378ADD"),
                    ("Tipo D", 172, 168, "#B5D4F4", "#378ADD"),
                ])

        Cómo obtener los datos:
            - Desde tu DosisController calculas la AGD media por tipo y año.
            - Llamas a chart.set_data(controller.get_agd_por_tipo()) en ViewDosis.populate_chart()
        """
        self._data = data
        self.update()

    def paintEvent(self, event):
        if not self._data:
            return
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        w, h = self.width(), self.height()
        margin_l, margin_b, margin_t = 38, 28, 10

        chart_h = h - margin_b - margin_t
        chart_w = w - margin_l - 12

        # Grid lines
        for y_val in [0, 1.0, 2.0, 3.0]:
            y = h - margin_b - int(chart_h * y_val / 3.5)
            p.setPen(QPen(QColor(0, 0, 0, 25), 1, Qt.DashLine))
            p.drawLine(margin_l, y, w - 12, y)
            p.setPen(QColor("#9a9890"))
            font = p.font()
            font.setPointSize(7)
            p.setFont(font)
            p.drawText(0, y + 4, 34, 14, Qt.AlignRight, f"{y_val:.1f}")

        # Barras
        group_w = chart_w / len(self._data)
        bar_w = group_w * 0.22
        gap = bar_w * 0.3

        for idx, (label_txt, h1, h2, c1, c2) in enumerate(self._data):
            gx = margin_l + idx * group_w + group_w * 0.15
            max_h = 180

            bh1 = int(chart_h * h1 / max_h)
            x1 = int(gx)
            p.setPen(Qt.NoPen)
            p.setBrush(QBrush(QColor(c1)))
            p.drawRoundedRect(x1, h - margin_b - bh1, int(bar_w), bh1, 2, 2)

            bh2 = int(chart_h * h2 / max_h)
            x2 = int(gx + bar_w + gap)
            p.setBrush(QBrush(QColor(c2)))
            p.drawRoundedRect(x2, h - margin_b - bh2, int(bar_w), bh2, 2, 2)

            p.setPen(QColor("#9a9890"))
            font2 = p.font()
            font2.setPointSize(7)
            p.setFont(font2)
            center_x = int(gx + bar_w + gap / 2)
            p.drawText(center_x - 22, h - margin_b + 6, 44, 14, Qt.AlignCenter, label_txt)


class ScatterPlot(QWidget):
    """
    Gráfico de dispersión Espesor vs. AGD por tipo de densidad.

    Los puntos se inyectan con set_data(); sin datos, el gráfico
    dibuja solo los ejes y la línea de referencia EUREF.
    """

    DENSITY_COLORS = ["#97C459", "#378ADD", "#EF9F27", "#D85A30"]

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumHeight(240)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self._points = []    # Se rellena con set_data()

    # ── MÉTODO PÚBLICO ─────────────────────────────────────────────────────
    def set_data(self, points: list):
        """
        Define los puntos del scatter plot.

        Parámetros
        ----------
        points : list de tuplas
            Formato: [(espesor_mm: float, agd_mGy: float, densidad_idx: int), ...]
            densidad_idx: 0=A, 1=B, 2=C, 3=D

            Ejemplo (desde controller):
                scatter.set_data([
                    (42.5, 1.21, 0),   # paciente con densidad A
                    (55.0, 1.84, 1),   # paciente con densidad B
                    ...
                ])

        Cómo obtener los datos:
            - Tu DosisController itera los registros y extrae (espesor, agd, densidad_idx).
            - Llamas a scatter.set_data(controller.get_scatter_points()) en ViewDosis.populate_scatter()
        """
        self._points = points
        self.update()

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        w, h = self.width(), self.height()
        ml, mb, mt, mr = 36, 28, 10, 12

        chart_w = w - ml - mr
        chart_h = h - mb - mt

        # Ejes
        p.setPen(QPen(QColor(0, 0, 0, 50), 1))
        p.drawLine(ml, mt, ml, h - mb)
        p.drawLine(ml, h - mb, w - mr, h - mb)

        # Línea de referencia EUREF
        ref_y = mt + int(chart_h * (1 - 2.5 / 4.5))
        p.setPen(QPen(QColor("#D85A30"), 1, Qt.DashLine))
        p.drawLine(ml, ref_y, w - mr, ref_y)
        p.setPen(QColor("#D85A30"))
        font = p.font()
        font.setPointSize(7)
        p.setFont(font)
        p.drawText(w - mr - 50, ref_y - -2, 50, 12, Qt.AlignRight, "Ref. EUREF")

        # Etiquetas eje X
        p.setPen(QColor("#9a9890"))
        font2 = p.font()
        font2.setPointSize(7)
        p.setFont(font2)
        for val, txt in [(0, "30mm"), (0.5, "60mm"), (1.0, "90mm")]:
            x = ml + int(chart_w * val)
            p.drawText(x - 15, h - mb + 6, 30, 12, Qt.AlignCenter, txt)

        # Puntos
        for thickness, agd, d in self._points:
            xp = ml + int(chart_w * (thickness - 30) / 60)
            yp = mt + int(chart_h * (1 - agd / 4.5))
            color = QColor(self.DENSITY_COLORS[d % len(self.DENSITY_COLORS)])
            color.setAlpha(180)
            p.setPen(Qt.NoPen)
            p.setBrush(QBrush(color))
            p.drawEllipse(xp - 3, yp - 3, 7, 7)


# ══════════════════════════════════════════════════════════════════════════════
#  COMPONENTES DE SHELL  (Sidebar · Topbar · Panel)
# ══════════════════════════════════════════════════════════════════════════════

class Sidebar(QWidget):
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
        super().__init__(parent)
        self.setFixedWidth(220)
        self.setStyleSheet(
            f"background:{COLORS['bg_primary']}; border-right:1px solid rgba(0,0,0,0.08);"
        )
        self._on_nav = on_nav
        self._buttons = {}
        self._build()

    def _build(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Logo
        logo_w = QWidget()
        logo_w.setFixedHeight(72)
        logo_w.setStyleSheet(
            f"background:{COLORS['bg_primary']}; border-bottom:1px solid rgba(0,0,0,0.08);"
        )
        ll = QVBoxLayout(logo_w)
        ll.setContentsMargins(16, 16, 16, 12)
        ll.setSpacing(3)

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

        # Nav
        nav_scroll = QScrollArea()
        nav_scroll.setWidgetResizable(True)
        nav_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        nav_scroll.setStyleSheet("background:transparent; border:none;")

        nav_container = QWidget()
        nav_container.setStyleSheet("background:transparent;")
        nav_layout = QVBoxLayout(nav_container)
        nav_layout.setContentsMargins(8, 12, 8, 12)
        nav_layout.setSpacing(0)

        first_btn = None
        for section_name, items in self.NAV_ITEMS:
            sec_lbl = label(section_name.upper(), 10, COLORS["text_tertiary"])
            sec_lbl.setStyleSheet(
                f"font-size:10px; color:{COLORS['text_tertiary']}; font-weight:600; "
                "letter-spacing:0.06em; padding:0 8px; background:transparent; border:none;"
            )
            nav_layout.addSpacing(12)
            nav_layout.addWidget(sec_lbl)
            nav_layout.addSpacing(4)

            for view_id, name, icon in items:
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
                    first_btn = btn

        nav_layout.addStretch()
        nav_scroll.setWidget(nav_container)
        layout.addWidget(nav_scroll, 1)

        # Footer de estado
        footer = QWidget()
        footer.setFixedHeight(40)
        footer.setStyleSheet(
            f"background:{COLORS['bg_primary']}; border-top:1px solid rgba(0,0,0,0.08);"
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

        if first_btn:
            first_btn.setChecked(True)

    def _nav_click(self, view_id, clicked_btn):
        for btn in self._buttons.values():
            btn.setChecked(False)
        clicked_btn.setChecked(True)
        self._on_nav(view_id)

    def activate(self, view_id):
        for vid, btn in self._buttons.items():
            btn.setChecked(vid == view_id)

    # ── MÉTODO PÚBLICO ─────────────────────────────────────────────────────
    def set_connection_status(self, online: bool, text: str = None):
        """
        Actualiza el indicador de conexión del footer.

        Parámetros
        ----------
        online : bool  — True=verde (conectado), False=gris (offline)
        text   : str   — Texto descriptivo opcional

        Uso:
            sidebar.set_connection_status(True, "Conectado a PACS")
            sidebar.set_connection_status(False, "Sin conexión")
        """
        color = COLORS["status_green"] if online else COLORS["text_tertiary"]
        self._status_dot.setStyleSheet(
            f"color:{color}; font-size:8px; background:transparent; border:none;"
        )
        if text:
            self._status_label.setText(text)


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

        self.title = QLabel("")
        self.title.setStyleSheet(
            f"font-size:15px; font-weight:600; color:{COLORS['text_primary']}; "
            "background:transparent; border:none;"
        )
        layout.addWidget(self.title, 1)

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
        self.title.setText(text)


class Panel(QWidget):
    """Tarjeta con cabecera y cuerpo genérico."""

    def __init__(self, title="", parent=None):
        super().__init__(parent)
        self.setStyleSheet(
            f"background:{COLORS['bg_primary']}; border-radius:12px; "
            "border:0.5px solid rgba(0,0,0,0.10);"
        )
        self._layout = QVBoxLayout(self)
        self._layout.setContentsMargins(0, 0, 0, 0)
        self._layout.setSpacing(0)

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

        self._body = QWidget()
        self._body.setStyleSheet("background:transparent;")
        self._body_layout = QVBoxLayout(self._body)
        self._body_layout.setContentsMargins(16, 14, 16, 16)
        self._body_layout.setSpacing(10)
        self._layout.addWidget(self._body)

    def body(self):
        return self._body_layout


class MetricCard(QWidget):
    """Tarjeta de métrica con título, valor, subtítulo y badge."""

    def __init__(self, title, value="—", subtitle="", badge_text="", badge_style="blue", parent=None):
        super().__init__(parent)
        self.setStyleSheet(f"background:{COLORS['bg_secondary']}; border-radius:8px; border:none;")
        layout = QVBoxLayout(self)
        layout.setContentsMargins(14, 12, 14, 14)
        layout.setSpacing(4)

        lbl_title = QLabel(title.upper())
        lbl_title.setStyleSheet(
            f"font-size:10px; font-weight:600; color:{COLORS['text_tertiary']}; "
            "letter-spacing:0.05em; background:transparent; border:none;"
        )
        layout.addWidget(lbl_title)

        self._lbl_val = QLabel(value)
        self._lbl_val.setStyleSheet(
            f"font-size:22px; font-weight:500; color:{COLORS['text_primary']}; "
            "background:transparent; border:none;"
        )
        layout.addWidget(self._lbl_val)

        self._lbl_sub = QLabel(subtitle)
        self._lbl_sub.setStyleSheet(
            f"font-size:11px; color:{COLORS['text_tertiary']}; background:transparent; border:none;"
        )
        layout.addWidget(self._lbl_sub)

        self._badge = badge(badge_text, badge_style)
        layout.addWidget(self._badge)
        layout.addStretch()

    # ── MÉTODO PÚBLICO ─────────────────────────────────────────────────────
    def set_values(self, value: str, subtitle: str = None, badge_text: str = None, badge_style: str = None):
        """
        Actualiza los datos de la tarjeta.

        Parámetros
        ----------
        value      : str  — Valor principal  (p. ej. "1,84 mGy")
        subtitle   : str  — Línea de contexto (p. ej. "Media ponderada")
        badge_text : str  — Texto del badge   (p. ej. "Dentro EUREF")
        badge_style: str  — "blue" | "green" | "amber" | "coral" | "gray"

        Uso:
            card_dosis.set_values("1,84 mGy", "Media ponderada", "Dentro EUREF", "green")
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


# ════════════════════════════════════════════════════════════════════════════
#  ██████████████████████████████████████████████████████████████████████████
#  ██                                                                      ██
#  ██   VENTANA 1 — VIEW RESUMEN                                           ██
#  ██   Archivo destino: view_resumen.py                                   ██
#  ██                                                                      ██
#  ██████████████████████████████████████████████████████████████████████████
# ════════════════════════════════════════════════════════════════════════════

class ViewResumen(QWidget):
    """
    Vista principal de resumen.

    DATOS NECESARIOS (populate_*)
    ───────────────────────────────────────────────────────────────────────
    populate_metrics(data)     ← 4 tarjetas de KPI superiores
    populate_chart(data)       ← Gráfico de barras AGD por grupo
    populate_density(data)     ← Barras de distribución por densidad
    populate_steps(steps)      ← Estado del proceso (pipeline)
    populate_alerts(alerts)    ← Alertas y avisos

    CUÁNDO LLAMAR A ESTOS MÉTODOS
    ───────────────────────────────────────────────────────────────────────
    Desde MainWindow.__init__() o desde ResumenController tras cargar datos:

        resumen_ctrl = ResumenController(db_session)
        self.views["resumen"].populate_metrics(resumen_ctrl.get_metrics())
        self.views["resumen"].populate_density(resumen_ctrl.get_density_distribution())
        ...
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet("background:transparent;")
        main = QVBoxLayout(self)
        main.setContentsMargins(20, 20, 20, 20)
        main.setSpacing(16)

        # ── Tarjetas métricas ─────────────────────────────────────────────
        cards_row = QWidget()
        cards_row.setStyleSheet("background:transparent;")
        grid = QGridLayout(cards_row)
        grid.setSpacing(12)
        grid.setContentsMargins(0, 0, 0, 0)

        # Tarjetas vacías — se rellenan con populate_metrics()
        metric_titles = [
            "Pacientes totales",
            "Dosis media (mGy)",
            "Registros cruzados",
            "Desviación estándar",
        ]
        self._metric_cards = []
        for i, title in enumerate(metric_titles):
            card = MetricCard(title)
            self._metric_cards.append(card)
            grid.addWidget(card, 0, i)

        main.addWidget(cards_row)

        # ── Dos columnas ──────────────────────────────────────────────────
        two_col = QWidget()
        two_col.setStyleSheet("background:transparent;")
        tc = QHBoxLayout(two_col)
        tc.setContentsMargins(0, 0, 0, 0)
        tc.setSpacing(16)

        # Columna izquierda
        left = QWidget()
        left.setStyleSheet("background:transparent;")
        lv = QVBoxLayout(left)
        lv.setContentsMargins(0, 0, 0, 0)
        lv.setSpacing(16)

        # Gráfico de barras
        chart_panel = Panel("Dosis media AGD por grupo de densidad (mGy)")
        self._bar_chart = BarChart()
        chart_panel.body().addWidget(self._bar_chart)

        leg = QWidget()
        leg.setStyleSheet("background:transparent;")
        leg_l = QHBoxLayout(leg)
        leg_l.setContentsMargins(0, 4, 0, 0)
        leg_l.setSpacing(14)
        for color, txt in [("#B5D4F4", "Año anterior"), ("#378ADD", "Año actual")]:
            dot = QLabel("■")
            dot.setStyleSheet(f"color:{color}; font-size:11px; background:transparent; border:none;")
            t = label(txt, 11, COLORS["text_secondary"])
            leg_l.addWidget(dot)
            leg_l.addWidget(t)
        leg_l.addStretch()
        chart_panel.body().addWidget(leg)
        lv.addWidget(chart_panel)

        # Panel distribución de densidad
        dens_panel = Panel("Distribución por tipo de densidad")
        self._density_rows = []
        density_colors = ["#97C459", "#378ADD", "#EF9F27", "#D85A30"]
        for i, tipo in enumerate(["Tipo A", "Tipo B", "Tipo C", "Tipo D"]):
            row = QWidget()
            row.setStyleSheet("background:transparent;")
            rl = QHBoxLayout(row)
            rl.setContentsMargins(5, 2, 5, 2)
            rl.setSpacing(15)

            l1 = label(tipo, 11, COLORS["text_primary"], "bold")
            l1.setFixedWidth(60)
            rl.addWidget(l1)

            bar = ProgressBar(0.0, density_colors[i], 8)
            rl.addWidget(bar, 1)

            l2 = label("—", 12, COLORS["text_primary"], "bold")
            l2.setFixedWidth(40)
            l2.setContentsMargins(5, 2, 5, 2)
            rl.addWidget(l2)

            l3 = label("n=—", 11, COLORS["text_tertiary"])
            l3.setFixedWidth(65)
            l3.setContentsMargins(5, 2, 5, 2)
            rl.addWidget(l3)

            self._density_rows.append((bar, l2, l3))
            dens_panel.body().addWidget(row)

        lv.addWidget(dens_panel)
        tc.addWidget(left, 1)

        # Columna derecha
        right = QWidget()
        right.setStyleSheet("background:transparent;")
        rv = QVBoxLayout(right)
        rv.setContentsMargins(0, 0, 0, 0)
        rv.setSpacing(16)
        right.setFixedWidth(300)

        # Panel estado del proceso
        proc_panel = Panel("Estado del proceso")
        self._step_rows = []
        step_names = [
            ("Importar DICOM",           "Pendiente"),
            ("Cruzar con RIS",           "Pendiente"),
            ("Calcular AGD por densidad","Pendiente"),
            ("Generar informe EUREF",    "Pendiente"),
            ("Exportar resultados",      "Pendiente"),
        ]
        for idx, (name, detail) in enumerate(step_names):
            row = QWidget()
            row.setStyleSheet("background:transparent; padding-left: 10px;")
            rl = QHBoxLayout(row)
            rl.setContentsMargins(12, 8, 12, 8)
            rl.setSpacing(12)

            num = QLabel(str(idx + 1))
            num.setStyleSheet(
                f"background:{COLORS['bg_secondary']}; color:{COLORS['text_secondary']}; "
                "border-radius:11px; font-size:10px; font-weight:600; "
                "min-width:22px; max-width:22px; min-height:22px; max-height:22px; border:none;"
            )
            num.setAlignment(Qt.AlignCenter)
            num.setFixedSize(22, 22)
            rl.addWidget(num)

            col = QWidget()
            col.setStyleSheet("background:transparent;")
            cv = QVBoxLayout(col)
            cv.setContentsMargins(0, 0, 0, 0)
            cv.setSpacing(1)
            lbl_name   = label(name, 12, COLORS["text_primary"])
            lbl_detail = label(detail, 11, COLORS["text_tertiary"])
            cv.addWidget(lbl_name)
            cv.addWidget(lbl_detail)
            rl.addWidget(col, 1)

            self._step_rows.append((num, lbl_detail))
            proc_panel.body().addWidget(row)
            if idx < len(step_names) - 1:
                proc_panel.body().addWidget(separator())

        rv.addWidget(proc_panel)

        # Panel alertas
        alerts_panel = Panel("Alertas y avisos")
        self._alerts_layout = alerts_panel.body()
        rv.addWidget(alerts_panel)
        rv.addStretch()
        tc.addWidget(right)

        main.addWidget(two_col)
        main.addStretch()

    # ── MÉTODOS PÚBLICOS ───────────────────────────────────────────────────

    def populate_metrics(self, data: list):
        """
        Rellena las 4 tarjetas de KPI superiores.

        Parámetros
        ----------
        data : list de dicts con claves: value, subtitle, badge_text, badge_style
            Orden: [pacientes_totales, dosis_media, registros_cruzados, desviacion_std]

            Ejemplo:
                data = [
                    {"value": "8.342", "subtitle": "Exploración 2023–2024",
                     "badge_text": "+312 nuevo lote", "badge_style": "blue"},
                    {"value": "1,84",  "subtitle": "Media ponderada",
                     "badge_text": "Dentro EUREF",    "badge_style": "green"},
                    {"value": "8.189", "subtitle": "98,2% tasa de match",
                     "badge_text": "153 descartados", "badge_style": "green"},
                    {"value": "0,41",  "subtitle": "Dosis AGD",
                     "badge_text": "Revisar tipo C",  "badge_style": "amber"},
                ]
                view.populate_metrics(data)
        """
        for card, d in zip(self._metric_cards, data):
            card.set_values(
                value=d.get("value", "—"),
                subtitle=d.get("subtitle"),
                badge_text=d.get("badge_text"),
                badge_style=d.get("badge_style"),
            )

    def populate_chart(self, data: list):
        """
        Rellena el gráfico de barras AGD.
        Delega directamente en BarChart.set_data(data).

        Ver BarChart.set_data() para el formato esperado.
        """
        self._bar_chart.set_data(data)

    def populate_density(self, data: list):
        """
        Rellena las barras de distribución por tipo de densidad.

        Parámetros
        ----------
        data : list de dicts, uno por tipo A/B/C/D, en orden
            Claves: proportion (0.0–1.0), pct_text (str), n (str)

            Ejemplo:
                data = [
                    {"proportion": 0.18, "pct_text": "18%", "n": "1.498"},
                    {"proportion": 0.42, "pct_text": "42%", "n": "3.503"},
                    {"proportion": 0.30, "pct_text": "30%", "n": "2.502"},
                    {"proportion": 0.10, "pct_text": "10%", "n": "835"},
                ]
                view.populate_density(data)
        """
        for (bar, lbl_pct, lbl_n), d in zip(self._density_rows, data):
            bar.set_value(d.get("proportion", 0.0))
            lbl_pct.setText(d.get("pct_text", "—"))
            lbl_n.setText(f"n={d.get('n', '—')}")

    def populate_steps(self, steps: list):
        """
        Actualiza el estado del pipeline de proceso.

        Parámetros
        ----------
        steps : list de dicts, uno por paso (mismo orden que la UI)
            Claves: state ("done" | "active" | ""), detail (str)

            Ejemplo:
                steps = [
                    {"state": "done",   "detail": "8.342 estudios cargados"},
                    {"state": "done",   "detail": "8.189 registros enlazados"},
                    {"state": "active", "detail": "En proceso…"},
                    {"state": "",       "detail": "Pendiente"},
                    {"state": "",       "detail": "Pendiente"},
                ]
                view.populate_steps(steps)
        """
        step_icons = {"done": "✓", "active": "→"}
        step_styles = {
            "done":   f"background:{COLORS['green_light']}; color:{COLORS['green']};",
            "active": f"background:{COLORS['blue_light']}; color:{COLORS['blue']};",
            "":       f"background:{COLORS['bg_secondary']}; color:{COLORS['text_secondary']};",
        }
        for i, ((num_lbl, detail_lbl), step) in enumerate(zip(self._step_rows, steps)):
            state = step.get("state", "")
            num_lbl.setText(step_icons.get(state, str(i + 1)))
            num_lbl.setStyleSheet(
                f"{step_styles.get(state, step_styles[''])} "
                "border-radius:11px; font-size:10px; font-weight:600; "
                "min-width:22px; max-width:22px; min-height:22px; max-height:22px; border:none;"
            )
            detail_lbl.setText(step.get("detail", "Pendiente"))

    def populate_alerts(self, alerts: list):
        """
        Rellena el panel de alertas dinámicamente.

        Parámetros
        ----------
        alerts : list de dicts
            Claves: style ("amber"|"coral"|"blue"), title (str), subtitle (str)

            Ejemplo:
                alerts = [
                    {"style": "amber", "title": "Tipo C — 47 pacientes superan ref.",
                     "subtitle": "AGD > 2,5 mGy en tipo C"},
                    {"style": "coral", "title": "12 estudios sin densidad",
                     "subtitle": "Metadatos DICOM incompletos"},
                    {"style": "blue",  "title": "Nuevo lote PACS disponible",
                     "subtitle": "312 estudios pendientes"},
                ]
                view.populate_alerts(alerts)
        """
        # Limpiar alertas previas
        while self._alerts_layout.count():
            item = self._alerts_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        a_colors = {
            "amber": (COLORS["amber_light"], COLORS["amber"]),
            "coral": (COLORS["coral_light"], COLORS["coral"]),
            "blue":  (COLORS["blue_light"],  COLORS["blue"]),
        }
        for a in alerts:
            bg_c, fg_c = a_colors.get(a.get("style", "blue"), a_colors["blue"])
            row = QWidget()
            row.setStyleSheet(f"background:{bg_c}; border-radius:8px; border:none;")
            rl = QVBoxLayout(row)
            rl.setContentsMargins(12, 10, 12, 10)
            rl.setSpacing(2)
            rl.addWidget(label(a.get("title", ""), 12, fg_c, "bold"))
            rl.addWidget(label(a.get("subtitle", ""), 11, fg_c))
            self._alerts_layout.addWidget(row)


# ════════════════════════════════════════════════════════════════════════════
#  ██████████████████████████████████████████████████████████████████████████
#  ██                                                                      ██
#  ██   VENTANA 2 — VIEW DOSIS                                             ██
#  ██   Archivo destino: view_dosis.py                                     ██
#  ██                                                                      ██
#  ██████████████████████████████████████████████████████████████████████████
# ════════════════════════════════════════════════════════════════════════════

class ViewDosis(QWidget):
    """
    Vista de análisis de dosis AGD.

    DATOS NECESARIOS (populate_*)
    ───────────────────────────────────────────────────────────────────────
    populate_stats(data)        ← 3 tarjetas AGD media / P75 / P95
    populate_scatter(points)    ← Gráfico de dispersión espesor vs AGD
    populate_compliance(data)   ← Tabla de cumplimiento EUREF por densidad
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet("background:transparent;")
        main = QVBoxLayout(self)
        main.setContentsMargins(20, 20, 20, 20)
        main.setSpacing(16)

        # ── Tarjetas de estadísticas ──────────────────────────────────────
        stats_row = QWidget()
        stats_row.setStyleSheet("background:transparent;")
        sg = QGridLayout(stats_row)
        sg.setSpacing(10)
        sg.setContentsMargins(0, 0, 0, 0)

        stat_defs = [
            ("AGD media",    "Global ponderada"),
            ("Percentil 75", "75% pacientes"),
            ("Percentil 95", "Casos extremos"),
        ]
        self._stat_boxes = []
        for i, (t, s) in enumerate(stat_defs):
            box = QWidget()
            box.setStyleSheet(f"background:{COLORS['bg_secondary']}; border-radius:8px; border:none;")
            bv = QVBoxLayout(box)
            bv.setContentsMargins(12, 10, 12, 12)
            bv.setSpacing(3)
            bv.addWidget(label(t.upper(), 9, COLORS["text_tertiary"]))
            lbl_val = label("—", 18, COLORS["text_primary"], "bold")
            bv.addWidget(lbl_val)
            bv.addWidget(label(s, 10, COLORS["text_tertiary"]))
            self._stat_boxes.append(lbl_val)
            sg.addWidget(box, 0, i)

        main.addWidget(stats_row)

        # ── Scatter plot ──────────────────────────────────────────────────
        scatter_panel = Panel("Dispersión Espesor vs. AGD")
        self._scatter = ScatterPlot()
        scatter_panel.body().addWidget(self._scatter)

        leg = QWidget()
        leg.setStyleSheet("background:transparent;")
        ll = QHBoxLayout(leg)
        ll.setContentsMargins(10, 6, 4, 6)
        ll.setSpacing(14)
        for color, txt in [("#97C459","Tipo A"),("#378ADD","Tipo B"),
                           ("#EF9F27","Tipo C"),("#D85A30","Tipo D")]:
            dot = QLabel("●")
            dot.setStyleSheet(f"color:{color}; font-size:11px; background:transparent; border:none;")
            t = label(txt, 11, COLORS["text_secondary"])
            ll.addWidget(dot)
            ll.addWidget(t)
        ll.addStretch()
        scatter_panel.body().addWidget(leg)
        main.addWidget(scatter_panel)

        # ── Tabla de cumplimiento EUREF ───────────────────────────────────
        comply_panel = Panel("Cumplimiento EUREF por tipo de densidad")
        self._comply_rows = []
        for tipo in ["Tipo A", "Tipo B", "Tipo C", "Tipo D"]:
            row = QWidget()
            row.setStyleSheet("background:transparent;")
            rl = QHBoxLayout(row)
            rl.setContentsMargins(12, 4, 12, 4)
            rl.setSpacing(12)
            rl.addWidget(label(tipo, 12, COLORS["text_primary"]))
            bar = ProgressBar(0.0, COLORS["green"], 6)
            bar.setFixedWidth(120)
            rl.addWidget(bar)
            val_l = label("—", 12, COLORS["text_primary"], "bold")
            val_l.setFixedWidth(42)
            val_l.setAlignment(Qt.AlignRight)
            rl.addWidget(val_l)
            bdg = badge("—", "gray")
            rl.addWidget(bdg)
            rl.addStretch()
            self._comply_rows.append((bar, val_l, bdg))
            comply_panel.body().addWidget(row)

        main.addWidget(comply_panel)
        main.addStretch()

    # ── MÉTODOS PÚBLICOS ───────────────────────────────────────────────────

    def populate_stats(self, data: list):
        """
        Rellena las 3 tarjetas de estadísticas de dosis.

        Parámetros
        ----------
        data : list de str  [agd_media, percentil_75, percentil_95]
            Los valores deben venir ya formateados con unidades.

            Ejemplo:
                view.populate_stats(["1,84 mGy", "2,41 mGy", "3,18 mGy"])
        """
        for lbl_val, value in zip(self._stat_boxes, data):
            lbl_val.setText(value)

    def populate_scatter(self, points: list):
        """
        Rellena el gráfico de dispersión.
        Delega en ScatterPlot.set_data(points).

        Ver ScatterPlot.set_data() para el formato esperado.
        """
        self._scatter.set_data(points)

    def populate_compliance(self, data: list):
        """
        Rellena la tabla de cumplimiento EUREF.

        Parámetros
        ----------
        data : list de dicts, uno por tipo A/B/C/D (en orden)
            Claves: proportion (0.0–1.0), pct_text (str), style ("green"|"amber"|"coral")

            Ejemplo:
                data = [
                    {"proportion": 0.972, "pct_text": "97,2%", "style": "green"},
                    {"proportion": 0.941, "pct_text": "94,1%", "style": "green"},
                    {"proportion": 0.813, "pct_text": "81,3%", "style": "amber"},
                    {"proportion": 0.768, "pct_text": "76,8%", "style": "amber"},
                ]
                view.populate_compliance(data)
        """
        bar_colors = {"green": COLORS["green"], "amber": COLORS["amber"], "coral": COLORS["coral"]}
        for (bar, val_l, bdg), d in zip(self._comply_rows, data):
            style = d.get("style", "green")
            bar.set_value(d.get("proportion", 0.0), bar_colors.get(style, COLORS["green"]))
            val_l.setText(d.get("pct_text", "—"))
            badge_text = "OK" if style == "green" else "Revisar"
            bdg.setText(badge_text)
            badge_styles = {
                "blue":  "background:#E6F1FB; color:#185FA5;",
                "green": "background:#EAF3DE; color:#3B6D11;",
                "amber": "background:#FAEEDA; color:#854F0B;",
                "coral": "background:#FAECE7; color:#993C1D;",
                "gray":  "background:#f0ede8; color:#5f5e5a;",
            }
            bdg.setStyleSheet(
                f"{badge_styles.get(style, badge_styles['green'])} "
                "font-size:10px; font-weight:600; padding:2px 8px; "
                "border-radius:99px; border:none;"
            )


# ════════════════════════════════════════════════════════════════════════════
#  ██████████████████████████████████████████████████████████████████████████
#  ██                                                                      ██
#  ██   VENTANA 3 — VIEW HISTORIAL                                         ██
#  ██   Archivo destino: view_historial.py                                 ██
#  ██                                                                      ██
#  ██████████████████████████████████████████████████████████████████████████
# ════════════════════════════════════════════════════════════════════════════

class ViewHistorial(QWidget):
    """
    Vista de historial de exploraciones.

    DATOS NECESARIOS (populate_*)
    ───────────────────────────────────────────────────────────────────────
    populate_table(rows)   ← Rellena la tabla de pacientes

    SEÑALES INTERNAS
    ───────────────────────────────────────────────────────────────────────
    El QLineEdit de búsqueda y los chips de filtro están expuestos como
    atributos públicos para que el controller conecte sus señales:

        view.search_input.textChanged.connect(ctrl.on_search)
        view.filter_chips["Tipo A"].toggled.connect(ctrl.on_filter)
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet("background:transparent;")
        main = QVBoxLayout(self)
        main.setContentsMargins(20, 20, 20, 20)
        main.setSpacing(16)

        # ── Buscador + filtros ────────────────────────────────────────────
        search_row = QWidget()
        search_row.setStyleSheet("background:transparent;")
        sr = QHBoxLayout(search_row)
        sr.setContentsMargins(0, 0, 0, 0)
        sr.setSpacing(10)

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Buscar paciente…")
        self.search_input.setFixedHeight(34)
        self.search_input.setStyleSheet(
            f"QLineEdit {{ background:{COLORS['bg_secondary']}; border:0.5px solid rgba(0,0,0,0.18); "
            "border-radius:8px; padding:0 12px; font-size:13px; color:#1a1a18; }}"
            "QLineEdit:focus { border-color:#185FA5; }"
        )
        sr.addWidget(self.search_input, 1)

        self.filter_chips = {}
        for filt in ["Todos", "Tipo A", "Tipo B", "Tipo C", "Tipo D"]:
            chip = QPushButton(filt)
            chip.setCheckable(True)
            chip.setFixedHeight(28)
            if filt == "Todos":
                chip.setChecked(True)
            chip.setStyleSheet(
                f"QPushButton {{ background:transparent; border:0.5px solid rgba(0,0,0,0.18); "
                "border-radius:99px; padding:0 10px; font-size:11px; "
                f"color:{COLORS['text_secondary']}; }}"
                f"QPushButton:checked {{ background:{COLORS['blue_light']}; border-color:{COLORS['blue']}; "
                f"color:{COLORS['blue']}; font-weight:600; }}"
            )
            sr.addWidget(chip)
            self.filter_chips[filt] = chip

        main.addWidget(search_row)

        # ── Tabla de exploraciones ────────────────────────────────────────
        table_panel = Panel("Exploraciones recientes")
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.horizontalHeader().setDefaultAlignment(Qt.AlignCenter)
        self.table.setHorizontalHeaderLabels(
            ["ID Paciente", "Edad", "Densidad", "AGD (mGy)", "Fecha", "Estado"]
        )
        self.table.setStyleSheet(
            f"QTableWidget {{ background:{COLORS['bg_primary']}; border:none; "
            "gridline-color:rgba(0,0,0,0.06); font-size:12px; }}"
            f"QHeaderView::section {{ background:{COLORS['bg_secondary']}; color:{COLORS['text_tertiary']}; "
            "font-size:10px; font-weight:600; text-transform:uppercase; letter-spacing:0.05em; "
            "border:none; border-bottom:0.5px solid rgba(0,0,0,0.08); padding:6px 10px; }}"
            f"QTableWidget::item {{ padding:6px 10px; color:{COLORS['text_secondary']}; border:none; "
            "border-bottom:0.5px solid rgba(0,0,0,0.06); }}"
            f"QTableWidget::item:selected {{ background:{COLORS['blue_light']}; color:{COLORS['blue']}; }}"
        )
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.verticalHeader().setVisible(False)
        self.table.setShowGrid(False)
        self.table.setAlternatingRowColors(False)
        self.table.setMinimumHeight(240)
        table_panel.body().addWidget(self.table)
        main.addWidget(table_panel)
        main.addStretch()

    # ── MÉTODO PÚBLICO ─────────────────────────────────────────────────────
    def populate_table(self, rows: list):
        """
        Rellena la tabla de exploraciones.

        Parámetros
        ----------
        rows : list de dicts
            Claves: id, age, density, agd, date, status ("ok"|"revisar")

            Ejemplo:
                rows = [
                    {"id": "PAC-04821", "age": 52, "density": "A",
                     "agd": 1.21, "date": "14 mar 2024", "status": "ok"},
                    {"id": "PAC-04822", "age": 45, "density": "B",
                     "agd": 1.67, "date": "14 mar 2024", "status": "ok"},
                    {"id": "PAC-04823", "age": 58, "density": "C",
                     "agd": 2.31, "date": "12 mar 2024", "status": "revisar"},
                ]
                view.populate_table(rows)

        NOTA: Para búsqueda/filtrado conecta search_input y filter_chips
        al controller y llama a populate_table() con los datos filtrados.
        """
        self.table.setRowCount(len(rows))
        for row_idx, r in enumerate(rows):
            status = r.get("status", "ok")
            items = [
                QTableWidgetItem(str(r.get("id", ""))),
                QTableWidgetItem(f"{r.get('age', '')} años"),
                QTableWidgetItem(f"Tipo {r.get('density', '')}"),
                QTableWidgetItem(f"{r.get('agd', 0):.2f}"),
                QTableWidgetItem(str(r.get("date", ""))),
                QTableWidgetItem("OK" if status == "ok" else "Revisar"),
            ]
            for col, item in enumerate(items):
                item.setTextAlignment(Qt.AlignCenter)
                if col == 5:
                    item.setForeground(
                        QColor(COLORS["blue"] if status == "ok" else COLORS["amber"])
                    )
                self.table.setItem(row_idx, col, item)
            self.table.setRowHeight(row_idx, 36)


# ════════════════════════════════════════════════════════════════════════════
#  ██████████████████████████████████████████████████████████████████████████
#  ██                                                                      ██
#  ██   VENTANA 4 — VIEW CARGAR                                            ██
#  ██   Archivo destino: view_cargar.py                                    ██
#  ██                                                                      ██
#  ██████████████████████████████████████████████████████████████████████████
# ════════════════════════════════════════════════════════════════════════════

class ViewCargar(QWidget):
    """
    Vista de carga de archivos.

    SEÑALES INTERNAS
    ───────────────────────────────────────────────────────────────────────
    process_btn.clicked  — conecta al controller para lanzar el procesado:
        view.process_btn.clicked.connect(ctrl.on_process_files)

    Para conocer los archivos seleccionados accede a:
        view.selected_files   → dict { "DICOM": path, "RIS": path, "META": path }
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet("background:transparent;")
        main = QVBoxLayout(self)
        main.setContentsMargins(20, 20, 20, 20)
        main.setSpacing(16)

        self.selected_files = {}   # Expuesto al controller

        upload_panel = Panel("Cargar nuevos archivos")

        file_slots = [
            ("dicom", "📁 Archivos DICOM (.dcm)",
             "Arrastra los archivos DICOM aquí o haz clic para seleccionar"),
            ("ris",   "📄 Informe RIS / CSV",
             "Exportación del sistema RIS en formato CSV o Excel"),
            ("meta",  "📋 Metadatos adicionales",
             "Archivo JSON o XML con parámetros de adquisición"),
        ]

        for slot_key, title, hint in file_slots:
            drop_btn = QPushButton()
            drop_btn.setCursor(QCursor(Qt.PointingHandCursor))
            drop_btn.setMinimumHeight(90)
            drop_btn.setStyleSheet(
                "QPushButton { background:transparent; border:0.5px dashed rgba(0,0,0,0.25); "
                "border-radius:8px; font-size:12px; color:#5f5e5a; }"
                f"QPushButton:hover {{ background:{COLORS['bg_secondary']}; }}"
            )
            btn_layout = QVBoxLayout(drop_btn)
            btn_layout.setSpacing(4)
            btn_layout.setAlignment(Qt.AlignCenter)
            btn_layout.addWidget(label(title, 12, COLORS["text_primary"], "bold"))
            btn_layout.addWidget(label(hint, 11, COLORS["text_tertiary"]))

            def make_handler(b=drop_btn, t=title, key=slot_key):
                def handler():
                    import os
                    path, _ = QFileDialog.getOpenFileName(self, f"Seleccionar {t}")
                    if path:
                        fname = os.path.basename(path)
                        self.selected_files[key] = path
                        b.setStyleSheet(
                            "QPushButton { background:#EAF3DE; border:0.5px solid #639922; "
                            "border-radius:8px; font-size:12px; color:#3B6D11; }"
                        )
                        for i in range(b.layout().count()):
                            w = b.layout().itemAt(i).widget()
                            if isinstance(w, QLabel):
                                w.setText(fname if i == 1 else ("✓ Archivo cargado" if i == 0 else ""))
                return handler

            drop_btn.clicked.connect(make_handler())
            upload_panel.body().addWidget(drop_btn)

        # ── MÉTODO PÚBLICO: process_btn expuesto al controller ────────────
        self.process_btn = QPushButton("Procesar archivos cargados")
        self.process_btn.setFixedHeight(36)
        self.process_btn.setCursor(QCursor(Qt.PointingHandCursor))
        self.process_btn.setStyleSheet(
            f"QPushButton {{ background:{COLORS['blue']}; color:#ffffff; border:none; "
            "border-radius:8px; font-size:13px; font-weight:600; }}"
            "QPushButton:hover { background:#0C447C; }"
        )
        upload_panel.body().addWidget(self.process_btn)
        main.addWidget(upload_panel)
        main.addStretch()


# ════════════════════════════════════════════════════════════════════════════
#  ██████████████████████████████████████████████████████████████████████████
#  ██                                                                      ██
#  ██   VENTANA 5 — VIEW CONFIG                                            ██
#  ██   Archivo destino: view_config.py                                    ██
#  ██                                                                      ██
#  ██████████████████████████████████████████████████████████████████████████
# ════════════════════════════════════════════════════════════════════════════

class ViewConfig(QWidget):
    """
    Vista de configuración.

    DATOS NECESARIOS (populate_*)
    ───────────────────────────────────────────────────────────────────────
    populate_euref_params(params)      ← Parámetros EUREF editables
    populate_integrations(integrations)← Estado de las integraciones

    SEÑALES INTERNAS
    ───────────────────────────────────────────────────────────────────────
    Los QLineEdit de parámetros EUREF se exponen en:
        view.euref_inputs   → dict { "Límite AGD tipo A (mGy)": QLineEdit, ... }

    Para guardar cambios conecta al controller:
        save_btn.clicked.connect(ctrl.on_save_config)
        ... y lee view.euref_inputs["Límite AGD tipo A (mGy)"].text()
    """

    EUREF_PARAM_NAMES = [
        "Límite AGD tipo A (mGy)",
        "Límite AGD tipo B (mGy)",
        "Límite AGD tipo C (mGy)",
        "Límite AGD tipo D (mGy)",
        "Umbral alerta (% pacientes sobre límite)",
    ]

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet("background:transparent;")
        main = QVBoxLayout(self)
        main.setContentsMargins(20, 20, 20, 20)
        main.setSpacing(16)

        # ── Parámetros EUREF ──────────────────────────────────────────────
        euref_panel = Panel("Parámetros EUREF")
        self.euref_inputs = {}

        for param_name in self.EUREF_PARAM_NAMES:
            row = QWidget()
            row.setStyleSheet("background:transparent;")
            rl = QHBoxLayout(row)
            rl.setContentsMargins(12, 6, 6, 6)
            rl.setSpacing(12)
            rl.addWidget(label(param_name, 12, COLORS["text_primary"]), 1)

            val_input = QLineEdit()    # Sin valor por defecto — se rellena con populate_euref_params()
            val_input.setFixedSize(80, 28)
            val_input.setAlignment(Qt.AlignCenter)
            val_input.setStyleSheet(
                f"QLineEdit {{ background:{COLORS['bg_secondary']}; "
                "border:0.5px solid rgba(0,0,0,0.18); border-radius:6px; "
                "font-size:12px; font-weight:600; color:#1a1a18; padding:0 8px; }}"
                "QLineEdit:focus { border-color:#185FA5; }"
            )
            rl.addWidget(val_input)
            self.euref_inputs[param_name] = val_input
            euref_panel.body().addWidget(row)
            euref_panel.body().addWidget(separator())

        main.addWidget(euref_panel)

        # ── Integraciones ─────────────────────────────────────────────────
        integr_panel = Panel("Integraciones")
        self._integration_badges = {}

        integration_defs = [
            ("pacs", "🔵", "PACS — Sectra IDS7",     "Importación automática de imágenes DICOM"),
            ("ris",  "🟢", "RIS — Carestream Vue",    "Exportación de informes al sistema RIS"),
            ("his",  "⚪", "HIS — Cerner Millennium", "Integración con historia clínica"),
        ]

        for key, icon, name, desc in integration_defs:
            row = QWidget()
            row.setStyleSheet(
                f"background:{COLORS['bg_primary']}; border-radius:8px; "
                "border:0.5px solid rgba(0,0,0,0.08);"
            )
            rl = QHBoxLayout(row)
            rl.setContentsMargins(14, 12, 14, 12)
            rl.setSpacing(14)

            ico = label(icon, 20, "#000")
            ico.setFixedWidth(36)
            rl.addWidget(ico)

            col = QWidget()
            col.setStyleSheet("background:transparent; padding-left: 10px;")
            cv = QVBoxLayout(col)
            cv.setContentsMargins(0, 0, 0, 0)
            cv.setSpacing(2)
            cv.addWidget(label(name, 13, COLORS["text_primary"], "bold"))
            cv.addWidget(label(desc, 11, COLORS["text_tertiary"]))
            rl.addWidget(col, 1)

            bdg = badge("—", "gray")
            rl.addWidget(bdg)
            self._integration_badges[key] = bdg
            integr_panel.body().addWidget(row)

        main.addWidget(integr_panel)
        main.addStretch()

    # ── MÉTODOS PÚBLICOS ───────────────────────────────────────────────────

    def populate_euref_params(self, params: dict):
        """
        Rellena los campos de parámetros EUREF.

        Parámetros
        ----------
        params : dict  { nombre_param: valor_str }

            Ejemplo:
                params = {
                    "Límite AGD tipo A (mGy)": "2,0",
                    "Límite AGD tipo B (mGy)": "2,5",
                    "Límite AGD tipo C (mGy)": "3,0",
                    "Límite AGD tipo D (mGy)": "3,5",
                    "Umbral alerta (% pacientes sobre límite)": "10%",
                }
                view.populate_euref_params(params)

        Cómo obtener los datos:
            Carga los valores desde un JSON/DB en ConfigController
            y llama a este método al arrancar la vista.
        """
        for name, widget in self.euref_inputs.items():
            if name in params:
                widget.setText(params[name])

    def populate_integrations(self, integrations: dict):
        """
        Actualiza los badges de estado de cada integración.

        Parámetros
        ----------
        integrations : dict  { key: {"active": bool, "label": str} }
            Keys esperadas: "pacs", "ris", "his"

            Ejemplo:
                integrations = {
                    "pacs": {"active": True,  "label": "Conectado"},
                    "ris":  {"active": True,  "label": "Conectado"},
                    "his":  {"active": False, "label": "Inactivo"},
                }
                view.populate_integrations(integrations)
        """
        for key, bdg in self._integration_badges.items():
            info = integrations.get(key, {})
            active = info.get("active", False)
            lbl_text = info.get("label", "—")
            style = "green" if active else "gray"
            bdg.setText(lbl_text)
            styles = {
                "green": "background:#EAF3DE; color:#3B6D11;",
                "gray":  "background:#f0ede8; color:#5f5e5a;",
            }
            bdg.setStyleSheet(
                f"{styles[style]} font-size:10px; font-weight:600; "
                "padding:2px 8px; border-radius:99px; border:none;"
            )


# ════════════════════════════════════════════════════════════════════════════
#  ██████████████████████████████████████████████████████████████████████████
#  ██                                                                      ██
#  ██   VENTANA PRINCIPAL — MAIN WINDOW                                    ██
#  ██   Archivo destino: main_window.py                                    ██
#  ██                                                                      ██
#  ██████████████████████████████████████████████████████████████████████████
# ════════════════════════════════════════════════════════════════════════════

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
        # self._init_controllers()
        # self._load_initial_data()

    def _on_nav(self, view_id):
        view = self.views.get(view_id)
        if view:
            self.stack.setCurrentWidget(view)
        self.topbar.set_title(self.TITLES.get(view_id, ""))

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