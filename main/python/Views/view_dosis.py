from PySide6.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout,
    QLabel, QGridLayout,
)
from PySide6.QtGui import Qt
from main.python.Views.colors import COLORS
from main.python.Views.utils import Panel, ProgressBar, ScatterPlot, badge, label


# ══════════════════════════════════════════════════════════════════════════════
#  VISTA: Análisis de dosis
#  Muestra el análisis detallado de la dosis AGD del lote.
#
#  ESTRUCTURA VISUAL:
#    ┌──────────────┬──────────────┬──────────────┐
#    │ AGD media    │ Percentil 75 │ Percentil 95 │   ← Tarjetas estadísticas
#    ├──────────────┴──────────────┴──────────────┤
#    │  Scatter plot: Espesor vs. AGD             │   ← Gráfico de dispersión
#    ├─────────────────────────────────────────────┤
#    │  Cumplimiento EUREF por tipo de densidad   │   ← Barras de cumplimiento
#    └─────────────────────────────────────────────┘
#
#  MÉTODOS DE DATOS (llamar desde DosisController):
#    populate_stats(data)       → tarjetas AGD media / P75 / P95
#    populate_scatter(points)   → scatter plot espesor vs AGD
#    populate_compliance(data)  → tabla de cumplimiento EUREF
# ══════════════════════════════════════════════════════════════════════════════

