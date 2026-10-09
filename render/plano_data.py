"""Datos de la planta FINAL (según el plano del arquitecto + cambios pedidos).

Unidades: planta en CENTÍMETROS (x este, y norte; origen = esquina SO interior del dormitorio 1);
alturas z en METROS. Lo usan la escena de Blender y la construcción en SketchUp.
"""
WALL_H = 2.40
DOOR_H = 2.05

# (nombre, x0, y0, x1, y1, puertas[(a0,a1)] , ventanas[(a0,a1,z0,z1)])  -- a* sobre el eje largo del muro
WALLS = [
    ("Pared_Sur", -20, -20, 975, 0, [], [(80, 290, 0.90, 2.10), (410, 560, 1.40, 2.10), (690, 900, 0.90, 2.10)]),
    ("Pared_D1_Oeste", -20, 0, 0, 370, [], []),
    ("Pared_D1_Closet_Norte", -20, 350, 225, 370, [], []),
    ("Pared_D1_Este", 315, 0, 335, 370, [(95, 165), (240, 320)], []),
    ("Pared_Banos_Norte", 335, 180, 525, 200, [], []),
    ("Particion_Banos", 465, 0, 475, 180, [], []),
    ("Pared_Vestidor_Norte", 335, 350, 485, 370, [], []),
    ("Pared_Vestidor_Este", 465, 200, 485, 350, [], []),
    ("Pared_D2_Oeste", 595, 0, 615, 180, [(98, 168)], []),
    ("Pared_D2_Norte", 595, 270, 975, 290, [], []),
    ("Pared_D2_Este", 955, 0, 975, 270, [], []),
    ("Pared_Sala_Este", 928, 290, 948, 584, [], [(300, 510, 1.00, 2.10)]),
    ("Pared_Sala_Norte", 127, 584, 948, 604, [], []),
]

# contorno del piso (cm)
FLOOR = [(-20, -20), (975, -20), (975, 290), (948, 290), (948, 604), (127, 604), (127, 370), (-20, 370)]

BOXES = []   # (nombre, x0,y0,x1,y1, z0,z1, material, bisel_m)
CYLS = []    # (nombre, x, y, z0, z1, r, rx, material)


def B(name, x0, y0, x1, y1, z0, z1, mat, bevel=0.0):
    BOXES.append((name, x0, y0, x1, y1, z0, z1, mat, bevel))


def C(name, x, y, z0, z1, r, mat, rx=None):
    CYLS.append((name, x, y, z0, z1, r, r if rx is None else rx, mat))


def window_h(prefix, a0, a1, z0, z1, yc):           # ventana en muro horizontal (eje x)
    B(prefix + "_vidrio", a0, yc - 0.4, a1, yc + 0.4, z0, z1, "vidrio")
    B(prefix + "_marco_inf", a0, yc - 3, a1, yc + 3, z0, z0 + 0.04, "aluminio")
    B(prefix + "_marco_sup", a0, yc - 3, a1, yc + 3, z1 - 0.04, z1, "aluminio")
    B(prefix + "_marco_izq", a0, yc - 3, a0 + 4, yc + 3, z0, z1, "aluminio")
    B(prefix + "_marco_der", a1 - 4, yc - 3, a1, yc + 3, z0, z1, "aluminio")
    B(prefix + "_marco_med", (a0 + a1) / 2 - 2, yc - 3, (a0 + a1) / 2 + 2, yc + 3, z0, z1, "aluminio")


def window_v(prefix, a0, a1, z0, z1, xc):           # ventana en muro vertical (eje y)
    B(prefix + "_vidrio", xc - 0.4, a0, xc + 0.4, a1, z0, z1, "vidrio")
    B(prefix + "_marco_inf", xc - 3, a0, xc + 3, a1, z0, z0 + 0.04, "aluminio")
    B(prefix + "_marco_sup", xc - 3, a0, xc + 3, a1, z1 - 0.04, z1, "aluminio")
    B(prefix + "_marco_a", xc - 3, a0, xc + 3, a0 + 4, z0, z1, "aluminio")
    B(prefix + "_marco_b", xc - 3, a1 - 4, xc + 3, a1, z0, z1, "aluminio")
    B(prefix + "_marco_med", xc - 3, (a0 + a1) / 2 - 2, xc + 3, (a0 + a1) / 2 + 2, z0, z1, "aluminio")


