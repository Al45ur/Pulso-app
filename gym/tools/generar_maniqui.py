#!/usr/bin/env python3
"""Genera el personaje 3D de la app: Pulso/Resources/maniqui.json + maniqui.bin.

- La piel de cada segmento del cuerpo es una malla suave construida por "loft": una pila de secciones
  elípticas a lo largo de un eje, remuestreada con splines para que la superficie sea lisa.
- Cada músculo es una "capa": se recorta de la propia malla de la piel y se eleva con un perfil suave,
  así sigue exactamente la curvatura del cuerpo y se puede teñir sin tocar la piel.

Todas las mallas están en el sistema de su articulación (origen en la articulación, extremidades hacia -y,
el personaje mira a +z, +x = su izquierda), el mismo que usa Maniqui.swift: la app solo cuelga cada malla
del nodo de su articulación.

Uso:  python3 gym/tools/generar_maniqui.py
Depende solo de numpy. Las medidas de los huesos deben coincidir con Medidas.swift.
"""
import json
from pathlib import Path

import numpy as np

N = 64          # puntos por sección
PASO = 0.008    # separación entre anillos tras el remuestreo (m)
FRACCION_RELIEVE = 0.6   # parte de la altura de cada músculo que se modela en la propia piel
ESCALA_RELIEVE = 1.35    # exagera un poco el relieve para que se lea a distancia de teléfono


# --- Mallas ----------------------------------------------------------------------------
class Malla:
    def __init__(self, v, f):
        self.v = np.asarray(v, dtype=np.float64)
        self.f = np.asarray(f, dtype=np.int64)


def unir(mallas):
    vs, fs, base = [], [], 0
    for m in mallas:
        vs.append(m.v)
        fs.append(m.f + base)
        base += len(m.v)
    return Malla(np.vstack(vs), np.vstack(fs))


def espejo(m):
    """Refleja en x (izquierda <-> derecha) y corrige el orden de los triángulos."""
    return Malla(m.v * np.array([-1.0, 1.0, 1.0]), m.f[:, ::-1])


def volumen(m):
    a, b, c = m.v[m.f[:, 0]], m.v[m.f[:, 1]], m.v[m.f[:, 2]]
    return float(np.sum(np.einsum("ij,ij->i", a, np.cross(b, c))) / 6.0)


def normales(m):
    a, b, c = m.v[m.f[:, 0]], m.v[m.f[:, 1]], m.v[m.f[:, 2]]
    cara = np.cross(b - a, c - a)  # ponderada por el área
    n = np.zeros_like(m.v)
    for i in range(3):
        np.add.at(n, m.f[:, i], cara)
    largo = np.linalg.norm(n, axis=1, keepdims=True)
    largo[largo == 0] = 1
    return n / largo


def _coord(eje, t, u, w):
    if eje == "y":
        return (u, t, w)   # sección en (x, z)
    if eje == "x":
        return (t, u, w)   # sección en (y, z)
    return (u, w, t)       # eje z: sección en (x, y)


def remuestrear(secciones, paso):
    """Interpola las secciones con splines de Catmull-Rom (no uniformes) cada `paso` metros."""
    s = np.array(secciones, dtype=float)               # (k, 5): t, a, b, ra, rb
    k = len(s)
    param = np.concatenate([[0], np.cumsum(np.abs(np.diff(s[:, 0])))])
    total = param[-1]
    destino = np.linspace(0, total, max(int(np.ceil(total / paso)) + 1, 2))
    tangentes = np.zeros_like(s)
    for i in range(k):
        a, b = max(i - 1, 0), min(i + 1, k - 1)
        tangentes[i] = (s[b] - s[a]) / (param[b] - param[a])
    salida = []
    for x in destino:
        i = min(int(np.searchsorted(param, x, side="right")) - 1, k - 2)
        h = param[i + 1] - param[i]
        u = (x - param[i]) / h
        h00, h10 = 2 * u**3 - 3 * u**2 + 1, u**3 - 2 * u**2 + u
        h01, h11 = -2 * u**3 + 3 * u**2, u**3 - u**2
        fila = h00 * s[i] + h10 * h * tangentes[i] + h01 * s[i + 1] + h11 * h * tangentes[i + 1]
        fila[3:] = np.maximum(fila[3:], 1e-3)
        salida.append(tuple(fila))
    return salida


