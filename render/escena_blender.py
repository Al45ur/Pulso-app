"""Escena de la planta FINAL (plano del arquitecto) para renderizar con Blender (bpy) + Cycles.

Coordenadas en centímetros (x este, y norte, origen = esquina SO interior del dormitorio 1);
se convierten a metros al crear la geometría. Mismo diseño que la planta de index.html.
Los datos vienen de plano_data.py. Variables de entorno: OUT, SAMPLES, RES_X, RES_Y, CAM (aerial|dorm1|dorm2|sala|cocina).
"""
import bpy, bmesh, math, os, sys
from mathutils import Vector

OUT = os.environ.get("OUT", "/tmp/render.png")
SAMPLES = int(os.environ.get("SAMPLES", "32"))
RES_X = int(os.environ.get("RES_X", "960"))
RES_Y = int(os.environ.get("RES_Y", "600"))
WALLH = float(os.environ.get("WALLH", "2.4"))
CAM = os.environ.get("CAM", "aerial")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import plano_data as D

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
    "ropa_a": fabric_mat("Ropa_a", srgb(70, 90, 120), 0.2), "ropa_b": fabric_mat("Ropa_b", srgb(150, 60, 55), 0.2),
    "ropa_c": fabric_mat("Ropa_c", srgb(210, 210, 205), 0.2), "ropa_d": fabric_mat("Ropa_d", srgb(60, 60, 70), 0.2),
}
CLOTHES = [srgb(210, 210, 205), srgb(70, 90, 120), srgb(150, 60, 55), srgb(40, 40, 44), srgb(190, 170, 130),
           srgb(90, 120, 90), srgb(230, 225, 215), srgb(60, 60, 70)]


# ------------------------------------------------------------------ geometría (cm -> m)
def link(ob): col.objects.link(ob); return ob


def box(name, x0, y0, x1, y1, z0, z1, mat, bevel=0.0, seg=3):
    """Caja: planta en CENTÍMETROS, z en METROS."""
    X0, X1, Y0, Y1 = x0 * C, x1 * C, y0 * C, y1 * C
    bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1.0)
    for v in bm.verts:
        v.co = Vector(((X1 - X0) * v.co.x, (Y1 - Y0) * v.co.y, (z1 - z0) * v.co.z))
    me = bpy.data.meshes.new(name); bm.to_mesh(me); bm.free()
    ob = bpy.data.objects.new(name, me); link(ob)
    ob.location = ((X0 + X1) / 2, (Y0 + Y1) / 2, (z0 + z1) / 2)
    ob.data.materials.append(MAT[mat] if isinstance(mat, str) else mat)
    if bevel > 0:
        b = ob.modifiers.new("b", "BEVEL"); b.width = min(bevel, 0.4 * min(X1 - X0, Y1 - Y0, z1 - z0)); b.segments = seg; b.limit_method = "ANGLE"
    if bevel >= 0.03:
        for p in me.polygons: p.use_smooth = True
    return ob


def cyl(name, x, y, z0, z1, r, rx, mat, verts=24):
    bm = bmesh.new()
    bmesh.ops.create_cone(bm, cap_ends=True, segments=verts, radius1=r, radius2=rx, depth=z1 - z0)
    me = bpy.data.meshes.new(name); bm.to_mesh(me); bm.free()
    ob = bpy.data.objects.new(name, me); link(ob); ob.location = (x * C, y * C, (z0 + z1) / 2)
    for p in me.polygons: p.use_smooth = True
    ob.data.materials.append(MAT[mat]); return ob


def sphere(name, x, y, z, r, mat, sx=1, sy=1, sz=1):
    bm = bmesh.new(); bmesh.ops.create_uvsphere(bm, u_segments=20, v_segments=12, radius=r)
    me = bpy.data.meshes.new(name); bm.to_mesh(me); bm.free()
    ob = bpy.data.objects.new(name, me); link(ob); ob.location = (x * C, y * C, z); ob.scale = (sx, sy, sz)
    for p in me.polygons: p.use_smooth = True
    ob.data.materials.append(MAT[mat]); return ob


