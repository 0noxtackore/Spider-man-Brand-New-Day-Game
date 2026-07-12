import os
import json
import math
from PIL import Image

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
COSTUMES_DIR = os.path.join(BASE_DIR, "images-game", "costumes-section")
SHEET_DIR = os.path.join(COSTUMES_DIR, "spritesheets")
METADATA_PATH = os.path.join(COSTUMES_DIR, "spritesheets.json")

COLS = 5

def gif_to_spritesheet(gif_path, output_path):
    gif = Image.open(gif_path)
    n_frames = gif.n_frames
    fw, fh = gif.size
    rows = math.ceil(n_frames / COLS)
    sheet_w = fw * COLS
    sheet_h = fh * rows

    sheet = Image.new("RGBA", (sheet_w, sheet_h), (0, 0, 0, 0))
    for i in range(n_frames):
        gif.seek(i)
        frame = gif.convert("RGBA")
        col = i % COLS
        row = i // COLS
        sheet.paste(frame, (col * fw, row * fh))
    sheet.save(output_path, "PNG")
    return {"frames": n_frames, "cols": COLS, "rows": rows, "frame_w": fw, "frame_h": fh}

def main():
    os.makedirs(SHEET_DIR, exist_ok=True)
    metadata = {}

    print("Convirtiendo shadow.gif...")
    gif_path = os.path.join(COSTUMES_DIR, "shadow.gif")
    out_path = os.path.join(SHEET_DIR, "shadow.png")
    if os.path.exists(gif_path):
        metadata["shadow"] = gif_to_spritesheet(gif_path, out_path)
        print(f"  -> {metadata['shadow']}")

    for i in range(1, 19):
        gif_path = os.path.join(COSTUMES_DIR, f"suit-pose/{i}.gif")
        out_path = os.path.join(SHEET_DIR, f"suit-pose-{i}.png")
        if os.path.exists(gif_path):
            key = f"suit-pose-{i}"
            metadata[key] = gif_to_spritesheet(gif_path, out_path)
            print(f"  {key}: {metadata[key]}")
        else:
            print(f"  suit-pose/{i}.gif: NOT FOUND, skipped")

    with open(METADATA_PATH, "w") as f:
        json.dump(metadata, f, indent=2)
    print(f"\nMetadata guardada en: {METADATA_PATH}")
    print(f"Spritesheets guardados en: {SHEET_DIR}")
    print("Listo! Ahora puedes eliminar los GIFs originales si quieres.")

if __name__ == "__main__":
    main()