def tubo(secciones, eje="y", p=2.2, n=N, paso=PASO):
    """secciones: [(t, a, b, ra, rb)]: posición a lo largo del eje, centro (a, b) y semiejes (ra, rb)."""
    if paso:
        secciones = remuestrear(secciones, paso)
    ang = np.linspace(0, 2 * np.pi, n, endpoint=False)
    c, s = np.cos(ang), np.sin(ang)
    ux = np.sign(c) * np.abs(c) ** (2 / p)
    uw = np.sign(s) * np.abs(s) ** (2 / p)
    v = []
    for (t, a, b, ra, rb) in secciones:
        for k in range(n):
            v.append(_coord(eje, t, a + ra * ux[k], b + rb * uw[k]))
    f = []
    ns = len(secciones)
    for i in range(ns - 1):
        for k in range(n):
            k2 = (k + 1) % n
            a0, a1, b0, b1 = i * n + k, i * n + k2, (i + 1) * n + k, (i + 1) * n + k2
            f += [(a0, a1, b1), (a0, b1, b0)]
    for i in (0, ns - 1):
        t, a, b, _, _ = secciones[i]
        centro = len(v)
        v.append(_coord(eje, t, a, b))
        for k in range(n):
            f.append((centro, i * n + k, i * n + (k + 1) % n))
    m = Malla(v, f)
    if volumen(m) < 0:  # que las caras miren hacia fuera
        m.f = m.f[:, ::-1]
    return m


def con_esferas(secciones, ini=False, fin=False):
    """Redondea los extremos con medio elipsoide; así dos segmentos giran sin dejar huecos."""
    secciones = list(secciones)
    sentido = np.sign(secciones[-1][0] - secciones[0][0]) or 1.0
    angulos = np.radians([78, 62, 46, 30, 14])

    def tapa(base, signo):
        t, a, b, ra, rb = base
        h = (ra + rb) / 2
        return [(t + signo * h * np.sin(q), a, b, max(ra * np.cos(q), 1e-3), max(rb * np.cos(q), 1e-3))
                for q in angulos]

    if ini:
        secciones = tapa(secciones[0], -sentido) + secciones
    if fin:
        secciones = secciones + tapa(secciones[-1], sentido)[::-1]
    return secciones


S = lambda t, a, b, ra, rb: (t, a, b, ra, rb)  # noqa: E731


def grueso(secciones, f):
    """Engrosa los radios de una lista de secciones (para dar más volumen a una extremidad)."""
    return [(t, a, b, ra * f, rb * f) for (t, a, b, ra, rb) in secciones]


# --- Piel ----------------------------------------------------------------------------------------
def pelvis():
    return tubo(con_esferas([
        S(0.07, 0, 0, 0.140, 0.096),
        S(0.02, 0, 0, 0.158, 0.110),
        S(-0.04, 0, -0.004, 0.164, 0.116),
        S(-0.09, 0, 0, 0.146, 0.104),
        S(-0.125, 0, 0.004, 0.100, 0.080),
    ], fin=True), p=2.4)


def torso():
    return tubo(con_esferas([
        S(-0.03, 0, 0, 0.145, 0.100),
        S(0.05, 0, 0, 0.140, 0.097),
        S(0.12, 0, 0, 0.142, 0.100),
        S(0.22, 0, 0.002, 0.166, 0.112),
        S(0.32, 0, 0.006, 0.184, 0.122),
        S(0.40, 0, 0.002, 0.180, 0.116),
        S(0.45, 0, -0.010, 0.145, 0.092),
        S(0.47, 0, -0.012, 0.075, 0.062),
    ], fin=True), p=2.5)


