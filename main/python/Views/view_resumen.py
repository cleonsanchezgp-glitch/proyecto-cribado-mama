
from PySide6.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout,
    QLabel,QGridLayout
)

from PySide6.QtGui import Qt
from main.python.Views.colors import COLORS
from main.python.Views.utils import BarChart, MetricCard, Panel, ProgressBar, label, separator

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