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
        self.setStyleSheet("background:transparent;")
        main = QVBoxLayout(self)
        main.setContentsMargins(20, 20, 20, 20)
        main.setSpacing(16)

        # Panel principal de exportación
        export_panel = Panel("Exportar resultados")

        # Descripción introductoria
        intro = label(
            "Elige el destino para los datos procesados del lote actual.",
            12, COLORS["text_secondary"], wrap=True
        )
        export_panel.body().addWidget(intro)
        export_panel.body().addWidget(separator())

        #  Exportar a CSV
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

        # Insertar en base de datos 
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
        db_hl.addWidget(label("🗄️ Oracle Database", 13, COLORS["text_primary"], "bold"), 1)
        db_hl.addWidget(badge("23ai Free", "amber")) # Badge actualizado al sistema
        db_layout.addWidget(db_header)

        db_layout.addWidget(
            label(
                "Conexión directa con FREEPDB1. Almacena de forma permanente "
                "los estudios calculados y actualiza el historial clínico.",
                11, COLORS["text_tertiary"], wrap=True
            )
        )

        self.export_db_btn = QPushButton("Sincronizar con Base de Datos")
        self.export_db_btn.setFixedHeight(40) # Un poco más alto para destacar
        self.export_db_btn.setCursor(QCursor(Qt.PointingHandCursor))
        self.export_db_btn.setStyleSheet(
            f"QPushButton {{ background:{COLORS['bg_primary']}; border:1px solid {COLORS['blue']}; "
            f"border-radius:8px; font-size:13px; font-weight:600; color:{COLORS['blue']}; }}"
            f"QPushButton:hover {{ background:{COLORS['blue']}; color: white; }}"
        )
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
                generate_csv_doc(filename)
                QMessageBox.information(self, "Exportación Exitosa", f"Archivo guardado en:\n{filename}")
            except Exception as e:
                QMessageBox.critical(self, "Error de Archivo", f"No se pudo generar el CSV:\n{str(e)}")

    def on_export_db(self):
        """Maneja la inserción en la base de datos Oracle."""
        # 1. Confirmación del usuario
        reply = QMessageBox.question(
            self, "Confirmar Sincronización",
            "¿Deseas volcar los datos actuales en la base de datos Oracle?",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )

        if reply == QMessageBox.Yes:

            self.setCursor(Qt.WaitCursor)
            self.export_db_btn.setEnabled(False)
            self.export_db_btn.setText("Conectando con Oracle...")

            try:
            
                insert_data_DB()
                
                QMessageBox.information(
                    self, "Sincronización Exitosa", 
                    "Los datos se han guardado correctamente en FREEPDB1."
                )
            except Exception as e:
                # Error detallado para depuración
                QMessageBox.critical(
                    self, "Error de Conexión", 
                    f"No se pudo conectar con Oracle:\n{str(e)}"
                )
            finally:
             
                self.setCursor(Qt.ArrowCursor)
                self.export_db_btn.setEnabled(True)
                self.export_db_btn.setText("Sincronizar con Base de Datos")