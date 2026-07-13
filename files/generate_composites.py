import subprocess
import os
import imageio_ffmpeg

FFMPEG = imageio_ffmpeg.get_ffmpeg_exe()
BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MAIN = os.path.join(BASE, "images-game", "main-game")
COST = os.path.join(BASE, "images-game", "costumes-section")
OUT_MAIN = os.path.join(MAIN, "videos-composites")
OUT_COST = os.path.join(COST, "videos-composites")


def run_ffmpeg(args):
    cmd = [FFMPEG] + args
    print("  running: " + " ".join(cmd[:8]) + " ...")
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
    if r.returncode != 0:
        print("  ERROR: " + r.stderr[-300:])
    return r.returncode == 0


def overlay(bg, fg, output, crf=18):
    return run_ffmpeg([
        "-y", "-i", bg, "-i", fg,
        "-filter_complex",
        "[1:v]colorkey=black:0.3:0.2[fg];[0:v][fg]overlay=0:0",
        "-c:v", "libx264", "-crf", str(crf),
        "-pix_fmt", "yuv420p", output
    ])


def overlay_white(bg, fg, output, crf=18):
    return run_ffmpeg([
        "-y", "-i", bg, "-i", fg,
        "-filter_complex",
        "[1:v]colorkey=white:0.15:0.1[fg];[0:v][fg]overlay=0:0",
        "-c:v", "libx264", "-crf", str(crf),
        "-pix_fmt", "yuv420p", output
    ])


def concat_two(v1, v2, output):
    concat_file = os.path.join(OUT_MAIN, "_concat.txt")
    with open(concat_file, "w") as f:
        f.write("file '" + v1.replace("\\", "/") + "'\n")
        f.write("file '" + v2.replace("\\", "/") + "'\n")
    return run_ffmpeg([
        "-y", "-f", "concat", "-safe", "0",
        "-i", concat_file,
        "-c:v", "libx264", "-crf", "18",
        "-pix_fmt", "yuv420p", output
    ])


def multiply_blend(fg1, fg2, output, crf=18):
    return run_ffmpeg([
        "-y", "-i", fg1, "-i", fg2,
        "-filter_complex",
        "[0:v][1:v]blend=all_mode=multiply",
        "-c:v", "libx264", "-crf", str(crf),
        "-pix_fmt", "yuv420p", output
    ])


def generate_start_composites():
    print("=== START MENU COMPOSITES ===")
    sun_bg = os.path.join(MAIN, "videos", "sun-background.mp4")
    night_bg = os.path.join(MAIN, "videos", "night-background.mp4")
    spidey_menu = os.path.join(MAIN, "videos", "spider-man-ps-spidey.mp4")
    spidey_start = os.path.join(MAIN, "videos", "spider-man-start-spidey.mp4")
    spider_effect = os.path.join(MAIN, "videos", "spider-effect.mp4")

    print("[1/3] start-menu-sun.mp4 (sun-bg + spidey-menu overlaid)")
    overlay(sun_bg, spidey_menu, os.path.join(OUT_MAIN, "start-menu-sun.mp4"))

    print("[2/3] start-menu-night.mp4 (night-bg + spidey-menu overlaid)")
    overlay(night_bg, spidey_menu, os.path.join(OUT_MAIN, "start-menu-night.mp4"))

    print("[3/3] start-action.mp4 (spidey-start then spider-effect)")
    tmp_action = os.path.join(OUT_MAIN, "_tmp_action.mp4")
    overlay(sun_bg, spidey_start, tmp_action)
    concat_two(tmp_action, spider_effect, os.path.join(OUT_MAIN, "start-action.mp4"))
    if os.path.exists(tmp_action):
        os.remove(tmp_action)


def generate_costume_composites():
    print("\n=== COSTUME COMPOSITES ===")
    shadow = os.path.join(COST, "videos", "shadow.mp4")
    for i in range(1, 19):
        pose = os.path.join(COST, "videos", "suit-pose-{}.mp4".format(i))
        output = os.path.join(OUT_COST, "costume-{}.mp4".format(i))
        print("[{}/18] costume-{}.mp4 (shadow + pose)".format(i, i))
        multiply_blend(shadow, pose, output)


if __name__ == "__main__":
    os.makedirs(OUT_MAIN, exist_ok=True)
    os.makedirs(OUT_COST, exist_ok=True)
    generate_start_composites()
    generate_costume_composites()
    print("\nDone! All composites generated.")