window_h("Vent_D1", 80, 290, 0.90, 2.10, -10)
window_h("Vent_Bano", 410, 560, 1.40, 2.10, -10)
window_h("Vent_D2", 690, 900, 0.90, 2.10, -10)
window_v("Vent_Cocina", 300, 510, 1.00, 2.10, 938)


def chair(prefix, x0, y0, back_north):
    B(prefix + "_asiento", x0, y0, x0 + 44, y0 + 44, 0.43, 0.47, "silla", 0.012)
    for k, (lx, ly) in enumerate([(x0 + 2, y0 + 2), (x0 + 39, y0 + 2), (x0 + 2, y0 + 39), (x0 + 39, y0 + 39)]):
        B("%s_pata%d" % (prefix, k), lx, ly, lx + 3, ly + 3, 0.0, 0.43, "madera_oscura", 0.003)
    if back_north:
        B(prefix + "_respaldo", x0, y0 + 41, x0 + 44, y0 + 44, 0.47, 0.88, "silla", 0.015)
    else:
        B(prefix + "_respaldo", x0, y0, x0 + 44, y0 + 3, 0.47, 0.88, "silla", 0.015)


def lamp(prefix, x, y, z):
    C(prefix + "_base", x, y, z, z + 0.16, 0.035, "negro")
    C(prefix + "_pantalla", x, y, z + 0.16, z + 0.36, 0.11, "blanco", 0.085)


# ---------------- Dormitorio 1 (cama centrada entre pared sur y closet; cabecero al oeste)
B("Alfombra_D1", 40, 21, 250, 271, 0, 0.012, "alfombra", 0.003)
B("Cama1_Cabecero", 0.5, 71, 8, 221, 0.0, 1.05, "cabecero", 0.04)
B("Cama1_Base", 8, 73, 188, 219, 0.0, 0.28, "madera", 0.01)
B("Cama1_Colchon", 8, 71, 190, 221, 0.28, 0.52, "blanco", 0.04)
B("Cama1_Edredon", 55, 69, 192, 223, 0.52, 0.60, "tela_gris", 0.035)
B("Cama1_Almohada_S", 14, 79, 48, 141, 0.52, 0.66, "blanco", 0.07)
B("Cama1_Almohada_N", 14, 151, 48, 213, 0.52, 0.66, "blanco", 0.07)
B("Cama1_Manta", 150, 71, 175, 221, 0.60, 0.63, "tela_beige", 0.015)
B("Mesa_Noche_1S", 1, 25, 41, 65, 0.0, 0.5, "madera", 0.008)
B("Mesa_Noche_1N", 1, 227, 41, 267, 0.0, 0.5, "madera", 0.008)
lamp("Lampara_1S", 21, 45, 0.5)
lamp("Lampara_1N", 21, 247, 0.5)
B("Cuadro1_Marco", 0.5, 96, 2.3, 196, 1.25, 1.85, "negro")
B("Cuadro1_Lienzo", 2.3, 99, 2.9, 193, 1.28, 1.82, "tela_roja")
# closet del dormitorio 1 (2.25 x 0.6 m): cuerpo + 4 puertas con tiradores
B("Closet1_Cuerpo", 0, 292, 225, 350, 0.0, 2.30, "gabinete", 0.004)
for i in range(4):
    a = i * 56.25 + 0.4
    B("Closet1_Puerta%d" % i, a, 290.4, a + 55.4, 292, 0.05, 2.25, "madera", 0.003)
    B("Closet1_Tirador%d" % i, a + 23, 289.2, a + 28, 290.4, 1.0, 1.2, "acero")

# ---------------- Vestidor del dormitorio 1 (1.30 x 1.50 m): barra con ropa + repisas
B("Vest_Fondo_N", 335, 348, 465, 350, 0.0, 2.3, "madera")
B("Vest_Lado_O", 335, 320, 337, 348, 0.0, 2.3, "madera")
B("Vest_Techo_N", 335, 320, 465, 348, 2.28, 2.30, "madera")
B("Vest_Repisa_N", 337, 320, 463, 348, 2.0, 2.03, "madera")
B("Vest_Barra", 337, 333, 463, 335, 1.74, 1.77, "acero")
for i, x in enumerate(range(341, 460, 11)):
    B("Vest_Ropa_%d" % i, x, 323, x + 3, 345, 0.85 + (i % 3) * 0.05, 1.72, ["ropa_a", "ropa_b", "ropa_c", "ropa_d"][i % 4], 0.004)
