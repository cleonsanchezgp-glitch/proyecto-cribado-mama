from PySide6.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout, QLineEdit
)
from PySide6.QtCore import Qt
from main.python.Views.colors import COLORS
from main.python.Views.utils import Panel, badge, label, separator


# ══════════════════════════════════════════════════════════════════════════════
#  VISTA: Configuración
#  Permite editar los parámetros EUREF y consultar el estado de las integraciones.
#
#  ESTRUCTURA VISUAL:
#    ┌──────────────────────────────────────────┐
#    │  Parámetros EUREF                        │
#    │    Límite AGD tipo A (mGy)  [ 2,0 ]      │
#    │    Límite AGD tipo B (mGy)  [ 2,5 ]      │
#    │    ...                                   │
#    ├──────────────────────────────────────────┤
#    │  Integraciones                           │
#    │    🔵 PACS — Sectra IDS7     [Conectado] │
#    │    🟢 RIS  — Carestream Vue  [Conectado] │
#    │    ⚪ HIS  — Cerner           [Inactivo]  │
#    └──────────────────────────────────────────┘
#
#  ATRIBUTOS PÚBLICOS (leer desde ConfigController al guardar):
#    euref_inputs   → dict { nombre_param: QLineEdit }
#
#  MÉTODOS DE DATOS (llamar desde ConfigController):
#    populate_euref_params(params)       → carga los valores guardados en los inputs
#    populate_integrations(integrations) → actualiza los badges de estado de cada sistema
# ══════════════════════════════════════════════════════════════════════════════

