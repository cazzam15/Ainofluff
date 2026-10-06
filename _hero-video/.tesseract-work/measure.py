"""Measure the rendered width of each jargon word (frames before the strike draws) -> strike-widths.json"""
import json, subprocess, sys
T, base = sys.argv[1], int(sys.argv[2])
widths = []
for k in range(3):
    png = f'.tesseract-work/checks/measure{k}.png'
    subprocess.run([T, 'preview', '--project', 'hero-loop.tsrct', '--time', str(k * 3 + 0.55), '--output', png], check=True, capture_output=True)
    raw = subprocess.run(['ffmpeg', '-v', 'error', '-i', png, '-f', 'rawvideo', '-pix_fmt', 'gray', '-'], capture_output=True, check=True).stdout
    xs = [x for y in range(base - 90, base + 25) for x in range(1080) if raw[y * 1080 + x] > 45]
    widths.append(max(xs) - 96 if xs else None)
print(widths)
json.dump(widths, open('.tesseract-work/strike-widths.json', 'w'))
