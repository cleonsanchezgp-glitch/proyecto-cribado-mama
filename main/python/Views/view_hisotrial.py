from PySide6.QtWidgets import (
    QLineEdit, QWidget, QHBoxLayout, QVBoxLayout, QPushButton,
    QTableWidget, QTableWidgetItem, QHeaderView
)
from PySide6.QtGui import QColor, Qt
from main.python.Views.colors import COLORS
from main.python.Views.utils import Panel


# ══════════════════════════════════════════════════════════════════════════════
#  VISTA: Historial de exploraciones
#  Tabla de pacientes del lote con buscador y filtros por tipo de densidad.
#
#  ESTRUCTURA VISUAL:
#    ┌──────────────────────────────────────────────────────┐
#    │  [Buscador]  [Todos] [Tipo A] [Tipo B] [Tipo C] [Tipo D]  │
#    ├──────────────────────────────────────────────────────┤
#    │  ID Paciente │ Edad │ Densidad │ AGD │ Fecha │ Estado │
#    │  ...         │ ...  │ ...      │ ... │ ...   │ ...    │
#    └──────────────────────────────────────────────────────┘
#
#  ATRIBUTOS PÚBLICOS (conectar desde HistorialController):
#    search_input          → QLineEdit: conectar .textChanged para filtrado en tiempo real
#    filter_chips          → dict[str, QPushButton]: conectar .toggled por tipo
#    table                 → QTableWidget: accesible si se necesita manipulación directa
#
#  MÉTODO DE DATOS:
#    populate_table(rows)  → rellena la tabla con la lista de pacientes filtrada
# ══════════════════════════════════════════════════════════════════════════════

class ViewHistorial(QWidget):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet("background:transparent;")
        main = QVBoxLayout(self)
        main.setContentsMargins(20, 20, 20, 20)
        main.setSpacing(16)

        # ── SECCIÓN 1: Buscador y chips de filtro ─────────────────────────
        # El buscador filtra por ID de paciente en tiempo real.
        # Los chips de densidad filtran la tabla por tipo (A/B/C/D).
        # Conectar desde HistorialController:
        #   view.search_input.textChanged.connect(ctrl.on_search)
        #   view.filter_chips["Tipo A"].toggled.connect(ctrl.on_filter_tipo_a)
        search_row = QWidget()
        search_row.setStyleSheet("background:transparent;")
        sr = QHBoxLayout(search_row)
        sr.setContentsMargins(0, 0, 0, 0)
        sr.setSpacing(10)

        # Campo de búsqueda por ID de paciente
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Buscar paciente…")
        self.search_input.setFixedHeight(34)
        self.search_input.setStyleSheet(
            f"QLineEdit {{ background:{COLORS['bg_secondary']}; border:0.5px solid rgba(0,0,0,0.18); "
            "border-radius:8px; padding:0 12px; font-size:13px; color:#1a1a18; }}"
            "QLineEdit:focus { border-color:#185FA5; }"
        )
        sr.addWidget(self.search_input, 1)

        # Chips de filtro por tipo de densidad
        # self.filter_chips["Todos"] está activo por defecto
        self.filter_chips = {}
        for filt in ["Todos", "Tipo A", "Tipo B", "Tipo C", "Tipo D"]:
            chip = QPushButton(filt)
            chip.setCheckable(True)
            chip.setFixedHeight(28)
            if filt == "Todos":
                chip.setChecked(True)   # "Todos" activo por defecto al arrancar
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

        # ── SECCIÓN 2: Tabla de exploraciones recientes ───────────────────
        # Tabla principal con una fila por paciente del lote.
        # Las columnas son: ID, Edad, Densidad, AGD, Fecha, Estado.
        # La columna Estado se colorea: azul=OK, amber=Revisar.
        # Se rellena (y vacía/recarga) con populate_table(rows).
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
        self.table.setSelectionBehavior(QTableWidget.SelectRows)    # Selección de fila completa
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)     # Solo lectura
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)  # Columnas que se expanden
        self.table.verticalHeader().setVisible(False)               # Sin numeración de filas
        self.table.setShowGrid(False)
        self.table.setAlternatingRowColors(False)
        self.table.setMinimumHeight(240)
        table_panel.body().addWidget(self.table)
        main.addWidget(table_panel)
        main.addStretch()

    # ══════════════════════════════════════════════════════════════════════
    #  MÉTODOS DE DATOS — Llamar desde HistorialController
    # ══════════════════════════════════════════════════════════════════════

    def populate_table(self, rows: list):
        """
        ── PUNTO DE ENTRADA DE DATOS ──────────────────────────────────────
        Vacía la tabla y la rellena con los datos proporcionados.
        Se llama tanto en la carga inicial como tras aplicar filtros/búsqueda.

        rows: list de dicts
            Claves: id (str), age (int), density (str), agd (float), date (str),
                    status ("ok" | "revisar")

        Ejemplo (carga inicial):
            view.populate_table(historial_controller.get_all())

        Ejemplo (tras filtro):
            view.populate_table(historial_controller.filter_by_density("B"))

        Flujo de filtrado recomendado:
            1. Usuario escribe en search_input → controller filtra → llama populate_table()
            2. Usuario activa chip "Tipo C"    → controller filtra → llama populate_table()
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
                # Colorear la columna Estado: azul=OK, amber=Revisar
                if col == 5:
                    item.setForeground(
                        QColor(COLORS["blue"] if status == "ok" else COLORS["amber"])
                    )
                self.table.setItem(row_idx, col, item)
            self.table.setRowHeight(row_idx, 36)