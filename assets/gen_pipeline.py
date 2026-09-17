# Generates assets/pipeline.svg (isometric deploy pipeline). Run from repo root: python3 assets/gen_pipeline.py
import sys
C, S = 0.8660254, 0.5
OX, OY, W, H = 110, 215, 860, 460
BG = "#0D1117"

def P(x, y, z):
    return OX + (x - y) * C, OY + (x + y) * S - z

def pts(*ps):
    return " ".join(f"{a:.1f},{b:.1f}" for a, b in (P(*p) for p in ps))

def mix(hex_, f):
    a = [int(hex_[i:i + 2], 16) for i in (1, 3, 5)]
    b = [int(BG[i:i + 2], 16) for i in (1, 3, 5)]
    return "#" + "".join(f"{round(bb + (aa - bb) * f):02X}" for aa, bb in zip(a, b))

def box(x0, y0, z0, dx, dy, dz, col):
    x1, y1, z1 = x0 + dx, y0 + dy, z0 + dz
    return (f'<g stroke="{col}" stroke-opacity=".55" stroke-linejoin="round">'
            f'<polygon points="{pts((x0,y0,z1),(x1,y0,z1),(x1,y1,z1),(x0,y1,z1))}" fill="{mix(col, .95)}"/>'
            f'<polygon points="{pts((x0,y1,z0),(x1,y1,z0),(x1,y1,z1),(x0,y1,z1))}" fill="{mix(col, .6)}"/>'
            f'<polygon points="{pts((x1,y0,z0),(x1,y1,z0),(x1,y1,z1),(x1,y0,z1))}" fill="{mix(col, .38)}"/></g>')

def line(a, b, col, w=1.5, extra=""):
    (x1, y1), (x2, y2) = P(*a), P(*b)
    return f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="{col}" stroke-width="{w}" stroke-linecap="round"{extra}/>'

def label(x, y, z, name, tool, col):
    sx, sy = P(x, y, z)
    return (f'<text x="{sx:.1f}" y="{sy - 22:.1f}" text-anchor="middle" class="nm" style="fill:{col}">{name}</text>'
            f'<text x="{sx:.1f}" y="{sy - 6:.1f}" text-anchor="middle" class="dim">{tool}</text>')

BLUE, GREEN, CYAN, PURPLE, ORANGE, BELT = "#58A6FF", "#3FB950", "#56D4DD", "#BC8CFF", "#F0883E", "#30363D"
o = []

# conveyor: segment B (right-up leg) first, it sits behind segment A
o.append(f'<g stroke="{BELT}" stroke-linejoin="round">'
         f'<polygon points="{pts((352,-388,8),(388,-388,8),(388,-18,8),(352,-18,8))}" fill="#21262D"/>'
         f'<polygon points="{pts((388,-388,0),(388,-18,0),(388,-18,8),(388,-388,8))}" fill="#161B22"/>'
         f'<polygon points="{pts((-18,-18,8),(388,-18,8),(388,18,8),(-18,18,8))}" fill="#21262D"/>'
         f'<polygon points="{pts((-18,18,0),(388,18,0),(388,18,8),(-18,18,8))}" fill="#161B22"/>'
         f'<polygon points="{pts((388,-18,0),(388,18,0),(388,18,8),(388,-18,8))}" fill="#161B22"/></g>')
a, b, c = P(0, 0, 8), P(370, 0, 8), P(370, -370, 8)
o.append(f'<polyline points="{a[0]:.1f},{a[1]:.1f} {b[0]:.1f},{b[1]:.1f} {c[0]:.1f},{c[1]:.1f}" fill="none" stroke="#484F58" stroke-dasharray="4 7"/>')

# packets ride the belt; drawn before stations so they vanish "into" each machine
dx, dy = P(370, 0, 0)[0] - P(0, 0, 0)[0], P(370, 0, 0)[1] - P(0, 0, 0)[1]
for i, d in enumerate((0, -2.4, -4.8)):
    o.append(f'<g class="pkt" style="animation-delay:{d}s">{box(-6, -6, 8, 12, 12, 12, "#E6EDF3")}</g>')

