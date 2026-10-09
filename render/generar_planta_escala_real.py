# Planta completa a escala real (cm). x este, y norte. Origen: esquina SO interior del dormitorio 1.
D1W, D1H = 305, 305            # dormitorio 1 (medida real)
D2W, D2H = 270, 270            # dormitorio 2 (medida real)
GAP = 240                      # entre cuartos (cara interior a cara interior)
T = 12                         # muro
E1 = D1W                       # cara interior este del dorm 1
X2 = D1W + GAP                 # cara interior oeste del dorm 2 (545)
SALA_D = 270                   # fondo de la sala (medida real)
N1 = D1H + T                   # cara exterior norte del dorm 1 (317)
SN = N1 + SALA_D               # cara interior norte de la sala (587)
TOP = SN + T + 66              # para voltear y
def Y(y): return TOP - y
out = []
def rect(x0, y0, x1, y1, fill, stroke=None, sw=0, extra=""):
    st = f' stroke="{stroke}" stroke-width="{sw}"' if stroke else ""
    out.append(f'<rect x="{x0}" y="{Y(y1)}" width="{x1-x0}" height="{y1-y0}" fill="{fill}"{st} {extra}/>')
def text(x, y, s, size=14, cls="", anchor="middle", extra=""):
    c = f' class="{cls}"' if cls else ""
    out.append(f'<text x="{x}" y="{Y(y)}" text-anchor="{anchor}" font-size="{size}"{c} {extra}>{s}</text>')
def line(x0, y0, x1, y1, cls="dim", extra=""):
    out.append(f'<line x1="{x0}" y1="{Y(y0)}" x2="{x1}" y2="{Y(y1)}" class="{cls}" {extra}/>')
def hdim(x0, x1, y, label, real=True):
    cl, tc = ("dim", "dimt") if real else ("dimg", "dimgt")
    line(x0, y, x1, y, cl); line(x0, y-5, x0, y+5, cl); line(x1, y-5, x1, y+5, cl)
    text((x0+x1)/2, y+8, label, 15, tc)
def vdim(x, y0, y1, label, real=True, side=-1):
    cl, tc = ("dim", "dimt") if real else ("dimg", "dimgt")
    line(x, y0, x, y1, cl); line(x-5, y0, x+5, y0, cl); line(x-5, y1, x+5, y1, cl)
    out.append(f'<text transform="translate({x+side*16},{Y((y0+y1)/2)}) rotate(-90)" text-anchor="middle" font-size="15" class="{tc}">{label}</text>')
FLOOR, BATH, WALL = "var(--floor)", "var(--bath)", "var(--wall)"
W = lambda x0, y0, x1, y1: rect(x0, y0, x1, y1, WALL)

# posiciones derivadas
CL0, CL1 = E1 + T, E1 + T + 104          # vestidor / módulo izq: 317..421
DV0, DV1 = CL1, CL1 + T                  # divisor 421..433
RM0, RM1 = DV1, X2 - T                   # módulo der: 433..533
SW0, SE = 100, 785                       # sala: cara interior oeste / este
BATH_D, CLOS_D = 152, 55

