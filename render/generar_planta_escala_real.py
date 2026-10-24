# Planta 2D generada desde render/plano_data.py (los mismos datos de SketchUp y Blender). Unidades: cm.
import sys, re
sys.path.insert(0, "/home/user/Pulso-app/render")
import plano_data as D
TOP = 720
def Y(y): return TOP - y
o = []
def rect(x0, y0, x1, y1, fill, stroke=None, sw=0, extra=""):
    st = f' stroke="{stroke}" stroke-width="{sw}"' if stroke else ""
    o.append(f'<rect x="{x0}" y="{Y(y1)}" width="{x1-x0}" height="{y1-y0}" fill="{fill}"{st} {extra}/>')
def text(x, y, s, size=14, cls="", anchor="middle", extra=""):
    c = f' class="{cls}"' if cls else ""
    o.append(f'<text x="{x}" y="{Y(y)}" text-anchor="{anchor}" font-size="{size}"{c} {extra}>{s}</text>')
def line(x0, y0, x1, y1, cls="dim", extra=""):
    o.append(f'<line x1="{x0}" y1="{Y(y0)}" x2="{x1}" y2="{Y(y1)}" class="{cls}" {extra}/>')
def hdim(x0, x1, y, label, up=8):
    line(x0, y, x1, y, "dim"); line(x0, y-5, x0, y+5, "dim"); line(x1, y-5, x1, y+5, "dim"); text((x0+x1)/2, y+up, label, 14, "dimt")
def vdim(x, y0, y1, label, side=-1):
    line(x, y0, x, y1, "dim"); line(x-5, y0, x+5, y0, "dim"); line(x-5, y1, x+5, y1, "dim")
    o.append(f'<text transform="translate({x+side*14},{Y((y0+y1)/2)}) rotate(-90)" text-anchor="middle" font-size="14" class="dimt">{label}</text>')
FLOOR_C, BATH_C, WALL_C = "var(--floor)", "var(--bath)", "var(--wall)"
COL = {"cabecero": "#8a8a90", "madera": "#b98a5e", "blanco": "#f2f2f2", "tela_gris": "#9a9a9a", "tela_beige": "#cbbfa8", "tela_sofa": "#e6dccb",
       "tela_roja": "#8c2622", "ceramica": "#f4f4f4", "gabinete": "#e8e6e2", "meson": "#cfc9bf", "negro": "#3a3a3c", "acero": "#9aa4ad",
       "nevera": "#b8bcc0", "madera_oscura": "#7a5236", "silla": "#c9bfae", "verde": "#5c8a4a", "maceta": "#d2cdc3", "vidrio": "#bfe4f2",
       "espejo": "#cfe0ea", "puerta": "#c29664", "alfombra": "#d9cdb8", "aluminio": "#444", "baldosa": "#d5d8da", "ropa_a": "#46607a", "ropa_b": "#963c37",
       "ropa_c": "#d2d2cd", "ropa_d": "#3c3c46"}
SKIP = re.compile(r"^(Vent_|Baranda_Poste|Mesa_Pata|Mesa_Centro_Pata|Silla_.*(pata|respaldo)|Closet1_(Puerta|Tirador)|Nevera_(Linea|Manija)|Meson.*(puerta|mango|zocalo|cubierta)|Estufa_(Horno|Mango|Placa)|Cuadro|Puerta_|TV_|Cama.*_(Manta)|Cojin|Sofa_Cojin|Vest_(Ropa|Barra|Techo|Fondo|Lado|Repisa_N)|.*_(Espejo|Ducha_Cristal)|Fregadero_Hondo|Grifo)")
# pisos
pts = " ".join(f"{x},{Y(y)}" for x, y in D.FLOOR)
o.append(f'<polygon points="{pts}" fill="{FLOOR_C}"/>')
rect(335, 0, 460, 240, BATH_C); rect(470, 0, 595, 240, BATH_C)
# muebles (de abajo hacia arriba)
items = [b for b in D.BOXES if not SKIP.match(b[0])]
items.sort(key=lambda b: (0 if b[0].startswith("Alfombra") or b[0].startswith("Baldosa") else 1, b[6]))
for (nm, x0, y0, x1, y1, z0, z1, mat, bev) in items:
    if nm.startswith("Baldosa"): continue
    op = ' opacity=".75"' if nm.startswith("Alfombra") else ""
    rect(x0, y0, x1, y1, COL.get(mat, "#999"), "#5a5a5a" if not nm.startswith("Alfombra") else None, 1.3, extra=op)
for (nm, x, y, z0, z1, r, rx, mat) in D.CYLS:
    if nm.endswith("_base") or nm in ("Florero", "Grifo_Cocina") or "Cabezal" in nm or "Grifo" in nm: continue
    rr = max(r, rx) * 100
    o.append(f'<circle cx="{x}" cy="{Y(y)}" r="{rr:.1f}" fill="{COL.get(mat,"#999")}" stroke="#5a5a5a" stroke-width="1.2"/>')
# paredes con huecos de puerta
G = 'stroke="var(--ok)" stroke-width="6" stroke-dasharray="10 5"'
for (nm, x0, y0, x1, y1, notches, windows) in D.WALLS:
    horiz = (x1 - x0) >= (y1 - y0)
    cuts = sorted(notches)
    a_lo, a_hi = (x0, x1) if horiz else (y0, y1)
    cur = a_lo
    for (n0, n1) in cuts + [(a_hi, a_hi)]:
        if n0 > cur:
            (rect(cur, y0, n0, y1, WALL_C) if horiz else rect(x0, cur, x1, n0, WALL_C))
        cur = n1
    for (w0, w1, z0, z1) in windows:
        (rect(w0, y0, w1, y1, "#7ec8ee", "#245", 2) if horiz else rect(x0, w0, x1, w1, "#7ec8ee", "#245", 2))
    for (n0, n1) in notches:
        (line(n0, (y0 + y1) / 2, n1, (y0 + y1) / 2, "dim", G) if horiz else line((x0 + x1) / 2, n0, (x0 + x1) / 2, n1, "dim", G))
