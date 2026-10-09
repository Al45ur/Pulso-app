"""Escena del departamento para renderizar con Blender (bpy) + Cycles.

Mismas coordenadas que el modelo de SketchUp (1 m = 100 px del render original).
Variables de entorno: OUT, SAMPLES, RES_X, RES_Y, WALLH, CAM (aerial|dorm2|dorm1|cocina).
"""
import bpy, bmesh, math, os
from mathutils import Vector

OUT = os.environ.get("OUT", "/tmp/render.png")
SAMPLES = int(os.environ.get("SAMPLES", "32"))
RES_X = int(os.environ.get("RES_X", "960"))
RES_Y = int(os.environ.get("RES_Y", "600"))
WALLH = float(os.environ.get("WALLH", "2.4"))
CAM = os.environ.get("CAM", "aerial")

bpy.ops.wm.read_factory_settings(use_empty=True)
scene = bpy.context.scene
col = scene.collection


def mx(x): return (x - 120) * 0.01
def my(y): return (712 - y) * 0.01


# ------------------------------------------------------------------ materiales
def new_mat(name, color, rough=0.5, metal=0.0, extra=None):
    m = bpy.data.materials.new(name)
    try:
        m.use_nodes = True
    except Exception:
        pass
    b = m.node_tree.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = (*color, 1.0)
    b.inputs["Roughness"].default_value = rough
    b.inputs["Metallic"].default_value = metal
    if extra:
        for k, v in extra.items():
            b.inputs[k].default_value = v
    return m


def srgb(r, g, b):
    f = lambda c: ((c / 255 + 0.055) / 1.055) ** 2.4 if c / 255 > 0.04045 else c / 255 / 12.92
    return (f(r), f(g), f(b))


def wood_floor_mat():
    m = bpy.data.materials.new("Piso_Madera")
    m.use_nodes = True
    nt = m.node_tree; nt.nodes.clear()
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    bsdf = nt.nodes.new("ShaderNodeBsdfPrincipled")
    tc = nt.nodes.new("ShaderNodeTexCoord")
    brick = nt.nodes.new("ShaderNodeTexBrick")
    brick.offset = 0.4; brick.offset_frequency = 2
    brick.inputs["Color1"].default_value = (*srgb(190, 140, 95), 1)
    brick.inputs["Color2"].default_value = (*srgb(165, 115, 72), 1)
    brick.inputs["Mortar"].default_value = (*srgb(60, 40, 25), 1)
    brick.inputs["Scale"].default_value = 1.0
    brick.inputs["Mortar Size"].default_value = 0.004
    brick.inputs["Brick Width"].default_value = 1.2
    brick.inputs["Row Height"].default_value = 0.15
    brick.inputs["Bias"].default_value = 0.0
    noise = nt.nodes.new("ShaderNodeTexNoise")
    noise.inputs["Scale"].default_value = 6.0
    noise.inputs["Detail"].default_value = 8.0
    mapn = nt.nodes.new("ShaderNodeMapping")
    mapn.inputs["Scale"].default_value = (1.0, 28.0, 1.0)      # veta alargada
    mix = nt.nodes.new("ShaderNodeMix"); mix.data_type = "RGBA"; mix.blend_type = "MULTIPLY"
    mix.inputs[0].default_value = 0.35
    bump = nt.nodes.new("ShaderNodeBump"); bump.inputs["Strength"].default_value = 0.15
    nt.links.new(tc.outputs["Object"], brick.inputs["Vector"])
    nt.links.new(tc.outputs["Object"], mapn.inputs["Vector"])
    nt.links.new(mapn.outputs["Vector"], noise.inputs["Vector"])
    nt.links.new(brick.outputs["Color"], mix.inputs[6])
    nt.links.new(noise.outputs["Fac"], mix.inputs[7])
    nt.links.new(mix.outputs[2], bsdf.inputs["Base Color"])
    nt.links.new(noise.outputs["Fac"], bump.inputs["Height"])
    nt.links.new(bump.outputs["Normal"], bsdf.inputs["Normal"])
    bsdf.inputs["Roughness"].default_value = 0.38
    nt.links.new(bsdf.outputs["BSDF"], out.inputs["Surface"])
    return m


def tile_mat(color, size=0.6, mortar=0.006):
    m = bpy.data.materials.new("Baldosa")
    m.use_nodes = True
    nt = m.node_tree; nt.nodes.clear()
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    bsdf = nt.nodes.new("ShaderNodeBsdfPrincipled")
    tc = nt.nodes.new("ShaderNodeTexCoord")
    brick = nt.nodes.new("ShaderNodeTexBrick")
    brick.offset = 0.0
    brick.inputs["Color1"].default_value = (*color, 1)
    brick.inputs["Color2"].default_value = (*[c * 0.93 for c in color], 1)
    brick.inputs["Mortar"].default_value = (*[c * 0.55 for c in color], 1)
    brick.inputs["Mortar Size"].default_value = mortar
    brick.inputs["Brick Width"].default_value = size
    brick.inputs["Row Height"].default_value = size
    nt.links.new(tc.outputs["Object"], brick.inputs["Vector"])
    nt.links.new(brick.outputs["Color"], bsdf.inputs["Base Color"])
    bsdf.inputs["Roughness"].default_value = 0.2
    nt.links.new(bsdf.outputs["BSDF"], out.inputs["Surface"])
    return m


