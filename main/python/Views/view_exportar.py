from PySide6.QtWidgets import (
    QHBoxLayout, QWidget, QVBoxLayout, QPushButton
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QCursor
from main.python.Views.colors import COLORS
from main.python.Views.utils import Panel, label, separator

from main.python.Views.utils import badge, label
from main.python.Services.export_service import generate_csv_doc

class ViewExportar(QWidget):
    """
    Vista de exportación de resultados.

    SEÑALES INTERNAS
    ───────────────────────────────────────────────────────────────────────
    export_csv_btn.clicked  — conecta al controller para exportar a CSV:
        view.export_csv_btn.clicked.connect(ctrl.on_export_csv)

    export_db_btn.clicked   — conecta al controller para insertar en BD:
        view.export_db_btn.clicked.connect(ctrl.on_export_db)
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.pacientes = []
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
        db_layout.addWidget(self.export_db_btn)
        export_panel.body().addWidget(db_row)

        main.addWidget(export_panel)
        main.addStretch()

    def on_export_csv(self):
        from PySide6.QtWidgets import QFileDialog
        filename, _ = QFileDialog.getSaveFileName(self, "Guardar CSV", "", "CSV files (*.csv)")
        if filename:
            generate_csv_doc(self.pacientes, filename)
