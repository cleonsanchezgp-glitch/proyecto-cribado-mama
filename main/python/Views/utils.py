
from PySide6.QtWidgets import (
    QFrame, QWidget, QHBoxLayout, QVBoxLayout, QPushButton, QScrollArea,QSizePolicy, QLabel
)

from PySide6.QtCore import Qt
from PySide6.QtGui import (
    QColor, QPainter, QPen, QBrush, QCursor
)

from main.python.Views.colors import COLORS

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

def load_stylesheet(file_path):
    """Lee un archivo CSS y devuelve el contenido como string."""
    try:
        with open(file_path, "r") as f:
            return f.read()
    except FileNotFoundError:
        print(f"Error: No se encontró el archivo {file_path}")
        return ""

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
        self._buttons = {}
        self._build()

    def _build(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Logo
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
        nav_container.setStyleSheet(f"background:{COLORS['bg_primary']};")
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
