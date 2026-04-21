from PySide6.QtWidgets import (
    QWidget, QVBoxLayout,
    QLabel, QPushButton, QFileDialog,
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QCursor
from main.python.Views.colors import COLORS
from main.python.Views.utils import Panel, label


# ══════════════════════════════════════════════════════════════════════════════
#  VISTA: Cargar archivos
#  Permite al usuario seleccionar los tres tipos de archivos de entrada
#  necesarios para ejecutar el análisis: DICOM, RIS/CSV y metadatos.
#
#  ESTRUCTURA VISUAL:
#    ┌──────────────────────────────────────────┐
#    │  [Zona drag-drop] Archivos DICOM (.dcm)  │
#    │  [Zona drag-drop] Informe RIS / CSV      │
#    │  [Zona drag-drop] Metadatos adicionales  │
#    │  [Botón] Procesar archivos cargados      │
#    └──────────────────────────────────────────┘
#
#  ATRIBUTOS PÚBLICOS (acceder desde CargarController):
#    selected_files   → dict {"dicom": path, "ris": path, "meta": path}
#    process_btn      → QPushButton: conectar .clicked para lanzar el procesado
#
#  CONEXIÓN DESDE MainWindow:
#    view.process_btn.clicked.connect(ctrl.on_process_files)
# ══════════════════════════════════════════════════════════════════════════════

class ViewCargar(QWidget):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet("background:transparent;")
        main = QVBoxLayout(self)
        main.setContentsMargins(20, 20, 20, 20)
        main.setSpacing(16)

        # Diccionario de rutas de archivos seleccionados, expuesto al controller.
        # Claves: "dicom", "ris", "meta" → se rellenan cuando el usuario selecciona un archivo.
        # El controller lo lee en: ctrl.on_process_files() → view.selected_files
        self.selected_files = {}

        upload_panel = Panel("Cargar nuevos archivos")

        # ── SECCIÓN 1: Zonas de selección de archivos ─────────────────────
        # Tres botones tipo "drop zone" que abren el diálogo de selección de archivo.
        # Al seleccionar un archivo: cambia el estilo a verde y muestra el nombre del archivo.
        # slot_key identifica el tipo de archivo para selected_files.
        file_slots = [
            ("dicom", "📁 Archivos DICOM (.dcm)",
             "Arrastra los archivos DICOM aquí o haz clic para seleccionar"),
            # Archivos de imagen mamográfica en formato DICOM exportados desde el PACS

            ("ris",   "📄 Informe RIS / CSV",
             "Exportación del sistema RIS en formato CSV o Excel"),
            # Datos clínicos y de la exploración exportados desde el sistema RIS

            ("meta",  "📋 Metadatos adicionales",
             "Archivo JSON o XML con parámetros de adquisición"),
            # Parámetros técnicos de adquisición no incluidos en el DICOM estándar
        ]

        for slot_key, title, hint in file_slots:
            drop_btn = QPushButton()
            drop_btn.setCursor(QCursor(Qt.PointingHandCursor))
            drop_btn.setMinimumHeight(90)
            # Estilo inicial: borde discontinuo, fondo transparente
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
                    # Abre el diálogo nativo del SO para seleccionar un archivo
                    path, _ = QFileDialog.getOpenFileName(self, f"Seleccionar {t}")
                    if path:
                        fname = os.path.basename(path)
                        # Guardar la ruta en el diccionario expuesto al controller
                        self.selected_files[key] = path
                        # Cambiar estilo a "cargado": fondo verde, borde verde
                        b.setStyleSheet(
                            "QPushButton { background:#EAF3DE; border:0.5px solid #639922; "
                            "border-radius:8px; font-size:12px; color:#3B6D11; }"
                        )
                        # Actualizar el texto del botón con el nombre del archivo seleccionado
                        for i in range(b.layout().count()):
                            w = b.layout().itemAt(i).widget()
                            if isinstance(w, QLabel):
                                w.setText(fname if i == 1 else ("✓ Archivo cargado" if i == 0 else ""))
                return handler

            drop_btn.clicked.connect(make_handler())
            upload_panel.body().addWidget(drop_btn)

        # ── SECCIÓN 2: Botón de procesado ─────────────────────────────────
        # Botón principal que lanza el pipeline de análisis con los archivos cargados.
        # Se expone como atributo público para conectarlo desde MainWindow o CargarController:
        #   view.process_btn.clicked.connect(ctrl.on_process_files)
        # El controller debe validar que selected_files contiene al menos "dicom" y "ris"
        # antes de iniciar el procesado.
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