# ---- pisos
rect(0, 0, D1W, D1H, FLOOR); rect(X2, 0, X2 + D2W, D2H, FLOOR)
rect(SW0, N1, SE, SN, FLOOR)
rect(CL0, D2H + T, SE, N1, FLOOR)
rect(CL0, BATH_D + T + CLOS_D + T, RM1, D2H + T, FLOOR)       # sobre el vestidor
rect(RM0, BATH_D + T, RM1, BATH_D + T + CLOS_D + T, FLOOR)    # hueco sobre el baño
rect(X2, D2H, X2 + 80, D2H + T, FLOOR)                         # entrada dorm 2
rect(CL0, BATH_D + T, CL1, BATH_D + T + CLOS_D, FLOOR)         # vestidor
rect(CL0, 0, CL1, BATH_D, BATH); rect(RM0, 0, RM1, BATH_D, BATH)
# ---- muebles
by0 = (D1H - 150) // 2                                         # cama 1 centrada
rect(0, by0, 190, by0 + 150, "#9a9a9a", "#555", 2); rect(0, by0, 34, by0 + 150, "#f2f2f2", "#555", 2)
text(112, by0 + 85, "Cama 1", 17, "lbl"); text(112, by0 + 65, "1.5 × 1.9 m", 13)
rect(0, by0 - 46, 40, by0 - 6, "#b98a5e", "#7a5a3a", 2); rect(0, by0 + 156, 40, by0 + 196, "#b98a5e", "#7a5a3a", 2)
b2x = X2 + D2W - 150
rect(b2x, 0, b2x + 150, 190, "#9a9a9a", "#555", 2); rect(b2x, 0, b2x + 150, 28, "#f2f2f2", "#555", 2)
text(b2x + 75, 105, "Cama 2", 17, "lbl"); text(b2x + 75, 85, "1.5 × 1.9 m", 13); text(b2x + 75, 66, "pies ↑ · espaldar ↓", 12)
rect(b2x - 43, 0, b2x - 3, 40, "#b98a5e", "#7a5a3a", 2)
n0 = SN - 90                                                   # sofá L
rect(SW0, n0, 300, SN, "#e6dccb", "#8a7d6a", 2); rect(SW0, n0 - 130, 190, n0, "#e6dccb", "#8a7d6a", 2)
out.append(f'<circle cx="320" cy="{Y(SN-21)}" r="15" fill="#5c8a4a"/>')
ty = SN - 156                                                   # mesa
rect(350, ty - 40, 490, ty + 40, "#7a5236", "#4a2f1a", 2); text(420, ty - 5, "1.4 × 0.8 m", 13, extra='style="fill:#fff"')
for (cx0, cy0) in [(363, ty + 35), (433, ty + 35), (363, ty - 79), (433, ty - 79)]:
    rect(cx0, cy0, cx0 + 44, cy0 + 44, "#c9bfae", "#7a6f5e", 2)
