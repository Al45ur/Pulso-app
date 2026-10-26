#!/usr/bin/env python3
"""Renderiza el personaje de maniqui.json/maniqui.bin en cada fase de cada ejercicio, sin Xcode.

Usa la misma cinemática que la app (verificar_poses.py), z-buffer y eliminación de caras traseras,
así que si una malla tiene las caras al revés aparece vacía o rota, igual que pasaría en SceneKit.

Uso:  python3 gym/tools/vista_previa_maniqui.py SALIDA_DIR [ejercicio-id] [--neutra] [--anatomia]
Requiere numpy y Pillow.
"""
import json
import math
import sys
from pathlib import Path

import numpy as np
from PIL import Image

sys.path.insert(0, str(Path(__file__).parent))
import verificar_poses as V  # noqa: E402

RAIZ = Path(__file__).resolve().parent.parent / "Pulso" / "Resources"
COLORES = {
    "cuerpo": np.array([51, 71, 97]) / 255.0,
    "neutro": np.array([77, 102, 135]) / 255.0,
    "piel": np.array([214, 163, 129]) / 255.0,
    "ropa": np.array([22, 24, 30]) / 255.0,
    "calzado": np.array([232, 234, 238]) / 255.0,
    "ojos": np.array([14, 14, 18]) / 255.0,
    "principal": np.array([255, 64, 51]) / 255.0,
    "secundario": np.array([255, 153, 38]) / 255.0,
    "fondo": np.array([10, 23, 38]) / 255.0,
}


def cargar():
    manifiesto = json.loads((RAIZ / "maniqui.json").read_text())
    binario = (RAIZ / "maniqui.bin").read_bytes()
    partes = []
    for p in manifiesto["partes"]:
        o, nv, ni = p["o"], p["v"], p["i"]
        v = np.frombuffer(binario, "<f4", nv * 3, o).reshape(-1, 3).astype(float)
        n = np.frombuffer(binario, "<f4", nv * 3, o + nv * 12).reshape(-1, 3).astype(float)
        f = np.frombuffer(binario, "<u4", ni, o + nv * 24).reshape(-1, 3).astype(int)
        partes.append({**p, "vert": v, "nor": n, "caras": f})
    return partes


def a_mundo(parte, J):
    pos, rot = J["T:" + parte["junta"]]
    R = np.array(rot)
    return parte["vert"] @ R.T + np.array(pos), parte["nor"] @ R.T


def rasterizar(triangulos, colores, normales, vista, tam=420, ss=2, props=None):
    """triangulos: (M,3,3) en mundo. Cámara ortográfica: 'perfil' (desde +x) o 'frente' (desde +z)."""
    if vista == "perfil":
        look = np.array([-1.0, 0, 0]); derecha = np.array([0, 0, -1.0])
    elif vista == "frente":
        look = np.array([0, 0, -1.0]); derecha = np.array([1.0, 0, 0])
    else:  # espalda
        look = np.array([0, 0, 1.0]); derecha = np.array([-1.0, 0, 0])
    arriba = np.array([0, 1.0, 0])
    W = tam * ss
    esc = W * 0.40
    sx = triangulos @ derecha
    sy = triangulos @ arriba
    prof = triangulos @ look            # mayor = más lejos
    X = W / 2 + sx * esc
    Y = W * 0.93 - sy * esc
    img = np.tile(COLORES["fondo"], (W, W, 1))
    zbuf = np.full((W, W), np.inf)
    hacia = -look
    luz_cam = hacia * 0.45 - derecha * 0.55 + arriba * 0.55   # desde arriba a la izquierda de la cámara
    luz_cam /= np.linalg.norm(luz_cam)
    for i in range(len(triangulos)):
        t = triangulos[i]
        n = np.cross(t[1] - t[0], t[2] - t[0])
        ln = np.linalg.norm(n)
        if ln < 1e-12:
            continue
        n /= ln
        if n @ look >= 0:               # cara trasera
            continue
        xs, ys, zs = X[i], Y[i], prof[i]
        x0, x1 = int(max(xs.min(), 0)), int(min(xs.max() + 1, W - 1))
        y0, y1 = int(max(ys.min(), 0)), int(min(ys.max() + 1, W - 1))
        if x1 <= x0 or y1 <= y0:
            continue
        gx, gy = np.meshgrid(np.arange(x0, x1 + 1) + 0.5, np.arange(y0, y1 + 1) + 0.5)
        d = (ys[1] - ys[2]) * (xs[0] - xs[2]) + (xs[2] - xs[1]) * (ys[0] - ys[2])
        if abs(d) < 1e-12:
            continue
        l0 = ((ys[1] - ys[2]) * (gx - xs[2]) + (xs[2] - xs[1]) * (gy - ys[2])) / d
        l1 = ((ys[2] - ys[0]) * (gx - xs[2]) + (xs[0] - xs[2]) * (gy - ys[2])) / d
        l2 = 1 - l0 - l1
        dentro = (l0 >= 0) & (l1 >= 0) & (l2 >= 0)
        if not dentro.any():
            continue
        z = l0 * zs[0] + l1 * zs[1] + l2 * zs[2]
        zona = zbuf[y0:y1 + 1, x0:x1 + 1]
        gana = dentro & (z < zona - 1e-6)
        if not gana.any():
            continue
        nn = (l0[..., None] * normales[i, 0] + l1[..., None] * normales[i, 1] + l2[..., None] * normales[i, 2])
        nn /= np.maximum(np.linalg.norm(nn, axis=-1, keepdims=True), 1e-9)
        brillo = 0.22 + 0.78 * np.clip(nn @ luz_cam, 0, 1)
        col = colores[i][None, None, :] * brillo[..., None]
        zona[gana] = z[gana]
        img[y0:y1 + 1, x0:x1 + 1][gana] = col[gana]
    foto = Image.fromarray((np.clip(img, 0, 1) * 255).astype(np.uint8))
    return foto.resize((tam, tam), Image.LANCZOS)