# S0 code: laptop
o.append(box(-30, -22, 8, 60, 44, 6, BLUE))
o.append(box(-30, -22, 14, 60, 4, 40, BLUE))
o.append(f'<polygon points="{pts((-26,-17.9,18),(26,-17.9,18),(26,-17.9,50),(-26,-17.9,50))}" fill="{BG}"/>')
for z, x0, x1, col in ((44, -22, 8, BLUE), (38, -16, 16, GREEN), (32, -16, 2, "#8B949E"), (26, -22, 12, BLUE)):
    o.append(line((x0, -17.8, z), (x1, -17.8, z), col, 2))
o.append(label(-30, -22, 54, "code", "git push", BLUE))

# S4 prod: pedestal + globe (drawn early: far back)
o.append(box(346, -394, 8, 48, 48, 10, ORANGE))
gx, gy = P(370, -370, 18)
o.append(f'<ellipse class="ping" cx="{gx:.1f}" cy="{gy:.1f}" rx="36.7" ry="21.2" fill="none" stroke="{ORANGE}" stroke-width="1.5"/>')
o.append(f'<circle cx="{gx:.1f}" cy="{gy - 30:.1f}" r="30" fill="url(#sphere)"/>'
         f'<g fill="none" stroke="#FFD8B5" stroke-opacity=".55"><ellipse cx="{gx:.1f}" cy="{gy - 30:.1f}" rx="30" ry="10"/>'
         f'<ellipse cx="{gx:.1f}" cy="{gy - 30:.1f}" rx="12" ry="30"/><ellipse cx="{gx:.1f}" cy="{gy - 44:.1f}" rx="22" ry="6"/></g>')
o.append(f'<text x="{gx:.1f}" y="{gy - 90:.1f}" text-anchor="middle" class="nm" style="fill:{ORANGE}">prod</text>'
         f'<text x="{gx:.1f}" y="{gy - 74:.1f}" text-anchor="middle" class="dim">real users</text>')

# S1 ci: cube with a check on its top face
o.append(box(157, -28, 8, 56, 56, 44, GREEN))
# check mark drawn in the top-face plane: p = screen-right axis, q = screen-down axis
chk = [P(185 + (pp + q) / 2 ** .5, (q - pp) / 2 ** .5, 52.2) for pp, q in ((-15, 0), (-5, 10), (15, -10))]
o.append(f'<polyline points="{" ".join(f"{a:.1f},{b:.1f}" for a, b in chk)}" fill="none" stroke="#F0FFF4" stroke-width="5" stroke-linecap="round" stroke-linejoin="round"/>')
o.append(label(157, -28, 52, "ci", "test · lint", GREEN))

# S3 infra: server tower with blinking LEDs
o.append(box(346, -209, 8, 48, 48, 100, PURPLE))
for i, z in enumerate((30, 50, 70, 90)):
    o.append(line((352, -160.8, z), (388, -160.8, z), mix(PURPLE, .25), 2))
    o.append(line((394.2, -196, z), (394.2, -167, z), mix(PURPLE, .2), 2))
    lx, ly = P(394.2, -203, z)
    o.append(f'<circle class="led" style="animation-delay:{i * .35:.2f}s" cx="{lx:.1f}" cy="{ly:.1f}" r="2.2" fill="{GREEN}"/>')
o.append(label(346, -209, 108, "infra", "terraform", PURPLE))

# S2 build: stacked containers with ribs
def crate(x0, y0, z0, dx, dy, dz):
    parts = [box(x0, y0, z0, dx, dy, dz, CYAN)]
    rib = mix(CYAN, .3)
    for x in range(x0 + 8, x0 + dx - 4, 8):
        parts.append(line((x, y0 + dy + .2, z0 + 4), (x, y0 + dy + .2, z0 + dz - 4), rib))
    for y in range(y0 + 7, y0 + dy - 3, 7):
        parts.append(line((x0 + dx + .2, y, z0 + 4), (x0 + dx + .2, y, z0 + dz - 4), rib))
    return "".join(parts)
