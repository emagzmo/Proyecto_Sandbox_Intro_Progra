"""Animal terrestre con forma de cuadrúpedo (cuerpo, cabeza con ojo y patas).

La forma ocupa una caja de 3 filas x 5 columnas y se voltea según hacia
dónde camina. Cada parte tiene su código en la matriz (11 cuerpo, 13 cabeza,
14 ojo, 15 patas). Reglas: se mueve solo (inicia hacia la derecha y rebota en
bordes y obstáculos), cae por gravedad, no entra al agua, no atraviesa
sólidos y nunca sale de la matriz. Opcionales: come plantas y muere con fuego.
"""
from constantes import *

# (fila, columna, código) mirando a la derecha dentro de la caja 3 x 5
FORMA = [
    (0, 1, ANIMAL), (0, 2, ANIMAL), (0, 3, ANIMAL_CABEZA), (0, 4, ANIMAL_OJO),
    (1, 0, ANIMAL), (1, 1, ANIMAL), (1, 2, ANIMAL), (1, 3, ANIMAL_CABEZA), (1, 4, ANIMAL_CABEZA),
    (2, 1, ANIMAL_PATA), (2, 3, ANIMAL_PATA),
]


class Animal:
    ALTO = 3
    ANCHO = 5

    def __init__(self, fila, col, direccion=1, contador=0):
        self.fila = fila        # fila de la esquina superior izquierda de la caja
        self.col = col
        self.direccion = direccion  # 1 = derecha, -1 = izquierda
        self.contador = contador

    # ---- utilidades ----
    def celdas(self, fila=None, col=None, direccion=None):
        """Lista de (fila, col, código) de las casillas que ocupa."""
        fila = self.fila if fila is None else fila
        col = self.col if col is None else col
        direccion = self.direccion if direccion is None else direccion
        return [(fila + i, col + (j if direccion == 1 else self.ANCHO - 1 - j), cod)
                for i, j, cod in FORMA]

    def intacto(self, mundo):
        return all(mundo.matriz[f][c] == cod for f, c, cod in self.celdas())

    def borrar(self, mundo):
        for f, c, _ in self.celdas():
            if mundo.dentro(f, c) and mundo.matriz[f][c] in CODIGOS_ANIMAL:
                mundo.matriz[f][c] = AIRE

    def _poner(self, mundo, fila, col, direccion):
        self.borrar(mundo)
        self.fila, self.col, self.direccion = fila, col, direccion
        for f, c, cod in self.celdas():
            mundo.matriz[f][c] = cod

    def _en_peligro(self, mundo):
        propias = {(f, c) for f, c, _ in self.celdas()}
        for f, c in propias:
            for nf, nc in ((f - 1, c), (f + 1, c), (f, c - 1), (f, c + 1)):
                if (nf, nc) not in propias and mundo.dentro(nf, nc) \
                        and mundo.matriz[nf][nc] == FUEGO:
                    return True
        return False

    def _destino_valido(self, mundo, fila, col, direccion):
        """Destino dentro de la matriz, libre y con suelo seguro (no agua ni fuego)."""
        n, m = mundo.n, mundo.matriz
        destino = self.celdas(fila, col, direccion)
        propias = {(f, c) for f, c, _ in self.celdas()}
        pos = {(f, c) for f, c, _ in destino}
        for f, c in pos:
            if not (0 <= f < n and 0 <= c < n):
                return False
            if (f, c) not in propias and m[f][c] != AIRE:
                return False
        # Casillas que quedan justo debajo del cuerpo (los apoyos)
        apoyos = [(f + 1, c) for f, c in pos if (f + 1, c) not in pos]
        while True:
            if any(f >= n for f, c in apoyos):
                return True                      # llegaría al piso del mundo
            ocupados = [m[f][c] for f, c in apoyos
                        if m[f][c] != AIRE and (f, c) not in propias]   # su cuerpo actual no cuenta
            if ocupados:
                return not all(v in (AGUA, FUEGO) for v in ocupados)
            apoyos = [(f + 1, c) for f, c in apoyos]   # caería una casilla más

    # ---- comportamiento ----
    def paso(self, mundo):
        """Devuelve False si el animal murió."""
        n, m = mundo.n, mundo.matriz
        if ANIMAL_MUERE_FUEGO and self._en_peligro(mundo):
            self.borrar(mundo)
            return False

        propias = {(f, c) for f, c, _ in self.celdas()}
        # Gravedad: cae si ninguna casilla de apoyo tiene algo debajo
        apoyos = [(f + 1, c) for f, c in propias if (f + 1, c) not in propias]
        if all(f < n and m[f][c] == AIRE for f, c in apoyos):
            self._poner(mundo, self.fila + 1, self.col, self.direccion)
            return True

        self.contador += 1
        if self.contador % VELOCIDAD_ANIMAL != 0:
            return True

        d = self.direccion
        nc = self.col + d
        if nc < 0 or nc + self.ANCHO > n:
            self._girar(mundo)
            return True

        if ANIMAL_COME_PLANTAS:
            for f, c in propias:
                if (f, c + d) not in propias and mundo.dentro(f, c + d) \
                        and m[f][c + d] in CODIGOS_PLANTA:
                    mundo.eliminar_planta(f, c + d)

        if self._destino_valido(mundo, self.fila, nc, d):
            self._poner(mundo, self.fila, nc, d)
        elif self._destino_valido(mundo, self.fila - 1, nc, d):    # trepa 1 casilla
            self._poner(mundo, self.fila - 1, nc, d)
        else:
            self._girar(mundo)                                     # obstáculo: da la vuelta
        return True

    def _girar(self, mundo):
        nueva = -self.direccion
        if self._destino_valido(mundo, self.fila, self.col, nueva):
            self._poner(mundo, self.fila, self.col, nueva)

    def a_dict(self):
        return {"fila": self.fila, "col": self.col,
                "direccion": self.direccion, "contador": self.contador}
