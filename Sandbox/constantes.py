"""Constantes globales del simulador Sandbox de Elementos.

Códigos de la matriz (la matriz es la fuente de verdad del mundo):
    0 Aire | 1 Arena | 2 Agua | 3 Piedra | 4 Tierra | 5 Fuego | 6 Semilla
    7 Pasto | 8, 9, 10 Planta (etapas 1, 2, 3) | 11 Animal terrestre
    Códigos extra (documentados): 12 Tronco y 16 Flor (planta, etapa 3);
    13 Cabeza, 14 Ojo y 15 Pata (partes del animal)
"""

# --- Códigos de elementos ---
AIRE = 0
ARENA = 1
AGUA = 2
PIEDRA = 3
TIERRA = 4
FUEGO = 5
SEMILLA = 6
PASTO = 7
PLANTA_1 = 8
PLANTA_2 = 9
PLANTA_3 = 10
ANIMAL = 11
TRONCO = 12          # extra: tronco de la planta (etapa 3)
ANIMAL_CABEZA = 13   # extra: cabeza del animal
ANIMAL_OJO = 14      # extra: ojo del animal
ANIMAL_PATA = 15     # extra: patas del animal
FLOR = 16            # extra: flores de la planta (etapa 3)

NOMBRES = {
    AIRE: "Aire", ARENA: "Arena", AGUA: "Agua", PIEDRA: "Piedra",
    TIERRA: "Tierra", FUEGO: "Fuego", SEMILLA: "Semilla", PASTO: "Pasto",
    PLANTA_1: "Planta (etapa 1)", PLANTA_2: "Planta (etapa 2)",
    PLANTA_3: "Planta (etapa 3)", ANIMAL: "Animal", TRONCO: "Tronco",
    ANIMAL_CABEZA: "Animal (cabeza)", ANIMAL_OJO: "Animal (ojo)",
    ANIMAL_PATA: "Animal (pata)", FLOR: "Flor",
}

CODIGOS_VALIDOS = set(NOMBRES.keys())
CODIGOS_PLANTA = {PLANTA_1, PLANTA_2, PLANTA_3, TRONCO, FLOR}
CODIGOS_ANIMAL = {ANIMAL, ANIMAL_CABEZA, ANIMAL_OJO, ANIMAL_PATA}

# Materiales que el fuego puede quemar
INFLAMABLES = {PASTO, SEMILLA, PLANTA_1, PLANTA_2, PLANTA_3, TRONCO, FLOR}
# Materiales sobre los que puede apoyarse una planta
SOLIDOS_SOPORTE = {PIEDRA, TIERRA, PASTO, ARENA}

# --- Tamaño del mundo ---
N_MIN = 20
N_MAX = 100
N_INICIAL = 40
TAM_LIENZO = 640  # píxeles aproximados del lado del lienzo

# --- Parámetros de la simulación ---
PROB_HUMEDAD = 0.25          # tierra + agua -> pasto
PROB_GERMINACION = 0.05      # semilla sobre pasto -> planta
PROB_PROPAGACION = 0.50      # fuego -> material inflamable vecino
FUEGO_VIDA_AIRE = (3, 6)     # duración del fuego sobre aire
FUEGO_VIDA_MATERIAL = (6, 10)  # duración del fuego sobre material inflamable
TICKS_POR_ETAPA = 40         # pasos entre etapas de crecimiento de una planta
ETAPA_MAXIMA = 3
VELOCIDAD_ANIMAL = 3         # el animal se mueve cada 3 pasos
ANIMAL_COME_PLANTAS = True   # funcionalidad opcional
ANIMAL_MUERE_FUEGO = True    # funcionalidad opcional

VERSION_ARCHIVO = 1
