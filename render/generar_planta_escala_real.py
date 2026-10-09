# Planta completa a escala real. Unidades: cm. x hacia el este, y hacia el norte; origen = esquina SO interior del dormitorio 1.
TOP = 553.0
def Y(y): return TOP - y
out = []
def rect(x0, y0, x1, y1, fill, stroke=None, sw=0, extra=""):
    st = f' stroke="{stroke}" stroke-width="{sw}"' if stroke else ""
    out.append(f'<rect x="{x0}" y="{Y(y1)}" width="{x1-x0}" height="{y1-y0}" fill="{fill}"{st} {extra}/>')
def text(x, y, s, size=14, cls="", anchor="middle", extra="", weight=None):
    w = f' font-weight="{weight}"' if weight else ""
    c = f' class="{cls}"' if cls else ""
    out.append(f'<text x="{x}" y="{Y(y)}" text-anchor="{anchor}" font-size="{size}"{w}{c} {extra}>{s}</text>')
def line(x0, y0, x1, y1, cls="dim", extra=""):
    out.append(f'<line x1="{x0}" y1="{Y(y0)}" x2="{x1}" y2="{Y(y1)}" class="{cls}" {extra}/>')
def hdim(x0, x1, y, label, real=True, off=-8):
    cl = "dim" if real else "dimg"; tc = "dimt" if real else "dimgt"
    line(x0, y, x1, y, cl); line(x0, y-5, x0, y+5, cl); line(x1, y-5, x1, y+5, cl)
    text((x0+x1)/2, y-off*-1 if False else y+8, label, 15, tc)
def vdim(x, y0, y1, label, real=True, side=-1):
    cl = "dim" if real else "dimg"; tc = "dimt" if real else "dimgt"
    line(x, y0, x, y1, cl); line(x-5, y0, x+5, y0, cl); line(x-5, y1, x+5, y1, cl)
    out.append(f'<text transform="translate({x+side*9},{Y((y0+y1)/2)}) rotate(-90)" text-anchor="middle" font-size="15" class="{tc}">{label}</text>')

FLOOR, BATH, WALL = "var(--floor)", "var(--bath)", "var(--wall)"
# ---- pisos
rect(0, 0, 283, 219, FLOOR)                       # dormitorio 1
rect(523, 0, 793, 270, FLOOR)                     # dormitorio 2
rect(100, 282, 763, 501, FLOOR)                   # sala-cocina
rect(100, 231, 511, 282, FLOOR)
rect(411, 164, 511, 231, FLOOR)                   # hueco sobre el baño
rect(523, 270, 603, 282, FLOOR)                   # entrada al dormitorio 2
rect(295, 164, 399, 219, FLOOR)                   # vestidor
rect(295, 0, 399, 152, BATH); rect(411, 0, 511, 152, BATH)   # baño (2 módulos)
# ---- muebles
rect(0, 0, 190, 150, "#9a9a9a", "#555", 2); rect(0, 0, 34, 150, "#f2f2f2", "#555", 2)       # cama 1
text(112, 85, "Cama 1", 17, "lbl"); text(112, 65, "1.5 × 1.9 m", 13)
rect(643, 0, 793, 190, "#9a9a9a", "#555", 2); rect(643, 0, 793, 28, "#f2f2f2", "#555", 2)   # cama 2
text(718, 105, "Cama 2", 17, "lbl"); text(718, 85, "1.5 × 1.9 m", 13); text(718, 66, "pies ↑ · espaldar ↓", 12)
rect(600, 0, 640, 40, "#b98a5e", "#7a5a3a", 2)                                              # mesa de noche
rect(100, 411, 300, 501, "#e6dccb", "#8a7d6a", 2); rect(100, 281, 190, 411, "#e6dccb", "#8a7d6a", 2)   # sofá L
out.append(f'<circle cx="320" cy="{Y(480)}" r="15" fill="#5c8a4a"/>')
rect(350, 305, 490, 385, "#7a5236", "#4a2f1a", 2); text(420, 340, "1.4 × 0.8 m", 13, extra='style="fill:#fff"')
for (cx0, cy0) in [(363, 380), (433, 380), (363, 266), (433, 266)]:
    rect(cx0, cy0, cx0+44, cy0+44, "#c9bfae", "#7a6f5e", 2)