def wall(name, x0, y0, x1, y1, notches, windows):
    ob = box(name, x0, y0, x1, y1, 0, D.WALL_H, "pared")
    horiz = (x1 - x0) >= (y1 - y0)
    cutters = []
    for (a0, a1) in notches:
        cutters.append(box(name + "_p", a0, y0 - 3, a1, y1 + 3, -0.1, D.DOOR_H, "pared") if horiz
                       else box(name + "_p", x0 - 3, a0, x1 + 3, a1, -0.1, D.DOOR_H, "pared"))
    for (a0, a1, z0, z1) in windows:
        cutters.append(box(name + "_v", a0, y0 - 3, a1, y1 + 3, z0, z1, "pared") if horiz
                        else box(name + "_v", x0 - 3, a0, x1 + 3, a1, z0, z1, "pared"))
    for ct in cutters:
        m = ob.modifiers.new("cut", "BOOLEAN"); m.object = ct; m.operation = "DIFFERENCE"; m.solver = "EXACT"
        ct.hide_render = True; ct.hide_viewport = True
    return ob


# piso (losa de madera)
bm = bmesh.new()
f = bm.faces.new([bm.verts.new((x * C, y * C, 0.0)) for (x, y) in D.FLOOR])
if f.normal.z < 0: f.normal_flip()
ext = bmesh.ops.extrude_face_region(bm, geom=[f])
for v in [e for e in ext["geom"] if isinstance(e, bmesh.types.BMVert)]: v.co.z = -0.06
bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
me = bpy.data.meshes.new("Piso"); bm.to_mesh(me); bm.free()
piso = bpy.data.objects.new("Piso", me); link(piso); piso.data.materials.append(MAT["piso"])

for (nm, x0, y0, x1, y1, notches, windows) in D.WALLS:
    wall(nm, x0, y0, x1, y1, notches, windows)
for (nm, x0, y0, x1, y1, z0, z1, mat, bevel) in D.BOXES:
    box(nm, x0, y0, x1, y1, z0, z1, mat, bevel, seg=4 if bevel >= 0.03 else 3)
for (nm, x, y, z0, z1, r, rx, mat) in D.CYLS:
    cyl(nm, x, y, z0, z1, r, rx, mat)
# follaje de la planta (esferas)
for i in range(7):
    a = i * 0.9
    sphere("Hoja_%d" % i, 500 + 14 * math.cos(a), 566 + 14 * math.sin(a), 0.62 + 0.12 * (i % 3), 0.17, "verde", 0.7, 0.7, 1.4)

# ------------------------------------------------------------------ entorno y luz
bm = bmesh.new(); bmesh.ops.create_grid(bm, x_segments=1, y_segments=1, size=60)
me = bpy.data.meshes.new("Terreno"); bm.to_mesh(me); bm.free()
terr = bpy.data.objects.new("Terreno", me); link(terr); terr.location = (4.7, 3.0, -0.07)
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
    "aerial": dict(loc=(5.0, -0.5, 11.6), tgt=(4.9, 2.9, 0.0), lens=30),
    "dorm1": dict(loc=(3.0, 0.35, 2.1), tgt=(0.6, 2.1, 0.5), lens=17),
    "dorm2": dict(loc=(7.4, 2.55, 2.0), tgt=(9.1, 0.6, 0.55), lens=16),
    "sala": dict(loc=(4.2, -2.2, 6.8), tgt=(4.8, 4.6, 0.4), lens=24),
    "sala2": dict(loc=(-0.9, 4.5, 4.2), tgt=(6.5, 5.0, 0.6), lens=20),
    "cocina": dict(loc=(5.4, 3.3, 1.9), tgt=(8.9, 5.0, 0.9), lens=18),
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
