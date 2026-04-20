
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout,
    QLabel, QPushButton, QFileDialog,
)

from PySide6.QtCore import Qt
from PySide6.QtGui import QCursor

from main.python.Views.colors import COLORS
from main.python.Views.utils import Panel, label

class ViewCargar(QWidget):
    """
    Vista de carga de archivos.

    SEÑALES INTERNAS
    ───────────────────────────────────────────────────────────────────────
    process_btn.clicked  — conecta al controller para lanzar el procesado:
        view.process_btn.clicked.connect(ctrl.on_process_files)

    Para conocer los archivos seleccionados accede a:
        view.selected_files   → dict { "DICOM": path, "RIS": path, "META": path }
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet("background:transparent;")
        main = QVBoxLayout(self)
        main.setContentsMargins(20, 20, 20, 20)
        main.setSpacing(16)

        self.selected_files = {}   # Expuesto al controller

        upload_panel = Panel("Cargar nuevos archivos")

        file_slots = [
            ("dicom", "📁 Archivos DICOM (.dcm)",
             "Arrastra los archivos DICOM aquí o haz clic para seleccionar"),
            ("ris",   "📄 Informe RIS / CSV",
             "Exportación del sistema RIS en formato CSV o Excel"),
            ("meta",  "📋 Metadatos adicionales",
             "Archivo JSON o XML con parámetros de adquisición"),
        ]

        for slot_key, title, hint in file_slots:
            drop_btn = QPushButton()
            drop_btn.setCursor(QCursor(Qt.PointingHandCursor))
            drop_btn.setMinimumHeight(90)
            drop_btn.setStyleSheet(
                "QPushButton { background:transparent; border:0.5px dashed rgba(0,0,0,0.25); "
                "border-radius:8px; font-size:12px; color:#5f5e5a; }"
                f"QPushButton:hover {{ background:{COLORS['bg_secondary']}; }}"
            )
            btn_layout = QVBoxLayout(drop_btn)
            btn_layout.setSpacing(4)
            btn_layout.setAlignment(Qt.AlignCenter)
            btn_layout.addWidget(label(title, 12, COLORS["text_primary"], "bold"))
            btn_layout.addWidget(label(hint, 11, COLORS["text_tertiary"]))

            def make_handler(b=drop_btn, t=title, key=slot_key):
                def handler():
                    import os
                    path, _ = QFileDialog.getOpenFileName(self, f"Seleccionar {t}")
                    if path:
                        fname = os.path.basename(path)
                        self.selected_files[key] = path
                        b.setStyleSheet(
                            "QPushButton { background:#EAF3DE; border:0.5px solid #639922; "
                            "border-radius:8px; font-size:12px; color:#3B6D11; }"
                        )
                        for i in range(b.layout().count()):
                            w = b.layout().itemAt(i).widget()
                            if isinstance(w, QLabel):
                                w.setText(fname if i == 1 else ("✓ Archivo cargado" if i == 0 else ""))
                return handler

            drop_btn.clicked.connect(make_handler())
            upload_panel.body().addWidget(drop_btn)

        # ── MÉTODO PÚBLICO: process_btn expuesto al controller ────────────
        self.process_btn = QPushButton("Procesar archivos cargados")
        self.process_btn.setFixedHeight(36)
        self.process_btn.setCursor(QCursor(Qt.PointingHandCursor))
        self.process_btn.setStyleSheet(
            f"QPushButton {{ background:{COLORS['blue']}; color:#ffffff; border:none; "
            "border-radius:8px; font-size:13px; font-weight:600; }}"
            "QPushButton:hover { background:#0C447C; }"
        )
        upload_panel.body().addWidget(self.process_btn)
        main.addWidget(upload_panel)
        main.addStretch()