def cabeza():
    cuello = tubo(con_esferas([S(-0.05, 0, -0.004, 0.092, 0.070), S(-0.02, 0, 0, 0.066, 0.062), S(0.0, 0, 0, 0.054, 0.056), S(0.07, 0, 0, 0.050, 0.052)]), p=2.2)
    craneo = tubo(con_esferas([
        S(0.03, 0, 0, 0.050, 0.052),
        S(0.06, 0, 0.004, 0.052, 0.058),
        S(0.095, 0, 0.020, 0.064, 0.082),   # mandíbula
        S(0.13, 0, 0.012, 0.082, 0.096),
        S(0.17, 0, 0.004, 0.092, 0.106),
        S(0.20, 0, -0.002, 0.088, 0.100),
    ], fin=True), p=2.0)
    nariz = tubo(con_esferas([
        S(0.092, 0, 0.122, 0.004, 0.007),
        S(0.104, 0, 0.116, 0.008, 0.017),
        S(0.114, 0, 0.112, 0.010, 0.021),
        S(0.122, 0, 0.108, 0.007, 0.013),
    ], fin=True), eje="z", paso=0.004, n=24)
    oreja = tubo(con_esferas([
        S(0.078, 0.135, -0.004, 0.020, 0.011),
        S(0.086, 0.135, -0.004, 0.024, 0.013),
        S(0.094, 0.135, -0.002, 0.018, 0.008),
    ], fin=True), eje="x", paso=0.004, n=24)
    return unir([cuello, craneo, nariz, oreja, espejo(oreja)])


def ojo():
    # Esfera pequeña a la altura de los ojos (y ≈ 0.145 sobre el cuello), a la izquierda del personaje.
    esfera = tubo(con_esferas([S(-0.004, 0.034, 0.100, 0.007, 0.007), S(0.004, 0.034, 0.100, 0.007, 0.007)],
                              ini=True, fin=True), paso=0.002, n=20)
    esfera.v = esfera.v + np.array([0.0, 0.145, 0.0])
    return esfera


def brazo():
    return tubo(con_esferas(grueso([
        S(0.0, 0, 0, 0.054, 0.056),
        S(-0.06, 0, 0, 0.052, 0.054),
        S(-0.15, 0, 0, 0.046, 0.048),
        S(-0.25, 0, 0, 0.039, 0.041),
        S(-0.30, 0, 0, 0.037, 0.038),
    ], 1.14), ini=True, fin=True))


def antebrazo():
    codo_a_muneca = tubo(con_esferas(grueso([
        S(0.0, 0, 0, 0.037, 0.039),
        S(-0.06, 0, 0, 0.041, 0.043),
        S(-0.13, 0, 0, 0.036, 0.038),
        S(-0.21, 0, 0, 0.028, 0.032),
        S(-0.27, 0, 0, 0.025, 0.028),
    ], 1.10), ini=True))
    mano = tubo(con_esferas([
        S(-0.255, 0, 0, 0.026, 0.028),
        S(-0.295, 0, 0.002, 0.044, 0.020),
        S(-0.345, 0, 0.002, 0.042, 0.018),
        S(-0.385, 0, 0.002, 0.028, 0.015),
    ], fin=True), p=2.6)
    return unir([codo_a_muneca, mano])


def muslo():
    return tubo(con_esferas(grueso([
        S(0.0, 0, 0, 0.086, 0.090),
        S(-0.10, 0, 0, 0.088, 0.094),
        S(-0.20, 0, 0, 0.080, 0.086),
        S(-0.31, 0, 0, 0.064, 0.070),
        S(-0.42, 0, 0, 0.051, 0.055),
    ], 1.08), ini=True, fin=True))


