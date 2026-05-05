from PySide6.QtWidgets import (
    QHBoxLayout, QWidget, QVBoxLayout, QPushButton, QFileDialog, QMessageBox
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QCursor
from main.python.Views.colors import COLORS
from main.python.Views.utils import Panel, label, separator, badge

# Importamos ambos métodos del servicio de exportación
from main.python.Services.export_service import generate_csv_doc, insert_data_DB

class ViewExportar(QWidget):
    """
    Vista de exportación de resultados.
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.pacientes = [] # Se mantiene por compatibilidad, aunque ahora usamos la memoria global
        self.setStyleSheet("background:transparent;")
        main = QVBoxLayout(self)
        main.setContentsMargins(20, 20, 20, 20)
        main.setSpacing(16)

        # ── Panel principal de exportación ────────────────────────────────
        export_panel = Panel("Exportar resultados")

        # Descripción introductoria
        intro = label(
            "Elige el destino para los datos procesados del lote actual.",
            12, COLORS["text_secondary"], wrap=True
        )
        export_panel.body().addWidget(intro)
        export_panel.body().addWidget(separator())

        # ── Opción 1: Exportar a CSV ───────────────────────────────────────
        csv_row = QWidget()
        csv_row.setStyleSheet(
            f"background:{COLORS['bg_secondary']}; border-radius:8px; border:none;"
        )
        csv_layout = QVBoxLayout(csv_row)
        csv_layout.setContentsMargins(16, 14, 16, 14)
        csv_layout.setSpacing(6)

        csv_header = QWidget()
        csv_header.setStyleSheet("background:transparent;")
        csv_hl = QHBoxLayout(csv_header)
        csv_hl.setContentsMargins(0, 0, 0, 0)
        csv_hl.setSpacing(10)
        csv_hl.addWidget(label("📄 Exportar a CSV", 13, COLORS["text_primary"], "bold"), 1)
        csv_hl.addWidget(badge("Recomendado", "blue"))
        csv_layout.addWidget(csv_header)

        csv_layout.addWidget(
            label(
                "Genera un archivo .csv con todos los registros de pacientes "
                "y sus dosis calculadas, listo para análisis externo o archivo.",
                11, COLORS["text_tertiary"], wrap=True
            )
        )

        self.export_csv_btn = QPushButton("Exportar CSV")
        self.export_csv_btn.setFixedHeight(36)
        self.export_csv_btn.setCursor(QCursor(Qt.PointingHandCursor))
        self.export_csv_btn.setStyleSheet(
            f"QPushButton {{ background:{COLORS['blue']}; color:#ffffff; border:none; "
            "border-radius:8px; font-size:13px; font-weight:600; }}"
            "QPushButton:hover { background:#0C447C; }"
        )
        self.export_csv_btn.clicked.connect(self.on_export_csv)
        csv_layout.addWidget(self.export_csv_btn)
        export_panel.body().addWidget(csv_row)

        export_panel.body().addWidget(separator())

        # ── Opción 2: Insertar en base de datos ───────────────────────────
        db_row = QWidget()
        db_row.setStyleSheet(
            f"background:{COLORS['bg_secondary']}; border-radius:8px; border:none;"
        )
        db_layout = QVBoxLayout(db_row)
        db_layout.setContentsMargins(16, 14, 16, 14)
        db_layout.setSpacing(6)

        db_header = QWidget()
        db_header.setStyleSheet("background:transparent;")
        db_hl = QHBoxLayout(db_header)
        db_hl.setContentsMargins(0, 0, 0, 0)
        db_hl.setSpacing(10)
        db_hl.addWidget(label("🗄️ Insertar en base de datos", 13, COLORS["text_primary"], "bold"), 1)
        db_hl.addWidget(badge("BD", "gray"))
        db_layout.addWidget(db_header)

        db_layout.addWidget(
            label(
                "Vuelca los datos procesados directamente en la base de datos "
                "configurada, creando o actualizando los registros correspondientes.",
                11, COLORS["text_tertiary"], wrap=True
            )
        )

        self.export_db_btn = QPushButton("Insertar en base de datos")
        self.export_db_btn.setFixedHeight(36)
        self.export_db_btn.setCursor(QCursor(Qt.PointingHandCursor))
        self.export_db_btn.setStyleSheet(
            "QPushButton { background:transparent; border:0.5px solid rgba(0,0,0,0.25); "
            f"border-radius:8px; font-size:13px; font-weight:600; color:{COLORS['text_primary']}; }}"
            f"QPushButton:hover {{ background:{COLORS['bg_primary']}; }}"
        )
        # Conectamos el botón de la base de datos
        self.export_db_btn.clicked.connect(self.on_export_db)
        
        db_layout.addWidget(self.export_db_btn)
        export_panel.body().addWidget(db_row)

        main.addWidget(export_panel)
        main.addStretch()

    def on_export_csv(self):
        """Maneja la exportación del archivo CSV."""
        filename, _ = QFileDialog.getSaveFileName(self, "Guardar CSV", "", "CSV files (*.csv)")
        if filename:
            try:
                generate_csv_doc(filename) # Ya no necesita la lista como parámetro
                QMessageBox.information(self, "Éxito", "Archivo CSV exportado correctamente.")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"No se pudo exportar el archivo: {str(e)}")

    def on_export_db(self):
        """Maneja la inserción en la base de datos."""
        try:
            insert_data_DB() # Llama directamente a la inserción en la BD
            QMessageBox.information(self, "Éxito", "Datos insertados en la base de datos correctamente.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error al insertar en la base de datos:\n{str(e)}")