B("Vest_Fondo_E", 463, 200, 465, 320, 0.0, 2.3, "madera")
for k, zz in enumerate([0.05, 0.5, 0.95, 1.4, 1.85, 2.28]):
    B("Vest_Repisa_E%d" % k, 435, 200, 463, 318, zz, zz + 0.03, "madera")

# ---------------- Baño 1 (1.30 x 1.80 m): inodoro, ducha, lavabo
B("Baldosa_Bano1", 335, 0, 465, 180, 0, 0.004, "baldosa")
B("B1_Inodoro_Tanque", 345, 8, 383, 24, 0.0, 0.78, "ceramica", 0.02)
B("B1_Inodoro_Taza", 347, 24, 381, 60, 0.0, 0.40, "ceramica", 0.04)
B("B1_Ducha_Base", 395, 5, 463, 75, 0.0, 0.04, "ceramica", 0.004)
B("B1_Ducha_Cristal_N", 395, 75, 463, 76.4, 0.04, 2.0, "vidrio")
B("B1_Ducha_Cristal_O", 393.6, 5, 395, 75, 0.04, 2.0, "vidrio")
C("B1_Ducha_Cabezal", 450, 20, 2.05, 2.07, 0.09, "acero")
B("B1_Mueble_Lav", 395, 140, 455, 178, 0.12, 0.82, "gabinete", 0.005)
B("B1_Cubierta_Lav", 393.5, 138.5, 456.5, 178, 0.82, 0.86, "meson", 0.004)
C("B1_Lavabo", 425, 160, 0.86, 0.90, 0.17, "ceramica", 0.15)
C("B1_Grifo", 425, 172, 0.86, 1.0, 0.012, "acero")
B("B1_Espejo", 400, 177.5, 450, 179, 1.15, 1.95, "espejo")
# ---------------- Baño 2 (1.20 x 1.80 m)
B("Baldosa_Bano2", 475, 0, 595, 180, 0, 0.004, "baldosa")
B("B2_Inodoro_Tanque", 485, 8, 523, 24, 0.0, 0.78, "ceramica", 0.02)
B("B2_Inodoro_Taza", 487, 24, 521, 60, 0.0, 0.40, "ceramica", 0.04)
B("B2_Ducha_Base", 530, 5, 593, 85, 0.0, 0.04, "ceramica", 0.004)
B("B2_Ducha_Cristal_N", 530, 85, 593, 86.4, 0.04, 2.0, "vidrio")
B("B2_Ducha_Cristal_O", 528.6, 5, 530, 85, 0.04, 2.0, "vidrio")
C("B2_Ducha_Cabezal", 575, 20, 2.05, 2.07, 0.09, "acero")
B("B2_Mueble_Lav", 485, 140, 525, 178, 0.12, 0.82, "gabinete", 0.005)
B("B2_Cubierta_Lav", 483.5, 138.5, 526.5, 178, 0.82, 0.86, "meson", 0.004)
C("B2_Lavabo", 505, 160, 0.86, 0.90, 0.15, "ceramica", 0.13)
C("B2_Grifo", 505, 172, 0.86, 1.0, 0.012, "acero")
B("B2_Espejo", 488, 177.5, 522, 179, 1.15, 1.95, "espejo")

