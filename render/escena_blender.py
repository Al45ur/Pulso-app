"""Escena del departamento a ESCALA REAL para renderizar con Blender (bpy) + Cycles.

Coordenadas en centímetros (x este, y norte, origen = esquina SO interior del dormitorio 1);
se convierten a metros al crear la geometría. Mismo diseño que la planta de index.html.
Variables de entorno: OUT, SAMPLES, RES_X, RES_Y, WALLH, CAM (aerial|dorm1|dorm2|cocina).
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
C = 0.01  # cm -> m


# ------------------------------------------------------------------ materiales
def new_mat(name, color, rough=0.5, metal=0.0, extra=None):
    m = bpy.data.materials.new(name)
    try: m.use_nodes = True
    except Exception: pass
    b = m.node_tree.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = (*color, 1.0)
    b.inputs["Roughness"].default_value = rough
    b.inputs["Metallic"].default_value = metal
    for k, v in (extra or {}).items():
        b.inputs[k].default_value = v
    return m


def srgb(r, g, b):
    f = lambda c: ((c / 255 + 0.055) / 1.055) ** 2.4 if c / 255 > 0.04045 else c / 255 / 12.92
    return (f(r), f(g), f(b))


def wood_floor_mat():
    m = bpy.data.materials.new("Piso_Madera"); m.use_nodes = True
    nt = m.node_tree; nt.nodes.clear()
    out = nt.nodes.new("ShaderNodeOutputMaterial"); bsdf = nt.nodes.new("ShaderNodeBsdfPrincipled")
    tc = nt.nodes.new("ShaderNodeTexCoord"); brick = nt.nodes.new("ShaderNodeTexBrick")
    brick.offset = 0.4; brick.offset_frequency = 2
    brick.inputs["Color1"].default_value = (*srgb(190, 140, 95), 1)
    brick.inputs["Color2"].default_value = (*srgb(165, 115, 72), 1)
    brick.inputs["Mortar"].default_value = (*srgb(60, 40, 25), 1)
    brick.inputs["Mortar Size"].default_value = 0.004
    brick.inputs["Brick Width"].default_value = 1.2; brick.inputs["Row Height"].default_value = 0.15
    noise = nt.nodes.new("ShaderNodeTexNoise")
    noise.inputs["Scale"].default_value = 6.0; noise.inputs["Detail"].default_value = 8.0
    mapn = nt.nodes.new("ShaderNodeMapping"); mapn.inputs["Scale"].default_value = (1.0, 28.0, 1.0)
    mix = nt.nodes.new("ShaderNodeMix"); mix.data_type = "RGBA"; mix.blend_type = "MULTIPLY"
    mix.inputs[0].default_value = 0.35
    bump = nt.nodes.new("ShaderNodeBump"); bump.inputs["Strength"].default_value = 0.15
    nt.links.new(tc.outputs["Object"], brick.inputs["Vector"])
    nt.links.new(tc.outputs["Object"], mapn.inputs["Vector"])
    nt.links.new(mapn.outputs["Vector"], noise.inputs["Vector"])
    nt.links.new(brick.outputs["Color"], mix.inputs[6]); nt.links.new(noise.outputs["Fac"], mix.inputs[7])
    nt.links.new(mix.outputs[2], bsdf.inputs["Base Color"])
    nt.links.new(noise.outputs["Fac"], bump.inputs["Height"]); nt.links.new(bump.outputs["Normal"], bsdf.inputs["Normal"])
    bsdf.inputs["Roughness"].default_value = 0.38
    nt.links.new(bsdf.outputs["BSDF"], out.inputs["Surface"])
    return m


def tile_mat(color, size=0.6, mortar=0.006):
    m = bpy.data.materials.new("Baldosa"); m.use_nodes = True
    nt = m.node_tree; nt.nodes.clear()
    out = nt.nodes.new("ShaderNodeOutputMaterial"); bsdf = nt.nodes.new("ShaderNodeBsdfPrincipled")
    tc = nt.nodes.new("ShaderNodeTexCoord"); brick = nt.nodes.new("ShaderNodeTexBrick")
    brick.offset = 0.0
    brick.inputs["Color1"].default_value = (*color, 1)
    brick.inputs["Color2"].default_value = (*[c * 0.93 for c in color], 1)
    brick.inputs["Mortar"].default_value = (*[c * 0.55 for c in color], 1)
    brick.inputs["Mortar Size"].default_value = mortar
    brick.inputs["Brick Width"].default_value = size; brick.inputs["Row Height"].default_value = size
    nt.links.new(tc.outputs["Object"], brick.inputs["Vector"])
    nt.links.new(brick.outputs["Color"], bsdf.inputs["Base Color"])
    bsdf.inputs["Roughness"].default_value = 0.2
    nt.links.new(bsdf.outputs["BSDF"], out.inputs["Surface"])
    return m


def fabric_mat(name, color, bump=0.25, rough=0.95):
    m = new_mat(name, color, rough)
    nt = m.node_tree; b = nt.nodes["Principled BSDF"]
    n = nt.nodes.new("ShaderNodeTexNoise"); n.inputs["Scale"].default_value = 900.0
    bp = nt.nodes.new("ShaderNodeBump"); bp.inputs["Strength"].default_value = bump
    nt.links.new(n.outputs["Fac"], bp.inputs["Height"]); nt.links.new(bp.outputs["Normal"], b.inputs["Normal"])
    return m


MAT = {
    "pared": new_mat("Pared", srgb(238, 235, 228), 0.92), "piso": wood_floor_mat(), "baldosa": tile_mat(srgb(214, 216, 218)),
    "madera_oscura": new_mat("Madera_Mesa", srgb(110, 70, 44), 0.35), "madera": new_mat("Madera_Clara", srgb(176, 132, 92), 0.45),
    "tela_sofa": fabric_mat("Tela_Sofa", srgb(222, 210, 190)), "tela_gris": fabric_mat("Tela_Gris", srgb(92, 92, 98)),
    "tela_roja": fabric_mat("Tela_Roja", srgb(140, 38, 34)), "tela_beige": fabric_mat("Tela_Beige", srgb(196, 184, 164)),
    "blanco": fabric_mat("Ropa_Blanca", srgb(244, 244, 242), 0.15), "cabecero": fabric_mat("Cabecero", srgb(120, 118, 122), 0.2),
    "silla": new_mat("Silla", srgb(222, 214, 198), 0.7), "acero": new_mat("Acero", srgb(205, 208, 212), 0.4, 0.25),
    "nevera": new_mat("Nevera", srgb(196, 200, 205), 0.28, 0.0, {"Coat Weight": 0.3}),
    "negro": new_mat("Negro", srgb(28, 28, 30), 0.35, 0.3), "meson": new_mat("Meson_Piedra", srgb(205, 198, 186), 0.3),
    "gabinete": new_mat("Gabinete", srgb(226, 224, 220), 0.5), "ceramica": new_mat("Ceramica", srgb(246, 246, 246), 0.08),
    "vidrio": new_mat("Vidrio", (0.9, 0.95, 1.0), 0.0, 0.0, {"Transmission Weight": 1.0, "IOR": 1.45}),
    "puerta": new_mat("Puerta", srgb(194, 150, 100), 0.45), "aluminio": new_mat("Aluminio", srgb(35, 36, 38), 0.4, 0.8),
    "espejo": new_mat("Espejo", (0.9, 0.9, 0.92), 0.02, 1.0), "suelo": new_mat("Suelo", srgb(150, 150, 146), 0.9),
    "alfombra": fabric_mat("Alfombra", srgb(214, 204, 186), 0.4), "verde": new_mat("Planta", srgb(60, 110, 50), 0.6),
    "maceta": new_mat("Maceta", srgb(210, 205, 195), 0.7),
}
CLOTHES = [srgb(210, 210, 205), srgb(70, 90, 120), srgb(150, 60, 55), srgb(40, 40, 44), srgb(190, 170, 130),
           srgb(90, 120, 90), srgb(230, 225, 215), srgb(60, 60, 70)]


# ------------------------------------------------------------------ geometría (cm -> m)
def link(ob): col.objects.link(ob); return ob


def box(name, x0, y0, x1, y1, z0, z1, mat, bevel=0.0, seg=3, smooth=False, rotz=0.0):
    """Caja en CENTÍMETROS en planta (x0<x1, y0<y1) y z en METROS."""
    X0, X1, Y0, Y1 = x0 * C, x1 * C, y0 * C, y1 * C
    bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1.0)
    for v in bm.verts:
        v.co = Vector(((X1 - X0) * v.co.x, (Y1 - Y0) * v.co.y, (z1 - z0) * v.co.z))
    me = bpy.data.meshes.new(name); bm.to_mesh(me); bm.free()
    ob = bpy.data.objects.new(name, me); link(ob)
    ob.location = ((X0 + X1) / 2, (Y0 + Y1) / 2, (z0 + z1) / 2)
    if rotz: ob.rotation_euler = (0, 0, rotz)
    ob.data.materials.append(mat)
    if bevel > 0:
        b = ob.modifiers.new("b", "BEVEL"); b.width = bevel; b.segments = seg; b.limit_method = "ANGLE"
    if smooth:
        for p in me.polygons: p.use_smooth = True
    return ob


def cyl(name, x, y, z0, z1, r, mat, rx=None, verts=24):
    bm = bmesh.new()
    bmesh.ops.create_cone(bm, cap_ends=True, segments=verts, radius1=r, radius2=(rx if rx is not None else r), depth=z1 - z0)
    me = bpy.data.meshes.new(name); bm.to_mesh(me); bm.free()
    ob = bpy.data.objects.new(name, me); link(ob); ob.location = (x * C, y * C, (z0 + z1) / 2)
    for p in me.polygons: p.use_smooth = True
    ob.data.materials.append(mat); return ob


def sphere(name, x, y, z, r, mat, sx=1, sy=1, sz=1):
    bm = bmesh.new(); bmesh.ops.create_uvsphere(bm, u_segments=20, v_segments=12, radius=r)
    me = bpy.data.meshes.new(name); bm.to_mesh(me); bm.free()
    ob = bpy.data.objects.new(name, me); link(ob); ob.location = (x * C, y * C, z); ob.scale = (sx, sy, sz)
    for p in me.polygons: p.use_smooth = True
    ob.data.materials.append(mat); return ob


DOOR_H = 2.05
WIN0, WIN1 = 0.76, 2.13


def wall(name, x0, y0, x1, y1, notches=(), windows=(), height=None):
    """Pared (cm). notches: [(a0,a1)] puertas desde el piso; windows: [(a0,a1,z0,z1)]; a* sobre el eje largo."""
    h = WALLH if height is None else height
    ob = box(name, x0, y0, x1, y1, 0, h, MAT["pared"])
    horiz = (x1 - x0) >= (y1 - y0)
    cutters = []
    for (a0, a1) in notches:
        cutters.append(box(name + "_p", a0, y0 - 3, a1, y1 + 3, -0.1, DOOR_H, MAT["pared"]) if horiz
                       else box(name + "_p", x0 - 3, a0, x1 + 3, a1, -0.1, DOOR_H, MAT["pared"]))
    for (a0, a1, z0, z1) in windows:
        cutters.append(box(name + "_v", a0, y0 - 3, a1, y1 + 3, z0, z1, MAT["pared"]) if horiz
                       else box(name + "_v", x0 - 3, a0, x1 + 3, a1, z0, z1, MAT["pared"]))
    for ct in cutters:
        m = ob.modifiers.new("cut", "BOOLEAN"); m.object = ct; m.operation = "DIFFERENCE"; m.solver = "EXACT"
        ct.hide_render = True; ct.hide_viewport = True
    return ob


# ------------------------------------------------------------------ estructura (cm)
# parámetros de la planta
D1W = D1H = 305; D2W = D2H = 270; GAP = 240; T = 12
E1 = D1W; X2 = D1W + GAP; N1 = D1H + T; SN = N1 + 270
SW0, SE = 100, 785
BATH_D, CLOS_D = 152, 55
CL0, CL1 = E1 + T, E1 + T + 104; DV0, DV1 = CL1, CL1 + T; RM0, RM1 = DV1, X2 - T

# losa / piso
outline = [(-T, -T), (X2 + D2W + T, -T), (X2 + D2W + T, D2H + T), (SE + T, D2H + T), (SE + T, SN + T),
           (SW0 - T, SN + T), (SW0 - T, N1), (-T, N1)]
bm = bmesh.new()
vs = [bm.verts.new((x * C, y * C, 0.0)) for (x, y) in outline]
f = bm.faces.new(vs)
if f.normal.z < 0: f.normal_flip()
ext = bmesh.ops.extrude_face_region(bm, geom=[f])
for v in [e for e in ext["geom"] if isinstance(e, bmesh.types.BMVert)]: v.co.z = -0.06
bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
me = bpy.data.meshes.new("Piso"); bm.to_mesh(me); bm.free()
piso = bpy.data.objects.new("Piso", me); link(piso); piso.data.materials.append(MAT["piso"])

# paredes
wall("Pared_Sur", -T, -T, X2 + D2W + T, 0, windows=[(52, 252, WIN0, WIN1), (X2 + 35, X2 + 235, WIN0, WIN1)])
wall("Pared_D1_Oeste", -T, 0, 0, D1H)
wall("Pared_D1_Norte", -T, D1H, E1 + T, N1, notches=[(195, 275)])
wall("Pared_D1_Este", E1, 0, E1 + T, D1H, notches=[(20, 100), (167, 217)])
wall("Pared_Vestidor_Norte", CL0, BATH_D + T + CLOS_D, DV1, BATH_D + T + CLOS_D + T)
wall("Pared_Divisor", DV0, 0, DV1, BATH_D + T + CLOS_D)
wall("Pared_Bano_Norte_Izq", CL0, BATH_D, DV0, BATH_D + T)
wall("Pared_Bano_Norte_Der", RM0, BATH_D, RM1, BATH_D + T, notches=[(RM0 + 10, RM0 + 90)])
wall("Pared_D2_Oeste", X2 - T, 0, X2, D2H + T, notches=[(72, 152)])
wall("Pared_D2_Norte", X2 + 80, D2H, X2 + D2W + T, D2H + T)
wall("Pared_D2_Este", X2 + D2W, 0, X2 + D2W + T, D2H)
wall("Pared_Sala_Oeste", SW0 - T, N1, SW0, SN)
wall("Pared_Sala_Norte", SW0 - T, SN, SE + T, SN + T)
wall("Pared_Sala_Este", SE, D2H + T, SE + T, SN)

# ventanales: vidrio + marco (2.0 m, estimados)
for nm, (a, b) in {"D1": (52, 252), "D2": (X2 + 35, X2 + 235)}.items():
    box("Vidrio_" + nm, a, -6.4, b, -5.6, WIN0, WIN1, MAT["vidrio"])
    t = 0.04
    box("Marco_Inf_" + nm, a, -8, b, -4, WIN0, WIN0 + t, MAT["aluminio"])
    box("Marco_Sup_" + nm, a, -8, b, -4, WIN1 - t, WIN1, MAT["aluminio"])
    box("Marco_Izq_" + nm, a, -8, a + 4, -4, WIN0, WIN1, MAT["aluminio"])
    box("Marco_Der_" + nm, b - 4, -8, b, -4, WIN0, WIN1, MAT["aluminio"])
    box("Marco_Med_" + nm, (a + b) / 2 - 2, -8, (a + b) / 2 + 2, -4, WIN0, WIN1, MAT["aluminio"])

# puertas: corredizas medio abiertas (D1, D3, D4) y batiente del baño al hueco
def hoja(name, x0, y0, x1, y1): box(name, x0, y0, x1, y1, 0.02, DOOR_H - 0.02, MAT["puerta"], bevel=0.004)
hoja("Puerta_Dorm1_Sala", 155, D1H - 4, 235, D1H)                 # corre hacia el oeste, cara sur del muro
hoja("Puerta_Dorm1_Bano", E1 - 4, 60, E1, 140)                    # corre hacia el norte, cara oeste del muro
hoja("Puerta_Bano_Dorm2", X2, 106, X2 + 4, 186)                   # corre hacia el norte, cara este del muro
hoja("Puerta_Bano_Hueco", RM0 + 90, BATH_D + T, RM0 + 94, BATH_D + T + 80)   # batiente abierta 90°

# ------------------------------------------------------------------ dormitorio 1 (3.05 x 3.05)
by0 = (D1H - 150) // 2
box("Alfombra_D1", 40, by0 - 50, 250, by0 + 200, 0, 0.012, MAT["alfombra"], bevel=0.003)
box("Cama1_Cabecero", 0.5, by0, 8, by0 + 150, 0.0, 1.05, MAT["cabecero"], bevel=0.04, seg=4, smooth=True)
box("Cama1_Base", 8, by0 + 2, 188, by0 + 148, 0.0, 0.28, MAT["madera"], bevel=0.01)
box("Cama1_Colchon", 8, by0, 190, by0 + 150, 0.28, 0.52, MAT["blanco"], bevel=0.04, seg=4, smooth=True)
box("Cama1_Edredon", 55, by0 - 2, 192, by0 + 152, 0.52, 0.60, MAT["tela_gris"], bevel=0.035, seg=4, smooth=True)
box("Cama1_Almohada_S", 14, by0 + 8, 48, by0 + 70, 0.52, 0.66, MAT["blanco"], bevel=0.07, seg=5, smooth=True)
box("Cama1_Almohada_N", 14, by0 + 80, 48, by0 + 142, 0.52, 0.66, MAT["blanco"], bevel=0.07, seg=5, smooth=True)
box("Cama1_Manta", 150, by0, 175, by0 + 150, 0.60, 0.63, MAT["tela_beige"], bevel=0.015, seg=3, smooth=True)
for nm, (y0, y1) in {"S": (by0 - 46, by0 - 6), "N": (by0 + 156, by0 + 196)}.items():
    box("Mesa_Noche_1" + nm, 0.5, y0, 40.5, y1, 0.0, 0.5, MAT["madera"], bevel=0.008)
    cyl("Lampara_Base_1" + nm, 20, (y0 + y1) / 2, 0.5, 0.66, 0.035, MAT["negro"])
    cyl("Lampara_Pantalla_1" + nm, 20, (y0 + y1) / 2, 0.66, 0.86, 0.11, MAT["blanco"], rx=0.085)
box("Cuadro1_Marco", 0.5, by0 + 25, 2.3, by0 + 125, 1.25, 1.85, MAT["negro"])
box("Cuadro1_Lienzo", 2.3, by0 + 28, 2.9, by0 + 122, 1.28, 1.82, MAT["tela_roja"])
box("Cuadro1_Franja", 2.9, by0 + 45, 3.4, by0 + 105, 1.40, 1.70, MAT["tela_beige"])

# vestidor (1.04 x 0.55)
vy0, vy1 = BATH_D + T, BATH_D + T + CLOS_D
box("Vest_Repisa_Alta", CL0, vy0, CL1, vy1, 2.0, 2.03, MAT["madera"], bevel=0.004)
box("Vest_Repisa_Baja", CL0, vy0, CL1, vy1, 0.35, 0.38, MAT["madera"], bevel=0.004)
box("Vest_Barra", CL0 + 2, (vy0 + vy1) / 2 - 1, CL1 - 2, (vy0 + vy1) / 2 + 1, 1.74, 1.77, MAT["acero"])
for i, x in enumerate(range(CL0 + 6, CL1 - 8, 10)):
    box("Ropa_%d" % i, x, vy0 + 8, x + 2.6, vy1 - 8, 0.80 + (i % 3) * 0.04, 1.72,
        fabric_mat("Ropa_%d" % i, CLOTHES[i % len(CLOTHES)], 0.2), bevel=0.004)

# ------------------------------------------------------------------ dormitorio 2 (2.70 x 2.70)
b2x = X2 + D2W - 150
box("Alfombra_D2", X2 + 25, 0, X2 + D2W - 5, 215, 0, 0.012, MAT["alfombra"], bevel=0.003)
box("Cama2_Cabecero", b2x, 0.5, b2x + 150, 8, 0.0, 1.10, MAT["cabecero"], bevel=0.04, seg=4, smooth=True)
box("Cama2_Base", b2x + 2, 8, b2x + 148, 188, 0.0, 0.28, MAT["madera"], bevel=0.01)
box("Cama2_Colchon", b2x, 8, b2x + 150, 190, 0.28, 0.52, MAT["blanco"], bevel=0.04, seg=4, smooth=True)
box("Cama2_Edredon", b2x - 2, 50, b2x + 152, 192, 0.52, 0.60, MAT["tela_gris"], bevel=0.035, seg=4, smooth=True)
box("Cama2_Almohada_I", b2x + 8, 14, b2x + 70, 48, 0.52, 0.66, MAT["blanco"], bevel=0.07, seg=5, smooth=True)
box("Cama2_Almohada_D", b2x + 80, 14, b2x + 142, 48, 0.52, 0.66, MAT["blanco"], bevel=0.07, seg=5, smooth=True)
box("Cama2_Manta", b2x, 100, b2x + 150, 125, 0.60, 0.63, MAT["tela_beige"], bevel=0.015, seg=3, smooth=True)
box("Mesa_Noche_2", b2x - 43, 0.5, b2x - 3, 40.5, 0.0, 0.5, MAT["madera"], bevel=0.008)
cyl("Lampara_Base_2", b2x - 23, 20, 0.5, 0.66, 0.035, MAT["negro"])
cyl("Lampara_Pantalla_2", b2x - 23, 20, 0.66, 0.86, 0.11, MAT["blanco"], rx=0.085)
box("Cuadro2_Marco", X2 + D2W - 1.8, 90, X2 + D2W, 190, 1.20, 1.80, MAT["negro"])
box("Cuadro2_Lienzo", X2 + D2W - 2.4, 93, X2 + D2W - 1.8, 187, 1.23, 1.77, MAT["tela_beige"])
box("Cuadro2_Forma", X2 + D2W - 2.9, 118, X2 + D2W - 2.4, 162, 1.35, 1.65, MAT["tela_gris"])

# ------------------------------------------------------------------ baño (2 módulos 1.04 / 1.00 x 1.52)
box("Piso_Bano_I", CL0, 0, CL1, BATH_D, 0.0, 0.004, MAT["baldosa"])
box("Piso_Bano_D", RM0, 0, RM1, BATH_D, 0.0, 0.004, MAT["baldosa"])
# módulo izquierdo: lavabo al norte, inodoro al sur
box("Mueble_Lav_I", 340, 112, 400, 152, 0.12, 0.82, MAT["gabinete"], bevel=0.005)
box("Cubierta_Lav_I", 338.5, 110.5, 401.5, 152, 0.82, 0.86, MAT["meson"], bevel=0.004)
cyl("Lavabo_I", 370, 132, 0.86, 0.90, 0.19, MAT["ceramica"], rx=0.17)
cyl("Grifo_I", 370, 146, 0.86, 1.00, 0.012, MAT["acero"])
box("Espejo_I", 345, 150.6, 395, 152, 1.15, 1.95, MAT["espejo"])
box("Inodoro_Tanque", 351, 0.5, 389, 18, 0.0, 0.78, MAT["ceramica"], bevel=0.02, seg=4, smooth=True)
cyl("Inodoro_Taza", 370, 42, 0.0, 0.42, 0.20, MAT["ceramica"], rx=0.17)
box("Inodoro_Asiento", 351, 24, 389, 62, 0.42, 0.45, MAT["ceramica"], bevel=0.02, seg=3, smooth=True)
# módulo derecho: ducha al sur, lavabo contra el divisor
box("Ducha_Base", RM0, 0, RM1 - 20, 68, 0.0, 0.03, MAT["ceramica"], bevel=0.004)
box("Ducha_Cristal", RM0, 67, RM1 - 20, 68.4, 0.03, 2.0, MAT["vidrio"])
box("Ducha_Marco", RM0, 66.6, RM1 - 20, 68.8, 1.96, 2.0, MAT["aluminio"])
cyl("Ducha_Cabezal", RM1 - 40, 20, 2.05, 2.07, 0.09, MAT["acero"])
box("Mueble_Lav_D", RM0, 90, RM0 + 38, 140, 0.12, 0.82, MAT["gabinete"], bevel=0.005)
box("Cubierta_Lav_D", RM0, 88.5, RM0 + 39.5, 141.5, 0.82, 0.86, MAT["meson"], bevel=0.004)
cyl("Lavabo_D", RM0 + 17, 115, 0.86, 0.90, 0.17, MAT["ceramica"], rx=0.15)
box("Espejo_D", RM0 - 1.4, 95, RM0, 135, 1.15, 1.95, MAT["espejo"])

# ------------------------------------------------------------------ sala
n0 = SN - 90
box("Alfombra_Sala", 105, 360, 320, 540, 0, 0.012, MAT["alfombra"], bevel=0.003)
box("Sofa_Base_N", 100, n0, 300, SN, 0.05, 0.28, MAT["tela_sofa"], bevel=0.02, seg=3, smooth=True)
box("Sofa_Base_O", 100, n0 - 130, 190, n0, 0.05, 0.28, MAT["tela_sofa"], bevel=0.02, seg=3, smooth=True)
box("Sofa_Resp_N", 100, SN - 19, 300, SN, 0.28, 0.82, MAT["tela_sofa"], bevel=0.06, seg=4, smooth=True)
box("Sofa_Resp_O", 100, n0 - 130, 119, SN - 19, 0.28, 0.82, MAT["tela_sofa"], bevel=0.06, seg=4, smooth=True)
box("Sofa_Brazo_E", 282, n0, 300, SN - 19, 0.28, 0.62, MAT["tela_sofa"], bevel=0.06, seg=4, smooth=True)
box("Sofa_Brazo_S", 119, n0 - 130, 190, n0 - 112, 0.28, 0.62, MAT["tela_sofa"], bevel=0.06, seg=4, smooth=True)
for i, (a, b) in enumerate([(119, 210), (210, 282)]):
    box("Sofa_Cojin_N%d" % i, a, n0, b, SN - 19, 0.28, 0.45, MAT["tela_sofa"], bevel=0.05, seg=4, smooth=True)
box("Sofa_Cojin_O", 119, n0 - 112, 190, n0, 0.28, 0.45, MAT["tela_sofa"], bevel=0.05, seg=4, smooth=True)
box("Cojin_Rojo", 140, SN - 40, 175, SN - 20, 0.45, 0.78, MAT["tela_roja"], bevel=0.07, seg=4, smooth=True, rotz=0.25)
box("Cojin_Gris1", 235, SN - 40, 270, SN - 20, 0.45, 0.78, MAT["tela_gris"], bevel=0.07, seg=4, smooth=True, rotz=-0.2)
box("Cojin_Gris2", 122, n0 - 90, 142, n0 - 55, 0.45, 0.78, MAT["tela_gris"], bevel=0.07, seg=4, smooth=True)
cyl("Maceta", 320, SN - 21, 0.0, 0.34, 0.15, MAT["maceta"], rx=0.19)
for i in range(7):
    a = i * 0.9
    sphere("Hoja_%d" % i, 320 + 14 * math.cos(a), SN - 21 + 14 * math.sin(a), 0.62 + 0.12 * (i % 3), 0.17, MAT["verde"], 0.7, 0.7, 1.4)

# comedor
ty = SN - 156
box("Alfombra_Comedor", 320, ty - 85, 520, ty + 85, 0, 0.012, MAT["alfombra"], bevel=0.003)
box("Mesa_Tapa", 350, ty - 40, 490, ty + 40, 0.72, 0.76, MAT["madera_oscura"], bevel=0.012, seg=3)
for nm, (lx, ly) in {"a": (353, ty - 37), "b": (483, ty - 37), "c": (353, ty + 33), "d": (483, ty + 33)}.items():
    box("Mesa_Pata_" + nm, lx, ly, lx + 4.5, ly + 4.5, 0.0, 0.72, MAT["madera_oscura"], bevel=0.004)
cyl("Florero", 420, ty, 0.76, 1.00, 0.055, MAT["ceramica"], rx=0.04)
for i in range(5):
    sphere("Flor_%d" % i, 420 + 5 * math.cos(i * 1.3), ty + 5 * math.sin(i * 1.3), 1.05 + 0.04 * (i % 2), 0.045, MAT["tela_roja"])

def silla(nm, cx, y0, y1, respaldo_norte):
    x0, x1 = cx - 22, cx + 22
    ry0, ry1 = (y1 - 3, y1) if respaldo_norte else (y0, y0 + 3)
    box(nm + "_asiento", x0, y0, x1, y1, 0.43, 0.47, MAT["silla"], bevel=0.012, seg=3)
    for k, (lx, ly) in enumerate([(x0 + 2, y0 + 2), (x1 - 5, y0 + 2), (x0 + 2, y1 - 5), (x1 - 5, y1 - 5)]):
        box("%s_pata%d" % (nm, k), lx, ly, lx + 3, ly + 3, 0.0, 0.43, MAT["madera_oscura"], bevel=0.003)
    box(nm + "_respaldo", x0, ry0, x1, ry1, 0.47, 0.88, MAT["silla"], bevel=0.015, seg=3)
silla("Silla_NI", 385, ty + 35, ty + 79, True); silla("Silla_ND", 455, ty + 35, ty + 79, True)
silla("Silla_SI", 385, ty - 79, ty - 35, False); silla("Silla_SD", 455, ty - 79, ty - 35, False)

# ------------------------------------------------------------------ cocina (estimada)
box("Nevera", 552, SN - 70, 622, SN, 0.0, 1.85, MAT["nevera"], bevel=0.015, seg=3)
box("Nevera_Linea", 552, SN - 70.6, 622, SN - 69.4, 1.17, 1.19, MAT["negro"])
box("Nevera_Manija", 558, SN - 71.6, 561, SN - 70.6, 1.25, 1.75, MAT["negro"])
box("Nevera_Manija2", 558, SN - 71.6, 561, SN - 70.6, 0.70, 1.10, MAT["negro"])

def gabinetes(prefix, x0, y0, x1, y1, frente, n):
    box(prefix + "_cuerpo", x0, y0, x1, y1, 0.10, 0.86, MAT["gabinete"], bevel=0.004)
    box(prefix + "_zocalo", x0 + 3, y0 + 3, x1 - 3, y1 - 3, 0.0, 0.10, MAT["negro"])
    box(prefix + "_cubierta", x0 - 1, y0 - 1, x1 + 1, y1 + 1, 0.86, 0.90, MAT["meson"], bevel=0.004)
    if frente == "sur":
        L = x1 - x0
        for i in range(n):
            a = x0 + L * i / n + 0.4; b = x0 + L * (i + 1) / n - 0.4
            box("%s_puerta%d" % (prefix, i), a, y0 - 1.6, b, y0, 0.12, 0.84, MAT["gabinete"], bevel=0.003)
            box("%s_mango%d" % (prefix, i), (a + b) / 2 - 8, y0 - 2.8, (a + b) / 2 + 8, y0 - 1.6, 0.74, 0.76, MAT["acero"])
    else:
        L = y1 - y0
        for i in range(n):
            a = y0 + L * i / n + 0.4; b = y0 + L * (i + 1) / n - 0.4
            box("%s_puerta%d" % (prefix, i), x0 - 1.6, a, x0, b, 0.12, 0.84, MAT["gabinete"], bevel=0.003)
            box("%s_mango%d" % (prefix, i), x0 - 2.8, (a + b) / 2 - 8, x0 - 1.6, (a + b) / 2 + 8, 0.74, 0.76, MAT["acero"])
gabinetes("MesonA", 622, SN - 60, 662, SN, "sur", 1)
gabinetes("MesonB", 722, SN - 60, SE, SN, "sur", 1)
gabinetes("MesonL", SE - 60, SN - 190, SE, SN - 60, "oeste", 2)
box("Estufa", 662, SN - 60, 722, SN, 0.10, 0.86, MAT["acero"], bevel=0.005)
box("Estufa_Horno", 664, SN - 61.4, 720, SN - 60, 0.18, 0.80, MAT["negro"])
box("Estufa_Mango", 668, SN - 62.6, 716, SN - 61.4, 0.74, 0.77, MAT["acero"])
box("Estufa_Placa", 662, SN - 60, 722, SN, 0.86, 0.885, MAT["negro"], bevel=0.003)
for i, (bx, by) in enumerate([(676, SN - 45), (708, SN - 45), (676, SN - 15), (708, SN - 15)]):
    cyl("Hornilla_%d" % i, bx, by, 0.885, 0.895, 0.085 if i % 2 == 0 else 0.065, MAT["acero"])
box("Fregadero_Plato", SE - 48, SN - 156, SE - 8, SN - 91, 0.90, 0.905, MAT["acero"])
box("Fregadero_Hondo", SE - 44, SN - 152, SE - 12, SN - 95, 0.905, 0.915, MAT["negro"])
cyl("Grifo_Cocina", SE - 28, SN - 165, 0.90, 1.12, 0.014, MAT["acero"])
box("Grifo_Pico", SE - 30, SN - 165, SE - 26, SN - 150, 1.10, 1.12, MAT["acero"])
box("Isla_Cuerpo", 560, SN - 170, 650, SN - 130, 0.10, 0.88, MAT["gabinete"], bevel=0.004)
box("Isla_Zocalo", 563, SN - 167, 647, SN - 133, 0.0, 0.10, MAT["negro"])
box("Isla_Cubierta", 556, SN - 174, 654, SN - 126, 0.88, 0.93, MAT["meson"], bevel=0.005)

# ------------------------------------------------------------------ entorno y luz
bm = bmesh.new(); bmesh.ops.create_grid(bm, x_segments=1, y_segments=1, size=60)
me = bpy.data.meshes.new("Terreno"); bm.to_mesh(me); bm.free()
terr = bpy.data.objects.new("Terreno", me); link(terr); terr.location = (4.1, 3.0, -0.07)
terr.data.materials.append(MAT["suelo"])

world = bpy.data.worlds.new("Cielo"); scene.world = world; world.use_nodes = True
wn = world.node_tree; wn.nodes.clear()
tcw = wn.nodes.new("ShaderNodeTexCoord"); sep = wn.nodes.new("ShaderNodeSeparateXYZ"); ramp = wn.nodes.new("ShaderNodeValToRGB")
ramp.color_ramp.elements[0].position = 0.45; ramp.color_ramp.elements[0].color = (0.62, 0.62, 0.60, 1)
ramp.color_ramp.elements[1].position = 0.80; ramp.color_ramp.elements[1].color = (0.52, 0.68, 0.95, 1)
e = ramp.color_ramp.elements.new(0.52); e.color = (0.95, 0.93, 0.88, 1)
mr = wn.nodes.new("ShaderNodeMapRange"); mr.inputs["From Min"].default_value = -1.0; mr.inputs["From Max"].default_value = 1.0
bg = wn.nodes.new("ShaderNodeBackground"); bg.inputs["Strength"].default_value = 1.0
wo = wn.nodes.new("ShaderNodeOutputWorld")
wn.links.new(tcw.outputs["Generated"], sep.inputs["Vector"]); wn.links.new(sep.outputs["Z"], mr.inputs["Value"])
wn.links.new(mr.outputs["Result"], ramp.inputs["Fac"]); wn.links.new(ramp.outputs["Color"], bg.inputs["Color"])
wn.links.new(bg.outputs["Background"], wo.inputs["Surface"])

sun = bpy.data.lights.new("Sol", "SUN"); sun.energy = 5.0; sun.angle = math.radians(1.2); sun.color = (1.0, 0.93, 0.82)
sob = bpy.data.objects.new("Sol", sun); link(sob)
sob.rotation_euler = Vector((0.55, 0.65, -0.95)).normalized().to_track_quat("-Z", "Y").to_euler()

# ------------------------------------------------------------------ cámara
CAMS = {
    "aerial": dict(loc=(4.9, -0.4, 11.6), tgt=(4.1, 3.0, 0.0), lens=27),
    "dorm1": dict(loc=(2.9, 2.9, 2.15), tgt=(0.9, 1.3, 0.55), lens=17),
    "dorm2": dict(loc=(5.55, 2.6, 2.15), tgt=(7.4, 0.55, 0.55), lens=17),
    "cocina": dict(loc=(3.1, 3.5, 1.9), tgt=(7.3, 5.3, 0.8), lens=18),
}
c = CAMS.get(CAM) or dict(loc=tuple(float(v) for v in os.environ["CAM_LOC"].split(",")),
                         tgt=tuple(float(v) for v in os.environ["CAM_TGT"].split(",")),
                         lens=float(os.environ.get("CAM_LENS", "30")))
cd = bpy.data.cameras.new("Cam"); cd.lens = c["lens"]; cd.sensor_width = 36
cam = bpy.data.objects.new("Cam", cd); link(cam); cam.location = c["loc"]
cam.rotation_euler = (Vector(c["tgt"]) - Vector(c["loc"])).to_track_quat("-Z", "Y").to_euler()
scene.camera = cam

r = scene.render
r.engine = "CYCLES"; r.resolution_x = RES_X; r.resolution_y = RES_Y; r.resolution_percentage = 100
r.image_settings.file_format = "PNG"; r.filepath = OUT
cy = scene.cycles
cy.device = "CPU"; cy.samples = SAMPLES; cy.use_denoising = True
try: cy.denoiser = "OPENIMAGEDENOISE"
except Exception: pass
cy.max_bounces = 6; cy.transmission_bounces = 6; cy.glossy_bounces = 4; cy.use_adaptive_sampling = True
for vt in ("AgX", "Filmic", "Standard"):
    try: scene.view_settings.view_transform = vt; break
    except Exception: continue
scene.view_settings.exposure = -0.5
bpy.ops.render.render(write_still=True)
print("LISTO", OUT)
