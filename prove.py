from pathlib import Path
import re

from PIL import Image, ImageChops, ImageDraw


def log(name: str) -> str:
    return Path(f"{name}.log").read_text(encoding="utf-8", errors="replace")


legacy_log = log("legacy")
modern_log = log("modern")
assert re.search(r"Shaper:.*SIMPLE", legacy_log, re.I), "Old libass did not report SIMPLE"
assert re.search(r"Shaper:.*HarfBuzz", modern_log, re.I), "New libass lacks HarfBuzz"

legacy = Image.open("legacy.png").convert("RGB")
modern = Image.open("modern.png").convert("RGB")
assert legacy.size == modern.size == (1080, 1920)

regions = ((65, 220, 1015, 620), (65, 1320, 1015, 1720))
sheet = Image.new("RGB", (1900, 860), "#080c14")
draw = ImageDraw.Draw(sheet)
draw.text((20, 14), "FFmpeg 4.1 / SIMPLE", fill="white")
draw.text((970, 14), "FFmpeg 7.0.2 / HarfBuzz", fill="white")

for row, region in enumerate(regions):
    old_crop = legacy.crop(region)
    new_crop = modern.crop(region)
    assert ImageChops.difference(old_crop, new_crop).getbbox(), (
        f"No changed pixels in text region {row}"
    )
    sheet.paste(old_crop, (0, 60 + row * 400))
    sheet.paste(new_crop, (950, 60 + row * 400))

sheet.save("shaping-contact.png", optimize=True)
print("PASS: Linux libass logs report SIMPLE and HarfBuzz; both 1080x1920 text frames rendered and differ in title and caption pixels.")
