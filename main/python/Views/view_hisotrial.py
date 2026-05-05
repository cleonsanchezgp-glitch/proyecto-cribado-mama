from PySide6.QtWidgets import (
    QLineEdit, QWidget, QHBoxLayout, QVBoxLayout, QPushButton,
    QTableWidget, QTableWidgetItem, QHeaderView, QLabel
)
from PySide6.QtGui import QColor, Qt
from main.python.Views.colors import COLORS
from main.python.Views.utils import Panel


class ViewHistorial(QWidget):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet("background:transparent;")
        
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(16)

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
                "QPushButton { background:transparent; border:1px solid rgba(0,0,0,0.18); "
                "border-radius:14px; padding:4px 12px; font-size:12px; "
                "color:#5f5e5a; font-weight:500; }"
                f"QPushButton:checked {{ background:{COLORS['blue_light']}; border:1px solid {COLORS['blue']}; "
                f"color:{COLORS['blue']}; font-weight:bold; }}"
            )
            sr.addWidget(chip)
            self.filter_chips[filt] = chip

        main_layout.addWidget(search_row)

        table_panel = Panel("Exploraciones recientes")
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.horizontalHeader().setDefaultAlignment(Qt.AlignCenter)
        self.table.setHorizontalHeaderLabels(
            ["ID Paciente", "Edad", "Densidad", "AGD (mGy)", "Fecha", "Estado"]
        )
        self.table.setStyleSheet(
            f"QTableWidget {{ background:{COLORS['bg_primary']}; border:none; "
            "gridline-color:rgba(0,0,0,0.06); font-size:12px; color:#1a1a18; }}"
            f"QHeaderView::section {{ background:{COLORS['bg_secondary']}; color:#5f5e5a; "
            "font-size:10px; font-weight:800; text-transform:uppercase; letter-spacing:0.05em; "
            "border:none; border-bottom:0.5px solid rgba(0,0,0,0.08); padding:6px 10px; }}"
            f"QTableWidget::item {{ padding:6px 10px; color:#1a1a18; border:none; "
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
        main_layout.addWidget(table_panel)

        self.panel_detalles = QWidget()
        self.panel_detalles.setObjectName("panel_contenedor")
        self.panel_detalles.setVisible(False)
        self.panel_detalles.setStyleSheet("""
            QWidget#panel_contenedor { 
                background-color: #f8f9fa; 
                border-radius: 8px; 
                border: 1px solid #dee2e6; 
            }
            QLabel { 
                color: #1a1a18; 
                border: none; 
                font-size: 14px; 
                padding-bottom: 5px; 
            }
            QTableWidget { 
                background-color: white; 
                border: none; 
                color: #1a1a18;
            }
            QHeaderView::section {
                background-color: #f1f3f4;
                color: #5f5e5a;
                font-weight: bold;
                border: none;
                border-bottom: 1px solid #dee2e6;
                padding: 5px;
            }
            QTableWidget::item {
                color: #1a1a18;
                padding: 4px;
            }
            QTableWidget::item:selected {
                background-color: #e3f2fd;
                color: #0d47a1;
            }
        """)
        layout_detalles = QVBoxLayout(self.panel_detalles)
        
        self.lbl_info_paciente = QLabel("<b>Detalles del Paciente:</b> ")
        layout_detalles.addWidget(self.lbl_info_paciente)
        
        self.tabla_estudios = QTableWidget()
        self.tabla_estudios.setColumnCount(4)
        self.tabla_estudios.setHorizontalHeaderLabels(["Fecha / Hora", "Lateralidad", "Proyección", "Dosis (mGy)"])
        self.tabla_estudios.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.tabla_estudios.setEditTriggers(QTableWidget.NoEditTriggers)
        self.tabla_estudios.verticalHeader().setVisible(False)
        self.tabla_estudios.setFixedHeight(150)
        
        layout_detalles.addWidget(self.tabla_estudios)
        main_layout.addWidget(self.panel_detalles)

        main_layout.addStretch()

    def populate_table(self, rows: list):
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

    def mostrar_detalles_paciente(self, paciente):
        self.panel_detalles.setVisible(True)
        self.lbl_info_paciente.setText(f"<b>Estudios de {paciente.id}</b> | Edad: {paciente.edad} | Espesor: {paciente.espesor_mama_actual}mm")
        
        self.tabla_estudios.setRowCount(0)
        
        for estudio in paciente.estudios:
            row = self.tabla_estudios.rowCount()
            self.tabla_estudios.insertRow(row)
            
            fecha_hora = f"{estudio.fecha_realizacion} {estudio.hora_adquisicion}"
            
            items = [
                QTableWidgetItem(fecha_hora),
                QTableWidgetItem(str(estudio.lateralidad)),
                QTableWidgetItem(str(estudio.proyeccion)),
                QTableWidgetItem(f"{estudio.dosis_glandular:.2f}")
            ]
            
            for col, item in enumerate(items):
                item.setTextAlignment(Qt.AlignCenter)
                self.tabla_estudios.setItem(row, col, item)