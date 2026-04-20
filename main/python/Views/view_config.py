
from PySide6.QtWidgets import (
   QWidget, QHBoxLayout, QVBoxLayout,QLineEdit
)

from PySide6.QtCore import Qt


from main.python.Views.colors import COLORS
from main.python.Views.utils import Panel, badge, label, separator

class ViewConfig(QWidget):
    """
    Vista de configuración.

    DATOS NECESARIOS (populate_*)
    ───────────────────────────────────────────────────────────────────────
    populate_euref_params(params)      ← Parámetros EUREF editables
    populate_integrations(integrations)← Estado de las integraciones

    SEÑALES INTERNAS
    ───────────────────────────────────────────────────────────────────────
    Los QLineEdit de parámetros EUREF se exponen en:
        view.euref_inputs   → dict { "Límite AGD tipo A (mGy)": QLineEdit, ... }

    Para guardar cambios conecta al controller:
        save_btn.clicked.connect(ctrl.on_save_config)
        ... y lee view.euref_inputs["Límite AGD tipo A (mGy)"].text()
    """

    EUREF_PARAM_NAMES = [
        "Límite AGD tipo A (mGy)",
        "Límite AGD tipo B (mGy)",
        "Límite AGD tipo C (mGy)",
        "Límite AGD tipo D (mGy)",
        "Umbral alerta (% pacientes sobre límite)",
    ]

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet("background:transparent;")
        main = QVBoxLayout(self)
        main.setContentsMargins(20, 20, 20, 20)
        main.setSpacing(16)

        # ── Parámetros EUREF ──────────────────────────────────────────────
        euref_panel = Panel("Parámetros EUREF")
        self.euref_inputs = {}

        for param_name in self.EUREF_PARAM_NAMES:
            row = QWidget()
            row.setStyleSheet("background:transparent;")
            rl = QHBoxLayout(row)
            rl.setContentsMargins(12, 6, 6, 6)
            rl.setSpacing(12)
            rl.addWidget(label(param_name, 12, COLORS["text_primary"]), 1)

            val_input = QLineEdit()    # Sin valor por defecto — se rellena con populate_euref_params()
            val_input.setFixedSize(80, 28)
            val_input.setAlignment(Qt.AlignCenter)
            val_input.setStyleSheet(
                f"QLineEdit {{ background:{COLORS['bg_secondary']}; "
                "border:0.5px solid rgba(0,0,0,0.18); border-radius:6px; "
                "font-size:12px; font-weight:600; color:#1a1a18; padding:0 8px; }}"
                "QLineEdit:focus { border-color:#185FA5; }"
            )
            rl.addWidget(val_input)
            self.euref_inputs[param_name] = val_input
            euref_panel.body().addWidget(row)
            euref_panel.body().addWidget(separator())

        main.addWidget(euref_panel)

        # ── Integraciones ─────────────────────────────────────────────────
        integr_panel = Panel("Integraciones")
        self._integration_badges = {}

        integration_defs = [
            ("pacs", "🔵", "PACS — Sectra IDS7",     "Importación automática de imágenes DICOM"),
            ("ris",  "🟢", "RIS — Carestream Vue",    "Exportación de informes al sistema RIS"),
            ("his",  "⚪", "HIS — Cerner Millennium", "Integración con historia clínica"),
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

            ico = label(icon, 20, "#000")
            ico.setFixedWidth(36)
            rl.addWidget(ico)

            col = QWidget()
            col.setStyleSheet("background:transparent; padding-left: 10px;")
            cv = QVBoxLayout(col)
            cv.setContentsMargins(0, 0, 0, 0)
            cv.setSpacing(2)
            cv.addWidget(label(name, 13, COLORS["text_primary"], "bold"))
            cv.addWidget(label(desc, 11, COLORS["text_tertiary"]))
            rl.addWidget(col, 1)

            bdg = badge("—", "gray")
            rl.addWidget(bdg)
            self._integration_badges[key] = bdg
            integr_panel.body().addWidget(row)

        main.addWidget(integr_panel)
        main.addStretch()

    # ── MÉTODOS PÚBLICOS ───────────────────────────────────────────────────

    def populate_euref_params(self, params: dict):
        """
        Rellena los campos de parámetros EUREF.

        Parámetros
        ----------
        params : dict  { nombre_param: valor_str }

            Ejemplo:
                params = {
                    "Límite AGD tipo A (mGy)": "2,0",
                    "Límite AGD tipo B (mGy)": "2,5",
                    "Límite AGD tipo C (mGy)": "3,0",
                    "Límite AGD tipo D (mGy)": "3,5",
                    "Umbral alerta (% pacientes sobre límite)": "10%",
                }
                view.populate_euref_params(params)

        Cómo obtener los datos:
            Carga los valores desde un JSON/DB en ConfigController
            y llama a este método al arrancar la vista.
        """
        for name, widget in self.euref_inputs.items():
            if name in params:
                widget.setText(params[name])

    def populate_integrations(self, integrations: dict):
        """
        Actualiza los badges de estado de cada integración.

        Parámetros
        ----------
        integrations : dict  { key: {"active": bool, "label": str} }
            Keys esperadas: "pacs", "ris", "his"

            Ejemplo:
                integrations = {
                    "pacs": {"active": True,  "label": "Conectado"},
                    "ris":  {"active": True,  "label": "Conectado"},
                    "his":  {"active": False, "label": "Inactivo"},
                }
                view.populate_integrations(integrations)
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
