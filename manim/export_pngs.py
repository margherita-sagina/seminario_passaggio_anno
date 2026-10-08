"""Save the final frame of every presenter checkpoint and a contact sheet."""
from pathlib import Path
import json
import math
import sys
import av
from PIL import Image, ImageDraw
from seminar import SCENES

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "outputs" / "pngs"
OUT.mkdir(parents=True, exist_ok=True)
names = sys.argv[1:] or [scene.__name__ for scene in SCENES]
manifest = []

for name in names:
    source = ROOT / "slides" / f"{name}.json"
    if not source.exists():
        raise SystemExit(f"Missing {source}; render {name} first.")
    slides = json.loads(source.read_text())["slides"]
    for index, slide in enumerate(slides, 1):
        video = ROOT / slide["file"]
        with av.open(str(video)) as container:
            last = None
            for frame in container.decode(video=0):
                last = frame
            if last is None:
                raise SystemExit(f"No frames in {video}")
            target = OUT / f"{name}-{index:02d}.png"
            last.to_image().save(target)
        manifest.append({"scene": name, "checkpoint": index,
                         "png": target.name, "notes": slide.get("notes", "")})
        print(target.relative_to(ROOT))

(OUT / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2))

# One page per scene makes visual review practical even for the full deck.
for name in names:
    items = [item for item in manifest if item["scene"] == name]
    if not items:
        continue
    thumb_w, thumb_h, gap, header = 480, 270, 18, 36
    cols = min(3, len(items))
    rows = math.ceil(len(items) / cols)
    sheet = Image.new("RGB", (gap + cols * (thumb_w + gap),
                              gap + rows * (thumb_h + header + gap)), "#FFFCF5")
    draw = ImageDraw.Draw(sheet)
    for i, item in enumerate(items):
        x = gap + i % cols * (thumb_w + gap)
        y = gap + i // cols * (thumb_h + header + gap)
        with Image.open(OUT / item["png"]) as image:
            sheet.paste(image.convert("RGB").resize((thumb_w, thumb_h)), (x, y))
        draw.text((x, y + thumb_h + 5), f'{name} · checkpoint {item["checkpoint"]}',
                  fill="#3D4545")
    sheet.save(OUT / f"{name}-sheet.png")

# One thumbnail per scene gives a quick whole-deck layout review.
if set(names) == {scene.__name__ for scene in SCENES}:
    width, height, gap, header, cols = 400, 225, 16, 32, 4
    rows = math.ceil(len(SCENES) / cols)
    sheet = Image.new("RGB", (gap + cols*(width+gap),
                              gap + rows*(height+header+gap)), "#FFFCF5")
    draw = ImageDraw.Draw(sheet)
    for i, scene in enumerate(SCENES):
        item = [m for m in manifest if m["scene"] == scene.__name__][-1]
        x = gap + i%cols*(width+gap)
        y = gap + i//cols*(height+header+gap)
        with Image.open(OUT / item["png"]) as frame:
            sheet.paste(frame.convert("RGB").resize((width,height)), (x,y))
        draw.text((x,y+height+4), f"{scene.number:02d}  {scene.title}", fill="#3D4545")
    sheet.save(OUT / "deck-overview.png")

print(f"Exported {len(manifest)} checkpoint PNGs to {OUT}")
