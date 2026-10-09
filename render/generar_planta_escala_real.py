# Planta a escala real según el plano del arquitecto (cm). x este, y norte. Origen: esquina SO interior del dormitorio 1.
TOP = 700
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
def hdim(x0, x1, y, label, real=True, up=8):
    cl, tc = ("dim", "dimt") if real else ("dimg", "dimgt")
    line(x0, y, x1, y, cl); line(x0, y-5, x0, y+5, cl); line(x1, y-5, x1, y+5, cl)
    text((x0+x1)/2, y+up, label, 14, tc)
def vdim(x, y0, y1, label, real=True, side=-1):
    cl, tc = ("dim", "dimt") if real else ("dimg", "dimgt")
    line(x, y0, x, y1, cl); line(x-5, y0, x+5, y0, cl); line(x-5, y1, x+5, y1, cl)
    o.append(f'<text transform="translate({x+side*14},{Y((y0+y1)/2)}) rotate(-90)" text-anchor="middle" font-size="14" class="{tc}">{label}</text>')
FLOOR, BATH, WALL = "var(--floor)", "var(--bath)", "var(--wall)"
W = lambda x0, y0, x1, y1: rect(x0, y0, x1, y1, WALL)
HATCH = '<pattern id="ach" width="6" height="6" patternUnits="userSpaceOnUse"><path d="M0 0 L0 6" stroke="#7a6a5a" stroke-width="1.6"/></pattern>'
NN = 584                       # cara interior norte
# ---- pisos
rect(0, 0, 315, 350, FLOOR)                                   # dormitorio 1 (incluye hueco de la puerta)
rect(335, 0, 465, 180, BATH); rect(475, 0, 595, 180, BATH)   # dos baños
rect(615, 0, 955, 270, FLOOR)                                 # dormitorio 2 (3.40 con el closet)
rect(127, 370, 928, NN, FLOOR); rect(335, 200, 595, 370, FLOOR); rect(595, 290, 928, 370, FLOOR); rect(595, 200, 615, 290, FLOOR)  # sala
# ---- escalera que se mantiene (oeste de la línea roja)
rect(0, 370, 127, NN, "#cfcfcf", "#8a8a8a", 2); text(63, 480, "escalera", 13); text(63, 462, "(se mantiene)", 11)
for k in range(8): line(10, 380 + k*25, 117, 380 + k*25, "dimg")
# ---- muebles
rect(0, 71, 190, 221, "#9a9a9a", "#555", 2); rect(0, 71, 34, 221, "#f2f2f2", "#555", 2); text(112, 150, "Cama 1", 16, "lbl"); text(112, 132, "1.5 × 1.9 m", 12)
rect(1, 25, 41, 65, "#b98a5e", "#7a5a3a", 2); rect(1, 227, 41, 267, "#b98a5e", "#7a5a3a", 2)
rect(805, 0, 955, 190, "#9a9a9a", "#555", 2); rect(805, 0, 955, 28, "#f2f2f2", "#555", 2); text(880, 105, "Cama 2", 16, "lbl"); text(880, 87, "1.5 × 1.9 m", 12)
rect(758, 0, 798, 40, "#b98a5e", "#7a5a3a", 2)
rect(300, 494, 470, 584, "#e6dccb", "#8a7d6a", 2); rect(300, 424, 390, 494, "#e6dccb", "#8a7d6a", 2); text(440, 530, "Sofá L", 13)  # sofá
rect(600, 440, 740, 520, "#7a5236", "#4a2f1a", 2); text(670, 475, "mesa 1.4×0.8", 12, extra='style="fill:#fff"')
rect(630, 524, 700, 584, "#b8bcc0", "#6b7076", 2); text(665, 554, "Nevera", 11)
rect(700, 524, 940, 584, "#cfc9bf", "#8a847a", 2); rect(790, 524, 850, 584, "#333"); text(820, 554, "Estufa", 11, extra='style="fill:#fff"')
rect(780, 400, 900, 440, "none", "#8a847a", 2, extra='stroke-dasharray="6 4"'); text(840, 415, "isla (opcional)", 11)
# baño: bañera, inodoro, lavabo
# baño 1 (de dormitorio 1): inodoro, ducha, lavabo
rect(345, 8, 383, 60, "#f2f2f2", "#556", 2, extra='rx="12"'); rect(395, 5, 463, 75, "#d8e0e4", "#556", 2); text(429, 40, "ducha", 11)
rect(395, 140, 455, 178, "#f2f2f2", "#556", 2, extra='rx="10"')
# baño 2: inodoro, ducha, lavabo
rect(485, 8, 523, 60, "#f2f2f2", "#556", 2, extra='rx="12"'); rect(530, 5, 593, 85, "#d8e0e4", "#556", 2); text(561, 45, "ducha", 11)
rect(485, 140, 525, 178, "#f2f2f2", "#556", 2, extra='rx="10"')
# vestidor del dormitorio 1 (sale de la zona del sofá): estantes en U
o.append(f'<rect x="335" y="{Y(350)}" width="130" height="30" fill="url(#ach)" stroke="#7a6a5a" stroke-width="2"/>')
o.append(f'<rect x="435" y="{Y(320)}" width="30" height="120" fill="url(#ach)" stroke="#7a6a5a" stroke-width="2"/>')
# closets (rayados)
o.append(f'<rect x="0" y="{Y(350)}" width="225" height="58" fill="url(#ach)" stroke="#7a6a5a" stroke-width="2"/>'); text(112, 306, "closet 2.25×0.6", 11)
o.append(f'<rect x="615" y="{Y(180)}" width="77" height="180" fill="url(#ach)" stroke="#7a6a5a" stroke-width="2"/>')
# ---- paredes
W(-20, -20, 975, 0)                                          # sur
W(-20, 0, 0, 370); W(-20, 350, 225, 370)                     # oeste dorm 1 + norte del closet
W(315, 0, 335, 95); W(315, 165, 335, 240); W(315, 320, 335, 370)   # este dorm 1 (puertas 95-165 baño, 240-320 vestidor)
W(465, 0, 475, 180)                                          # partición entre los dos baños
W(335, 350, 485, 370); W(465, 200, 485, 350)               # norte y este del vestidor
W(335, 180, 525, 200)                                        # norte del baño (puerta 70 cm: 525-595)
W(595, 0, 615, 180); W(615, 180, 692, 200)                   # oeste dorm 2 + norte closet
W(595, 270, 975, 290)                                        # norte dorm 2
W(955, 0, 975, 270)                                          # este dorm 2
W(928, 290, 948, 584); W(107, NN, 948, NN+20)               # este y norte de la sala
# ---- elementos que se QUITAN (fantasma con X)
GH = 'fill="none" stroke="var(--new)" stroke-width="2.5" stroke-dasharray="8 5"'
o.append(f'<rect x="140" y="{Y(NN)}" width="160" height="100" {GH}/>')
line(140, NN, 300, NN-100, "dim"); line(140, NN-100, 300, NN, "dim"); text(220, NN-50, "gradas 10–15", 12, "dimt", extra='style="paint-order:stroke;stroke:#fff;stroke-width:4px"'); text(220, NN-66, "(se quitan)", 12, "dimt", extra='style="paint-order:stroke;stroke:#fff;stroke-width:4px"')
o.append(f'<rect x="476" y="{Y(NN)}" width="86" height="204" {GH}/>')
line(476, NN, 562, NN-204, "dim"); line(476, NN-204, 562, NN, "dim"); text(519, NN-100, "pared/closet", 12, "dimt", extra='style="paint-order:stroke;stroke:#fff;stroke-width:4px"'); text(519, NN-116, "(se quita)", 12, "dimt", extra='style="paint-order:stroke;stroke:#fff;stroke-width:4px"')
# ---- ventanas (plano)
for (a, b) in [(80, 290), (410, 560), (690, 900)]: rect(a, -20, b, 0, "#7ec8ee", "#245", 2)
rect(928, 300, 948, 510, "#7ec8ee", "#245", 2)
text(185, -34, "ventana 2.10", 12); text(485, -34, "ventana 1.50", 12); text(795, -34, "ventana 2.10", 12)
# ---- puertas
G = 'stroke="var(--ok)" stroke-width="6" stroke-dasharray="10 5"'
def door(x0, y0, x1, y1): o.append(f'<line x1="{x0}" y1="{Y(y0)}" x2="{x1}" y2="{Y(y1)}" {G}/>')
door(225, 360, 315, 360); door(525, 190, 595, 190); door(605, 180, 605, 270); door(325, 95, 325, 165); door(325, 240, 325, 320)
GT = 'style="fill:var(--ok)" font-weight="600"'
text(270, 383, "abertura 0.90", 12, extra=GT); text(560, 207, "puerta 0.70", 12, extra=GT); text(655, 225, "puerta 0.90", 12, extra=GT, anchor="start")
text(309, 130, "puerta 0.70", 11, extra=GT, anchor="end"); text(309, 280, "puerta 0.80", 11, extra=GT, anchor="end")
text(309, 148, "(a baño 1)", 11, extra=GT, anchor="end"); text(309, 263, "(a vestidor)", 11, extra=GT, anchor="end")
# ---- línea roja: inicio de la sala
o.append(f'<line x1="127" y1="{Y(370)}" x2="127" y2="{Y(NN)}" stroke="var(--new)" stroke-width="4"/>')
text(135, 395, "← inicio de la sala", 12, "dimt", anchor="start", extra='style="paint-order:stroke;stroke:#fff;stroke-width:4px"')
# ---- rótulos
text(165, 262, "Dormitorio 1", 17, "lbl"); text(165, 244, "3.15 × 3.50 m", 14, "dimt")
text(400, 112, "Baño 1", 14, "lbl"); text(400, 97, "1.30 × 1.80", 11); text(535, 112, "Baño 2", 14, "lbl"); text(535, 97, "1.20 × 1.80", 11)
text(385, 285, "Vestidor", 14, "lbl"); text(385, 268, "1.30 × 1.50", 11, "dimt")
text(790, 235, "Dormitorio 2", 17, "lbl"); text(790, 218, "3.40 × 2.70 m", 14, "dimt"); text(654, 100, "closet", 11, extra='transform="rotate(-90 654 %s)"' % Y(100))
text(240, 360-0, "", 1)
text(530, 300, "estar", 14, "lbl"); text(780, 335, "Sala – comedor – cocina", 17, "lbl")
# ---- cotas reales
hdim(0, 315, -75, "3.15 m"); hdim(335, 595, -75, "2.60 m"); hdim(615, 955, -75, "3.40 m")
hdim(0, 476, 650, "4.76 m"); hdim(496, 928, 650, "4.32 m")
vdim(-45, 0, 350, "3.50 m"); vdim(990, 0, 270, "2.70 m", side=1); vdim(970, 290, NN, "2.94 m", side=1)
svg = ('<svg viewBox="-100 0 1130 780" role="img" aria-label="Planta a escala real según el plano del arquitecto">\n      <defs>' + HATCH + '</defs>\n      '
       + "\n      ".join(o) + '\n    </svg>')