def segmentos_props(ficha, J):
    return V.props_pos(ficha, J)


def dibujar_props(foto, ficha, J, vista, tam=420):
    from PIL import ImageDraw
    d = ImageDraw.Draw(foto)
    if vista == "perfil":
        derecha = np.array([0, 0, -1.0])
    elif vista == "frente":
        derecha = np.array([1.0, 0, 0])
    else:
        derecha = np.array([-1.0, 0, 0])
    esc = tam * 0.40  # igual que en rasterizar()

    def pt(p):
        p = np.array(p, float)
        return (tam / 2 + (p @ derecha) * esc, tam * 0.93 - p[1] * esc)

    for a, b, tipo in segmentos_props(ficha, J):
        col = {"barra": (225, 230, 240), "cable": (115, 200, 255), "banco": (60, 75, 100)}[tipo]
        d.line([pt(a), pt(b)], fill=col, width=6 if tipo == "banco" else 3)


CUBIERTOS = {"gluteos", "cuadriceps", "isquiotibiales", "aductores"}
LOOK = {"anatomia": False}   # False = piel; True = anatomía gris azulada


def color_de(p, principales, secundarios):
    anatomia = LOOK["anatomia"]
    if p["rol"] == "musculo":
        m = p["musculo"]
        if m in principales:
            return COLORES["principal"]
        if m in secundarios:
            return COLORES["secundario"]
        return COLORES["neutro"] if anatomia else None   # en modo piel solo se dibujan los resaltados
    if p["rol"] == "piel" or p["rol"] == "cuerpo":
        return COLORES["cuerpo"] if anatomia else COLORES["piel"]
    if anatomia and p["rol"] in ("ropa", "calzado"):
        return None   # en modo anatomía no se dibuja la ropa
    if p["rol"] == "ropa" and CUBIERTOS & (principales | secundarios):
        return None   # se resalta un músculo que queda bajo el short: la ropa no se dibuja en la vista previa
    return COLORES[p["rol"]]


def render(partes, pose, ficha, principales, secundarios, vista, tam=420):
    J = V.esqueleto(pose)
    tri, col, nor = [], [], []
    for p in partes:
        c = color_de(p, principales, secundarios)
        if c is None:
            continue
        v, n = a_mundo(p, J)
        f = p["caras"]
        tri.append(v[f]); nor.append(n[f]); col.append(np.tile(c, (len(f), 1)))
    foto = rasterizar(np.vstack(tri), np.vstack(col), np.vstack(nor), vista, tam)
    if ficha:
        dibujar_props(foto, ficha, J, vista, tam)
    return foto


def main():
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    salida = Path(sys.argv[1]); salida.mkdir(parents=True, exist_ok=True)
    filtro = next((a for a in sys.argv[2:] if not a.startswith("--")), None)
    partes = cargar()
    LOOK["anatomia"] = "--anatomia" in sys.argv
    if "--neutra" in sys.argv:
        pose = {"raiz": {"pos": [0, 0.9, 0], "pitch": 0}, "art": {"hombroI": [0, 12], "hombroD": [0, 12]}}
        vistas = ("frente", "perfil", "espalda")
        hoja = Image.new("RGB", (420 * 3, 420))
        for i, v in enumerate(vistas):
            hoja.paste(render(partes, pose, None, {"triceps", "gluteos"}, {"isquiotibiales", "dorsales"}, v), (420 * i, 0))
        hoja.save(salida / ("neutra_anatomia.png" if LOOK["anatomia"] else "neutra.png"))
        print("neutra.png")
        return
    datos = json.loads((RAIZ / "ejercicios.json").read_text())
    for ficha in datos["ejercicios"]:
        if filtro and ficha["id"] != filtro:
            continue
        fases = ficha["fases"]
        hoja = Image.new("RGB", (420 * len(fases), 420 * 2))
        for i, fase in enumerate(fases):
            for fila, vista in enumerate(("perfil", "frente")):
                hoja.paste(render(partes, fase["pose"], ficha, set(ficha["musculosPrincipales"]),
                                  set(ficha["musculosSecundarios"]), vista), (420 * i, 420 * fila))
        hoja.save(salida / f"{ficha['id']}.png")
        print(ficha["id"])


if __name__ == "__main__":
    main()
