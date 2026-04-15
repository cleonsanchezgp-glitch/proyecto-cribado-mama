"""
Cribado Mama — H.U. Miguel Servet
Interfaz PySide6 — equivalente al diseño HTML original
Requiere: pip install PySide6
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


# ── Paleta de colores ──────────────────────────────────────────────────────────
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
    # Colores densidad
    "density_a":     "#97C459",
    "density_b":     "#378ADD",
    "density_c":     "#EF9F27",
    "density_d":     "#D85A30",
}

STYLESHEET = """
QWidget {
    background-color: #eeece6;
    color: #1a1a18;
    font-family: 'Segoe UI', sans-serif;
    font-size: 13px;
}
QScrollArea {
    border: none;
    background: transparent;
}
QScrollBar:vertical {
    width: 6px;
    background: transparent;
}
QScrollBar::handle:vertical {
    background: #c8c6c0;
    border-radius: 3px;
    min-height: 20px;
}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0px; }
QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical { background: transparent; }
"""


# ── Helpers de estilo ──────────────────────────────────────────────────────────

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
        "blue":  ("background:#E6F1FB; color:#185FA5;"),
        "green": ("background:#EAF3DE; color:#3B6D11;"),
        "amber": ("background:#FAEEDA; color:#854F0B;"),
        "coral": ("background:#FAECE7; color:#993C1D;"),
        "gray":  ("background:#f0ede8; color:#5f5e5a;"),
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


# ── Widget de barra de progreso horizontal ──────────────────────────────────

class ProgressBar(QWidget):
    def __init__(self, value=0.5, color="#185FA5", height=8, parent=None):
        super().__init__(parent)
        self._value = max(0.0, min(1.0, value))
        self._color = color
        self.setFixedHeight(height)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        r = self.rect()
        # Fondo
        p.setBrush(QBrush(QColor("#f0ede8")))
        p.setPen(Qt.NoPen)
        p.drawRoundedRect(r, 4, 4)
        # Relleno
        fill_w = int(r.width() * self._value)
        if fill_w > 0:
            fr = r.adjusted(0, 0, -(r.width() - fill_w), 0)
            p.setBrush(QBrush(QColor(self._color)))
            p.drawRoundedRect(fr, 4, 4)


# ── Widget de gráfico de barras ──────────────────────────────────────────────

class BarChart(QWidget):
    """Gráfico de barras agrupadas (2023/2024) para dosis AGD."""

    DATA = [
        ("Tipo A", 82,  78,  "#B5D4F4", "#378ADD"),
        ("Tipo B", 112, 108, "#B5D4F4", "#378ADD"),
        ("Tipo C", 145, 149, "#B5D4F4", "#378ADD"),
        ("Tipo D", 172, 168, "#B5D4F4", "#378ADD"),
    ]

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumHeight(220)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        w, h = self.width(), self.height()
        margin_l, margin_b, margin_t = 38, 28, 10

        chart_h = h - margin_b - margin_t
        chart_w = w - margin_l - 12

        # Grid lines
        for i, y_val in enumerate([0, 1.0, 2.0, 3.0]):
            y = h - margin_b - int(chart_h * y_val / 3.5)
            p.setPen(QPen(QColor(0, 0, 0, 25), 1, Qt.DashLine))
            p.drawLine(margin_l, y, w - 12, y)
            p.setPen(QColor("#9a9890"))
            font = p.font()
            font.setPointSize(7)
            p.setFont(font)
            p.drawText(0, y + 4, 34, 14, Qt.AlignRight, f"{y_val:.1f}")
            p.set

        # Barras
        group_w = chart_w / len(self.DATA)
        bar_w = group_w * 0.22
        gap = bar_w * 0.3

        for idx, (label_txt, h1, h2, c1, c2) in enumerate(self.DATA):
            gx = margin_l + idx * group_w + group_w * 0.15
            max_h = 180

            # Barra 2023
            bh1 = int(chart_h * h1 / max_h)
            x1 = int(gx)
            p.setPen(Qt.NoPen)
            p.setBrush(QBrush(QColor(c1)))
            p.drawRoundedRect(x1, h - margin_b - bh1, int(bar_w), bh1, 2, 2)

            # Barra 2024
            bh2 = int(chart_h * h2 / max_h)
            x2 = int(gx + bar_w + gap)
            p.setBrush(QBrush(QColor(c2)))
            p.drawRoundedRect(x2, h - margin_b - bh2, int(bar_w), bh2, 2, 2)

            # Etiqueta grupo
            p.setPen(QColor("#9a9890"))
            font2 = p.font()
            font2.setPointSize(7)
            p.setFont(font2)
            center_x = int(gx + bar_w + gap / 2)
            p.drawText(center_x - 22, h - margin_b + 6, 44, 14, Qt.AlignCenter, label_txt)


# ── Widget scatter plot ──────────────────────────────────────────────────────

class ScatterPlot(QWidget):
    import random as _random

    DENSITY_COLORS = ["#97C459", "#378ADD", "#EF9F27", "#D85A30"]
    DENSITY_PROB   = [0.18, 0.42, 0.30, 0.10]

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumHeight(240)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self._points = self._generate()

    def _generate(self):
        import random
        points = []
        for _ in range(160):
            r = random.random()
            d, cum = 0, 0
            for k, prob in enumerate(self.DENSITY_PROB):
                cum += prob
                if r < cum:
                    d = k
                    break
            thickness = random.uniform(30 + d * 12, 50 + d * 14)
            agd = random.uniform(0.5 + d * 0.6, 1.8 + d * 0.8)
            points.append((thickness, agd, d))
        return points

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

        # Etiquetas eje
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
            color = QColor(self.DENSITY_COLORS[d])
            color.setAlpha(180)
            p.setPen(Qt.NoPen)
            p.setBrush(QBrush(color))
            p.drawEllipse(xp - 3, yp - 3, 7, 7)


# ── Sidebar ──────────────────────────────────────────────────────────────────

class Sidebar(QWidget):
    NAV_ITEMS = [
        ("Análisis", [
            ("resumen",   "Resumen",          "◈"),
            ("dosis",     "Análisis de dosis", "◉"),
            ("historial", "Historial",         "≡"),
        ]),
        ("Datos", [
            ("cargar",   "Cargar archivos",   "⊞"),
            ("exportar", "Exportar resultados","↓"),
        ]),
        ("Sistema", [
            ("config",   "Configuración",     "⚙"),
        ]),
    ]

    def __init__(self, on_nav, parent=None):
        super().__init__(parent)
        self.setFixedWidth(220)
        self.setStyleSheet(f"background:{COLORS['bg_primary']}; border-right:1px solid rgba(0,0,0,0.08);")
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
        logo_w.setStyleSheet(f"background:{COLORS['bg_primary']}; border-bottom:1px solid rgba(0,0,0,0.08);")
        ll = QVBoxLayout(logo_w)
        ll.setContentsMargins(16, 16, 16, 12)
        ll.setSpacing(3)

        icon_lbl = QLabel("🩺")
        icon_lbl.setStyleSheet(
            f"background:{COLORS['blue']}; border-radius:8px; font-size:16px; "
            "padding:4px; border:none;"
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

        # Footer
        footer = QWidget()
        footer.setFixedHeight(40)
        footer.setStyleSheet(f"background:{COLORS['bg_primary']}; border-top:1px solid rgba(0,0,0,0.08);")
        fl = QHBoxLayout(footer)
        fl.setContentsMargins(16, 0, 16, 0)

        dot = QLabel("●")
        dot.setStyleSheet(f"color:{COLORS['status_green']}; font-size:8px; background:transparent; border:none;")
        status = label("Modo offline", 11, COLORS["text_tertiary"])
        fl.addWidget(dot)
        fl.addWidget(status)
        fl.addStretch()
        layout.addWidget(footer)

        # Activar primer item
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


# ── Topbar ────────────────────────────────────────────────────────────────────

class Topbar(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedHeight(52)
        self.setStyleSheet(
            f"background:{COLORS['bg_primary']}; "
            "border-bottom:1px solid rgba(0,0,0,0.08);"
        )
        layout = QHBoxLayout(self)
        layout.setContentsMargins(20, 0, 20, 0)
        layout.setSpacing(10)

        self.title = QLabel("Resumen del análisis")
        self.title.setStyleSheet(
            f"font-size:15px; font-weight:600; color:{COLORS['text_primary']}; "
            "background:transparent; border:none;"
        )
        layout.addWidget(self.title, 1)

        export_btn = QPushButton("↓  Exportar")
        export_btn.setCursor(QCursor(Qt.PointingHandCursor))
        export_btn.setFixedHeight(30)
        export_btn.setStyleSheet(
            f"QPushButton {{ background:transparent; color:{COLORS['text_secondary']}; "
            f"border:0.5px solid rgba(0,0,0,0.18); border-radius:8px; "
            "padding:0 12px; font-size:12px; }}"
            f"QPushButton:hover {{ background:{COLORS['bg_secondary']}; }}"
        )
        layout.addWidget(export_btn)

        new_btn = QPushButton("→  Nuevo análisis")
        new_btn.setCursor(QCursor(Qt.PointingHandCursor))
        new_btn.setFixedHeight(30)
        new_btn.setStyleSheet(
            f"QPushButton {{ background:{COLORS['blue']}; color:#ffffff; "
            "border:none; border-radius:8px; padding:0 14px; "
            "font-size:12px; font-weight:600; }}"
            "QPushButton:hover { background:#0C447C; }"
        )
        layout.addWidget(new_btn)

    def set_title(self, text):
        self.title.setText(text)


# ── Panel helper ─────────────────────────────────────────────────────────────

class Panel(QWidget):
    def __init__(self, title="", parent=None):
        super().__init__(parent)
        self.setStyleSheet(
            f"background:{COLORS['bg_primary']}; "
            "border-radius:12px; "
            "border:0.5px solid rgba(0,0,0,0.10);"
        )
        self._layout = QVBoxLayout(self)
        self._layout.setContentsMargins(0, 0, 0, 0)
        self._layout.setSpacing(0)

        if title:
            header = QWidget()
            header.setFixedHeight(44)
            header.setStyleSheet(
                "background:transparent; "
                "border-bottom:0.5px solid rgba(0,0,0,0.08);"
            )
            hl = QHBoxLayout(header)
            hl.setContentsMargins(16, 0, 16, 0)
            t = label(title, 13, COLORS["text_primary"], "bold")
            hl.addWidget(t)
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


# ── Tarjeta métrica ──────────────────────────────────────────────────────────

class MetricCard(QWidget):
    def __init__(self, title, value, subtitle, badge_text, badge_style="blue", parent=None):
        super().__init__(parent)
        self.setStyleSheet(
            f"background:{COLORS['bg_secondary']}; border-radius:8px; border:none;"
        )
        layout = QVBoxLayout(self)
        layout.setContentsMargins(14, 12, 14, 14)
        layout.setSpacing(4)

        lbl_title = QLabel(title.upper())
        lbl_title.setStyleSheet(
            f"font-size:10px; font-weight:600; color:{COLORS['text_tertiary']}; "
            "letter-spacing:0.05em; background:transparent; border:none;"
        )
        layout.addWidget(lbl_title)

        lbl_val = QLabel(value)
        lbl_val.setStyleSheet(
            f"font-size:22px; font-weight:500; color:{COLORS['text_primary']}; "
            "background:transparent; border:none;"
        )
        layout.addWidget(lbl_val)

        lbl_sub = QLabel(subtitle)
        lbl_sub.setStyleSheet(
            f"font-size:11px; color:{COLORS['text_tertiary']}; "
            "background:transparent; border:none;"
        )
        layout.addWidget(lbl_sub)
        layout.addWidget(badge(badge_text, badge_style))
        layout.addStretch()


# ════════════════════════════════════════════════════════════
#  VISTAS
# ════════════════════════════════════════════════════════════

class ViewResumen(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet("background:transparent;")
        main = QVBoxLayout(self)
        main.setContentsMargins(20, 20, 20, 20)
        main.setSpacing(16)

        # Tarjetas métricas
        cards_row = QWidget()
        cards_row.setStyleSheet("background:transparent;")
        grid = QGridLayout(cards_row)
        grid.setSpacing(12)
        grid.setContentsMargins(0, 0, 0, 0)

        metrics = [
            ("Pacientes totales",   "8.342", "Exploración 2023–2024", "+312 nuevo lote", "blue"),
            ("Dosis media (mGy)",   "1,84",  "Media ponderada",       "Dentro EUREF",    "green"),
            ("Registros cruzados",  "8.189", "98,2% tasa de match",   "153 descartados", "green"),
            ("Desviación estándar", "0,41",  "Dosis AGD",             "Revisar tipo C",  "amber"),
        ]
        for i, (t, v, s, b, bs) in enumerate(metrics):
            grid.addWidget(MetricCard(t, v, s, b, bs), 0, i)

        main.addWidget(cards_row)

        # Dos columnas
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

        chart_panel = Panel("Dosis media AGD por grupo de densidad (mGy)")
        chart = BarChart()
        chart_panel.body().addWidget(chart)

        # Leyenda
        leg = QWidget()
        leg.setStyleSheet("background:transparent;")
        leg_l = QHBoxLayout(leg)
        leg_l.setContentsMargins(0, 4, 0, 0)
        leg_l.setSpacing(14)
        for color, txt in [("#B5D4F4", "2023"), ("#378ADD", "2024")]:
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
        density_data = [
            ("Tipo A", 0.18, "#97C459", "18%", "1.498"),
            ("Tipo B", 0.42, "#378ADD", "42%", "3.503"),
            ("Tipo C", 0.30, "#EF9F27", "30%", "2.502"),
            ("Tipo D", 0.10, "#D85A30", "10%",   "835"),
        ]
        for lbl_txt, pct, color, pct_txt, n in density_data:
            row = QWidget()
            row.setStyleSheet("background:transparent;")
            rl = QHBoxLayout(row)
            rl.setContentsMargins(5, 2, 5, 2)
            rl.setSpacing(15)

            l1 = label(lbl_txt, 11, COLORS["text_primary"], "bold")
            l1.setFixedWidth(60)
            rl.addWidget(l1)

            bar_w = ProgressBar(pct, color, 8)
            rl.addWidget(bar_w, 1)

            l2 = label(pct_txt, 12, COLORS["text_primary"], "bold")
            l2.setFixedWidth(40)
            l2.setContentsMargins(5, 2, 5, 2)
            rl.addWidget(l2)

            l3 = label(f"n={n}", 11, COLORS["text_tertiary"])
            l3.setFixedWidth(65)
            l3.setContentsMargins(5, 2, 5, 2)
            rl.addWidget(l3)

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
        steps = [
            ("done",   "Importar DICOM",            "PACS — 8.342 estudios cargados"),
            ("done",   "Cruzar con RIS",             "8.189 registros enlazados"),
            ("active", "Calcular AGD por densidad",  "En proceso…"),
            ("",       "Generar informe EUREF",       "Pendiente"),
            ("",       "Exportar resultados",         "Pendiente"),
        ]
        for state, name, detail in steps:
            row = QWidget()
            row.setStyleSheet("background:transparent; padding-left: 10px;")
            rl = QHBoxLayout(row)
            rl.setContentsMargins(12, 8, 12, 8)
            rl.setSpacing(12)

            num = QLabel("✓" if state == "done" else ("→" if state == "active" else str(steps.index((state, name, detail)) + 1)))
            if state == "done":
                num.setStyleSheet(
                    f"background:{COLORS['green_light']}; color:{COLORS['green']}; "
                    "border-radius:11px; font-size:10px; font-weight:600; "
                    "min-width:22px; max-width:22px; min-height:22px; max-height:22px; border:none;"
                )
            elif state == "active":
                num.setStyleSheet(
                    f"background:{COLORS['blue_light']}; color:{COLORS['blue']}; "
                    "border-radius:11px; font-size:10px; font-weight:600; "
                    "min-width:22px; max-width:22px; min-height:22px; max-height:22px; border:none;"
                )
            else:
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
            cv.addWidget(label(name, 12, COLORS["text_primary"]))
            cv.addWidget(label(detail, 11, COLORS["text_tertiary"]))
            rl.addWidget(col, 1)

            proc_panel.body().addWidget(row)
            if steps.index((state, name, detail)) < len(steps) - 1:
                proc_panel.body().addWidget(separator())

        rv.addWidget(proc_panel)

        # Panel alertas
        alerts_panel = Panel("Alertas y avisos")
        alerts = [
            ("amber", "Tipo C — 47 pacientes superan ref.", "AGD > 2,5 mGy en tipo C"),
            ("coral", "12 estudios sin densidad",           "Metadatos DICOM incompletos"),
            ("blue",  "Nuevo lote PACS disponible",         "312 estudios pendientes"),
        ]
        for a_style, a_title, a_sub in alerts:
            a_colors = {
                "amber": (COLORS["amber_light"], COLORS["amber"]),
                "coral": (COLORS["coral_light"], COLORS["coral"]),
                "blue":  (COLORS["blue_light"],  COLORS["blue"]),
            }
            bg_c, fg_c = a_colors[a_style]
            row = QWidget()
            row.setStyleSheet(f"background:{bg_c}; border-radius:8px; border:none;")
            rl = QVBoxLayout(row)
            rl.setContentsMargins(12, 10, 12, 10)
            rl.setSpacing(2)
            rl.addWidget(label(a_title, 12, fg_c, "bold"))
            rl.addWidget(label(a_sub, 11, fg_c))
            alerts_panel.body().addWidget(row)

        rv.addWidget(alerts_panel)
        rv.addStretch()
        tc.addWidget(right)

        main.addWidget(two_col)
        main.addStretch()


class ViewDosis(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet("background:transparent;")
        main = QVBoxLayout(self)
        main.setContentsMargins(20, 20, 20, 20)
        main.setSpacing(16)

        # Stats grid
        stats_row = QWidget()
        stats_row.setStyleSheet("background:transparent;")
        sg = QGridLayout(stats_row)
        sg.setSpacing(10)
        sg.setContentsMargins(0, 0, 0, 0)
        stats = [
            ("AGD media", "1,84 mGy", "Global ponderada"),
            ("Percentil 75", "2,41 mGy", "75% pacientes"),
            ("Percentil 95", "3,18 mGy", "Casos extremos"),
        ]
        for i, (t, v, s) in enumerate(stats):
            box = QWidget()
            box.setStyleSheet(f"background:{COLORS['bg_secondary']}; border-radius:8px; border:none;")
            bv = QVBoxLayout(box)
            bv.setContentsMargins(12, 10, 12, 12)
            bv.setSpacing(3)
            bv.addWidget(label(t.upper(), 9, COLORS["text_tertiary"]))
            bv.addWidget(label(v, 18, COLORS["text_primary"], "bold"))
            bv.addWidget(label(s, 10, COLORS["text_tertiary"]))
            sg.addWidget(box, 0, i)
        main.addWidget(stats_row)

        # Scatter
        scatter_panel = Panel("Dispersión Espesor vs. AGD")
        scatter_panel.body().addWidget(ScatterPlot())

        # Leyenda scatter
        leg = QWidget()
        leg.setStyleSheet("background:transparent;")
        ll = QHBoxLayout(leg)
        ll.setContentsMargins(10, 6, 4, 6)
        ll.setSpacing(14)
        for color, txt in [("#97C459","Tipo A"),("#378ADD","Tipo B"),("#EF9F27","Tipo C"),("#D85A30","Tipo D")]:
            dot = QLabel("●")
            dot.setStyleSheet(f"color:{color}; font-size:11px; background:transparent; border:none;")
            t = label(txt, 11, COLORS["text_secondary"])
            ll.addWidget(dot)
            ll.addWidget(t)
        ll.addStretch()
        scatter_panel.body().addWidget(leg)
        main.addWidget(scatter_panel)

        # Tabla de cumplimiento EUREF
        comply_panel = Panel("Cumplimiento EUREF por tipo de densidad")
        comply_data = [
            ("Tipo A", 0.97, "97,2%", "green"),
            ("Tipo B", 0.94, "94,1%", "green"),
            ("Tipo C", 0.81, "81,3%", "amber"),
            ("Tipo D", 0.76, "76,8%", "amber"),
        ]
        for lbl_txt, pct, pct_txt, style in comply_data:
            row = QWidget()
            row.setStyleSheet("background:transparent;")
            rl = QHBoxLayout(row)
            rl.setContentsMargins(12, 4, 12, 4)
            rl.setSpacing(12)
            rl.addWidget(label(lbl_txt, 12, COLORS["text_primary"]))
            bar_colors = {"green": COLORS["green"], "amber": COLORS["amber"]}
            bar = ProgressBar(pct, bar_colors[style], 6)
            bar.setFixedWidth(120)
            rl.addWidget(bar)
            val_l = label(pct_txt, 12, COLORS["text_primary"], "bold")
            val_l.setFixedWidth(42)
            val_l.setAlignment(Qt.AlignRight)
            rl.addWidget(val_l)
            rl.addWidget(badge("OK" if style == "green" else "Revisar", style))
            rl.addStretch()
            comply_panel.body().addWidget(row)

        main.addWidget(comply_panel)
        main.addStretch()


class ViewHistorial(QWidget):
    PATIENTS = [
        ("PAC-04821", 52, "A", 1.21, "14 mar 2024", "ok",      "#97C459"),
        ("PAC-04822", 45, "B", 1.67, "14 mar 2024", "ok",      "#378ADD"),
        ("PAC-04823", 58, "C", 2.31, "12 mar 2024", "revisar", "#EF9F27"),
        ("PAC-04824", 63, "D", 2.89, "11 mar 2024", "ok",      "#D85A30"),
        ("PAC-04825", 49, "B", 1.58, "11 mar 2024", "ok",      "#378ADD"),
        ("PAC-04826", 55, "C", 2.74, "10 mar 2024", "revisar", "#EF9F27"),
    ]

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet("background:transparent;")
        main = QVBoxLayout(self)
        main.setContentsMargins(20, 20, 20, 20)
        main.setSpacing(16)

        # Buscador
        search_row = QWidget()
        search_row.setStyleSheet("background:transparent;")
        sr = QHBoxLayout(search_row)
        sr.setContentsMargins(0, 0, 0, 0)
        sr.setSpacing(10)

        search = QLineEdit()
        search.setPlaceholderText("Buscar paciente…")
        search.setFixedHeight(34)
        search.setStyleSheet(
            f"QLineEdit {{ background:{COLORS['bg_secondary']}; border:0.5px solid rgba(0,0,0,0.18); "
            "border-radius:8px; padding:0 12px; font-size:13px; color:#1a1a18; }}"
            "QLineEdit:focus { border-color:#185FA5; }"
        )
        sr.addWidget(search, 1)

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

        main.addWidget(search_row)

        # Tabla
        table_panel = Panel("Exploraciones recientes")
        table = QTableWidget()
        table.setColumnCount(6)
        table.horizontalHeader().setDefaultAlignment(Qt.AlignCenter)
        table.setHorizontalHeaderLabels(["ID Paciente", "Edad", "Densidad", "AGD (mGy)", "Fecha", "Estado"])
        table.setStyleSheet(
            f"QTableWidget {{ background:{COLORS['bg_primary']}; border:none; gridline-color:rgba(0,0,0,0.06); font-size:12px; }}"
            f"QHeaderView::section {{ background:{COLORS['bg_secondary']}; color:{COLORS['text_tertiary']}; "
            "font-size:10px; font-weight:600; text-transform:uppercase; letter-spacing:0.05em; "
            "border:none; border-bottom:0.5px solid rgba(0,0,0,0.08); padding:6px 10px; }}"
            f"QTableWidget::item {{ padding:6px 10px; color:{COLORS['text_secondary']}; border:none; "
            "border-bottom:0.5px solid rgba(0,0,0,0.06); }}"
            f"QTableWidget::item:selected {{ background:{COLORS['blue_light']}; color:{COLORS['blue']}; }}"
        )
        table.setSelectionBehavior(QTableWidget.SelectRows)
        table.setEditTriggers(QTableWidget.NoEditTriggers)
        table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        table.verticalHeader().setVisible(False)
        table.setShowGrid(False)
        table.setAlternatingRowColors(False)

        table.setRowCount(len(self.PATIENTS))
        for row, (pid, age, dens, agd, date, status, color) in enumerate(self.PATIENTS):
            items = [
                    QTableWidgetItem(pid),
                    QTableWidgetItem(f"{age} años"),
                    QTableWidgetItem(f"Tipo {dens}"),
                    QTableWidgetItem(f"{agd:.2f}"),
                    QTableWidgetItem(date),
                    QTableWidgetItem("OK" if status == "ok" else "Revisar")
                ]
            for col, item in enumerate(items):
                item.setTextAlignment(Qt.AlignCenter) # <--- Esta es la clave
            
                # El color del estado se mantiene aparte
                if col == 5:
                    item.setForeground(QColor(COLORS["blue"] if status == "ok" else COLORS["amber"]))
                table.setItem(row, col, item)
            table.setRowHeight(row, 36)

        table.setMinimumHeight(240)
        table_panel.body().addWidget(table)
        main.addWidget(table_panel)
        main.addStretch()


class ViewCargar(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet("background:transparent;")
        main = QVBoxLayout(self)
        main.setContentsMargins(20, 20, 20, 20)
        main.setSpacing(16)

        upload_panel = Panel("Cargar nuevos archivos")

        for title, hint in [
            ("📁 Archivos DICOM (.dcm)",     "Arrastra los archivos DICOM aquí o haz clic para seleccionar"),
            ("📄 Informe RIS / CSV",          "Exportación del sistema RIS en formato CSV o Excel"),
            ("📋 Metadatos adicionales",       "Archivo JSON o XML con parámetros de adquisición"),
        ]:
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

            def make_handler(b=drop_btn, t=title):
                def handler():
                    path, _ = QFileDialog.getOpenFileName(self, f"Seleccionar {t}")
                    if path:
                        import os
                        fname = os.path.basename(path)
                        b.setStyleSheet(
                            "QPushButton { background:#EAF3DE; border:0.5px solid #639922; "
                            "border-radius:8px; font-size:12px; color:#3B6D11; }"
                        )
                        for i in range(b.layout().count()):
                            w = b.layout().itemAt(i).widget()
                            if w and isinstance(w, QLabel):
                                w.setText(fname if i == 1 else ("Archivo cargado correctamente" if i == 2 else "✓"))
                return handler

            drop_btn.clicked.connect(make_handler())
            upload_panel.body().addWidget(drop_btn)

        # Botón de procesar
        process_btn = QPushButton("Procesar archivos cargados")
        process_btn.setFixedHeight(36)
        process_btn.setCursor(QCursor(Qt.PointingHandCursor))
        process_btn.setStyleSheet(
            f"QPushButton {{ background:{COLORS['blue']}; color:#ffffff; border:none; "
            "border-radius:8px; font-size:13px; font-weight:600; }}"
            "QPushButton:hover { background:#0C447C; }"
        )
        upload_panel.body().addWidget(process_btn)
        main.addWidget(upload_panel)
        main.addStretch()


class ViewConfig(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet("background:transparent;")
        main = QVBoxLayout(self)
        main.setContentsMargins(20, 20, 20, 20)
        main.setSpacing(16)

        # Parámetros EUREF
        euref_panel = Panel("Parámetros EUREF")
        params = [
            ("Límite AGD tipo A (mGy)", "2,0"),
            ("Límite AGD tipo B (mGy)", "2,5"),
            ("Límite AGD tipo C (mGy)", "3,0"),
            ("Límite AGD tipo D (mGy)", "3,5"),
            ("Umbral alerta (% pacientes sobre límite)", "10%"),
        ]
        for param_name, param_val in params:
            row = QWidget()
            row.setStyleSheet("background:transparent; ")
            rl = QHBoxLayout(row)
            rl.setContentsMargins(12, 6, 6, 6)
            rl.setSpacing(12)
            rl.addWidget(label(param_name, 12, COLORS["text_primary"]), 1)
            val_input = QLineEdit(param_val)
            val_input.setFixedSize(80, 28)
            val_input.setAlignment(Qt.AlignCenter)
            val_input.setStyleSheet(
                f"QLineEdit {{ background:{COLORS['bg_secondary']}; "
                "border:0.5px solid rgba(0,0,0,0.18); border-radius:6px; "
                "font-size:12px; font-weight:600; color:#1a1a18; padding:0 8px; }}"
                "QLineEdit:focus { border-color:#185FA5; }"
            )
            rl.addWidget(val_input)
            euref_panel.body().addWidget(row)
            euref_panel.body().addWidget(separator())

        main.addWidget(euref_panel)

        # Integraciones
        integr_panel = Panel("Integraciones")
        integrations = [
            ("🔵", "PACS — Sectra IDS7",    "Importación automática de imágenes DICOM", True),
            ("🟢", "RIS — Carestream Vue",   "Exportación de informes al sistema RIS",    True),
            ("⚪", "HIS — Cerner Millennium","Integración con historia clínica",           False),
        ]
        for icon, name, desc, active in integrations:
            row = QWidget()
            row.setStyleSheet(
                f"background:{COLORS['bg_secondary'] if not active else COLORS['bg_primary']}; "
                "border-radius:8px; border:0.5px solid rgba(0,0,0,0.08);"
            )
            if not active:
                row.setStyleSheet(
                    f"background:{COLORS['bg_secondary']}; border-radius:8px; "
                    "border:0.5px solid rgba(0,0,0,0.08); opacity:0.6;"
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

            rl.addWidget(badge("Conectado" if active else "Inactivo", "green" if active else "gray"))
            integr_panel.body().addWidget(row)

        main.addWidget(integr_panel)
        main.addStretch()


# ════════════════════════════════════════════════════════════
#  VENTANA PRINCIPAL
# ════════════════════════════════════════════════════════════

class MainWindow(QMainWindow):
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

        # Sidebar
        self.sidebar = Sidebar(self._on_nav)
        root.addWidget(self.sidebar)

        # Main area
        main_area = QWidget()
        main_area.setStyleSheet(f"background:{COLORS['bg_tertiary']};")
        mv = QVBoxLayout(main_area)
        mv.setContentsMargins(0, 0, 0, 0)
        mv.setSpacing(0)

        self.topbar = Topbar()
        mv.addWidget(self.topbar)

        # Área de scroll para las vistas
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

    def _on_nav(self, view_id):
        view = self.views.get(view_id)
        if view:
            self.stack.setCurrentWidget(view)
        self.topbar.set_title(self.TITLES.get(view_id, ""))


def main():
    app = QApplication(sys.argv)
    app.setStyle("Fusion")

    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
