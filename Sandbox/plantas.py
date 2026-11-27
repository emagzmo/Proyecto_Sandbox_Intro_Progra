"""Plantas: crecimiento gradual en 3 etapas visualmente distintas.

Cada forma se define con tuplas (dx, dy, codigo) relativas a la base de la
planta; dy crece hacia arriba. El estado de cada planta (etapa, contador y
casillas) se guarda y se restaura junto con el mapa.
"""
from constantes import *

FORMAS = {
    # etapa 1: brote con dos hojitas
    1: [(0, 0, PLANTA_1), (-1, 1, PLANTA_1), (1, 1, PLANTA_1)],
    # etapa 2: tallo con hojas alternadas
    2: [(0, 0, PLANTA_2), (0, 1, PLANTA_2), (0, 2, PLANTA_2), (0, 3, PLANTA_2),
        (-1, 1, PLANTA_2), (1, 2, PLANTA_2), (-1, 3, PLANTA_2)],
    # etapa 3: árbol con tronco, copa redonda y flores
    3: [(0, 0, TRONCO), (0, 1, TRONCO), (0, 2, TRONCO), (0, 3, TRONCO),
        (-2, 4, PLANTA_3), (-1, 4, PLANTA_3), (0, 4, PLANTA_3), (1, 4, FLOR), (2, 4, PLANTA_3),
        (-2, 5, PLANTA_3), (-1, 5, FLOR), (0, 5, PLANTA_3), (1, 5, PLANTA_3), (2, 5, PLANTA_3),
        (-1, 6, PLANTA_3), (0, 6, FLOR), (1, 6, PLANTA_3)],
}


class Planta:
    def __init__(self, fila, col, etapa=1, contador=0, celdas=None):
        self.fila = fila          # fila de la base
        self.col = col            # columna de la base
        self.etapa = etapa
        self.contador = contador  # pasos acumulados en la etapa actual
        self.celdas = celdas if celdas is not None else self.celdas_de_etapa(etapa)

    def celdas_de_etapa(self, etapa):
        """Lista de (fila, col, codigo) de la forma de una etapa."""
        return [(self.fila - dy, self.col + dx, cod) for dx, dy, cod in FORMAS[etapa]]

    def completa(self):
        return len(self.celdas) == len(FORMAS[self.etapa])

    def paso(self, mundo):
        """Un paso de crecimiento. Se detiene en la etapa máxima o sin espacio."""
        if self.etapa >= ETAPA_MAXIMA or not self.completa():
            return
        self.contador += 1
        if self.contador < TICKS_POR_ETAPA:
            return
        nuevas = self.celdas_de_etapa(self.etapa + 1)
        propias = {(f, c) for f, c, _ in self.celdas}
        for f, c, _ in nuevas:
            if not mundo.dentro(f, c):
                return                                  # sin espacio (borde)
            if (f, c) not in propias and mundo.matriz[f][c] != AIRE:
                return                                  # sin espacio (obstáculo)
        nuevas_pos = {(f, c) for f, c, _ in nuevas}
        for f, c, cod in self.celdas:            # limpia casillas que ya no forman parte
            if (f, c) not in nuevas_pos and mundo.matriz[f][c] == cod:
                mundo.matriz[f][c] = AIRE
        for f, c, cod in nuevas:
            mundo.matriz[f][c] = cod
        self.celdas = nuevas
        self.etapa += 1
        self.contador = 0

    def a_dict(self):
        return {"fila": self.fila, "col": self.col, "etapa": self.etapa,
                "contador": self.contador,
                "celdas": [[f, c, cod] for f, c, cod in self.celdas]}
