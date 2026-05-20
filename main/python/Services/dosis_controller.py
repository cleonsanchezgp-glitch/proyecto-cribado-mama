from statistics import mean, quantiles
from main.python.Views.view_dosis import ViewDosis
from main.python.Models.Paciente import Paciente

class dosis_controller:
    def __init__(self, view: ViewDosis, pacientes: list[Paciente]):
        self.view = view
        self.pacientes = pacientes
        self.cargar_datos_en_pantalla()

    # Métodos Auxiliares

    def _tipo_densidad(self, espesor: int) -> int:
        """
        Convierte el espesor de mama (mm) al índice de tipo de densidad:
            0 = Tipo A (verde)   → espesor < 40mm
            1 = Tipo B (azul)    → 40mm ≤ espesor < 60mm
            2 = Tipo C (naranja) → 60mm ≤ espesor < 75mm
            3 = Tipo D (rojo)    → espesor ≥ 75mm
        """
        if espesor < 40:
            return 0
        elif espesor < 60:
            return 1
        elif espesor < 75:
            return 2
        else:
            return 3

    def _obtener_todas_dosis(self) -> list[float]:
        """Devuelve una lista plana con todas las dosis_glandular de todos los estudios."""
        dosis = []
        for paciente in self.pacientes:
            for estudio in paciente.estudios:
                dosis.append(estudio.dosis_glandular)
        return dosis

    #  Métodos de cálculo

    def get_stats(self) -> list[str]:
        """
        Calcula AGD media, percentil 75 y percentil 95 de todas las dosis.
        Devuelve lista de 3 strings formateados para populate_stats().
        """
        dosis = self._obtener_todas_dosis()
        if len(dosis) < 2:
            return ["—", "—", "—"]

        media = mean(dosis)

        # quantiles devuelve 99 valores (percentiles 1-99)
        percentiles = quantiles(dosis, n=100)
        p75 = percentiles[74]   # índice 74 = percentil 75
        p95 = percentiles[94]   # índice 94 = percentil 95

        return [
            f"{media:.2f} mGy",
            f"{p75:.2f} mGy",
            f"{p95:.2f} mGy",
        ]

    def get_scatter_points(self) -> list[tuple]:
        """
        Construye la lista de puntos para el scatter plot.
        Formato: [(espesor, dosis_glandular, tipo_densidad_idx), ...]
        Un punto por cada estudio de cada paciente.
        """
        puntos = []
        for paciente in self.pacientes:
            for estudio in paciente.estudios:
                espesor = paciente.espesor_mama_actual
                agd = estudio.dosis_glandular
                tipo = self._tipo_densidad(espesor)
                puntos.append((espesor, agd, tipo))
        return puntos

    def get_cumplimiento_euref(self) -> list[dict]:
        """
        Calcula el cumplimiento EUREF por tipo de densidad (A/B/C/D).
        Un estudio cumple EUREF si su dosis_glandular está dentro del límite
        de referencia según el espesor.

        Límites EUREF aproximados por espesor:
            Tipo A (< 40mm)   → límite 1.0 mGy
            Tipo B (40-60mm)  → límite 2.5 mGy
            Tipo C (60-75mm)  → límite 4.0 mGy
            Tipo D (≥ 75mm)   → límite 6.5 mGy

        Devuelve lista de 4 dicts para populate_compliance().
        """
        # Límite de referencia EUREF por tipo
        limites_euref = {0: 2.0, 1: 2.5, 2: 3.0, 3: 4.0}
        nombres = ["Tipo A", "Tipo B", "Tipo C", "Tipo D"]

        # Contadores por tipo: [total, dentro_limite]
        contadores = {0: [0, 0], 1: [0, 0], 2: [0, 0], 3: [0, 0]}

        for paciente in self.pacientes:
            for estudio in paciente.estudios:
                tipo = self._tipo_densidad(paciente.espesor_mama_actual)
                contadores[tipo][0] += 1  # total
                if estudio.dosis_glandular <= limites_euref[tipo]:
                    contadores[tipo][1] += 1  # dentro del límite

        resultado = []
        for tipo in range(4):
            total, dentro = contadores[tipo]
            if total == 0:
                proporcion = 0.0
                pct_texto = "—"
            else:
                proporcion = dentro / total
                pct_texto = f"{proporcion * 100:.1f}%"

            # Determinar color según cumplimiento
            if proporcion >= 0.90:
                style = "green"
            elif proporcion >= 0.75:
                style = "amber"
            else:
                style = "coral"

            resultado.append({
                "proportion": proporcion,
                "pct_text": pct_texto,
                "style": style
            })

        return resultado

    #  Método Principal

    def cargar_datos_en_pantalla(self):
        self.view.populate_stats(self.get_stats())
        self.view.populate_scatter(self.get_scatter_points())
        self.view.populate_compliance(self.get_cumplimiento_euref())