o.append(crate(342, -28, 8, 56, 28, 22))
o.append(crate(342, 0, 8, 56, 28, 22))
o.append(crate(348, -14, 30, 44, 28, 20))
o.append(label(348, -14, 50, "build", "docker", CYAN))

svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-labelledby="title desc">
  <title id="title">How I ship</title>
  <desc id="desc">Isometric deploy pipeline: code (git push) to CI (test, lint) to build (Docker) to infra (Terraform) to prod, with packets moving along a conveyor.</desc>
  <style>
    text {{ font-family: ui-monospace, SFMono-Regular, 'SF Mono', Menlo, Consolas, 'Liberation Mono', monospace; font-size: 13px; fill: #E6EDF3; }}
    .dim {{ fill: #8B949E; }} .ok {{ fill: #3FB950; }} .acc {{ fill: #58A6FF; }}
    .nm {{ font-size: 14px; font-weight: 700; }}
    .cmd {{ font-size: 15px; }}
    .bar {{ font-size: 13px; fill: #8B949E; }}
    .pkt {{ animation: flow 7.2s linear infinite; }}
    .led {{ animation: blink 1.4s steps(1) infinite; }}
    .ping {{ transform-box: fill-box; transform-origin: center; animation: ping 2.4s ease-out infinite; }}
    @keyframes flow {{
      0% {{ transform: translate(0, 0); opacity: 0; }}
      6%, 94% {{ opacity: 1; }}
      50% {{ transform: translate({dx:.1f}px, {dy:.1f}px); }}
      100% {{ transform: translate({2 * dx:.1f}px, 0); opacity: 0; }}
    }}
    @keyframes blink {{ 50% {{ opacity: .25; }} }}
    @keyframes ping {{ from {{ transform: scale(.7); opacity: .8; }} to {{ transform: scale(1.7); opacity: 0; }} }}
    @media (prefers-reduced-motion: reduce) {{
      .pkt, .ping {{ display: none; }}
      * {{ animation: none !important; }}
    }}
  </style>
  <defs>
    <clipPath id="card"><rect width="{W}" height="{H}" rx="12"/></clipPath>
    <radialGradient id="sphere" cx="38%" cy="32%" r="75%">
      <stop offset="0" stop-color="#FFC08A"/><stop offset=".55" stop-color="#F0883E"/><stop offset="1" stop-color="#7A3A0E"/>
    </radialGradient>
    <radialGradient id="glow" cx="{P(185, -185, 0)[0]:.0f}" cy="{P(185, -185, 0)[1] + 60:.0f}" r="420" gradientUnits="userSpaceOnUse">
      <stop offset="0" stop-color="#BC8CFF" stop-opacity=".12"/><stop offset="1" stop-color="#BC8CFF" stop-opacity="0"/>
    </radialGradient>
  </defs>
  <g clip-path="url(#card)">
    <rect width="{W}" height="{H}" fill="{BG}"/>
    <rect width="{W}" height="{H}" fill="url(#glow)"/>
    <rect width="{W}" height="36" fill="#161B22"/>
    <rect y="36" width="{W}" height="1" fill="#30363D"/>
  </g>
  <rect x=".5" y=".5" width="{W - 1}" height="{H - 1}" rx="11.5" fill="none" stroke="#30363D"/>
  <circle cx="22" cy="18" r="6" fill="#FF5F57"/><circle cx="42" cy="18" r="6" fill="#FEBC2E"/><circle cx="62" cy="18" r="6" fill="#28C840"/>
  <text class="bar" x="{W / 2:.0f}" y="23" text-anchor="middle">pipeline · main</text>
  <text x="28" y="68" class="cmd"><tspan class="ok">$</tspan> git push origin main</text>
  <text x="{W - 28}" y="68" text-anchor="end" class="dim">commit → prod, fully automated</text>
  {"".join(o)}
  <text x="28" y="{H - 22}"><tspan class="ok">●</tspan> all checks passed <tspan class="dim">· shipped to prod</tspan></text>
</svg>
'''
open(sys.argv[1] if len(sys.argv) > 1 else "assets/pipeline.svg", "w").write(svg)
