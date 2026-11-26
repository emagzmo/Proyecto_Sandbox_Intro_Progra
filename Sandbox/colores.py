"""Paleta de colores de cada elemento (3 tonos por código para dar textura)."""
from constantes import *

COLOR_BASE = {
    AIRE: "#87CEEB", ARENA: "#E8CF8A", AGUA: "#2F7FE0", PIEDRA: "#7D7F85",
    TIERRA: "#7A4B2A", FUEGO: "#FF8A00", SEMILLA: "#2E1A0C", PASTO: "#4CAF50",
    PLANTA_1: "#B6F06A", PLANTA_2: "#38B24A", PLANTA_3: "#1B7A2E",
    ANIMAL: "#B5733A", TRONCO: "#6B4423",
    ANIMAL_CABEZA: "#8B5A2B", ANIMAL_OJO: "#111111", ANIMAL_PATA: "#5A3A1E",
    FLOR: "#FF6FB5",
}


def ajustar(color, delta):
    """Aclara (delta > 0) u oscurece (delta < 0) un color #rrggbb."""
    r, g, b = (int(color[i:i + 2], 16) for i in (1, 3, 5))
    r, g, b = (max(0, min(255, v + delta)) for v in (r, g, b))
    return "#%02x%02x%02x" % (r, g, b)


def texto_para(color):
    """Color de texto legible (negro o blanco) sobre un fondo dado."""
    r, g, b = (int(color[i:i + 2], 16) for i in (1, 3, 5))
    return "black" if (0.299 * r + 0.587 * g + 0.114 * b) > 140 else "white"


PALETA = {cod: [c, ajustar(c, 14), ajustar(c, -14)] for cod, c in COLOR_BASE.items()}
PALETA[AIRE] = ["#87CEEB", "#87CEEB", "#87CEEB"]
PALETA[FUEGO] = ["#FF8A00", "#FFC400", "#E63B00"]