p = "/home/user/Pulso-app/index.html"
s = open(p, encoding="utf-8").read()
a = s.index('<section class="card">\n    <h2>Planta según el plano del arquitecto (a escala real)</h2>')
b = s.index('</section>', a) + len('</section>')
new = ('<section class="card">\n    <h2>Planta según el plano del arquitecto (a escala real)</h2>\n    ' + svg +
       '\n    <small>Medidas del plano original (m): dormitorio 1 de 3.15 × 3.50 m con closet de 2.25 × 0.6 m; baño original de 2.60 × 1.80 m, ahora partido en dos baños (1.30 y 1.20 m de ancho); dormitorio 2 de 3.40 × 2.70 m con closet de 0.77 m; '
       'fondo del sector norte 2.94 m; norte 4.76 + 0.20 + 4.32 m. En rojo: lo que se quita (gradas 10–15 y el closet/pared central) y la línea donde empieza la sala. '
       'Rayado = closet. Verde = puertas y aberturas.</small>\n  </section>')
s = s[:a] + new + s[b:]
a2 = s.index('<h2>Qué cambia y qué revisar</h2>'); u0 = s.index('<ul>', a2); u1 = s.index('</ul>', u0) + 5
notas = '''<ul>
      <li><b>Se quita:</b> las gradas 10–15 y el closet/pared central (marcados con X). El sector norte queda como una sala abierta que empieza en la línea roja (≈ 1.3 m al este del dormitorio 1); la escalera restante se mantiene al oeste.</li>
      <li><b>Dos baños:</b> el baño de 2.60 × 1.80 m se parte en <i>Baño 1</i> (1.30 × 1.80 m, solo para el dormitorio 1) y <i>Baño 2</i> (1.20 × 1.80 m, para la sala y el dormitorio 2). Cada uno lleva inodoro, ducha y lavabo; sin espacio para la bañera de 1.60 m. Entre ambos hay una partición de 10 cm.</li>
      <li><b>Dormitorio 1 con 2 puertas más la abertura:</b> puerta 2 de 0.70 m al Baño 1 (baño propio) y puerta de 0.80 m al vestidor, ambas en la pared este; además la abertura de 0.90 m hacia la sala.</li>
      <li><b>Vestidor del dormitorio 1:</b> 1.30 × 1.50 m, sacado de la zona del estar donde dibujé el sofá; estantes en U y puerta desde el dormitorio. Deja un paso de ~1.1 m en el estar hacia el Baño 2 y el dormitorio 2.</li>
      <li><b>Dormitorio 2:</b> 3.40 × 2.70 m con closet de 0.77 m (parte libre ≈ 2.63 × 2.70 m). Puerta de 0.90 m desde el estar.</li>
      <li><b>Por confirmar:</b> (1) dormitorio 1: el plano dice 3.15 × 3.50 m y tú habías dicho 3.05 × 3.05; (2) el fondo del sector oeste de la sala (plano ≈ 2.1 m; tú dijiste 2.70 m); (3) dónde va la cocina, porque el lado este tiene un ventanal; (4) la posición del sofá y del comedor.</li>
    </ul>'''
s = s[:u0] + notas + s[u1:]
open(p, "w", encoding="utf-8").write(s)
print("ok")