def fabric_mat(name, color, bump=0.25, rough=0.95):
    m = new_mat(name, color, rough)
    nt = m.node_tree
    b = nt.nodes["Principled BSDF"]
    n = nt.nodes.new("ShaderNodeTexNoise"); n.inputs["Scale"].default_value = 900.0
    bp = nt.nodes.new("ShaderNodeBump"); bp.inputs["Strength"].default_value = bump
    nt.links.new(n.outputs["Fac"], bp.inputs["Height"])
    nt.links.new(bp.outputs["Normal"], b.inputs["Normal"])
    return m


def glass_mat():
    return new_mat("Vidrio", (0.9, 0.95, 1.0), 0.0, 0.0,
                   {"Transmission Weight": 1.0, "IOR": 1.45})


MAT = {
    "pared": new_mat("Pared", srgb(238, 235, 228), 0.92),
    "piso": wood_floor_mat(),
    "baldosa": tile_mat(srgb(214, 216, 218)),
    "madera_oscura": new_mat("Madera_Mesa", srgb(110, 70, 44), 0.35),
    "madera": new_mat("Madera_Clara", srgb(176, 132, 92), 0.45),
    "tela_sofa": fabric_mat("Tela_Sofa", srgb(222, 210, 190)),
    "tela_gris": fabric_mat("Tela_Gris", srgb(92, 92, 98)),
    "tela_roja": fabric_mat("Tela_Roja", srgb(140, 38, 34)),
    "tela_beige": fabric_mat("Tela_Beige", srgb(196, 184, 164)),
    "blanco": fabric_mat("Ropa_Blanca", srgb(244, 244, 242), 0.15),
    "cabecero": fabric_mat("Cabecero", srgb(120, 118, 122), 0.2),
    "silla": new_mat("Silla", srgb(222, 214, 198), 0.7),
    "acero": new_mat("Acero", srgb(205, 208, 212), 0.4, 0.25),
    "nevera": new_mat("Nevera", srgb(196, 200, 205), 0.28, 0.0, {"Coat Weight": 0.3}),
    "negro": new_mat("Negro", srgb(28, 28, 30), 0.35, 0.3),
    "meson": new_mat("Meson_Piedra", srgb(205, 198, 186), 0.3),
    "gabinete": new_mat("Gabinete", srgb(226, 224, 220), 0.5),
    "ceramica": new_mat("Ceramica", srgb(246, 246, 246), 0.08),
    "vidrio": glass_mat(),
    "puerta": new_mat("Puerta", srgb(194, 150, 100), 0.45),
    "aluminio": new_mat("Aluminio", srgb(35, 36, 38), 0.4, 0.8),
    "espejo": new_mat("Espejo", (0.9, 0.9, 0.92), 0.02, 1.0),
    "suelo": new_mat("Suelo", srgb(150, 150, 146), 0.9),
    "alfombra": fabric_mat("Alfombra", srgb(214, 204, 186), 0.4),
    "verde": new_mat("Planta", srgb(60, 110, 50), 0.6),
    "maceta": new_mat("Maceta", srgb(210, 205, 195), 0.7),
}
CLOTHES = [srgb(210, 210, 205), srgb(70, 90, 120), srgb(150, 60, 55), srgb(40, 40, 44), srgb(190, 170, 130),
           srgb(90, 120, 90), srgb(230, 225, 215), srgb(60, 60, 70)]


# ------------------------------------------------------------------ geometría
def link(ob):
    col.objects.link(ob)
    return ob