class ViewConfig(QWidget):

    # Nombres exactos de los parámetros EUREF — usados como claves en euref_inputs
    # y en el dict que recibe populate_euref_params()
    EUREF_PARAM_NAMES = [
        "Límite AGD tipo A (mGy)",                  # Límite máximo de dosis para densidad tipo A
        "Límite AGD tipo B (mGy)",                  # Límite máximo de dosis para densidad tipo B
        "Límite AGD tipo C (mGy)",                  # Límite máximo de dosis para densidad tipo C
        "Límite AGD tipo D (mGy)",                  # Límite máximo de dosis para densidad tipo D
        "Umbral alerta (% pacientes sobre límite)",  # % máximo aceptable de pacientes fuera de límite
    ]

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet("background:transparent;")
        main = QVBoxLayout(self)
        main.setContentsMargins(20, 20, 20, 20)
        main.setSpacing(16)

        # ── SECCIÓN 1: Parámetros EUREF editables ─────────────────────────
        # Campos de texto para modificar los límites de dosis y el umbral de alerta.
        # Estos valores determinan qué pacientes se marcan como "Revisar" en ViewDosis
        # y qué alertas se generan en ViewResumen.
        #
        # Para cargar los valores guardados al arrancar:
        #   view.populate_euref_params(config_controller.get_euref_params())
        #
        # Para leer los valores al guardar (desde un botón "Guardar" futuro):
        #   value = view.euref_inputs["Límite AGD tipo A (mGy)"].text()
        euref_panel = Panel("Parámetros EUREF")
        self.euref_inputs = {}   # dict { nombre_param: QLineEdit } expuesto al controller

        for param_name in self.EUREF_PARAM_NAMES:
            row = QWidget()
            row.setStyleSheet("background:transparent;")
            rl = QHBoxLayout(row)
            rl.setContentsMargins(12, 6, 6, 6)
            rl.setSpacing(12)

            # Nombre del parámetro a la izquierda
            rl.addWidget(label(param_name, 12, COLORS["text_primary"]), 1)

            # Campo de entrada numérica a la derecha
            # Se rellena con populate_euref_params() al arrancar la vista
            val_input = QLineEdit()
            val_input.setFixedSize(80, 28)
            val_input.setAlignment(Qt.AlignCenter)
            val_input.setStyleSheet(
                f"QLineEdit {{ background:{COLORS['bg_secondary']}; "
                "border:0.5px solid rgba(0,0,0,0.18); border-radius:6px; "
                "font-size:12px; font-weight:600; color:#1a1a18; padding:0 8px; }}"
                "QLineEdit:focus { border-color:#185FA5; }"
            )
            rl.addWidget(val_input)
            self.euref_inputs[param_name] = val_input   # Expuesto para lectura desde controller
            euref_panel.body().addWidget(row)
            euref_panel.body().addWidget(separator())   # Línea separadora entre parámetros

        main.addWidget(euref_panel)

        # ── SECCIÓN 2: Estado de las integraciones externas ───────────────
        # Muestra el estado de conexión de cada sistema externo (PACS, RIS, HIS).
        # Los badges de estado se actualizan con populate_integrations().
        # Para añadir una nueva integración: añadir una tupla a integration_defs.
        integr_panel = Panel("Integraciones")
        self._integration_badges = {}   # dict { key: QLabel badge } para actualizar estados

        integration_defs = [
            ("pacs", "🔵", "PACS — Sectra IDS7",
             "Importación automática de imágenes DICOM"),
            # Sistema de almacenamiento y comunicación de imágenes

            ("ris",  "🟢", "RIS — Carestream Vue",
             "Exportación de informes al sistema RIS"),
            # Sistema de información radiológica para gestión de informes

            ("his",  "⚪", "HIS — Cerner Millennium",
             "Integración con historia clínica"),
            # Sistema de información hospitalaria para historia clínica del paciente
        ]

        for key, icon, name, desc in integration_defs:
            row = QWidget()
            row.setStyleSheet(
                f"background:{COLORS['bg_primary']}; border-radius:8px; "
                "border:0.5px solid rgba(0,0,0,0.08);"
            )
            rl = QHBoxLayout(row)
            rl.setContentsMargins(14, 12, 14, 12)
            rl.setSpacing(14)

            # Icono identificador del sistema
            ico = label(icon, 20, "#000")
            ico.setFixedWidth(36)
            rl.addWidget(ico)

            # Nombre y descripción del sistema
            col = QWidget()
            col.setStyleSheet("background:transparent; padding-left: 10px;")
            cv = QVBoxLayout(col)
            cv.setContentsMargins(0, 0, 0, 0)
            cv.setSpacing(2)
            cv.addWidget(label(name, 13, COLORS["text_primary"], "bold"))
            cv.addWidget(label(desc, 11, COLORS["text_tertiary"]))
            rl.addWidget(col, 1)

            # Badge de estado: se actualiza con populate_integrations()
            # Valores típicos: "Conectado" (green) / "Inactivo" (gray) / "Error" (coral)
            bdg = badge("—", "gray")   # Arranca vacío hasta populate_integrations()
            rl.addWidget(bdg)
            self._integration_badges[key] = bdg
            integr_panel.body().addWidget(row)

        main.addWidget(integr_panel)
        main.addStretch()

    # ══════════════════════════════════════════════════════════════════════
    #  MÉTODOS DE DATOS — Llamar desde ConfigController
    # ══════════════════════════════════════════════════════════════════════

    def populate_euref_params(self, params: dict):
        """
        ── PUNTO DE ENTRADA DE DATOS ──────────────────────────────────────
        Carga los valores guardados en los campos de parámetros EUREF.
        Llamar al arrancar la vista para mostrar la configuración actual.

        params: dict { nombre_param: valor_str }

        Ejemplo:
            view.populate_euref_params({
                "Límite AGD tipo A (mGy)": "2,0",
                "Límite AGD tipo B (mGy)": "2,5",
                "Límite AGD tipo C (mGy)": "3,0",
                "Límite AGD tipo D (mGy)": "3,5",
                "Umbral alerta (% pacientes sobre límite)": "10%",
            })

        Fuente de datos recomendada: archivo JSON de configuración o base de datos.
        """
        for name, widget in self.euref_inputs.items():
            if name in params:
                widget.setText(params[name])

    def populate_integrations(self, integrations: dict):
        """
        ── PUNTO DE ENTRADA DE DATOS ──────────────────────────────────────
        Actualiza los badges de estado de cada integración.
        Llamar al arrancar la vista y también periódicamente si se hacen ping a los sistemas.

        integrations: dict { key: {"active": bool, "label": str} }
            Keys esperadas: "pacs", "ris", "his"

        Ejemplo:
            view.populate_integrations({
                "pacs": {"active": True,  "label": "Conectado"},
                "ris":  {"active": True,  "label": "Conectado"},
                "his":  {"active": False, "label": "Inactivo"},
            })

        Para un estado de error añadir: {"active": False, "label": "Error de conexión"}
        y cambiar el estilo del badge a "coral" si es necesario.
        """
        for key, bdg in self._integration_badges.items():
            info = integrations.get(key, {})
            active = info.get("active", False)
            lbl_text = info.get("label", "—")
            style = "green" if active else "gray"
            bdg.setText(lbl_text)
            styles = {
                "green": "background:#EAF3DE; color:#3B6D11;",
                "gray":  "background:#f0ede8; color:#5f5e5a;",
            }
            bdg.setStyleSheet(
                f"{styles[style]} font-size:10px; font-weight:600; "
                "padding:2px 8px; border-radius:99px; border:none;"
            )