def pantorrilla():
    return tubo(con_esferas(grueso([
        S(0.0, 0, 0, 0.051, 0.055),
        S(-0.09, 0, -0.012, 0.056, 0.064),   # gemelo
        S(-0.20, 0, -0.006, 0.048, 0.054),
        S(-0.33, 0, 0, 0.036, 0.040),
        S(-0.41, 0, 0, 0.032, 0.034),
    ], 1.06), ini=True, fin=True))


def zapatilla():
    """Zapatilla: la suela queda a -0.07 m del tobillo (Medidas.tobilloSuelo), como el pie anterior."""
    return tubo(con_esferas([
        S(-0.078, 0, -0.033, 0.036, 0.037),
        S(-0.040, 0, -0.030, 0.046, 0.040),
        S(0.020, 0, -0.036, 0.050, 0.034),
        S(0.100, 0, -0.042, 0.050, 0.028),
        S(0.160, 0, -0.050, 0.042, 0.020),
    ], fin=True), eje="z", p=2.6)


def short_pelvis():
    return tubo(con_esferas([
        S(0.092, 0, 0, 0.162, 0.118),
        S(0.074, 0, 0, 0.164, 0.120),
        S(0.020, 0, -0.004, 0.186, 0.146),
        S(-0.040, 0, -0.010, 0.192, 0.152),
        S(-0.095, 0, -0.004, 0.176, 0.136),
        S(-0.130, 0, 0.004, 0.130, 0.105),
    ], fin=True), p=2.4)


def short_pierna():
    return tubo([
        S(0.040, 0, -0.004, 0.118, 0.126),
        S(-0.060, 0, -0.004, 0.121, 0.130),
        S(-0.150, 0, 0, 0.114, 0.123),
        S(-0.225, 0, 0, 0.106, 0.114),
    ])


# --- Capas musculares --------------------------------------------------------------------------
def suave(x, a, b):
    """0 por debajo de a, 1 por encima de b, transición suave."""
    t = np.clip((x - a) / (b - a), 0.0, 1.0)
    return t * t * (3 - 2 * t)


def campana(x, centro, ancho):
    return np.clip(1 - ((x - centro) / ancho) ** 2, 0, 1) ** 0.8


def ventana(x, lo, hi, borde):
    return suave(x, lo, lo + borde) * (1 - suave(x, hi - borde, hi))


def evaluar(piel, mascara):
    n = normales(piel)
    x, y, z = piel.v[:, 0], piel.v[:, 1], piel.v[:, 2]
    return np.clip(mascara(x, y, z, n[:, 0], n[:, 1], n[:, 2]), 0, 1)


def simetrica(mascara):
    """Refleja una máscara definida a la izquierda para que valga en los dos lados de una pieza central."""
    return lambda x, y, z, nx, ny, nz: np.maximum(mascara(x, y, z, nx, ny, nz), mascara(-x, y, z, -nx, ny, nz))


def con_relieve(piel, reglas):
    """Modela los músculos en la propia piel: la desplaza hacia fuera según la suma de FRACCION_RELIEVE*altura*máscara.

    `reglas` es una lista de (máscara, altura). Así la piel muestra el relieve anatómico aunque no haya nada resaltado."""
    n = normales(piel)
    d = np.zeros(len(piel.v))
    for mascara, altura in reglas:
        d += FRACCION_RELIEVE * ESCALA_RELIEVE * altura * evaluar(piel, mascara)
    return Malla(piel.v + n * d[:, None], piel.f)