# ---------------- Dormitorio 2 (3.40 x 2.70 m, sin closet): cama contra la pared este, cabecero al ventanal (sur)
B("Alfombra_D2", 630, 0, 940, 215, 0, 0.012, "alfombra", 0.003)
B("Cama2_Cabecero", 805, 0.5, 955, 8, 0.0, 1.10, "cabecero", 0.04)
B("Cama2_Base", 807, 8, 953, 188, 0.0, 0.28, "madera", 0.01)
B("Cama2_Colchon", 805, 8, 955, 190, 0.28, 0.52, "blanco", 0.04)
B("Cama2_Edredon", 803, 50, 957, 192, 0.52, 0.60, "tela_gris", 0.035)
B("Cama2_Almohada_I", 813, 14, 875, 48, 0.52, 0.66, "blanco", 0.07)
B("Cama2_Almohada_D", 885, 14, 947, 48, 0.52, 0.66, "blanco", 0.07)
B("Cama2_Manta", 805, 100, 955, 125, 0.60, 0.63, "tela_beige", 0.015)
B("Mesa_Noche_2", 758, 0.5, 798, 40.5, 0.0, 0.5, "madera", 0.008)
lamp("Lampara_2", 778, 20, 0.5)
B("Comoda_2", 625, 215, 745, 255, 0.0, 0.85, "madera", 0.008)
B("Cuadro2_Marco", 953.2, 100, 955, 200, 1.2, 1.8, "negro")
B("Cuadro2_Lienzo", 952.6, 103, 953.2, 197, 1.23, 1.77, "tela_beige")

# ---------------- Sala (sofá, TV, aparador), comedor y cocina
B("Alfombra_Sala", 240, 380, 430, 580, 0, 0.012, "alfombra", 0.003)
# sofá de 3 plazas (2.0 x 0.9 m), mirando al este, con el respaldo hacia la baranda de la escalera
B("Sofa_Base", 135, 400, 225, 580, 0.05, 0.28, "tela_sofa", 0.02)
B("Sofa_Respaldo", 135, 400, 157, 580, 0.28, 0.82, "tela_sofa", 0.06)
B("Sofa_Brazo_N", 157, 560, 225, 580, 0.28, 0.62, "tela_sofa", 0.06)
B("Sofa_Brazo_S", 157, 400, 225, 420, 0.28, 0.62, "tela_sofa", 0.06)
for i in range(3):
    y = 420 + i * 46.67
    B("Sofa_Cojin%d" % i, 157, y, 225, y + 46.67, 0.28, 0.45, "tela_sofa", 0.05)
B("Cojin_Rojo", 160, 425, 185, 460, 0.45, 0.78, "tela_roja", 0.07)
B("Cojin_Gris", 160, 520, 185, 555, 0.45, 0.78, "tela_gris", 0.07)
# mesa de centro
B("Mesa_Centro_Tapa", 275, 450, 335, 530, 0.38, 0.42, "madera_oscura", 0.01)
for nm, (lx, ly) in {"a": (278, 453), "b": (328, 453), "c": (278, 523), "d": (328, 523)}.items():
    B("Mesa_Centro_Pata_" + nm, lx, ly, lx + 4, ly + 4, 0.0, 0.38, "madera_oscura", 0.003)
# mueble de TV (1.6 x 0.35 m) con televisor, mirando al oeste
B("Mueble_TV", 440, 400, 475, 560, 0.0, 0.45, "madera", 0.008)
B("TV_Base", 452, 465, 462, 495, 0.45, 0.50, "negro")
B("TV_Pantalla", 453, 425, 457, 535, 0.50, 1.10, "negro", 0.005)
# aparador contra la pared norte + lámparas
B("Aparador", 250, 564, 430, 584, 0.0, 0.80, "madera", 0.008)
lamp("Lampara_Aparador1", 275, 574, 0.80)
lamp("Lampara_Aparador2", 405, 574, 0.80)
# planta en maceta
C("Maceta", 500, 566, 0.0, 0.34, 0.15, "maceta", 0.19)
C("Planta", 500, 566, 0.34, 1.15, 0.10, "verde", 0.26)
# comedor: mesa 1.4 x 0.8 m + 4 sillas
B("Alfombra_Comedor", 520, 370, 740, 600 - 20, 0, 0.012, "alfombra", 0.003)
B("Mesa_Tapa", 560, 440, 700, 520, 0.72, 0.76, "madera_oscura", 0.012)
for nm, (lx, ly) in {"a": (563, 443), "b": (693, 443), "c": (563, 513), "d": (693, 513)}.items():
    B("Mesa_Pata_" + nm, lx, ly, lx + 4.5, ly + 4.5, 0.0, 0.72, "madera_oscura", 0.004)
