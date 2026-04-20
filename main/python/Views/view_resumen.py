from PySide6.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout,
    QLabel, QGridLayout
)
from PySide6.QtGui import Qt
from main.python.Views.colors import COLORS
from main.python.Views.utils import BarChart, MetricCard, Panel, ProgressBar, label, separator


# ══════════════════════════════════════════════════════════════════════════════
#  VISTA: Resumen del análisis
#  Pantalla principal que muestra un resumen global del lote de pacientes.
#
#  ESTRUCTURA VISUAL:
#    ┌─────────────────────────────────────────────────────┐
#    │  [KPI] Pacientes  [KPI] Dosis  [KPI] Cruzados  [KPI] Desv. │
#    ├──────────────────────────────┬──────────────────────┤
#    │  Gráfico barras AGD          │  Estado del proceso  │
#    │  Distribución por densidad   │  Alertas y avisos    │
#    └──────────────────────────────┴──────────────────────┘
#
#  MÉTODOS DE DATOS (llamar desde ResumenController):
#    populate_metrics(data)   → fila de 4 tarjetas KPI
#    populate_chart(data)     → gráfico de barras AGD
#    populate_density(data)   → barras de distribución por tipo
#    populate_steps(steps)    → estado del pipeline
#    populate_alerts(alerts)  → panel de alertas
# ══════════════════════════════════════════════════════════════════════════════