def capa(piel, mascara, altura, relieve=None, umbral=0.10, separacion=0.0012):
    """Recorta la zona donde mascara >= umbral y la eleva sobre la piel (con relieve, si se da).

    Los triángulos que cruzan el umbral se cortan por el punto exacto (interpolación lineal), así el contorno
    del músculo es liso y no depende de la resolución de la malla."""
    m = evaluar(piel, mascara)
    base = relieve if relieve is not None else piel
    n = normales(base)
    resto = (1 - FRACCION_RELIEVE) if relieve is not None else 1.0
    P = base.v + n * (separacion + resto * ESCALA_RELIEVE * altura * m)[:, None]
    f = piel.f

    verts, caras = [], []
    originales, cortes = {}, {}

    def original(i):
        if i not in originales:
            originales[i] = len(verts)
            verts.append(P[i])
        return originales[i]

    def corte(a, b):
        clave = (min(a, b), max(a, b))
        if clave not in cortes:
            lo, hi = clave
            t = (umbral - m[lo]) / (m[hi] - m[lo])
            cortes[clave] = len(verts)
            verts.append(P[lo] + (P[hi] - P[lo]) * t)
        return cortes[clave]

    for tri in f[m[f].max(axis=1) >= umbral]:
        poligono = []
        for a, b in ((tri[0], tri[1]), (tri[1], tri[2]), (tri[2], tri[0])):
            dentro_a, dentro_b = m[a] >= umbral, m[b] >= umbral
            if dentro_a:
                poligono.append(original(a))
            if dentro_a != dentro_b:
                poligono.append(corte(a, b))
        for k in range(1, len(poligono) - 1):
            caras.append((poligono[0], poligono[k], poligono[k + 1]))
    return Malla(verts, caras)


def fusiforme(direccion, y, centro, ancho, a0, a1):
    """Músculo en forma de huso: el ángulo cubierto se estrecha hacia los extremos y es máximo en el vientre."""
    vientre = campana(y, centro, ancho)
    return suave(direccion + 0.9 * (vientre - 1), a0, a1) * vientre


