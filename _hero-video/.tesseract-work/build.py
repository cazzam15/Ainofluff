"""Generates the HeroLoop action batch. Edit PAIRS / layout here, then re-run on a fresh project."""
import json

def hexc(h, a=1.0):
    h = h.lstrip('#'); return [int(h[i:i+2], 16) / 255 for i in (0, 2, 4)] + [a]

DARK_LINE, MUTED, TEAL, OFF, RED, DIM = hexc('#2C3242'), hexc('#888780'), hexc('#1D9E75'), hexc('#F5F5F0'), hexc('#E24B4A'), hexc('#5F5E5A')
X = 96
PAIR_MS = 3000
# (jargon, plain English, strike width in px measured from a preview render)
PAIRS = [
    ("Large language model", "A chatbot that writes like a person", None),
    ("Agentic AI", "AI that does the job for you", None),
    ("Hallucination", "When AI makes\nthings up", None),
]
try:
    PAIRS = [(j, p, w) for (j, p, _), w in zip(PAIRS, json.load(open('.tesseract-work/strike-widths.json')))]
except FileNotFoundError:
    pass

EASE = {"type": "cubicBezier", "x1": 0.2, "y1": 0, "x2": 0.2, "y2": 1}
EASE_IN = {"type": "cubicBezier", "x1": 0.4, "y1": 0, "x2": 1, "y2": 1}
LIN = {"type": "linear"}
T0 = lambda x, y: {"anchorPoint": [0, 0], "position": [x, y], "scale": [100, 100], "rotation": 0, "opacity": 100}

def rect(i, name, x, y, w, h, color, start=0, dur=9000):
    return {"type": "createFxRectLayer", "compositionId": "main", "layerId": i, "name": name, "insertIndex": 0,
            "activeRange": {"start": start, "duration": dur}, "transform": T0(x, y),
            "rect": {"size": [w, h], "fillColor": color}}

def text(i, name, x, y, s, family, style, size, color, start=0, dur=9000, box=None, tracking=None):
    st = {"text": s, "fontFamily": family, "fontStyle": style, "fontSize": size, "fillColor": color, "justification": "left"}
    if box: st.update({"boxText": True, "boxPosition": [0, 0], "boxSize": box})
    if tracking is not None: st["tracking"] = tracking
    return {"type": "createFxTextLayer", "compositionId": "main", "layerId": i, "name": name, "insertIndex": 0,
            "activeRange": {"start": start, "duration": dur}, "transform": T0(x, y), "sourceText": st}

def keys(layer, prop, pts, tag):
    return {"type": "setFxPropertyKeyframes", "compositionId": "main",
            "property": {"layerId": layer, "propertyType": prop},
            "keyframes": [{"id": f"{tag}-{prop}-{n}", "layerTime": t, "value": {"type": "float", "value": v}, "easing": e}
                          for n, (t, v, e) in enumerate(pts)]}

SG, INTER = "Space Grotesk Light", "Inter"
JARGON_BASE, PLAIN_TOP = 360, 590
acts = [
    text(1, "Label: jargon", X, 230, "JARGON", INTER, "Medium", 26, MUTED, tracking=180),
    rect(3, "Divider", X, 490, 888, 2, DARK_LINE),
    text(2, "Label: plain English", X, 530, "PLAIN ENGLISH", INTER, "Medium", 26, TEAL, tracking=180),
]
for k in range(3):  # progress dots
    acts.append(rect(4 + k, f"Dot {k+1}", X + k * 56, 870, 40, 6, DARK_LINE))
    acts.append(rect(7 + k, f"Dot {k+1} active", X + k * 56, 870, 40, 6, TEAL, k * PAIR_MS, PAIR_MS))
    acts.append(keys(7 + k, "scaleX", [(0, 0, LIN), (400, 100, EASE)], f"dot{k}"))

for k, (jargon, plain, sw) in enumerate(PAIRS):
    j, s, p, start, tag = 10 + k * 10, 11 + k * 10, 12 + k * 10, k * PAIR_MS, f"pair{k}"
    acts += [
        text(j, f"Jargon {k+1}", X, JARGON_BASE, jargon, SG, "Medium", 84, DIM, start, PAIR_MS),
        rect(s, f"Strike {k+1}", X - 8, JARGON_BASE - 30, (sw or 800) + 16, 8, RED, start, PAIR_MS),
        text(p, f"Plain {k+1}", X, PLAIN_TOP, plain, SG, "Bold", 84, OFF, start, PAIR_MS, box=[888, 220]),
        keys(j, "opacity", [(0, 0, LIN), (350, 100, EASE), (2600, 100, LIN), (2900, 0, EASE_IN)], tag + "j"),
        keys(j, "positionY", [(0, JARGON_BASE + 28, LIN), (450, JARGON_BASE, EASE)], tag + "j"),
        keys(s, "scaleX", [(0, 0, LIN), (650, 0, LIN), (1000, 100, EASE)], tag + "s"),
        keys(s, "opacity", [(0, 100, LIN), (2600, 100, LIN), (2900, 0, EASE_IN)], tag + "s"),
        keys(p, "opacity", [(0, 0, LIN), (1050, 0, LIN), (1450, 100, EASE), (2600, 100, LIN), (2900, 0, EASE_IN)], tag + "p"),
        keys(p, "positionY", [(0, PLAIN_TOP + 32, LIN), (1050, PLAIN_TOP + 32, LIN), (1550, PLAIN_TOP, EASE)], tag + "p"),
    ]
json.dump(acts, open('.tesseract-work/edits.json', 'w'), indent=1)
print(len(acts), "actions")