chair("Silla_NI", 575, 520, True); chair("Silla_ND", 640, 520, True)
chair("Silla_SI", 575, 396, False); chair("Silla_SD", 640, 396, False)
C("Florero", 630, 480, 0.76, 1.0, 0.055, "ceramica", 0.04)
# cocina: nevera + mesón al norte + mesón al este con fregadero junto a la ventana
B("Nevera", 730, 514, 800, 584, 0.0, 1.85, "nevera", 0.015)
B("Nevera_Linea", 730, 513.4, 800, 514.6, 1.17, 1.19, "negro")
B("Nevera_Manija_A", 736, 512.4, 739, 513.4, 1.25, 1.75, "negro")
B("Nevera_Manija_B", 736, 512.4, 739, 513.4, 0.70, 1.10, "negro")


def gabinetes(prefix, x0, y0, x1, y1, side, n):
    B(prefix + "_cuerpo", x0, y0, x1, y1, 0.10, 0.86, "gabinete", 0.004)
    B(prefix + "_zocalo", x0 + 3, y0 + 3, x1 - 3, y1 - 3, 0.0, 0.10, "negro")
    B(prefix + "_cubierta", x0 - 1, y0 - 1, x1 + 1, y1 + 1, 0.86, 0.90, "meson", 0.004)
    L = (x1 - x0) if side == "S" else (y1 - y0)
    for i in range(n):
        a = i * L / n + 0.4; b = (i + 1) * L / n - 0.4
        if side == "S":
            B("%s_puerta%d" % (prefix, i), x0 + a, y0 - 1.6, x0 + b, y0, 0.12, 0.84, "gabinete", 0.003)
            B("%s_mango%d" % (prefix, i), x0 + (a + b) / 2 - 8, y0 - 2.8, x0 + (a + b) / 2 + 8, y0 - 1.6, 0.74, 0.76, "acero")
        else:   # frente al oeste
            B("%s_puerta%d" % (prefix, i), x0 - 1.6, y0 + a, x0, y0 + b, 0.12, 0.84, "gabinete", 0.003)
            B("%s_mango%d" % (prefix, i), x0 - 2.8, y0 + (a + b) / 2 - 8, x0 - 1.6, y0 + (a + b) / 2 + 8, 0.74, 0.76, "acero")


gabinetes("MesonA", 800, 524, 860, 584, "S", 1)
B("Estufa", 860, 524, 920, 584, 0.10, 0.86, "acero", 0.005)
B("Estufa_Horno", 862, 522.6, 918, 524, 0.18, 0.80, "negro")
B("Estufa_Mango", 866, 521.4, 914, 522.6, 0.74, 0.77, "acero")
B("Estufa_Placa", 860, 524, 920, 584, 0.86, 0.885, "negro", 0.003)
for i, (hx, hy) in enumerate([(875, 539), (905, 539), (875, 569), (905, 569)]):
    C("Hornilla_%d" % i, hx, hy, 0.885, 0.895, 0.085 if i % 2 == 0 else 0.065, "acero")
gabinetes("MesonB", 920, 524, 928, 584, "S", 1)         # remate hasta el muro este
gabinetes("MesonE", 868, 330, 928, 524, "W", 3)         # mesón este con fregadero (frente a la ventana)
B("Fregadero_Plato", 878, 395, 920, 470, 0.90, 0.905, "acero")
B("Fregadero_Hondo", 882, 399, 916, 466, 0.905, 0.915, "negro")
C("Grifo_Cocina", 920, 432, 0.90, 1.12, 0.014, "acero")
B("Grifo_Pico", 905, 431, 921, 433, 1.10, 1.12, "acero")

# baranda de la escalera que se mantiene (borde oeste de la sala)
B("Baranda_Pasamanos", 125, 370, 129, 584, 0.98, 1.02, "negro")
for i, y in enumerate(range(372, 584, 30)):
    B("Baranda_Poste_%d" % i, 126, y, 128, y + 2, 0.0, 0.98, "negro")

# hojas de puerta (abiertas 90°)
for nm, (x0, y0, x1, y1) in {
    "Puerta_D1_Bano1": (245, 165, 315, 169), "Puerta_D1_Vestidor": (245, 320, 315, 324),
    "Puerta_D2_Bano2": (615, 98, 685, 102), "Puerta_D2_Estar": (615, 266, 705, 270),
    "Puerta_Bano2_Estar": (525, 200, 529, 270),
}.items():
    B(nm, x0, y0, x1, y1, 0.02, DOOR_H - 0.02, "puerta", 0.004)