def musculos(piel):
    """{id: (pieza de piel, máscara(x,y,z,nx,ny,nz), altura)} en el sistema de la pieza (lado izquierdo)."""
    r = {}

    # Brazo (origen en el hombro; la cara posterior es -z)
    r["triceps"] = ("brazo", lambda x, y, z, nx, ny, nz:
                    fusiforme(-nz + 0.2 * nx, y, -0.155, 0.125, 0.40, 0.85), 0.013)
    r["biceps"] = ("brazo", lambda x, y, z, nx, ny, nz:
                   fusiforme(nz, y, -0.165, 0.11, 0.45, 0.88), 0.012)
    # Las tres cabezas del deltoides se reparten por el ángulo de la normal alrededor del brazo
    # (0° = lateral, +90° = frente, -90° = espalda), sin solaparse.
    def psi(nx, nz):
        return np.degrees(np.arctan2(nz, nx))

    r["deltoides_anterior"] = ("brazo", lambda x, y, z, nx, ny, nz:
                               campana(y, -0.035, 0.10) * suave(psi(nx, nz), 25, 45) * (1 - suave(psi(nx, nz), 115, 135)), 0.015)
    r["deltoides_lateral"] = ("brazo", lambda x, y, z, nx, ny, nz:
                              campana(y, -0.035, 0.10) * suave(psi(nx, nz), -45, -25) * (1 - suave(psi(nx, nz), 25, 45)), 0.016)
    r["deltoides_posterior"] = ("brazo", lambda x, y, z, nx, ny, nz:
                                campana(y, -0.035, 0.10) * suave(psi(nx, nz), -135, -115) * (1 - suave(psi(nx, nz), -45, -25)), 0.015)
    r["antebrazos"] = ("antebrazo", lambda x, y, z, nx, ny, nz:
                       campana(y, -0.095, 0.14) * (0.65 + 0.35 * suave(nx, -0.5, 0.6)), 0.010)
    # Tronco (origen en la columna)
    r["pectorales"] = ("torso", lambda x, y, z, nx, ny, nz:
                       suave(nz, 0.10, 0.55)
                       * suave(1 - (((x - 0.085) / 0.098) ** 2 + ((y - 0.345) / 0.068) ** 2), 0.0, 0.5), 0.017)
    # Abdomen con la línea alba y tres intersecciones tendinosas (los "cuadritos")
    r["abdomen"] = ("torso", lambda x, y, z, nx, ny, nz:
                    suave(nz, 0.35, 0.8)
                    * suave(1 - ((np.abs(x) / 0.072) ** 3 + (np.abs(y - 0.135) / 0.140) ** 3), 0.0, 0.3)
                    * (1 - 0.55 * np.exp(-(x / 0.007) ** 2))
                    * (1 - 0.45 * sum(np.exp(-((y - yk) / 0.008) ** 2) for yk in (0.06, 0.125, 0.19))), 0.011)
    r["dorsales"] = ("torso", lambda x, y, z, nx, ny, nz:
                     suave(-nz, 0.15, 0.65)
                     * suave(1 - np.abs(x) / np.clip(0.07 + (y - 0.04) * 0.34, 0.07, 0.17), 0.0, 0.35)
                     * ventana(y, 0.03, 0.38, 0.06), 0.014)
    r["trapecio"] = ("torso", lambda x, y, z, nx, ny, nz:
                     suave(1 - ((np.abs(x) / 0.14) ** 1.6 + (np.abs(y - 0.385) / 0.125) ** 1.6), 0.0, 0.45)
                     * suave(-nz + 0.35 * ny, 0.0, 0.5), 0.014)
    r["lumbar"] = ("torso", lambda x, y, z, nx, ny, nz:
                   suave(-nz, 0.30, 0.7) * campana(x, 0.050, 0.034) * ventana(y, -0.01, 0.22, 0.05), 0.011)
    r["gluteos"] = ("pelvis", lambda x, y, z, nx, ny, nz:
                    suave(-nz, 0.05, 0.5)
                    * suave(1 - (((x - 0.078) / 0.082) ** 2 + ((y + 0.040) / 0.088) ** 2), 0.0, 0.4), 0.023)
    # Pierna (origen en la cadera / rodilla)
    r["cuadriceps"] = ("muslo", lambda x, y, z, nx, ny, nz:
                       fusiforme(nz + 0.25 * nx, y, -0.225, 0.17, 0.35, 0.80), 0.014)
    r["isquiotibiales"] = ("muslo", lambda x, y, z, nx, ny, nz:
                           fusiforme(-nz, y, -0.235, 0.17, 0.40, 0.82), 0.013)
    r["aductores"] = ("muslo", lambda x, y, z, nx, ny, nz:
                      fusiforme(-nx, y, -0.17, 0.12, 0.45, 0.88), 0.012)
    r["gemelos"] = ("pantorrilla", lambda x, y, z, nx, ny, nz:
                    fusiforme(-nz, y, -0.125, 0.135, 0.35, 0.80), 0.016)
    return r


def relieves_extra():
    """Detalles de la piel que no son un músculo resaltable: clavículas y costillas/serrato."""
    return {
        "torso": [
            (lambda x, y, z, nx, ny, nz: suave(nz, 0.2, 0.6) * campana(y, 0.428, 0.020)
             * ventana(np.abs(x), 0.03, 0.17, 0.04), 0.006),
            (lambda x, y, z, nx, ny, nz: suave(np.abs(nx), 0.45, 0.85) * ventana(y, 0.08, 0.30, 0.05)
             * (0.55 + 0.45 * np.cos((y - 0.08) * 2 * np.pi / 0.048)), 0.007),
        ],
    }


# --- Ensamblado ---------------------------------------------------------------------------------
JUNTA_DE = {"brazo": "hombro", "antebrazo": "codo", "muslo": "cadera", "pantorrilla": "rodilla", "pie": "tobillo",
            "torso": "columna", "pelvis": "raiz", "cabeza": "cuello"}
PARES = {"brazo", "antebrazo", "muslo", "pantorrilla", "pie"}
SIMETRICOS_EN_TRONCO = {"pectorales", "lumbar", "gluteos"}   # se definen a la izquierda y se reflejan
CENTRALES = {"abdomen", "dorsales", "trapecio"}              # una sola malla centrada


