"""Datos de la planta según el PLANO CON MEDIDAS (dos dormitorios, dos baños, sala-comedor-cocina).

Unidades: planta en CENTÍMETROS (x este, y norte; origen = esquina SO interior del dormitorio 1);
alturas z en METROS. Lo usan la escena de Blender, la planta 2D y la construcción en SketchUp.

Medidas del plano (libres, entre caras de muro): dormitorio 1 = 3.15 x 3.12; baños = 1.25 x 2.40 (cada uno, tabique 0.10);
dormitorio 2 = 3.47 al sur y 3.13 al norte (muro este inclinado); sala-comedor-cocina = 7.69 de ancho;
sector oeste de la sala = 2.82 de fondo; cocina: 1.83 desde el muro norte hasta el resalto de 0.70 x 0.20;
muros de 0.20 (tabique de baños 0.10); puertas 0.90 (dormitorios y entrada) y 0.70 (baños).
"""
WALL_H = 2.40
DOOR_H = 2.05

# (nombre, x0, y0, x1, y1, puertas[(a0,a1)] , ventanas[(a0,a1,z0,z1)])  -- a* absolutos sobre el eje largo del muro
WALLS = [
    ("Pared_Sur", -20, -20, 982, 0, [], [(65, 265, 0.90, 2.10), (341, 424, 1.40, 2.10), (481, 583, 1.40, 2.10), (675, 866, 0.90, 2.10)]),
    ("Pared_D1_Oeste", -20, 0, 0, 332, [], []),
    ("Pared_D1_Norte", 0, 312, 315, 332, [(225, 315)], []),                 # abertura 0.90 hacia la sala
    ("Pared_D1_Este", 315, 0, 335, 332, [(0, 70)], []),                      # puerta 0.70 al baño 1
    ("Pared_Banos_Norte", 335, 240, 522, 250, [], []),                       # el hueco 522..592 es la puerta al baño 2
    ("Particion_Banos", 460, 0, 470, 240, [], []),
    ("Pared_D2_Oeste", 595, 0, 615, 332, [(150, 220)], []),                  # puerta corrediza 0.70 baño 2 <-> dormitorio 2
    ("Pared_D2_Norte", 615, 312, 948, 332, [(615, 705)], []),                # puerta 0.90 al dormitorio 2
    ("Pared_Sala_Oeste", 95, 332, 115, 614, [], []),
    ("Pared_Sala_Norte", 95, 614, 904, 634, [], []),
    ("Pared_Sala_Este", 884, 332, 904, 614, [(332, 422)], [(445, 605, 1.00, 2.10)]),   # entrada 0.90 + ventana de la cocina
    ("Resalto_Sala", 590, 411, 660, 431, [], []),                            # resalto/columna 0.70 x 0.20
]

# muros no ortogonales (polígonos en planta): muro este del dormitorio 2, inclinado (3.47 al sur -> 3.13 al norte)
POLYWALLS = [
    ("Pared_D2_Este", [(962, 0), (982.12, 0), (948.12, 312), (928, 312)]),
]

# contorno del piso (cm)
FLOOR = [(-20, -20), (982, -20), (981, 2), (945, 332), (904, 332), (904, 634), (95, 634), (95, 332), (-20, 332)]

PLANT_XY = (138, 598)

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


window_h("Vent_D1", 65, 265, 0.90, 2.10, -10)
window_h("Vent_Bano1", 341, 424, 1.40, 2.10, -10)
window_h("Vent_Bano2", 481, 583, 1.40, 2.10, -10)
window_h("Vent_D2", 675, 866, 0.90, 2.10, -10)
window_v("Vent_Cocina", 445, 605, 1.00, 2.10, 894)


def chair(prefix, x0, y0, back):
    """Silla de 44 x 44 cm; back = lado del respaldo: N, S, E u O."""
    B(prefix + "_asiento", x0, y0, x0 + 44, y0 + 44, 0.43, 0.47, "silla", 0.012)
    for k, (lx, ly) in enumerate([(x0 + 2, y0 + 2), (x0 + 39, y0 + 2), (x0 + 2, y0 + 39), (x0 + 39, y0 + 39)]):
        B("%s_pata%d" % (prefix, k), lx, ly, lx + 3, ly + 3, 0.0, 0.43, "madera_oscura", 0.003)
    rb = {"N": (x0, y0 + 41, x0 + 44, y0 + 44), "S": (x0, y0, x0 + 44, y0 + 3),
          "E": (x0 + 41, y0, x0 + 44, y0 + 44), "O": (x0, y0, x0 + 3, y0 + 44)}[back]
    B(prefix + "_respaldo", *rb, 0.47, 0.88, "silla", 0.015)


