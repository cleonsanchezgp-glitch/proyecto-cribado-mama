
from PySide6.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout,
    QLabel, QGridLayout,
)
from PySide6.QtGui import Qt
from main.python.Views.colors import COLORS
from main.python.Views.utils import Panel, ProgressBar, ScatterPlot, badge, label

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