class ViewResumen(QWidget):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet("background:transparent;")
        main = QVBoxLayout(self)
        main.setContentsMargins(20, 20, 20, 20)
        main.setSpacing(16)

        # ── SECCIÓN 1: Fila de tarjetas KPI ──────────────────────────────
        # 4 tarjetas métricas en la parte superior: pacientes, dosis, cruzados, desviación.
        # Se rellenan con populate_metrics(data) desde el controller.
        cards_row = QWidget()
        cards_row.setStyleSheet("background:transparent;")
        grid = QGridLayout(cards_row)
        grid.setSpacing(12)
        grid.setContentsMargins(0, 0, 0, 0)

        metric_titles = [
            "Pacientes totales",    # Total de pacientes del lote
            "Dosis media (mGy)",    # AGD media ponderada global
            "Registros cruzados",   # Pacientes con match DICOM+RIS
            "Desviación estándar",  # Dispersión de la dosis AGD
        ]
        self._metric_cards = []
        for i, title in enumerate(metric_titles):
            card = MetricCard(title)   # Arranca con "—", se rellena con populate_metrics()
            self._metric_cards.append(card)
            grid.addWidget(card, 0, i)

        main.addWidget(cards_row)

        # ── SECCIÓN 2: Layout de dos columnas ────────────────────────────
        # Columna izquierda (ancha): gráficos y distribución
        # Columna derecha (fija 300px): estado del proceso y alertas
        two_col = QWidget()
        two_col.setStyleSheet("background:transparent;")
        tc = QHBoxLayout(two_col)
        tc.setContentsMargins(0, 0, 0, 0)
        tc.setSpacing(16)

        # ── COLUMNA IZQUIERDA ─────────────────────────────────────────────
        left = QWidget()
        left.setStyleSheet("background:transparent;")
        lv = QVBoxLayout(left)
        lv.setContentsMargins(0, 0, 0, 0)
        lv.setSpacing(16)

        # Panel: Gráfico de barras AGD por grupo de densidad
        # Muestra AGD media del año anterior vs. año actual para cada tipo A/B/C/D.
        # Rellenar con: populate_chart(data) → delega en BarChart.set_data()
        chart_panel = Panel("Dosis media AGD por grupo de densidad (mGy)")
        self._bar_chart = BarChart()   # Vacío hasta populate_chart()
        chart_panel.body().addWidget(self._bar_chart)

        # Leyenda del gráfico de barras (año anterior / año actual)
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

        # Panel: Distribución de pacientes por tipo de densidad mamaria (A/B/C/D)
        # Cada fila muestra: nombre del tipo + barra de progreso + porcentaje + nº pacientes.
        # Rellenar con: populate_density(data)
        dens_panel = Panel("Distribución por tipo de densidad")
        self._density_rows = []   # Lista de (ProgressBar, lbl_pct, lbl_n) para actualizar
        density_colors = ["#97C459", "#378ADD", "#EF9F27", "#D85A30"]  # A=verde, B=azul, C=naranja, D=rojo
        for i, tipo in enumerate(["Tipo A", "Tipo B", "Tipo C", "Tipo D"]):
            row = QWidget()
            row.setStyleSheet("background:transparent;")
            rl = QHBoxLayout(row)
            rl.setContentsMargins(5, 2, 5, 2)
            rl.setSpacing(15)

            l1 = label(tipo, 11, COLORS["text_primary"], "bold")
            l1.setFixedWidth(60)
            rl.addWidget(l1)

            bar = ProgressBar(0.0, density_colors[i], 8)   # Proporción vacía hasta populate_density()
            rl.addWidget(bar, 1)

            l2 = label("—", 12, COLORS["text_primary"], "bold")   # Porcentaje (p. ej. "18%")
            l2.setFixedWidth(40)
            l2.setContentsMargins(5, 2, 5, 2)
            rl.addWidget(l2)

            l3 = label("n=—", 11, COLORS["text_tertiary"])   # Número de pacientes (p. ej. "n=1.498")
            l3.setFixedWidth(65)
            l3.setContentsMargins(5, 2, 5, 2)
            rl.addWidget(l3)

            self._density_rows.append((bar, l2, l3))
            dens_panel.body().addWidget(row)

        lv.addWidget(dens_panel)
        tc.addWidget(left, 1)

        # ── COLUMNA DERECHA ───────────────────────────────────────────────
        right = QWidget()
        right.setStyleSheet("background:transparent;")
        rv = QVBoxLayout(right)
        rv.setContentsMargins(0, 0, 0, 0)
        rv.setSpacing(16)
        right.setFixedWidth(300)

        # Panel: Estado del proceso (pipeline de 5 pasos)
        # Muestra el progreso del pipeline: DICOM → RIS → AGD → Informe → Exportar.
        # Cada paso tiene estado: "" (pendiente), "active" (en curso), "done" (completado).
        # Rellenar con: populate_steps(steps)
        proc_panel = Panel("Estado del proceso")
        self._step_rows = []   # Lista de (lbl_numero, lbl_detalle) para actualizar el estado
        step_names = [
            ("Importar DICOM",            "Pendiente"),   # Paso 1: carga de imágenes DICOM desde PACS
            ("Cruzar con RIS",            "Pendiente"),   # Paso 2: match de registros con el sistema RIS
            ("Calcular AGD por densidad", "Pendiente"),   # Paso 3: cálculo de dosis AGD segmentada
            ("Generar informe EUREF",     "Pendiente"),   # Paso 4: generación del informe de cumplimiento
            ("Exportar resultados",       "Pendiente"),   # Paso 5: exportación a CSV/PDF
        ]
        for idx, (name, detail) in enumerate(step_names):
            row = QWidget()
            row.setStyleSheet("background:transparent; padding-left: 10px;")
            rl = QHBoxLayout(row)
            rl.setContentsMargins(12, 8, 12, 8)
            rl.setSpacing(12)

            # Indicador de estado: número (pendiente), "→" (activo), "✓" (completado)
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
            lbl_detail = label(detail, 11, COLORS["text_tertiary"])  # Se actualiza con populate_steps()
            cv.addWidget(lbl_name)
            cv.addWidget(lbl_detail)
            rl.addWidget(col, 1)

            self._step_rows.append((num, lbl_detail))
            proc_panel.body().addWidget(row)
            if idx < len(step_names) - 1:
                proc_panel.body().addWidget(separator())

        rv.addWidget(proc_panel)

        # Panel: Alertas y avisos
        # Lista dinámica de alertas generadas por el sistema (p. ej. pacientes fuera de rango).
        # El panel se vacía y se rellena de nuevo con populate_alerts(alerts).
        # Cada alerta tiene: estilo visual (amber/coral/blue), título y subtítulo.
        alerts_panel = Panel("Alertas y avisos")
        self._alerts_layout = alerts_panel.body()   # Layout expuesto para añadir/eliminar alertas
        rv.addWidget(alerts_panel)
        rv.addStretch()
        tc.addWidget(right)

        main.addWidget(two_col)
        main.addStretch()

    # ══════════════════════════════════════════════════════════════════════
    #  MÉTODOS DE DATOS — Llamar desde ResumenController
    # ══════════════════════════════════════════════════════════════════════

    def populate_metrics(self, data: list):
        """
        ── PUNTO DE ENTRADA DE DATOS ──────────────────────────────────────
        Rellena las 4 tarjetas KPI de la fila superior.

        data: list de 4 dicts con claves: value, subtitle, badge_text, badge_style
        Orden: [pacientes_totales, dosis_media, registros_cruzados, desviacion_std]

        Ejemplo:
            view.populate_metrics([
                {"value": "8.342", "subtitle": "Exploración 2023–2024",
                 "badge_text": "+312 nuevo lote", "badge_style": "blue"},
                {"value": "1,84",  "subtitle": "Media ponderada",
                 "badge_text": "Dentro EUREF",    "badge_style": "green"},
                ...
            ])
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
        ── PUNTO DE ENTRADA DE DATOS ──────────────────────────────────────
        Rellena el gráfico de barras AGD por grupo de densidad.
        Delega en BarChart.set_data(data) — ver su docstring para el formato.
        """
        self._bar_chart.set_data(data)

    def populate_density(self, data: list):
        """
        ── PUNTO DE ENTRADA DE DATOS ──────────────────────────────────────
        Rellena las barras de distribución por tipo de densidad.

        data: list de 4 dicts en orden A/B/C/D
            Claves: proportion (0.0–1.0), pct_text (str), n (str)

        Ejemplo:
            view.populate_density([
                {"proportion": 0.18, "pct_text": "18%", "n": "1.498"},
                {"proportion": 0.42, "pct_text": "42%", "n": "3.503"},
                ...
            ])
        """
        for (bar, lbl_pct, lbl_n), d in zip(self._density_rows, data):
            bar.set_value(d.get("proportion", 0.0))
            lbl_pct.setText(d.get("pct_text", "—"))
            lbl_n.setText(f"n={d.get('n', '—')}")

    def populate_steps(self, steps: list):
        """
        ── PUNTO DE ENTRADA DE DATOS ──────────────────────────────────────
        Actualiza el estado visual de cada paso del pipeline.

        steps: list de 5 dicts en orden (mismo orden que la UI)
            Claves: state ("done" | "active" | ""), detail (str)

        Ejemplo:
            view.populate_steps([
                {"state": "done",   "detail": "8.342 estudios cargados"},
                {"state": "done",   "detail": "8.189 registros enlazados"},
                {"state": "active", "detail": "En proceso…"},
                {"state": "",       "detail": "Pendiente"},
                {"state": "",       "detail": "Pendiente"},
            ])
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
        ── PUNTO DE ENTRADA DE DATOS ──────────────────────────────────────
        Vacía el panel de alertas y lo rellena con las alertas actuales.

        alerts: list de dicts
            Claves: style ("amber" | "coral" | "blue"), title (str), subtitle (str)

        Ejemplo:
            view.populate_alerts([
                {"style": "amber", "title": "Tipo C — 47 pacientes superan ref.",
                 "subtitle": "AGD > 2,5 mGy en tipo C"},
                {"style": "coral", "title": "12 estudios sin densidad",
                 "subtitle": "Metadatos DICOM incompletos"},
                {"style": "blue",  "title": "Nuevo lote PACS disponible",
                 "subtitle": "312 estudios pendientes"},
            ])
        """
        # Limpiar todas las alertas previas antes de añadir las nuevas
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