def partes():
    """Lista de (nombre, junta, rol, músculo, malla). La junta es 'raiz' (pelvis) o un nombre de Articulacion.

    Roles: piel, ropa, calzado, ojos (colores del personaje) y musculo (capa que se resalta)."""
    pieles = {
        "pelvis": pelvis(), "torso": torso(), "cabeza": cabeza(), "brazo": brazo(), "antebrazo": antebrazo(),
        "muslo": muslo(), "pantorrilla": pantorrilla(),
    }
    reglas_musculos = musculos(pieles)

    # Relieve: cada pieza de piel se modela con los músculos que lleva encima.
    reglas = {nombre: [] for nombre in pieles}
    for musculo, (sobre, mascara, altura) in reglas_musculos.items():
        mascara_piel = simetrica(mascara) if musculo in SIMETRICOS_EN_TRONCO else mascara
        reglas[sobre].append((mascara_piel, altura))
    for sobre, extra in relieves_extra().items():
        reglas[sobre].extend(extra)
    reliefs = {nombre: (con_relieve(pieles[nombre], reglas[nombre]) if reglas[nombre] else pieles[nombre]) for nombre in pieles}

    lista = []

    def agregar_par(nombre, base, rol, malla, musculo=None):
        lista.append((f"{nombre}_I", base + "I", rol, musculo, malla))
        lista.append((f"{nombre}_D", base + "D", rol, musculo, espejo(malla)))

    for nombre, malla in reliefs.items():
        if nombre in PARES:
            agregar_par(nombre, JUNTA_DE[nombre], "piel", malla)
        else:
            lista.append((nombre, JUNTA_DE[nombre], "piel", None, malla))

    agregar_par("pie", "tobillo", "calzado", zapatilla())
    lista.append(("short_pelvis", "raiz", "ropa", None, short_pelvis()))
    agregar_par("short", "cadera", "ropa", short_pierna())
    lista.append(("ojo_I", "cuello", "ojos", None, ojo()))
    lista.append(("ojo_D", "cuello", "ojos", None, espejo(ojo())))

    for musculo, (sobre, mascara, altura) in reglas_musculos.items():
        izquierda = capa(pieles[sobre], mascara, altura, relieve=reliefs[sobre])
        base = JUNTA_DE[sobre]
        if sobre in PARES:
            agregar_par(musculo, base, "musculo", izquierda, musculo)
        elif musculo in SIMETRICOS_EN_TRONCO:
            lista.append((f"{musculo}_I", base, "musculo", musculo, izquierda))
            lista.append((f"{musculo}_D", base, "musculo", musculo, espejo(izquierda)))
        else:
            lista.append((musculo, base, "musculo", musculo, izquierda))
    return lista


def exportar(destino: Path):
    manifiesto = {"version": 2, "partes": []}
    binario = bytearray()
    for nombre, junta, rol, musculo, malla in partes():
        if rol != "musculo":
            assert volumen(malla) > 0, f"{nombre}: caras hacia dentro"
        nv, ni = len(malla.v), malla.f.size
        manifiesto["partes"].append({
            "nombre": nombre, "junta": junta, "rol": rol, "musculo": musculo,
            "v": nv, "i": ni, "o": len(binario)})
        binario += malla.v.astype("<f4").tobytes()
        binario += normales(malla).astype("<f4").tobytes()
        binario += malla.f.astype("<u4").reshape(-1).tobytes()
    destino.mkdir(parents=True, exist_ok=True)
    (destino / "maniqui.bin").write_bytes(bytes(binario))
    (destino / "maniqui.json").write_text(json.dumps(manifiesto, ensure_ascii=False, indent=1))
    verts = sum(p["v"] for p in manifiesto["partes"])
    tris = sum(p["i"] for p in manifiesto["partes"]) // 3
    print(f"{len(manifiesto['partes'])} partes, {verts} vértices, {tris} triángulos, {len(binario) / 1024:.0f} KB")


if __name__ == "__main__":
    exportar(Path(__file__).resolve().parent.parent / "Pulso" / "Resources")