def lamp(prefix, x, y, z):
    C(prefix + "_base", x, y, z, z + 0.16, 0.035, "negro")
    C(prefix + "_pantalla", x, y, z + 0.16, z + 0.36, 0.11, "blanco", 0.085)


# ---------------- Dormitorio 1 (3.15 x 3.12 m): cama con el cabecero al oeste; closet de 2.25 x 0.55 m junto al muro norte
B("Alfombra_D1", 30, 25, 250, 235, 0, 0.012, "alfombra", 0.003)
B("Cama1_Cabecero", 0.5, 55, 8, 205, 0.0, 1.05, "cabecero", 0.04)
B("Cama1_Base", 8, 57, 188, 203, 0.0, 0.28, "madera", 0.01)
B("Cama1_Colchon", 8, 55, 190, 205, 0.28, 0.52, "blanco", 0.04)
B("Cama1_Edredon", 55, 53, 192, 207, 0.52, 0.60, "tela_gris", 0.035)
B("Cama1_Almohada_S", 14, 63, 48, 125, 0.52, 0.66, "blanco", 0.07)
B("Cama1_Almohada_N", 14, 135, 48, 197, 0.52, 0.66, "blanco", 0.07)
B("Cama1_Manta", 150, 55, 175, 205, 0.60, 0.63, "tela_beige", 0.015)
B("Mesa_Noche_1S", 1, 10, 41, 50, 0.0, 0.5, "madera", 0.008)
B("Mesa_Noche_1N", 1, 210, 41, 250, 0.0, 0.5, "madera", 0.008)
lamp("Lampara_1S", 21, 30, 0.5)
lamp("Lampara_1N", 21, 230, 0.5)
B("Cuadro1_Marco", 0.5, 80, 2.3, 180, 1.25, 1.85, "negro")
B("Cuadro1_Lienzo", 2.3, 83, 2.9, 177, 1.28, 1.82, "tela_roja")
B("Closet1_Cuerpo", 0, 257, 225, 312, 0.0, 2.30, "gabinete", 0.004)
for i in range(4):
    a = i * 56.25 + 0.4
    B("Closet1_Puerta%d" % i, a, 255.4, a + 55.4, 257, 0.05, 2.25, "madera", 0.003)
    B("Closet1_Tirador%d" % i, a + 23, 254.2, a + 28, 255.4, 1.0, 1.2, "acero")

# ---------------- Baño 1 (1.25 x 2.40 m): inodoro junto a la ventana, lavabo al oeste, ducha al norte
B("Baldosa_Bano1", 335, 0, 460, 240, 0, 0.004, "baldosa")
B("B1_Inodoro_Tanque", 420, 3, 455, 19, 0.0, 0.78, "ceramica", 0.02)
B("B1_Inodoro_Taza", 422, 19, 453, 57, 0.0, 0.40, "ceramica", 0.04)
B("B1_Ducha_Base", 337, 152, 458, 238, 0.0, 0.04, "ceramica", 0.004)
B("B1_Ducha_Cristal_S", 337, 150, 420, 151.4, 0.04, 2.0, "vidrio")
C("B1_Ducha_Cabezal", 397, 231, 2.05, 2.07, 0.09, "acero")
B("B1_Mueble_Lav", 335, 85, 370, 135, 0.12, 0.82, "gabinete", 0.005)
B("B1_Cubierta_Lav", 335, 83.5, 371.5, 136.5, 0.82, 0.86, "meson", 0.004)
C("B1_Lavabo", 352, 110, 0.86, 0.90, 0.15, "ceramica", 0.13)
C("B1_Grifo", 340, 110, 0.86, 1.0, 0.012, "acero")
B("B1_Espejo", 336, 88, 337.5, 132, 1.15, 1.95, "espejo")
# ---------------- Baño 2 (1.25 x 2.40 m): puertas al estar (norte) y al dormitorio 2 (corrediza, este)
B("Baldosa_Bano2", 470, 0, 595, 240, 0, 0.004, "baldosa")
B("B2_Inodoro_Tanque", 480, 3, 515, 19, 0.0, 0.78, "ceramica", 0.02)
B("B2_Inodoro_Taza", 482, 19, 513, 57, 0.0, 0.40, "ceramica", 0.04)
B("B2_Ducha_Base", 522, 2, 593, 90, 0.0, 0.04, "ceramica", 0.004)
B("B2_Ducha_Cristal_N", 522, 90, 560, 91.4, 0.04, 2.0, "vidrio")
B("B2_Ducha_Cristal_O", 520.6, 2, 522, 90, 0.04, 2.0, "vidrio")
C("B2_Ducha_Cabezal", 588, 45, 2.05, 2.07, 0.09, "acero")
B("B2_Mueble_Lav", 470, 100, 505, 150, 0.12, 0.82, "gabinete", 0.005)
B("B2_Cubierta_Lav", 470, 98.5, 506.5, 151.5, 0.82, 0.86, "meson", 0.004)
C("B2_Lavabo", 487, 125, 0.86, 0.90, 0.15, "ceramica", 0.13)
C("B2_Grifo", 474, 125, 0.86, 1.0, 0.012, "acero")
B("B2_Espejo", 470.2, 105, 471.7, 145, 1.15, 1.95, "espejo")

