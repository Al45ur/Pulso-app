#!/usr/bin/env python3
"""Verifica las poses de ejercicios.json sin necesidad de Xcode.

Replica la cinemática del maniquí de la app (Scene3D/Esqueleto.swift): mismas medidas,
mismos ejes y mismo orden de rotaciones. Dibuja cada fase de cada ejercicio de perfil
y de frente, e informa si los pies tocan el suelo.

Uso:  python3 gym/tools/verificar_poses.py SALIDA_DIR
Requiere Pillow.   Si cambias una medida aquí, cámbiala también en Esqueleto.swift.
"""
import json
import math
import sys
from pathlib import Path

from PIL import Image, ImageDraw

# --- Medidas (metros). Deben coincidir con Esqueleto.swift ---------------------------
COLUMNA = (0.0, 0.05, 0.0)       # relativo a la pelvis
HOMBRO = (0.19, 0.45, 0.0)       # relativo a la columna (izquierda = +x)
CUELLO = (0.0, 0.50, 0.0)        # relativo a la columna
CABEZA = (0.0, 0.14, 0.0)        # relativo al cuello
CADERA = (0.09, 0.0, 0.0)        # relativo a la pelvis (izquierda = +x)
BRAZO, ANTEBRAZO, MANO = 0.30, 0.27, 0.04   # la mano (agarre) está a ANTEBRAZO+MANO del codo
MUSLO, PANTORRILLA, TOBILLO_SUELO = 0.42, 0.41, 0.07
PIE_FRENTE, PIE_ATRAS = 0.18, 0.06
BANCO_ALTURA = 0.38


# --- Álgebra mínima ------------------------------------------------------------------
def rx(g):
    a = math.radians(g)
    c, s = math.cos(a), math.sin(a)
    return [[1, 0, 0], [0, c, -s], [0, s, c]]


def rz(g):
    a = math.radians(g)
    c, s = math.cos(a), math.sin(a)
    return [[c, -s, 0], [s, c, 0], [0, 0, 1]]


def ry(g):
    a = math.radians(g)
    c, s = math.cos(a), math.sin(a)
    return [[c, 0, s], [0, 1, 0], [-s, 0, c]]


def mul(a, b):
    return [[sum(a[i][k] * b[k][j] for k in range(3)) for j in range(3)] for i in range(3)]


def app(m, v):
    return [sum(m[i][k] * v[k] for k in range(3)) for i in range(3)]


def add(a, b):
    return [a[i] + b[i] for i in range(3)]


def art(pose, nombre, n=2):
    v = pose["art"].get(nombre, [])
    return [(v[i] if i < len(v) else 0.0) for i in range(n)]


# --- Cinemática directa (igual que Esqueleto.swift) ----------------------------------
def esqueleto(pose):
    raiz = pose["raiz"]
    R0 = rx(raiz.get("pitch", 0.0))
    p0 = list(raiz["pos"])
    J = {"pelvis": p0, "T:raiz": (p0, R0)}

    def nodo(padre_pos, padre_rot, local_pos, local_rot, nombre=None):
        pos, rot = add(padre_pos, app(padre_rot, local_pos)), mul(padre_rot, local_rot)
        if nombre:
            J["T:" + nombre] = (pos, rot)
        return pos, rot

    # Columna / cuello / cabeza
    flex, = art(pose, "columna", 1)
    pc, Rc = nodo(p0, R0, COLUMNA, rx(flex), "columna")
    J["columna"] = pc
    for lado, s in (("I", 1), ("D", -1)):
        # Hombro: Rx(-flex) * Rz(s*abd) * Ry(s*rotación); rotación positiva = externa (el antebrazo flexionado sale hacia fuera)
        f, a, r = art(pose, "hombro" + lado, 3)
        ph, Rh = nodo(pc, Rc, (s * HOMBRO[0], HOMBRO[1], HOMBRO[2]), mul(rx(-f), mul(rz(s * a), ry(s * r))), "hombro" + lado)
        J["hombro" + lado] = ph
        f, = art(pose, "codo" + lado, 1)
        pe, Re = nodo(ph, Rh, (0, -BRAZO, 0), rx(-f), "codo" + lado)
        J["codo" + lado] = pe
        J["mano" + lado] = add(pe, app(Re, (0, -(ANTEBRAZO + MANO), 0)))
        # Pierna
        f, a = art(pose, "cadera" + lado)
        pcad, Rcad = nodo(p0, R0, (s * CADERA[0], CADERA[1], CADERA[2]), mul(rx(-f), rz(s * a)), "cadera" + lado)
        J["cadera" + lado] = pcad
        f, = art(pose, "rodilla" + lado, 1)
        pr, Rr = nodo(pcad, Rcad, (0, -MUSLO, 0), rx(f), "rodilla" + lado)
        J["rodilla" + lado] = pr
        f, = art(pose, "tobillo" + lado, 1)
        pt, Rt = nodo(pr, Rr, (0, -PANTORRILLA, 0), rx(-f), "tobillo" + lado)
        J["tobillo" + lado] = pt
        J["suela" + lado] = add(pt, app(Rt, (0, -TOBILLO_SUELO, 0)))
        J["punta" + lado] = add(pt, app(Rt, (0, -TOBILLO_SUELO, PIE_FRENTE)))
        J["talon" + lado] = add(pt, app(Rt, (0, -TOBILLO_SUELO, -PIE_ATRAS)))
        J["_Rt" + lado] = Rt
    fc, = art(pose, "cuello", 1)
    pn, Rn = nodo(pc, Rc, CUELLO, rx(fc), "cuello")
    J["cuello"] = pn
    J["cabeza"] = add(pn, app(Rn, CABEZA))
    return J