def box(name, x0, y0, x1, y1, z0, z1, mat, bevel=0.0, seg=3, smooth=False, rotz=0.0, pivot=None):
    """Caja en metros (x0<x1, y0<y1)."""
    bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1.0)
    for v in bm.verts:
        v.co = Vector(((x1 - x0) * v.co.x, (y1 - y0) * v.co.y, (z1 - z0) * v.co.z))
    me = bpy.data.meshes.new(name); bm.to_mesh(me); bm.free()
    ob = bpy.data.objects.new(name, me); link(ob)
    ob.location = ((x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2)
    if rotz:
        if pivot:
            ob.location = Vector(ob.location)
            d = ob.location - Vector((pivot[0], pivot[1], ob.location.z))
            c, s = math.cos(rotz), math.sin(rotz)
            ob.location = Vector((pivot[0] + d.x * c - d.y * s, pivot[1] + d.x * s + d.y * c, ob.location.z))
        ob.rotation_euler = (0, 0, rotz)
    ob.data.materials.append(mat)
    if bevel > 0:
        b = ob.modifiers.new("b", "BEVEL"); b.width = bevel; b.segments = seg; b.limit_method = "ANGLE"
    if smooth:
        for p in me.polygons: p.use_smooth = True
    return ob


def pbox(name, xp0, yp0, xp1, yp1, z0, z1, mat, **kw):
    """Caja con coordenadas del plano (px del render), z en metros."""
    return box(name, mx(xp0), my(yp1), mx(xp1), my(yp0), z0, z1, mat, **kw)


def cyl(name, x, y, z0, z1, r, mat, verts=24, rx=None):
    bm = bmesh.new()
    bmesh.ops.create_cone(bm, cap_ends=True, segments=verts, radius1=r, radius2=(rx if rx is not None else r), depth=z1 - z0)
    me = bpy.data.meshes.new(name); bm.to_mesh(me); bm.free()
    ob = bpy.data.objects.new(name, me); link(ob)
    ob.location = (x, y, (z0 + z1) / 2)
    for p in me.polygons: p.use_smooth = True
    ob.data.materials.append(mat)
    return ob


def sphere(name, x, y, z, r, mat, sx=1, sy=1, sz=1):
    bm = bmesh.new(); bmesh.ops.create_uvsphere(bm, u_segments=20, v_segments=12, radius=r)
    me = bpy.data.meshes.new(name); bm.to_mesh(me); bm.free()
    ob = bpy.data.objects.new(name, me); link(ob)
    ob.location = (x, y, z); ob.scale = (sx, sy, sz)
    for p in me.polygons: p.use_smooth = True
    ob.data.materials.append(mat)
    return ob


def wall(name, axis, c, a0, a1, notches=(), windows=(), height=None, hshift=0.0):
    h = WALLH if height is None else height
    hp = 6.35
    if axis == "h":
        ob = pbox(name, a0, c - hp, a1, c + hp, 0, h, MAT["pared"])
    else:
        ob = pbox(name, c - hp, a0, c + hp, a1, 0, h, MAT["pared"])
    cutters = []
    for (o0, o1, zh) in notches:
        if axis == "h":
            ct = pbox(name + "_cut", o0, c - 12, o1, c + 12, -0.1, zh, MAT["pared"])
        else:
            ct = pbox(name + "_cut", c - 12, o0, c + 12, o1, -0.1, zh, MAT["pared"])
        cutters.append(ct)
    for (o0, o1, z0, z1) in windows:
        if axis == "h":
            ct = pbox(name + "_ven", o0, c - 12, o1, c + 12, z0, z1, MAT["pared"])
        else:
            ct = pbox(name + "_ven", c - 12, o0, c + 12, o1, z0, z1, MAT["pared"])
        cutters.append(ct)
    for ct in cutters:
        m = ob.modifiers.new("cut", "BOOLEAN"); m.object = ct; m.operation = "DIFFERENCE"; m.solver = "EXACT"
        ct.hide_render = True; ct.hide_viewport = True
    return ob


# ------------------------------------------------------------------ estructura
# suelo y losa
pts = [(243.65, 43.65), (1171.35, 43.65), (1171.35, 412), (1216.35, 412), (1216.35, 718.35), (113.65, 718.35),
       (113.65, 412), (243.65, 412)]
bm = bmesh.new()
vs = [bm.verts.new((mx(x), my(y), 0.0)) for (x, y) in pts]
f = bm.faces.new(vs)
if f.normal.z < 0: f.normal_flip()
ext = bmesh.ops.extrude_face_region(bm, geom=[f])
for v in [e for e in ext["geom"] if isinstance(e, bmesh.types.BMVert)]:
    v.co.z = -0.06
bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
me = bpy.data.meshes.new("Piso"); bm.to_mesh(me); bm.free()
piso = bpy.data.objects.new("Piso", me); link(piso)
piso.data.materials.append(MAT["piso"])

DOOR = 2.05
WIN0, WIN1 = 0.76, 2.13
S_H = WALLH
wall("Pared_Sala_Norte", "h", 50, 243.65, 1171.35)
wall("Pared_Sala_Oeste", "v", 250, 56.35, 405.65)
wall("Pared_Sala_Este", "v", 1165, 56.35, 405.65)
wall("Pared_Dorm1_Norte", "h", 412, 113.65, 455.65, notches=[(367, 443, DOOR)])
wall("Pared_Dorm1_Oeste", "v", 120, 418.35, 705.65)
wall("Pared_Vestidor_Norte", "h", 386, 455.65, 638.35)
wall("Pared_Dorm1_Bano", "v", 462, 392.35, 705.65, notches=[(394, 458, DOOR), (622, 698, DOOR)])
wall("Pared_Vestidor_Este", "v", 632, 392.35, 459.65)
wall("Pared_Bano_Norte", "h", 466, 468.35, 793.65, notches=[(662, 738, DOOR)])
wall("Pared_Bano_Divisor", "v", 632, 472.35, 705.65)
wall("Pared_Bano_Dorm2", "v", 800, 392.35, 705.65, notches=[(502, 578, DOOR)])
wall("Pared_Dorm2_Este", "v", 1210, 418.35, 705.65)
wall("Pared_Dorm2_Norte", "h", 412, 895, 1216.35)
wall("Pared_Sur", "h", 712, 113.65, 1216.35, windows=[(135, 405, WIN0, WIN1), (880, 1150, WIN0, WIN1)], height=S_H)

# ventanales: vidrio + marco
for nm, (a, b) in {"Dorm1": (135, 405), "Dorm2": (880, 1150)}.items():
    pbox("Vidrio_" + nm, a, 711.2, b, 712.8, WIN0, WIN1, MAT["vidrio"])
    t = 0.04
    pbox("Marco_Inf_" + nm, a, 710.5, b, 713.5, WIN0, WIN0 + t, MAT["aluminio"])
    pbox("Marco_Sup_" + nm, a, 710.5, b, 713.5, WIN1 - t, WIN1, MAT["aluminio"])
    pbox("Marco_Izq_" + nm, a, 710.5, a + 4, 713.5, WIN0, WIN1, MAT["aluminio"])
    pbox("Marco_Der_" + nm, b - 4, 710.5, b, 713.5, WIN0, WIN1, MAT["aluminio"])
    pbox("Marco_Med_" + nm, (a + b) / 2 - 2, 710.5, (a + b) / 2 + 2, 713.5, WIN0, WIN1, MAT["aluminio"])

# puertas corredizas (medio abiertas) con riel
def door(name, x0, y0, x1, y1):
    pbox(name, x0, y0, x1, y1, 0.02, DOOR - 0.02, MAT["puerta"], bevel=0.004)
door("Puerta_Dorm1_Sala", 325, 418.6, 405, 422.4)
door("Puerta_Bano_Sala", 700, 472.6, 780, 476.4)
door("Puerta_Dorm1_Bano", 451.5, 580, 455.4, 660)
door("Puerta_Bano_Dorm2", 806.6, 460, 810.4, 540)
for (x0, y0, x1, y1) in [(325, 418.6, 405, 422.4)]:
    pass

# ------------------------------------------------------------------ dormitorio 1
pbox("Alfombra_D1", 200, 440, 430, 660, 0, 0.012, MAT["alfombra"], bevel=0.003)
pbox("Cama1_Cabecero", 126.4, 452, 134, 647, 0.0, 1.05, MAT["cabecero"], bevel=0.04, seg=4, smooth=True)
pbox("Cama1_Base", 134, 454, 333, 645, 0.0, 0.28, MAT["madera"], bevel=0.01)
pbox("Cama1_Colchon", 134, 452, 335, 647, 0.28, 0.52, MAT["blanco"], bevel=0.04, seg=4, smooth=True)
pbox("Cama1_Edredon", 182, 449, 338, 650, 0.52, 0.60, MAT["tela_gris"], bevel=0.035, seg=4, smooth=True)
pbox("Cama1_Almohada_N", 140, 462, 176, 545, 0.52, 0.66, MAT["blanco"], bevel=0.07, seg=5, smooth=True)
pbox("Cama1_Almohada_S", 140, 555, 176, 638, 0.52, 0.66, MAT["blanco"], bevel=0.07, seg=5, smooth=True)
pbox("Cama1_Manta", 292, 452, 318, 647, 0.60, 0.63, MAT["tela_beige"], bevel=0.015, seg=3, smooth=True)
for nm, (y0, y1) in {"N": (420, 450), "S": (652, 692)}.items():
    pbox("Mesa_Noche_1" + nm, 128, y0, 168, y1, 0.0, 0.5, MAT["madera"], bevel=0.008)
    cx, cy = mx(148), my((y0 + y1) / 2)
    cyl("Lampara_Base_1" + nm, cx, cy, 0.5, 0.66, 0.035, MAT["negro"])
    cyl("Lampara_Pantalla_1" + nm, cx, cy, 0.66, 0.86, 0.11, MAT["blanco"], rx=0.085)

# cuadro sobre la cama 1 (pared oeste)
pbox("Cuadro1_Marco", 126.5, 495, 128.3, 605, 1.25, 1.85, MAT["negro"])
pbox("Cuadro1_Lienzo", 128.3, 498, 128.9, 602, 1.28, 1.82, MAT["tela_roja"])
pbox("Cuadro1_Franja", 128.9, 520, 129.4, 580, 1.40, 1.70, MAT["tela_beige"])

# vestidor
pbox("Vest_Repisa_Alta", 468.4, 392.4, 625.6, 459.6, 2.0, 2.03, MAT["madera"], bevel=0.004)
pbox("Vest_Repisa_Baja", 468.4, 392.4, 625.6, 459.6, 0.35, 0.38, MAT["madera"], bevel=0.004)
pbox("Vest_Barra", 470, 424, 624, 428, 1.74, 1.77, MAT["acero"])
xs = list(range(474, 616, 7))
for i, x in enumerate(xs):
    pbox("Ropa_%d" % i, x, 407, x + 2.6, 445, 0.80 + (i % 3) * 0.04, 1.72,
         fabric_mat("Ropa_%d" % i, CLOTHES[i % len(CLOTHES)], 0.2), bevel=0.004)

# ------------------------------------------------------------------ dormitorio 2 (espaldar al ventanal)
pbox("Alfombra_D2", 885, 440, 1150, 640, 0, 0.012, MAT["alfombra"], bevel=0.003)
pbox("Cama2_Cabecero", 916, 698.5, 1115, 705.6, 0.0, 1.10, MAT["cabecero"], bevel=0.04, seg=4, smooth=True)
pbox("Cama2_Base", 920, 497, 1111, 698.5, 0.0, 0.28, MAT["madera"], bevel=0.01)
pbox("Cama2_Colchon", 918, 495, 1113, 698.5, 0.28, 0.52, MAT["blanco"], bevel=0.04, seg=4, smooth=True)
pbox("Cama2_Edredon", 915, 495, 1116, 640, 0.52, 0.60, MAT["tela_gris"], bevel=0.035, seg=4, smooth=True)
pbox("Cama2_Almohada_I", 928, 660, 1010, 694, 0.52, 0.66, MAT["blanco"], bevel=0.07, seg=5, smooth=True)
pbox("Cama2_Almohada_D", 1021, 660, 1103, 694, 0.52, 0.66, MAT["blanco"], bevel=0.07, seg=5, smooth=True)
pbox("Cama2_Manta", 915, 560, 1116, 590, 0.60, 0.63, MAT["tela_beige"], bevel=0.015, seg=3, smooth=True)
for nm, (x0, x1) in {"I": (868, 912), "D": (1119, 1163)}.items():
    pbox("Mesa_Noche_2" + nm, x0, 662, x1, 700, 0.0, 0.5, MAT["madera"], bevel=0.008)
    cx, cy = mx((x0 + x1) / 2), my(681)
    cyl("Lampara_Base_2" + nm, cx, cy, 0.5, 0.66, 0.035, MAT["negro"])
    cyl("Lampara_Pantalla_2" + nm, cx, cy, 0.66, 0.86, 0.11, MAT["blanco"], rx=0.085)

# cuadro en la pared este del dormitorio 2
pbox("Cuadro2_Marco", 1204.5, 520, 1206.3, 620, 1.20, 1.80, MAT["negro"])
pbox("Cuadro2_Lienzo", 1203.9, 523, 1204.5, 617, 1.23, 1.77, MAT["tela_beige"])
pbox("Cuadro2_Forma", 1203.4, 548, 1203.9, 592, 1.35, 1.65, MAT["tela_gris"])

# ------------------------------------------------------------------ baño
for nm, (a, b) in {"I": (468.4, 625.6), "D": (638.4, 793.6)}.items():
    pbox("Piso_Bano_" + nm, a, 472.4, b, 705.6, 0.0, 0.004, MAT["baldosa"])
# lavamanos izquierdo (contra pared oeste)
pbox("Mueble_Lav_I", 470, 478, 534, 528, 0.12, 0.82, MAT["gabinete"], bevel=0.005)
pbox("Cubierta_Lav_I", 469.5, 476.5, 536, 529.5, 0.82, 0.86, MAT["meson"], bevel=0.004)
cyl("Lavabo_I", mx(503), my(503), 0.86, 0.90, 0.19, MAT["ceramica"], rx=0.17)
cyl("Grifo_I", mx(503), my(486), 0.86, 1.00, 0.012, MAT["acero"])
pbox("Espejo_I", 468.6, 485, 470, 521, 1.15, 1.95, MAT["espejo"])
# lavamanos derecho (contra pared norte)
pbox("Mueble_Lav_D", 700, 473, 788, 518, 0.12, 0.82, MAT["gabinete"], bevel=0.005)
pbox("Cubierta_Lav_D", 698.5, 473, 790, 520, 0.82, 0.86, MAT["meson"], bevel=0.004)
cyl("Lavabo_D", mx(745), my(497), 0.86, 0.90, 0.19, MAT["ceramica"], rx=0.17)
cyl("Grifo_D", mx(745), my(480), 0.86, 1.00, 0.012, MAT["acero"])
pbox("Espejo_D", 715, 473.4, 775, 474.8, 1.15, 1.95, MAT["espejo"])
# inodoro
pbox("Inodoro_Tanque", 565, 690, 605, 705.6, 0.0, 0.78, MAT["ceramica"], bevel=0.02, seg=4, smooth=True)
cyl("Inodoro_Taza", mx(585), my(668), 0.0, 0.42, 0.20, MAT["ceramica"], rx=0.17)
box("Inodoro_Asiento", mx(585) - 0.19, my(668) - 0.19, mx(585) + 0.19, my(668) + 0.19, 0.42, 0.45, MAT["ceramica"], bevel=0.02, seg=3, smooth=True)
# ducha
pbox("Ducha_Base", 650, 600, 788, 705.6, 0.0, 0.03, MAT["ceramica"], bevel=0.004)
pbox("Ducha_Cristal", 650, 598.8, 788, 600.2, 0.03, 2.0, MAT["vidrio"])
pbox("Ducha_Marco", 650, 598.2, 788, 600.8, 1.96, 2.0, MAT["aluminio"])
cyl("Ducha_Cabezal", mx(790), my(652), 2.05, 2.07, 0.09, MAT["acero"])
cyl("Ducha_Tubo", mx(792), my(652), 2.0, 2.08, 0.01, MAT["acero"])

# ------------------------------------------------------------------ sala
pbox("Alfombra_Sala", 270, 100, 486, 345, 0, 0.012, MAT["alfombra"], bevel=0.003)
pbox("Sofa_Base_N", 262, 95, 428, 175, 0.05, 0.28, MAT["tela_sofa"], bevel=0.02, seg=3, smooth=True)
pbox("Sofa_Base_O", 262, 175, 315, 325, 0.05, 0.28, MAT["tela_sofa"], bevel=0.02, seg=3, smooth=True)
pbox("Sofa_Resp_N", 262, 95, 428, 114, 0.28, 0.82, MAT["tela_sofa"], bevel=0.06, seg=4, smooth=True)
pbox("Sofa_Resp_O", 262, 114, 281, 325, 0.28, 0.82, MAT["tela_sofa"], bevel=0.06, seg=4, smooth=True)
pbox("Sofa_Brazo_E", 410, 114, 428, 175, 0.28, 0.62, MAT["tela_sofa"], bevel=0.06, seg=4, smooth=True)
pbox("Sofa_Brazo_S", 281, 307, 315, 325, 0.28, 0.62, MAT["tela_sofa"], bevel=0.06, seg=4, smooth=True)
for i, (a, b) in enumerate([(281, 345), (345, 410)]):
    pbox("Sofa_Cojin_N%d" % i, a, 114, b, 175, 0.28, 0.45, MAT["tela_sofa"], bevel=0.05, seg=4, smooth=True)
pbox("Sofa_Cojin_O0", 281, 175, 315, 245, 0.28, 0.45, MAT["tela_sofa"], bevel=0.05, seg=4, smooth=True)
pbox("Sofa_Cojin_O1", 281, 245, 315, 307, 0.28, 0.45, MAT["tela_sofa"], bevel=0.05, seg=4, smooth=True)
pbox("Cojin_Rojo", 296, 120, 334, 142, 0.45, 0.78, MAT["tela_roja"], bevel=0.07, seg=4, smooth=True, rotz=0.25)
pbox("Cojin_Gris1", 345, 120, 383, 142, 0.45, 0.78, MAT["tela_gris"], bevel=0.07, seg=4, smooth=True, rotz=-0.2)
pbox("Cojin_Gris2", 283, 205, 305, 243, 0.45, 0.78, MAT["tela_gris"], bevel=0.07, seg=4, smooth=True)
# planta
cyl("Maceta", mx(470), my(88), 0.0, 0.34, 0.15, MAT["maceta"], rx=0.19)
for i in range(7):
    a = i * 0.9
    sphere("Hoja_%d" % i, mx(470) + 0.14 * math.cos(a), my(88) + 0.14 * math.sin(a), 0.62 + 0.12 * (i % 3), 0.17, MAT["verde"], 0.7, 0.7, 1.4)

# ------------------------------------------------------------------ comedor
pbox("Alfombra_Comedor", 492, 150, 735, 365, 0, 0.012, MAT["alfombra"], bevel=0.003)
pbox("Mesa_Tapa", 540, 208, 685, 300, 0.72, 0.76, MAT["madera_oscura"], bevel=0.012, seg=3)
for nm, (lx, ly) in {"a": (545, 212), "b": (676, 212), "c": (545, 290), "d": (676, 290)}.items():
    pbox("Mesa_Pata_" + nm, lx, ly, lx + 4.5, ly + 4.5, 0.0, 0.72, MAT["madera_oscura"], bevel=0.004)
cyl("Florero", mx(612), my(254), 0.76, 1.00, 0.055, MAT["ceramica"], rx=0.04)
for i in range(5):
    sphere("Flor_%d" % i, mx(612) + 0.05 * math.cos(i * 1.3), my(254) + 0.05 * math.sin(i * 1.3), 1.05 + 0.04 * (i % 2), 0.045, MAT["tela_roja"])

def silla(nm, cx_px, y_near_px, hacia_norte):
    # silla 0.44 x 0.44 m; y_near_px = borde cercano a la mesa; hacia_norte: respaldo al norte
    x0, x1 = cx_px - 22, cx_px + 22
    if hacia_norte:
        y0, y1 = y_near_px - 44, y_near_px      # respaldo en y0 (norte)
        ry0, ry1 = y0, y0 + 3
    else:
        y0, y1 = y_near_px, y_near_px + 44      # respaldo en y1 (sur)
        ry0, ry1 = y1 - 3, y1
    pbox(nm + "_asiento", x0, y0, x1, y1, 0.43, 0.47, MAT["silla"], bevel=0.012, seg=3)
    for k, (lx, ly) in enumerate([(x0 + 2, y0 + 2), (x1 - 5, y0 + 2), (x0 + 2, y1 - 5), (x1 - 5, y1 - 5)]):
        pbox("%s_pata%d" % (nm, k), lx, ly, lx + 3, ly + 3, 0.0, 0.43, MAT["madera_oscura"], bevel=0.003)
    pbox(nm + "_respaldo", x0, ry0, x1, ry1, 0.47, 0.88, MAT["silla"], bevel=0.015, seg=3)
silla("Silla_NI", 584, 232, True)
silla("Silla_ND", 644, 232, True)
silla("Silla_SI", 584, 276, False)
silla("Silla_SD", 644, 276, False)

# ------------------------------------------------------------------ cocina
pbox("Nevera", 750, 58, 840, 150, 0.0, 1.85, MAT["nevera"], bevel=0.015, seg=3)
pbox("Nevera_Linea", 750, 149.4, 840, 150.6, 1.17, 1.19, MAT["negro"])
pbox("Nevera_Manija", 757, 150.5, 760, 151.5, 1.25, 1.75, MAT["negro"])
pbox("Nevera_Manija2", 757, 150.5, 760, 151.5, 0.7, 1.1, MAT["negro"])
def gabinetes(prefix, x0, y0, x1, y1, frente, n=None):
    """cuerpo + cubierta + puertas en el frente 'sur' o 'oeste'."""
    pbox(prefix + "_cuerpo", x0, y0, x1, y1, 0.10, 0.86, MAT["gabinete"], bevel=0.004)
    pbox(prefix + "_zocalo", x0 + 3, y0 + 3, x1 - 3, y1 - 3, 0.0, 0.10, MAT["negro"])
    pbox(prefix + "_cubierta", x0 - 1, y0 - 1, x1 + 1, y1 + 1, 0.86, 0.90, MAT["meson"], bevel=0.004)
    if frente == "sur":
        L = x1 - x0; n = n or max(1, round(L / 60))
        for i in range(n):
            a = x0 + L * i / n + 0.4; b = x0 + L * (i + 1) / n - 0.4
            pbox("%s_puerta%d" % (prefix, i), a, y1, b, y1 + 1.6, 0.12, 0.84, MAT["gabinete"], bevel=0.003)
            pbox("%s_mango%d" % (prefix, i), (a + b) / 2 - 8, y1 + 1.6, (a + b) / 2 + 8, y1 + 2.8, 0.74, 0.76, MAT["acero"])
    else:  # frente oeste
        L = y1 - y0; n = n or max(1, round(L / 60))
        for i in range(n):
            a = y0 + L * i / n + 0.4; b = y0 + L * (i + 1) / n - 0.4
            pbox("%s_puerta%d" % (prefix, i), x0 - 1.6, a, x0, b, 0.12, 0.84, MAT["gabinete"], bevel=0.003)
            pbox("%s_mango%d" % (prefix, i), x0 - 2.8, (a + b) / 2 - 8, x0 - 1.6, (a + b) / 2 + 8, 0.74, 0.76, MAT["acero"])
gabinetes("MesonA", 840, 58, 905, 138, "sur", 1)
gabinetes("MesonB", 975, 58, 1159, 138, "sur", 3)
gabinetes("MesonL", 1050, 138, 1159, 305, "oeste", 3)
pbox("Estufa", 905, 58, 975, 138, 0.10, 0.86, MAT["acero"], bevel=0.005)
pbox("Estufa_Horno", 907, 138, 973, 139.4, 0.18, 0.80, MAT["negro"])
pbox("Estufa_Mango", 910, 139.4, 970, 140.6, 0.74, 0.77, MAT["acero"])
pbox("Estufa_Placa", 905, 58, 975, 138, 0.86, 0.885, MAT["negro"], bevel=0.003)
for i, (bx, by) in enumerate([(924, 78), (956, 78), (924, 116), (956, 116)]):
    cyl("Hornilla_%d" % i, mx(bx), my(by), 0.885, 0.895, 0.085 if i % 2 == 0 else 0.065, MAT["acero"], verts=24)
pbox("Fregadero_Plato", 1085, 185, 1145, 255, 0.90, 0.905, MAT["acero"])
pbox("Fregadero_Hondo", 1090, 190, 1140, 250, 0.905, 0.915, MAT["negro"])
cyl("Grifo_Cocina", mx(1114), my(180), 0.90, 1.12, 0.014, MAT["acero"])
box("Grifo_Pico", mx(1114) - 0.01, my(190), mx(1114) + 0.01, my(180) + 0.01, 1.10, 1.12, MAT["acero"])
pbox("Isla_Cuerpo", 780, 268, 875, 306, 0.10, 0.88, MAT["gabinete"], bevel=0.004)
pbox("Isla_Zocalo", 783, 271, 872, 303, 0.0, 0.10, MAT["negro"])
pbox("Isla_Cubierta", 776, 264, 879, 310, 0.88, 0.93, MAT["meson"], bevel=0.005)

# ------------------------------------------------------------------ entorno y luz
bm = bmesh.new(); bmesh.ops.create_grid(bm, x_segments=1, y_segments=1, size=60)
me = bpy.data.meshes.new("Terreno"); bm.to_mesh(me); bm.free()
terr = bpy.data.objects.new("Terreno", me); link(terr); terr.location = (5.5, 3.0, -0.07)
terr.data.materials.append(MAT["suelo"])

world = bpy.data.worlds.new("Cielo"); scene.world = world; world.use_nodes = True
wn = world.node_tree; wn.nodes.clear()
tcw = wn.nodes.new("ShaderNodeTexCoord")
sep = wn.nodes.new("ShaderNodeSeparateXYZ")
ramp = wn.nodes.new("ShaderNodeValToRGB")
ramp.color_ramp.elements[0].position = 0.45; ramp.color_ramp.elements[0].color = (0.62, 0.62, 0.60, 1)
ramp.color_ramp.elements[1].position = 0.80; ramp.color_ramp.elements[1].color = (0.52, 0.68, 0.95, 1)
e = ramp.color_ramp.elements.new(0.52); e.color = (0.95, 0.93, 0.88, 1)
mr = wn.nodes.new("ShaderNodeMapRange"); mr.inputs["From Min"].default_value = -1.0; mr.inputs["From Max"].default_value = 1.0
bg = wn.nodes.new("ShaderNodeBackground"); bg.inputs["Strength"].default_value = 1.0
wo = wn.nodes.new("ShaderNodeOutputWorld")
wn.links.new(tcw.outputs["Generated"], sep.inputs["Vector"])
wn.links.new(sep.outputs["Z"], mr.inputs["Value"])
wn.links.new(mr.outputs["Result"], ramp.inputs["Fac"])
wn.links.new(ramp.outputs["Color"], bg.inputs["Color"])
wn.links.new(bg.outputs["Background"], wo.inputs["Surface"])

sun = bpy.data.lights.new("Sol", "SUN"); sun.energy = 5.0; sun.angle = math.radians(1.2)
sun.color = (1.0, 0.93, 0.82)
sob = bpy.data.objects.new("Sol", sun); link(sob)
d = Vector((0.55, 0.65, -0.95)).normalized()      # luz viaja de SO a NE
sob.rotation_euler = d.to_track_quat("-Z", "Y").to_euler()

# ------------------------------------------------------------------ cámara
CAMS = {
    "aerial": dict(loc=(6.4, -1.9, 13.2), tgt=(5.4, 3.2, 0.0), lens=34),
    "dorm2": dict(loc=(8.2, 2.85, 2.15), tgt=(9.3, 0.5, 0.6), lens=17),
    "dorm1": dict(loc=(3.3, 2.85, 2.15), tgt=(1.2, 0.8, 0.6), lens=17),
    "cocina": dict(loc=(4.2, 3.7, 2.0), tgt=(9.3, 5.9, 0.8), lens=20),
}
c = CAMS.get(CAM) or dict(loc=tuple(float(v) for v in os.environ["CAM_LOC"].split(",")),
                         tgt=tuple(float(v) for v in os.environ["CAM_TGT"].split(",")),
                         lens=float(os.environ.get("CAM_LENS", "30")))
cd = bpy.data.cameras.new("Cam"); cd.lens = c["lens"]; cd.sensor_width = 36
cam = bpy.data.objects.new("Cam", cd); link(cam)
cam.location = c["loc"]
cam.rotation_euler = (Vector(c["tgt"]) - Vector(c["loc"])).to_track_quat("-Z", "Y").to_euler()
scene.camera = cam

# ------------------------------------------------------------------ render
r = scene.render
r.engine = "CYCLES"; r.resolution_x = RES_X; r.resolution_y = RES_Y; r.resolution_percentage = 100
r.image_settings.file_format = "PNG"; r.filepath = OUT
cy = scene.cycles
cy.device = "CPU"; cy.samples = SAMPLES; cy.use_denoising = True
try: cy.denoiser = "OPENIMAGEDENOISE"
except Exception: pass
cy.max_bounces = 6; cy.transmission_bounces = 6; cy.glossy_bounces = 4
cy.use_adaptive_sampling = True
for vt in ("AgX", "Filmic", "Standard"):
    try:
        scene.view_settings.view_transform = vt; break
    except Exception:
        continue
try: scene.view_settings.look = "AgX - Medium High Contrast"
except Exception: pass
scene.view_settings.exposure = -0.5
bpy.ops.render.render(write_still=True)
print("LISTO", OUT, "view_transform=", scene.view_settings.view_transform)