class ViewDosis(QWidget):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet("background:transparent;")
        main = QVBoxLayout(self)
        main.setContentsMargins(20, 20, 20, 20)
        main.setSpacing(16)

        # ── SECCIÓN 1: Tarjetas de estadísticas de dosis ──────────────────
        # 3 tarjetas en fila: AGD media global, percentil 75 y percentil 95.
        # Los percentiles permiten identificar casos extremos de dosis alta.
        # Rellenar con: populate_stats(["1,84 mGy", "2,41 mGy", "3,18 mGy"])
        stats_row = QWidget()
        stats_row.setStyleSheet("background:transparent;")
        sg = QGridLayout(stats_row)
        sg.setSpacing(10)
        sg.setContentsMargins(0, 0, 0, 0)

        stat_defs = [
            ("AGD media",    "Global ponderada"),   # Media de todos los pacientes del lote
            ("Percentil 75", "75% pacientes"),       # El 75% de pacientes tiene dosis ≤ este valor
            ("Percentil 95", "Casos extremos"),      # El 95% de pacientes tiene dosis ≤ este valor
        ]
        self._stat_boxes = []   # Lista de QLabel de valor para actualizar con populate_stats()
        for i, (t, s) in enumerate(stat_defs):
            box = QWidget()
            box.setStyleSheet(f"background:{COLORS['bg_secondary']}; border-radius:8px; border:none;")
            bv = QVBoxLayout(box)
            bv.setContentsMargins(12, 10, 12, 12)
            bv.setSpacing(3)
            bv.addWidget(label(t.upper(), 9, COLORS["text_tertiary"]))
            lbl_val = label("—", 18, COLORS["text_primary"], "bold")  # Se actualiza con populate_stats()
            bv.addWidget(lbl_val)
            bv.addWidget(label(s, 10, COLORS["text_tertiary"]))
            self._stat_boxes.append(lbl_val)
            sg.addWidget(box, 0, i)

        main.addWidget(stats_row)

        # ── SECCIÓN 2: Scatter plot Espesor vs. AGD ───────────────────────
        # Gráfico de dispersión donde cada punto es un paciente.
        # Eje X = espesor mamario comprimido (mm), Eje Y = dosis AGD (mGy).
        # Los puntos se colorean por tipo de densidad (A=verde, B=azul, C=naranja, D=rojo).
        # La línea roja discontinua es el límite de referencia EUREF.
        # Rellenar con: populate_scatter([(espesor, agd, densidad_idx), ...])
        scatter_panel = Panel("Dispersión Espesor vs. AGD")
        self._scatter = ScatterPlot()   # Vacío hasta populate_scatter()
        scatter_panel.body().addWidget(self._scatter)

        # Leyenda de colores del scatter por tipo de densidad
        leg = QWidget()
        leg.setStyleSheet("background:transparent;")
        ll = QHBoxLayout(leg)
        ll.setContentsMargins(10, 6, 4, 6)
        ll.setSpacing(14)
        for color, txt in [("#97C459", "Tipo A"), ("#378ADD", "Tipo B"),
                           ("#EF9F27", "Tipo C"), ("#D85A30", "Tipo D")]:
            dot = QLabel("●")
            dot.setStyleSheet(f"color:{color}; font-size:11px; background:transparent; border:none;")
            t = label(txt, 11, COLORS["text_secondary"])
            ll.addWidget(dot)
            ll.addWidget(t)
        ll.addStretch()
        scatter_panel.body().addWidget(leg)
        main.addWidget(scatter_panel)

        # ── SECCIÓN 3: Tabla de cumplimiento EUREF por tipo de densidad ───
        # Una fila por cada tipo de densidad (A/B/C/D).
        # Cada fila muestra: nombre + barra de progreso + porcentaje + badge OK/Revisar.
        # Un tipo está "OK" si el % de pacientes dentro del límite EUREF supera el umbral.
        # Rellenar con: populate_compliance(data)
        comply_panel = Panel("Cumplimiento EUREF por tipo de densidad")
        self._comply_rows = []   # Lista de (ProgressBar, lbl_pct, badge) para actualizar
        for tipo in ["Tipo A", "Tipo B", "Tipo C", "Tipo D"]:
            row = QWidget()
            row.setStyleSheet("background:transparent;")
            rl = QHBoxLayout(row)
            rl.setContentsMargins(12, 4, 12, 4)
            rl.setSpacing(12)

            rl.addWidget(label(tipo, 12, COLORS["text_primary"]))

            bar = ProgressBar(0.0, COLORS["green"], 6)  # Vacío hasta populate_compliance()
            bar.setFixedWidth(120)
            rl.addWidget(bar)

            val_l = label("—", 12, COLORS["text_primary"], "bold")  # Porcentaje (p. ej. "97,2%")
            val_l.setFixedWidth(42)
            val_l.setAlignment(Qt.AlignRight)
            rl.addWidget(val_l)

            bdg = badge("—", "gray")  # Badge de estado: "OK" (verde) o "Revisar" (amber)
            rl.addWidget(bdg)
            rl.addStretch()
            self._comply_rows.append((bar, val_l, bdg))
            comply_panel.body().addWidget(row)

        main.addWidget(comply_panel)
        main.addStretch()

    # ══════════════════════════════════════════════════════════════════════
    #  MÉTODOS DE DATOS — Llamar desde DosisController
    # ══════════════════════════════════════════════════════════════════════

    def populate_stats(self, data: list):
        """
        ── PUNTO DE ENTRADA DE DATOS ──────────────────────────────────────
        Rellena las 3 tarjetas de estadísticas de dosis.

        data: list de 3 strings ya formateados con unidades [media, p75, p95]

        Ejemplo:
            view.populate_stats(["1,84 mGy", "2,41 mGy", "3,18 mGy"])
        """
        for lbl_val, value in zip(self._stat_boxes, data):
            lbl_val.setText(value)

    def populate_scatter(self, points: list):
        """
        ── PUNTO DE ENTRADA DE DATOS ──────────────────────────────────────
        Rellena el scatter plot con los datos de pacientes.
        Delega en ScatterPlot.set_data(points) — ver su docstring para el formato.

        Ejemplo:
            view.populate_scatter(dosis_controller.get_scatter_points())
        """
        self._scatter.set_data(points)

    def populate_compliance(self, data: list):
        """
        ── PUNTO DE ENTRADA DE DATOS ──────────────────────────────────────
        Rellena la tabla de cumplimiento EUREF por tipo de densidad.

        data: list de 4 dicts en orden A/B/C/D
            Claves: proportion (0.0–1.0), pct_text (str), style ("green"|"amber"|"coral")

        Ejemplo:
            view.populate_compliance([
                {"proportion": 0.972, "pct_text": "97,2%", "style": "green"},
                {"proportion": 0.941, "pct_text": "94,1%", "style": "green"},
                {"proportion": 0.813, "pct_text": "81,3%", "style": "amber"},
                {"proportion": 0.768, "pct_text": "76,8%", "style": "amber"},
            ])
        """
        bar_colors = {
            "green": COLORS["green"],
            "amber": COLORS["amber"],
            "coral": COLORS["coral"],
        }
        badge_styles = {
            "blue":  "background:#E6F1FB; color:#185FA5;",
            "green": "background:#EAF3DE; color:#3B6D11;",
            "amber": "background:#FAEEDA; color:#854F0B;",
            "coral": "background:#FAECE7; color:#993C1D;",
            "gray":  "background:#f0ede8; color:#5f5e5a;",
        }
        for (bar, val_l, bdg), d in zip(self._comply_rows, data):
            style = d.get("style", "green")
            # Actualizar barra de progreso con la proporción y color según estado
            bar.set_value(d.get("proportion", 0.0), bar_colors.get(style, COLORS["green"]))
            # Actualizar etiqueta de porcentaje
            val_l.setText(d.get("pct_text", "—"))
            # Actualizar badge: "OK" si cumple, "Revisar" si no
            bdg.setText("OK" if style == "green" else "Revisar")
            bdg.setStyleSheet(
                f"{badge_styles.get(style, badge_styles['green'])} "
                "font-size:10px; font-weight:600; padding:2px 8px; "
                "border-radius:99px; border:none;"
            )