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
rect(335, 0, 465, 180, BATH_C); rect(475, 0, 595, 180, BATH_C)
# estantes del vestidor (E) como bloque rayado
# muebles (de abajo hacia arriba)
items = [b for b in D.BOXES if not SKIP.match(b[0])]
items.sort(key=lambda b: (0 if b[0].startswith("Alfombra") or b[0].startswith("Baldosa") else 1, b[6]))
for (nm, x0, y0, x1, y1, z0, z1, mat, bev) in items:
    if nm.startswith("Baldosa"): continue
    if nm.startswith("Vest_Repisa_E") and nm != "Vest_Repisa_E1": continue
    op = ' opacity=".75"' if nm.startswith("Alfombra") else ""
    rect(x0, y0, x1, y1, COL.get(mat, "#999"), "#5a5a5a" if not nm.startswith("Alfombra") else None, 1.3, extra=op)
for (nm, x, y, z0, z1, r, rx, mat) in D.CYLS:
    if nm.endswith("_base") or nm in ("Florero", "Grifo_Cocina") or "Cabezal" in nm or "Grifo" in nm: continue
    rr = max(r, rx) * 100
    o.append(f'<circle cx="{x}" cy="{Y(y)}" r="{rr:.1f}" fill="{COL.get(mat,"#999")}" stroke="#5a5a5a" stroke-width="1.2"/>')
# paredes con huecos de puerta
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
# escalera que se mantiene + línea roja
rect(0, 370, 127, 584, "#cfcfcf", "#8a8a8a", 2); text(63, 480, "escalera", 13); text(63, 462, "(se mantiene)", 11)
for k in range(8): line(10, 380 + k*25, 117, 380 + k*25, "dimg")
o.append(f'<line x1="127" y1="{Y(370)}" x2="127" y2="{Y(584)}" stroke="var(--new)" stroke-width="4"/>')
text(135, 395, "← inicio de la sala", 12, "dimt", anchor="start", extra='style="paint-order:stroke;stroke:#fff;stroke-width:4px"')
# puertas / aberturas
G = 'stroke="var(--ok)" stroke-width="6" stroke-dasharray="10 5"'
def door(x0, y0, x1, y1): o.append(f'<line x1="{x0}" y1="{Y(y0)}" x2="{x1}" y2="{Y(y1)}" {G}/>')
door(225, 360, 315, 360); door(325, 95, 325, 165); door(325, 240, 325, 320); door(525, 190, 595, 190); door(605, 180, 605, 270); door(605, 98, 605, 168)
GT = 'style="fill:var(--ok)" font-weight="600"'
text(270, 383, "abertura 0.90", 12, extra=GT); text(309, 130, "puerta 0.70", 11, extra=GT, anchor="end"); text(309, 148, "(a baño 1)", 11, extra=GT, anchor="end")
text(309, 280, "puerta 0.80", 11, extra=GT, anchor="end"); text(309, 263, "(a vestidor)", 11, extra=GT, anchor="end")
text(560, 207, "puerta 0.70", 12, extra=GT); text(655, 225, "puerta 0.90", 12, extra=GT, anchor="start")
text(628, 133, "puerta 0.70", 11, extra=GT, anchor="start"); text(628, 118, "(a baño 2)", 11, extra=GT, anchor="start")
# rótulos
text(120, 255, "Dormitorio 1", 17, "lbl"); text(120, 237, "3.15 × 3.50 m", 14, "dimt")
text(800, 290-30, "Dormitorio 2", 17, "lbl"); text(800, 218+30-30, "3.40 × 2.70 m", 14, "dimt")
text(400, 112, "Baño 1", 13, "lbl"); text(400, 98, "1.30 × 1.80", 11); text(535, 112, "Baño 2", 13, "lbl"); text(535, 98, "1.20 × 1.80", 11)
text(385, 270, "Vestidor", 14, "lbl"); text(385, 254, "1.30 × 1.50", 11, "dimt")
text(212, 340, "closet 2.25×0.6", 11); text(530, 300, "estar", 14, "lbl")
text(335, 430, "mesa", 10); text(458, 480, "TV", 10)
text(330, 560, "aparador", 11); text(185, 490, "sofá", 11); text(630, 480, "comedor", 12, extra='style="fill:#fff"')
text(690, 340, "Sala – comedor – cocina", 15, "lbl"); text(900, 340, "fregadero", 11, anchor="middle")
text(765, 553, "Nevera", 11, extra='style="fill:#222"'); text(890, 590+0, "", 1)
# cotas del plano
hdim(0, 315, -75, "3.15 m"); hdim(335, 595, -75, "2.60 m"); hdim(615, 955, -75, "3.40 m")
hdim(0, 476, 650, "4.76 m"); hdim(496, 928, 650, "4.32 m")
vdim(-45, 0, 350, "3.50 m"); vdim(990, 0, 270, "2.70 m", side=1); vdim(970, 290, 584, "2.94 m", side=1)
svg = ('<svg viewBox="-100 0 1130 800" role="img" aria-label="Planta final a escala real">\n      ' + "\n      ".join(o) + '\n    </svg>')
p = "/home/user/Pulso-app/index.html"
s = open(p, encoding="utf-8").read()
a = s.index('<section class="card">\n    <h2>Planta final a escala real (según el plano del arquitecto)</h2>')
b = s.index('</section>', a) + len('</section>')
new = ('<section class="card">\n    <h2>Planta final a escala real (según el plano del arquitecto)</h2>\n    ' + svg +
       '\n    <small>Medidas del plano original (m). Dos baños (1.30 y 1.20 m) en lugar de uno de 2.60 m; vestidor del dormitorio 1 (1.30 × 1.50 m); dormitorio 2 sin closet y con puerta al baño 2; '
       'gradas, closet central y closet del dormitorio 2 quitados. Cocina al norte con fregadero y mueble junto a la ventana del lado este. Sala con sofá de 3 plazas, mueble de TV, mesa de centro y aparador; comedor de 4 puestos. '
       'Verde punteado = puertas y aberturas. La planta se genera desde los mismos datos que el modelo de SketchUp y los renders.</small>\n  </section>')