for (nm, pts4) in D.POLYWALLS:
    o.append('<polygon points="%s" fill="%s"/>' % (" ".join(f"{x},{Y(y)}" for x, y in pts4), WALL_C))
GT = 'style="fill:var(--ok)" font-weight="600"'
text(270, 350, "abertura 0.90", 12, extra=GT); text(309, 40, "puerta 0.70", 11, extra=GT, anchor="end"); text(309, 26, "(a baño 1)", 11, extra=GT, anchor="end")
text(557, 262, "puerta 0.70", 12, extra=GT); text(660, 345, "puerta 0.90", 12, extra=GT)
text(622, 112, "corrediza 0.70", 10, extra=GT, anchor="start"); text(622, 99, "(baño 2)", 10, extra=GT, anchor="start")
text(842, 386, "entrada 0.90", 12, extra=GT)
# rótulos
text(252, 150, "Dormitorio 1", 17, "lbl"); text(252, 130, "3.15 × 3.12 m", 14, "dimt")
text(405, 190, "Baño 1", 13, "lbl"); text(405, 175, "1.25 × 2.40", 11)
text(545, 190, "Baño 2", 13, "lbl"); text(545, 175, "1.25 × 2.40", 11)
text(790, 247, "Dormitorio 2", 15, "lbl"); text(790, 230, "3.47 / 3.13 × 3.12 m", 12, "dimt")
text(240, 372, "Sala", 15, "lbl"); text(532, 600, "Comedor", 12, "lbl"); text(770, 490, "Cocina", 14, "lbl")
text(855, 488, "fregadero", 10, extra='style="fill:#222"'); text(690, 586, "Nevera", 10, extra='style="fill:#222"')
text(137, 400, "TV", 10); text(375, 500, "sofá", 11); text(120, 640, "", 1)
text(640, 398, "resalto 0.70 × 0.20", 9)
# cotas del plano
hdim(0, 315, -45, "3.15 m"); hdim(335, 460, -45, "1.25 m"); hdim(470, 595, -45, "1.25 m"); hdim(615, 962, -45, "3.47 m")
hdim(115, 884, 655, "7.69 m")
vdim(-45, 0, 312, "3.12 m"); vdim(1000, 0, 312, "3.12 m", side=1); vdim(70, 332, 614, "2.82 m"); vdim(940, 431, 614, "1.83 m", side=1)
svg = ('<svg viewBox="-100 0 1130 800" role="img" aria-label="Planta final a escala real">\n      ' + "\n      ".join(o) + '\n    </svg>')
p = "/home/user/Pulso-app/index.html"
s = open(p, encoding="utf-8").read()
a = s.index('<section class="card">\n    <h2>Planta final a escala real')
b = s.index('</section>', a) + len('</section>')
new = ('<section class="card">\n    <h2>Planta final a escala real (según el plano con medidas)</h2>\n    ' + svg +
       '\n    <small>Medidas del plano con medidas (m): dormitorio 1 de 3.15 × 3.12; dos baños de 1.25 × 2.40; dormitorio 2 de 3.47 al sur y 3.13 al norte (el muro este es inclinado) × 3.12; '
       'sala-comedor-cocina de 7.69 m de ancho (2.82 m de fondo en el sector oeste). Verde punteado = puertas y aberturas (0.90 dormitorios y entrada, 0.70 baños). '
       'El mobiliario es una propuesta. La planta se genera desde los mismos datos que el modelo de SketchUp y los renders.</small>\n  </section>')
s = s[:a] + new + s[b:]
a2 = s.index('<h2>Qué cambia y qué revisar</h2>'); u0 = s.index('<ul>', a2); u1 = s.index('</ul>', u0) + 5
notas = '''<ul>
      <li><b>Dormitorio 1</b> (3.15 × 3.12 m): puerta de 0.90 m hacia la sala, puerta de 0.70 m al Baño 1, cama con el cabecero al oeste y closet de 2.25 × 0.55 m junto al muro norte.</li>
      <li><b>Dos baños</b> (1.25 × 2.40 m cada uno, tabique de 0.10 m): el Baño 1 se abre al dormitorio 1; el Baño 2 tiene dos puertas de 0.70 m: al estar (batiente) y al dormitorio 2 (corrediza).</li>
      <li><b>Dormitorio 2</b> (3.47 m al sur y 3.13 m al norte × 3.12 m): el muro este del plano es inclinado y así lo dibujé. Cama con el cabecero hacia el ventanal.</li>
      <li><b>Sala – comedor – cocina</b> (7.69 m de ancho): TV al oeste, sofá de 3 plazas como divisor, comedor de 4 puestos y cocina en L (nevera, estufa y mesón al norte; fregadero y mesón junto a la ventana del este). Entrada de 0.90 m por el este y un resalto de 0.70 × 0.20 m como en el plano.</li>
      <li><b>No aparece en este plano</b> el vestidor del dormitorio 1 que pediste antes; lo puedo agregar sacándolo del sector de la sala.</li>
      <li><b>Por confirmar:</b> alturas de las ventanas (0.90 m en dormitorios, 1.40 m en baños y 1.00 m en la cocina), el largo de la ventana de la cocina y el mobiliario.</li>
    </ul>'''
s = s[:u0] + notas + s[u1:]
open(p, "w", encoding="utf-8").write(s)
print("ok", len(o))
