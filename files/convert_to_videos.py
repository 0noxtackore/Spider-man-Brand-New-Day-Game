import os
import subprocess
import json
import imageio_ffmpeg

FFMPEG = imageio_ffmpeg.get_ffmpeg_exe()
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FPS = 30

def frames_to_mp4(folder, ext, count, output_path, fps=FPS):
    pattern = os.path.join(folder, "frm%04d." + ext)
    cmd = [
        FFMPEG, "-y", "-framerate", str(fps),
        "-i", pattern,
        "-c:v", "libx264", "-pix_fmt", "yuv420p",
        "-crf", "18", "-preset", "fast",
        output_path
    ]
    subprocess.run(cmd, capture_output=True, check=True)

def gif_to_mp4(gif_path, output_path, fps=FPS):
    cmd = [
        FFMPEG, "-y", "-i", gif_path,
        "-c:v", "libx264", "-pix_fmt", "yuv420p",
        "-crf", "18", "-preset", "fast",
        "-vf", "scale=1920:1080:force_original_aspect_ratio=decrease,pad=1920:1080:(ow-iw)/2:(oh-ih)/2:color=black@0.0",
        "-r", str(fps),
        output_path
    ]
    subprocess.run(cmd, capture_output=True, check=True)

def main():
    main_dir = os.path.join(BASE_DIR, "images-game", "main-game")
    costumes_dir = os.path.join(BASE_DIR, "images-game", "costumes-section")
    videos_main = os.path.join(main_dir, "videos")
    videos_costumes = os.path.join(costumes_dir, "videos")
    os.makedirs(videos_main, exist_ok=True)
    os.makedirs(videos_costumes, exist_ok=True)

    sequences = [
        ("sun/background", "jpg", 80),
        ("night/background", "jpg", 80),
        ("spider-man/ps-spidey", "png", 80),
        ("spider-man/start-spidey", "png", 80),
        ("spider-effect", "png", 40),
    ]

    for seq_name, ext, count in sequences:
        folder = os.path.join(main_dir, seq_name)
        vid_name = seq_name.replace("/", "-") + ".mp4"
        out = os.path.join(videos_main, vid_name)
        if os.path.exists(out):
            print(f"  SKIP {vid_name} (ya existe)")
            continue
        print(f"  Convirtiendo {seq_name} ({count} frames)...")
        try:
            frames_to_mp4(folder, ext, count, out)
            size_mb = os.path.getsize(out) / (1024 * 1024)
            print(f"    -> {vid_name} ({size_mb:.1f} MB)")
        except Exception as e:
            print(f"    ERROR: {e}")

    print("\n--- Costumes (GIF -> MP4) ---")
    gif_files = ["shadow.gif"] + [f"suit-pose/{i}.gif" for i in range(1, 19)]
    for gif_name in gif_files:
        gif_path = os.path.join(costumes_dir, gif_name)
        vid_name = gif_name.replace("/", "-").replace(".gif", ".mp4")
        out = os.path.join(videos_costumes, vid_name)
        if os.path.exists(out):
            print(f"  SKIP {vid_name} (ya existe)")
            continue
        if not os.path.exists(gif_path):
            print(f"  SKIP {gif_name} (no existe)")
            continue
        print(f"  Convirtiendo {gif_name}...")
        try:
            gif_to_mp4(gif_path, out)
            size_mb = os.path.getsize(out) / (1024 * 1024)
            print(f"    -> {vid_name} ({size_mb:.1f} MB)")
        except Exception as e:
            print(f"    ERROR: {e}")

    print("\nListo!")

if __name__ == "__main__":
    main()