s = s[:a] + new + s[b:]
a2 = s.index('<h2>Qué cambia y qué revisar</h2>'); u0 = s.index('<ul>', a2); u1 = s.index('</ul>', u0) + 5
notas = '''<ul>
      <li><b>Quitado:</b> gradas 10–15, closet/pared central, closet del dormitorio 2 y el mobiliario de ejemplo anterior. La sala empieza en la línea roja (≈ 1.3 m al este del dormitorio 1).</li>
      <li><b>Dos baños:</b> Baño 1 (1.30 × 1.80 m, del dormitorio 1) y Baño 2 (1.20 × 1.80 m) con inodoro, ducha y lavabo. El Baño 2 tiene dos puertas: al estar y al dormitorio 2.</li>
      <li><b>Dormitorio 1:</b> puerta 2 al Baño 1 y puerta a su vestidor (1.30 × 1.50 m, con barra y repisas); además la abertura de 0.90 m a la sala. Cama de 1.5 × 1.9 m, closet de 2.25 × 0.6 m.</li>
      <li><b>Dormitorio 2:</b> 3.40 × 2.70 m completo; cama bajo el ventanal, cómoda y mesa de noche.</li>
      <li><b>Cocina:</b> mesón en L: al norte nevera, mesón y estufa; al este un mesón de 1.9 m con <b>fregadero y grifo bajo la ventana</b> (ventana a 1.00 m del piso para quedar sobre el mesón).</li>
      <li><b>Sala y comedor:</b> sofá de 3 plazas con el respaldo hacia la baranda de la escalera, mesa de centro, mueble de TV de 1.6 m (a ~2.2 m del sofá), aparador y lámparas; comedor con mesa de 1.4 × 0.8 m y 4 sillas, y planta decorativa.</li>
      <li><b>Por confirmar:</b> la ventana de la cocina (altura de antepecho real), las alturas de las ventanas (puse 0.90 m en dormitorios y 1.40 m en el baño) y el reparto exacto de los muebles.</li>
    </ul>'''
s = s[:u0] + notas + s[u1:]
open(p, "w", encoding="utf-8").write(s)
print("ok", len(o))