def props_pos(ficha, J):
    """Segmentos de los props en coordenadas del mundo, como en la escena 3D."""
    segs = []
    mI, mD = J["manoI"], J["manoD"]
    centro = [(mI[i] + mD[i]) / 2 for i in range(3)]
    for p in ficha.get("props", []):
        t = p["tipo"]
        if t == "barra":
            d = [mI[i] - mD[i] for i in range(3)]
            n = math.sqrt(sum(x * x for x in d)) or 1.0
            e = p.get("alargue", 0.06)
            segs.append((add(mI, [x / n * e for x in d]), add(mD, [-x / n * e for x in d]), "barra"))
        elif t == "cable":
            destino = {"centro": centro, "manoD": mD, "manoI": mI}[p.get("hacia", "centro")]
            segs.append((p["ancla"], destino, "cable"))
        elif t == "mancuernas":
            for m in (mI, mD):
                segs.append((add(m, [-0.07, 0, 0]), add(m, [0.07, 0, 0]), "barra"))
        elif t == "manija":
            m = J["mano" + p["mano"]]
            segs.append((add(m, [-0.06, 0, 0]), add(m, [0.06, 0, 0]), "barra"))
        elif t == "banco":
            segs.append(([0, BANCO_ALTURA, -0.9], [0, BANCO_ALTURA, 0.25], "banco"))
        elif t == "bancoInclinado":
            ang = math.radians(p.get("angulo", 65))
            segs.append(([0, BANCO_ALTURA, -0.18], [0, BANCO_ALTURA, 0.30], "banco"))
            segs.append(([0, BANCO_ALTURA, -0.18], [0, BANCO_ALTURA + 0.78 * math.sin(ang), -0.18 - 0.78 * math.cos(ang)], "banco"))
    return segs


# --- Dibujo --------------------------------------------------------------------------
HUESOS = [
    ("pelvis", "columna"), ("hombroI", "hombroD"),
    ("hombroI", "codoI"), ("codoI", "manoI"), ("hombroD", "codoD"), ("codoD", "manoD"),
    ("pelvis", "caderaI"), ("pelvis", "caderaD"),
    ("caderaI", "rodillaI"), ("rodillaI", "tobilloI"), ("caderaD", "rodillaD"), ("rodillaD", "tobilloD"),
    ("tobilloI", "puntaI"), ("tobilloD", "puntaD"), ("tobilloI", "talonI"), ("tobilloD", "talonD"),
    ("cuello", "cabeza"),
]


def dibujar(ficha, fase, vista, tam=380):
    img = Image.new("RGB", (tam, tam), (10, 20, 34))
    d = ImageDraw.Draw(img)
    J = esqueleto(fase["pose"])
    J["hombroI"], J["hombroD"] = J["hombroI"], J["hombroD"]
    # columna -> cuello como segmento del torso
    ejes = (2, 1) if vista == "perfil" else (0, 1)      # perfil: z horizontal; frente: x
    esc, ox, oy = 130.0, tam / 2, tam - 40

    def pt(p):
        h = p[ejes[0]]
        if vista == "frente":
            h = -h  # la izquierda del personaje (+x) queda a la derecha de quien mira
        return (ox + h * esc, oy - p[1] * esc)

    d.line([(0, oy), (tam, oy)], fill=(60, 90, 120), width=2)
    for a, b, tipo in props_pos(ficha, J):
        color = {"barra": (240, 240, 240), "cable": (120, 200, 255), "banco": (90, 100, 120)}[tipo]
        d.line([pt(a), pt(b)], fill=color, width=6 if tipo == "banco" else 3)
    for a, b in HUESOS:
        d.line([pt(J[a]), pt(J[b])], fill=(255, 140, 90), width=5)
    d.line([pt(J["columna"]), pt(J["cuello"])], fill=(255, 140, 90), width=7)
    d.line([pt(J["hombroI"]), pt(J["hombroD"])], fill=(255, 140, 90), width=5)
    cx, cy = pt(J["cabeza"])
    d.ellipse([cx - 14, cy - 14, cx + 14, cy + 14], outline=(255, 200, 160), width=3)
    for k in ("manoI", "manoD"):
        x, y = pt(J[k])
        d.ellipse([x - 5, y - 5, x + 5, y + 5], fill=(60, 240, 160))
    d.text((8, 6), f"{fase['nombre']} · {vista}", fill=(200, 220, 255))
    return img, J


def main():
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    salida = Path(sys.argv[1])
    salida.mkdir(parents=True, exist_ok=True)
    datos = json.loads((Path(__file__).parent.parent / "Pulso/Resources/ejercicios.json").read_text())
    for ficha in datos["ejercicios"]:
        fases = ficha["fases"]
        hoja = Image.new("RGB", (380 * len(fases), 380 * 2))
        print(f"\n{ficha['nombre']}")
        for i, fase in enumerate(fases):
            for fila, vista in enumerate(("perfil", "frente")):
                img, J = dibujar(ficha, fase, vista)
                hoja.paste(img, (380 * i, 380 * fila))
            suela = min(J["suelaI"][1], J["suelaD"][1])
            pitch_pie = [round(math.degrees(math.atan2(J["puntaI"][1] - J["talonI"][1],
                                                       J["puntaI"][2] - J["talonI"][2])), 1)]
            print(f"  {fase['nombre']:<10} suela_y={suela:+.3f} m  inclinación pie={pitch_pie[0]}°  "
                  f"manos_y=({J['manoI'][1]:.2f},{J['manoD'][1]:.2f})")
        hoja.save(salida / f"{ficha['id']}.png")


if __name__ == "__main__":
    main()