# ---------------- Dormitorio 2 (3.47 al sur / 3.13 al norte x 3.12 m): cama con el cabecero hacia el ventanal (sur)
B("Alfombra_D2", 650, 10, 900, 230, 0, 0.012, "alfombra", 0.003)
B("Cama2_Cabecero", 695, 0.5, 845, 8, 0.0, 1.10, "cabecero", 0.04)
B("Cama2_Base", 697, 8, 843, 188, 0.0, 0.28, "madera", 0.01)
B("Cama2_Colchon", 695, 8, 845, 190, 0.28, 0.52, "blanco", 0.04)
B("Cama2_Edredon", 693, 50, 847, 192, 0.52, 0.60, "tela_gris", 0.035)
B("Cama2_Almohada_I", 703, 14, 765, 48, 0.52, 0.66, "blanco", 0.07)
B("Cama2_Almohada_D", 775, 14, 837, 48, 0.52, 0.66, "blanco", 0.07)
B("Cama2_Manta", 695, 100, 845, 125, 0.60, 0.63, "tela_beige", 0.015)
B("Mesa_Noche_2O", 650, 0.5, 690, 40.5, 0.0, 0.5, "madera", 0.008)
B("Mesa_Noche_2E", 850, 0.5, 890, 40.5, 0.0, 0.5, "madera", 0.008)
lamp("Lampara_2O", 670, 20, 0.5)
lamp("Lampara_2E", 870, 20, 0.5)
B("Comoda_2", 720, 272, 880, 312, 0.0, 0.85, "madera", 0.008)

# ---------------- Sala (TV al oeste, sofá de 3 plazas como divisor), comedor y cocina
B("Alfombra_Sala", 175, 400, 355, 590, 0, 0.012, "alfombra", 0.003)
B("Mueble_TV", 120, 420, 155, 580, 0.0, 0.45, "madera", 0.008)          # mueble de 1.6 x 0.35 m, TV mirando al este
B("TV_Base", 127, 485, 137, 515, 0.45, 0.50, "negro")
B("TV_Pantalla", 128, 455, 132, 545, 0.50, 1.10, "negro", 0.005)
# sofá de 3 plazas (1.9 x 0.9 m) mirando al oeste, con el respaldo hacia el comedor
B("Sofa_Base", 330, 405, 420, 595, 0.05, 0.28, "tela_sofa", 0.02)
B("Sofa_Respaldo", 398, 405, 420, 595, 0.28, 0.82, "tela_sofa", 0.06)
B("Sofa_Brazo_N", 330, 575, 398, 595, 0.28, 0.62, "tela_sofa", 0.06)
B("Sofa_Brazo_S", 330, 405, 398, 425, 0.28, 0.62, "tela_sofa", 0.06)
for i in range(3):
    y = 425 + i * 50
    B("Sofa_Cojin%d" % i, 330, y, 398, y + 50, 0.28, 0.45, "tela_sofa", 0.05)
B("Cojin_Rojo", 372, 430, 396, 465, 0.45, 0.78, "tela_roja", 0.07)
B("Cojin_Gris", 372, 535, 396, 570, 0.45, 0.78, "tela_gris", 0.07)
# mesa de centro (0.6 x 0.8 m)
B("Mesa_Centro_Tapa", 215, 455, 275, 535, 0.38, 0.42, "madera_oscura", 0.01)
for nm, (lx, ly) in {"a": (218, 458), "b": (268, 458), "c": (218, 528), "d": (268, 528)}.items():
    B("Mesa_Centro_Pata_" + nm, lx, ly, lx + 4, ly + 4, 0.0, 0.38, "madera_oscura", 0.003)
