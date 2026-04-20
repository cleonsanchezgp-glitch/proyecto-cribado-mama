
from PySide6.QtWidgets import (
    QLineEdit, QWidget, QHBoxLayout, QVBoxLayout, QPushButton, QTableWidget, QTableWidgetItem, QHeaderView
)
from PySide6.QtGui import QColor, Qt

from main.python.Views.colors import COLORS
from main.python.Views.utils import Panel

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
