import os
import json
import math
import glob
from PIL import Image

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MAIN_DIR = os.path.join(BASE_DIR, "images-game", "main-game")
SHEET_DIR = os.path.join(MAIN_DIR, "spritesheets")
METADATA_PATH = os.path.join(MAIN_DIR, "spritesheets.json")

COLS = 10

SEQUENCES = [
    ("sun/background", "jpg", 80),
    ("night/background", "jpg", 80),
    ("spider-man/ps-spidey", "png", 80),
    ("spider-man/start-spidey", "png", 80),
    ("shadow/spider-man/wait", "png", 80),
    ("shadow/spider-man/start", "png", 80),
    ("spider-effect", "png", 40),
]

def frames_to_spritesheet(folder, ext, count, output_path):
    fw, fh = None, None
    frames = []
    for i in range(count):
        path = os.path.join(folder, f"frm{i:04d}.{ext}")
        if not os.path.exists(path):
            print(f"  WARN: {path} not found, skipping")
            continue
        img = Image.open(path).convert("RGBA")
        if fw is None:
            fw, fh = img.size
        frames.append(img)

    if not frames:
        return None

    n = len(frames)
    rows = math.ceil(n / COLS)
    sheet_w = fw * COLS
    sheet_h = fh * rows

    sheet = Image.new("RGBA", (sheet_w, sheet_h), (0, 0, 0, 0))
    for i, frame in enumerate(frames):
        col = i % COLS
        row = i // COLS
        sheet.paste(frame, (col * fw, row * fh))

    sheet.save(output_path, "PNG")
    return {"frames": n, "cols": COLS, "rows": rows, "frame_w": fw, "frame_h": fh, "ext": ext}

def main():
    os.makedirs(SHEET_DIR, exist_ok=True)
    metadata = {}

    for seq_name, ext, count in SEQUENCES:
        folder = os.path.join(MAIN_DIR, seq_name)
        sheet_name = seq_name.replace("/", "_")
        out_path = os.path.join(SHEET_DIR, f"{sheet_name}.png")
        print(f"Convirtiendo {seq_name} ({count} frames, {ext})...")
        result = frames_to_spritesheet(folder, ext, count, out_path)
        if result:
            metadata[seq_name] = result
            print(f"  -> {result}")
        else:
            print(f"  -> SKIP (no frames found)")

    with open(METADATA_PATH, "w") as f:
        json.dump(metadata, f, indent=2)
    print(f"\nMetadata guardada en: {METADATA_PATH}")
    print(f"Spritesheets guardados en: {SHEET_DIR}")
    print("Listo!")

if __name__ == "__main__":
    main()