# aparador contra el muro norte + lámparas, planta en la esquina
B("Aparador", 170, 589, 290, 614, 0.0, 0.80, "madera", 0.008)
lamp("Lampara_Aparador1", 190, 601.5, 0.80)
lamp("Lampara_Aparador2", 270, 601.5, 0.80)
C("Maceta", PLANT_XY[0], PLANT_XY[1], 0.0, 0.34, 0.15, "maceta", 0.19)
C("Planta", PLANT_XY[0], PLANT_XY[1], 0.34, 1.15, 0.10, "verde", 0.26)
# comedor: mesa de 0.85 x 1.5 m + 4 sillas (respaldos hacia los extremos laterales)
B("Alfombra_Comedor", 440, 400, 625, 612, 0, 0.012, "alfombra", 0.003)
B("Mesa_Tapa", 490, 435, 575, 585, 0.72, 0.76, "madera_oscura", 0.012)
for nm, (lx, ly) in {"a": (493, 438), "b": (567.5, 438), "c": (493, 578), "d": (567.5, 578)}.items():
    B("Mesa_Pata_" + nm, lx, ly, lx + 4.5, ly + 4.5, 0.0, 0.72, "madera_oscura", 0.004)
chair("Silla_OS", 444, 455, "O"); chair("Silla_ON", 444, 530, "O")
chair("Silla_ES", 577, 455, "E"); chair("Silla_EN", 577, 530, "E")
C("Florero", 532, 510, 0.76, 1.0, 0.055, "ceramica", 0.04)
# cocina: nevera + mesón + estufa al norte; mesón este con fregadero junto a la ventana
B("Nevera", 655, 544, 725, 614, 0.0, 1.85, "nevera", 0.015)
B("Nevera_Linea", 655, 543.4, 725, 544.6, 1.17, 1.19, "negro")
B("Nevera_Manija_A", 661, 542.4, 664, 543.4, 1.25, 1.75, "negro")
B("Nevera_Manija_B", 661, 542.4, 664, 543.4, 0.70, 1.10, "negro")


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


gabinetes("MesonA", 725, 554, 764, 614, "S", 1)
B("Estufa", 764, 554, 824, 614, 0.10, 0.86, "acero", 0.005)
B("Estufa_Horno", 766, 552.6, 822, 554, 0.18, 0.80, "negro")
B("Estufa_Mango", 770, 551.4, 818, 552.6, 0.74, 0.77, "acero")
B("Estufa_Placa", 764, 554, 824, 614, 0.86, 0.885, "negro", 0.003)
for i, (hx, hy) in enumerate([(779, 569), (809, 569), (779, 599), (809, 599)]):
    C("Hornilla_%d" % i, hx, hy, 0.885, 0.895, 0.085 if i % 2 == 0 else 0.065, "acero")
gabinetes("MesonB", 824, 554, 884, 614, "S", 0)          # módulo de esquina (ciego) hasta el muro este
gabinetes("MesonE", 824, 434, 884, 554, "W", 2)          # mesón este con fregadero (bajo la ventana)
B("Fregadero_Plato", 834, 455, 876, 530, 0.90, 0.905, "acero")
B("Fregadero_Hondo", 838, 459, 872, 526, 0.905, 0.915, "negro")
C("Grifo_Cocina", 879, 492.5, 0.90, 1.12, 0.014, "acero")
B("Grifo_Pico", 863, 491.5, 879, 493.5, 1.10, 1.12, "acero")

# hojas de puerta (abiertas 90°)
for nm, (x0, y0, x1, y1) in {
    "Puerta_D1_Bano1": (335, 70, 405, 74),        # abre hacia el baño 1
    "Puerta_D1_Norte": (311, 222, 315, 312),      # abertura 0.90 dormitorio 1 <-> sala (abre hacia el dormitorio)
    "Puerta_D2_Norte": (701, 222, 705, 312),      # dormitorio 2 <-> estar
    "Puerta_D2_Bano2": (615, 185, 618, 255),      # corrediza 0.70, abierta junto al muro
    "Puerta_Bano2_Norte": (588, 170, 592, 240),   # baño 2 <-> estar
    "Puerta_Entrada": (794, 418, 884, 422),       # entrada 0.90, abre hacia la sala
}.items():
    B(nm, x0, y0, x1, y1, 0.02, DOOR_H - 0.02, "puerta", 0.004)