rect(530, 431, 600, 501, "#b8bcc0", "#6b7076", 2); text(565, 468, "Nevera", 12)
rect(600, 441, 640, 501, "#cfc9bf", "#8a847a", 2); rect(640, 441, 700, 501, "#333"); text(670, 468, "Estufa", 12, extra='style="fill:#fff"')
rect(700, 441, 763, 501, "#cfc9bf", "#8a847a", 2); rect(703, 311, 763, 441, "#cfc9bf", "#8a847a", 2)
rect(715, 345, 755, 410, "#9aa4ad", "#555", 2)
# ---- paredes
def W(x0, y0, x1, y1): rect(x0, y0, x1, y1, WALL)
W(-12, -12, 805, 0)                                   # sur
W(-12, 0, 0, 231)                                     # dorm 1 oeste
W(-12, 219, 195, 231); W(275, 219, 411, 231)          # norte dorm 1 y vestidor (puerta 195-275)
W(283, 0, 295, 20); W(283, 100, 295, 167); W(283, 217, 295, 231)   # este dorm 1 (puerta baño 20-100, vestidor 167-217)
W(399, 0, 411, 231)                                   # divisor baño / este vestidor
W(283, 152, 420, 164); W(500, 152, 523, 164)          # norte del baño (puerta 420-500)
W(511, 0, 523, 66); W(511, 146, 523, 282)             # oeste dorm 2 (puerta 66-146)
W(603, 270, 805, 282)                                 # norte dorm 2 (entrada 523-603)
W(793, 0, 805, 282)                                   # este dorm 2
W(88, 231, 100, 513); W(88, 501, 775, 513); W(763, 282, 775, 513)   # sala
# ---- ventanales (estimados 2.0 m)
rect(41, -12, 241, 0, "#7ec8ee", "#245", 2); rect(558, -12, 758, 0, "#7ec8ee", "#245", 2)
# ---- puertas corredizas 0.8 m
G = 'stroke="var(--ok)" stroke-width="6" stroke-dasharray="10 5"'
def door(x0, y0, x1, y1): out.append(f'<line x1="{x0}" y1="{Y(y0)}" x2="{x1}" y2="{Y(y1)}" {G}/>')
door(195, 225, 275, 225); door(289, 20, 289, 100); door(289, 167, 289, 217)
door(420, 158, 500, 158); door(517, 66, 517, 146); door(523, 276, 603, 276)
GT = 'style="fill:var(--ok)" font-weight="600"'
text(235, 238, "puerta 0.8 m", 12, extra=GT); 
text(460, 168, "puerta 0.8 m", 12, extra=GT); 
text(563, 290, "entrada 0.8 m", 12, extra=GT)
# ---- rótulos
text(141, 188, "Dormitorio 1", 18, "lbl"); text(141, 168, "2.83 × 2.19 m", 15, "dimt")
text(658, 245, "Dormitorio 2", 18, "lbl"); text(658, 225, "2.70 × 2.70 m", 15, "dimt")
text(347, 110, "Baño", 15, "lbl"); text(347, 90, "WC + lavabo", 11); text(347, 74, "1.04 × 1.52 m", 11)
text(461, 110, "Baño", 15, "lbl"); text(461, 90, "ducha + lavabo", 11); text(461, 74, "1.00 × 1.52 m", 11)
text(347, 188, "Vestidor", 12, "lbl"); text(347, 173, "1.04 × 0.55 m", 11)
text(200, 365, "Sala", 18, "lbl"); text(420, 440, "Comedor", 16, "lbl"); text(660, 395, "Cocina", 18, "lbl")
# ---- cotas reales (rojo) y estimadas (gris)
hdim(0, 283, -40, "2.83 m"); hdim(283, 523, -40, "2.40 m entre cuartos"); hdim(523, 793, -40, "2.70 m")
hdim(-12, 805, -68, "≈ 8.2 m ancho total (estimado)", real=False)
vdim(-32, 0, 219, "2.19 m"); vdim(830, 0, 270, "2.70 m", side=1)
vdim(60, 231, 501, "2.70 m fondo de la sala"); hdim(100, 763, 530, "≈ 6.6 m ancho de la sala (estimado)", real=False)
vdim(872, -12, 513, "≈ 5.3 m fondo total (estimado)", real=False, side=1)
svg = ('<svg viewBox="-80 0 990 680" role="img" aria-label="Planta completa a escala real">\n      '
       + "\n      ".join(out) + '\n    </svg>')
open("/tmp/claude-0/-home-user-Pulso-app/6cc6d74c-1a3a-5158-89df-e971915a7f8d/scratchpad/planta.svg.txt", "w").write(svg)

p = "/home/user/Pulso-app/index.html"
s = open(p, encoding="utf-8").read()
a = s.index('<section class="card">\n    <h2>Planta completa a escala real</h2>')
b = s.index('</section>', a) + len('</section>')
new = ('<section class="card">\n    <h2>Planta completa a escala real</h2>\n    ' + svg +
       '\n    <small>Escala real: 1 unidad = 1 cm; muros de 12 cm. <b style="color:var(--new)">En rojo</b> las medidas que me diste '
       '(dormitorio 1, dormitorio 2, 2.40 m entre cuartos, fondo de la sala 2.70 m). <b>En gris</b> lo estimado: ancho de la sala, '
       'fondo del baño (1.52 m) y del vestidor (0.55 m), ventanales (2.0 m), posición de puertas y muebles de la cocina. '
       'Verde punteado = puertas corredizas de 0.8 m; el acceso al vestidor mide ~0.5 m. La isla del render no la dibujé: con 2.70 m de fondo no deja un paso cómodo (≥ 0.9 m) frente a los mesones.</small>\n  </section>')
s = s[:a] + new + s[b:]
open(p, "w", encoding="utf-8").write(s)
print("ok", len(out))