kx = SE - 763 + 0                                               # corrimiento este
rect(552, SN - 70, 622, SN, "#b8bcc0", "#6b7076", 2); text(587, SN - 33, "Nevera", 12)
rect(622, SN - 60, 662, SN, "#cfc9bf", "#8a847a", 2); rect(662, SN - 60, 722, SN, "#333"); text(692, SN - 33, "Estufa", 12, extra='style="fill:#fff"')
rect(722, SN - 60, SE, SN, "#cfc9bf", "#8a847a", 2); rect(SE - 60, SN - 190, SE, SN - 60, "#cfc9bf", "#8a847a", 2)
rect(SE - 48, SN - 156, SE - 8, SN - 91, "#9aa4ad", "#555", 2)
out.append(f'<rect x="560" y="{Y(SN-170)}" width="90" height="40" fill="none" stroke="#8a847a" stroke-width="2" stroke-dasharray="6 4"/>')
text(605, SN - 155, "isla 0.9×0.4 (opcional)", 11)
# ---- paredes
W(-T, -T, X2 + D2W + T, 0)                                      # sur
W(-T, 0, 0, N1)                                                 # dorm 1 oeste
W(-T, D1H, 195, N1); W(275, D1H, E1 + T, N1)                   # norte dorm 1 (puerta 195-275)
W(E1, 0, E1 + T, 20); W(E1, 100, E1 + T, 167); W(E1, 217, E1 + T, N1)   # este dorm 1
W(CL0, BATH_D + T + CLOS_D, DV1, BATH_D + T + CLOS_D + T)       # norte del vestidor
W(DV0, 0, DV1, BATH_D + T + CLOS_D + T)                         # divisor
W(E1, BATH_D, RM0 + 10, BATH_D + T); W(RM0 + 90, BATH_D, X2, BATH_D + T)   # norte del baño (puerta 443-523)
W(X2 - T, 0, X2, 66); W(X2 - T, 146, X2, D2H + T)               # oeste dorm 2 (puerta 66-146)
W(X2 + 80, D2H, X2 + D2W + T, D2H + T)                          # norte dorm 2 (entrada 80 cm)
W(X2 + D2W, 0, X2 + D2W + T, D2H + T)                           # este dorm 2
W(SW0 - T, N1, SW0, SN + T); W(SW0 - T, SN, SE + T, SN + T); W(SE, D2H + T, SE + T, SN + T)
# ---- ventanales (estimados 2.0 m centrados)
rect(D1W//2 - 100, -T, D1W//2 + 100, 0, "#7ec8ee", "#245", 2)
rect(X2 + D2W//2 - 100, -T, X2 + D2W//2 + 100, 0, "#7ec8ee", "#245", 2)
# ---- puertas corredizas
G = 'stroke="var(--ok)" stroke-width="6" stroke-dasharray="10 5"'
def door(x0, y0, x1, y1): out.append(f'<line x1="{x0}" y1="{Y(y0)}" x2="{x1}" y2="{Y(y1)}" {G}/>')
door(195, D1H + 6, 275, D1H + 6); door(E1 + 6, 20, E1 + 6, 100); door(E1 + 6, 167, E1 + 6, 217)
door(RM0 + 10, BATH_D + 6, RM0 + 90, BATH_D + 6); door(X2 - 6, 66, X2 - 6, 146); door(X2, D2H + 6, X2 + 80, D2H + 6)
GT = 'style="fill:var(--ok)" font-weight="600"'
text(235, D1H + 20, "puerta 0.8 m", 12, extra=GT); text(RM0 + 50, BATH_D + 18, "puerta 0.8 m", 12, extra=GT)
text(X2 + 40, D2H + 20, "entrada 0.8 m", 12, extra=GT)
# ---- rótulos
text(141, D1H - 40, "Dormitorio 1", 18, "lbl"); text(141, D1H - 60, "3.05 × 3.05 m", 15, "dimt")
text(X2 + 135, 245, "Dormitorio 2", 18, "lbl"); text(X2 + 135, 225, "2.70 × 2.70 m", 15, "dimt")
for (cx, a, b) in [((CL0 + CL1)/2, "WC + lavabo", "1.04 × 1.52 m"), ((RM0 + RM1)/2, "ducha + lavabo", "1.00 × 1.52 m")]:
    text(cx, 110, "Baño", 15, "lbl"); text(cx, 90, a, 11); text(cx, 74, b, 11)
text((CL0 + CL1)/2, BATH_D + T + 28, "Vestidor", 12, "lbl"); text((CL0 + CL1)/2, BATH_D + T + 13, "1.04 × 0.55 m", 11)
text(200, SN - 220, "Sala", 18, "lbl"); text(420, ty - 100, "Comedor", 16, "lbl"); text(690, SN - 215, "Cocina", 18, "lbl")
# ---- cotas
hdim(0, D1W, -40, "3.05 m"); hdim(D1W, X2, -40, "2.40 m entre cuartos"); hdim(X2, X2 + D2W, -40, "2.70 m")
hdim(-T, X2 + D2W + T, -68, "≈ 8.4 m ancho total (estimado)", real=False)
vdim(-32, 0, D1H, "3.05 m"); vdim(X2 + D2W + 30, 0, D2H, "2.70 m", side=1)
vdim(60, N1, SN, "2.70 m fondo de la sala"); hdim(SW0, SE, SN + T + 30, "≈ 6.9 m ancho de la sala (estimado)", real=False)
vdim(X2 + D2W + 70, -T, SN + T, "≈ 6.1 m fondo total (estimado)", real=False, side=1)
VB_H = TOP + 68 + 14
svg = (f'<svg viewBox="-80 0 1040 {VB_H}" role="img" aria-label="Planta completa a escala real">\n      '
       + "\n      ".join(out) + '\n    </svg>')

p = "/home/user/Pulso-app/index.html"
s = open(p, encoding="utf-8").read()
a = s.index('<section class="card">\n    <h2>Planta completa a escala real</h2>')
b = s.index('</section>', a) + len('</section>')
new = ('<section class="card">\n    <h2>Planta completa a escala real</h2>\n    ' + svg +
       '\n    <small>Escala real: 1 unidad = 1 cm; muros de 12 cm. <b style="color:var(--new)">En rojo</b> las medidas que me diste '
       '(dormitorio 1 de 3.05 × 3.05 m, dormitorio 2 de 2.70 × 2.70 m, 2.40 m entre cuartos, fondo de la sala 2.70 m). <b>En gris</b> lo estimado: ancho de la sala, '
       'fondo del baño (1.52 m) y del vestidor (0.55 m), ventanales (2.0 m), posición de puertas y muebles de la cocina. '
       'Verde punteado = puertas corredizas de 0.8 m; el acceso al vestidor mide ~0.5 m. Con la sala más profunda sobre el dormitorio 2 (≈ 3.05 m) la isla sí cabe, dibujada como opcional.</small>\n  </section>')
s = s[:a] + new + s[b:]
open(p, "w", encoding="utf-8").write(s)
print("ok", len(out), VB_H)
