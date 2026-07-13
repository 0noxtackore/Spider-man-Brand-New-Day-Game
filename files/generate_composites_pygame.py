import pygame
import os
import sys
import subprocess
import imageio_ffmpeg

pygame.init()
scr = pygame.display.set_mode((1920, 1080))

FFMPEG = imageio_ffmpeg.get_ffmpeg_exe()
BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MAIN = os.path.join(BASE, "images-game", "main-game")
COST = os.path.join(BASE, "images-game", "costumes-section")
OUT_MAIN = os.path.join(MAIN, "videos-composites")
OUT_COST = os.path.join(COST, "videos-composites")
TMP_MAIN = os.path.join(MAIN, "_tmp_frames")
TMP_COST = os.path.join(COST, "_tmp_frames")

SW, SH = 1920, 1080


def frames_to_mp4(frame_dir, output, fps=30):
    pattern = os.path.join(frame_dir, "frm%05d.jpg")
    cmd = [
        FFMPEG, "-y",
        "-framerate", str(fps),
        "-i", pattern,
        "-c:v", "libx264", "-crf", "18",
        "-pix_fmt", "yuv420p",
        output
    ]
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
    return r.returncode == 0


def generate_start_menu_composites():
    print("=== START MENU COMPOSITES ===")

    for label, bg_dir in [("sun", "sun/background"), ("night", "night/background")]:
        print("  " + label + " menu...")
        out_dir = os.path.join(TMP_MAIN, label + "_menu")
        os.makedirs(out_dir, exist_ok=True)

        bg_files = sorted(os.listdir(os.path.join(MAIN, bg_dir)))
        sp_files = sorted([f for f in os.listdir(os.path.join(MAIN, "spider-man/ps-spidey")) if f.endswith(".png")])

        count = min(len(bg_files), len(sp_files))
        for i in range(count):
            bg = pygame.image.load(os.path.join(MAIN, bg_dir, bg_files[i])).convert()
            sp = pygame.image.load(os.path.join(MAIN, "spider-man/ps-spidey", sp_files[i])).convert_alpha()
            scr.blit(bg, (0, 0))
            scr.blit(sp, (0, 0))
            pygame.image.save(scr, os.path.join(out_dir, "frm{:05d}.jpg".format(i)))
            if i % 20 == 0:
                print("    frame " + str(i) + "/" + str(count))

        output = os.path.join(OUT_MAIN, "start-menu-" + label + ".mp4")
        frames_to_mp4(out_dir, output)
        print("  -> " + output)

    import shutil
    if os.path.exists(os.path.join(TMP_MAIN, "sun_menu")):
        shutil.rmtree(os.path.join(TMP_MAIN, "sun_menu"))
    if os.path.exists(os.path.join(TMP_MAIN, "night_menu")):
        shutil.rmtree(os.path.join(TMP_MAIN, "night_menu"))


def generate_start_action_composite():
    print("=== START ACTION COMPOSITE ===")
    out_dir = os.path.join(TMP_MAIN, "action")
    os.makedirs(out_dir, exist_ok=True)

    bg_files = sorted(os.listdir(os.path.join(MAIN, "sun/background")))
    sp_start_files = sorted([f for f in os.listdir(os.path.join(MAIN, "spider-man/start-spidey")) if f.endswith(".png")])
    sp_effect_files = sorted([f for f in os.listdir(os.path.join(MAIN, "spider-effect")) if f.endswith(".png") and f != "black.png"])

    frame_idx = 0

    print("  Part 1: spider-man start (" + str(len(sp_start_files)) + " frames)")
    for i in range(len(sp_start_files)):
        bg_idx = i % len(bg_files)
        bg = pygame.image.load(os.path.join(MAIN, "sun/background", bg_files[bg_idx])).convert()
        sp = pygame.image.load(os.path.join(MAIN, "spider-man/start-spidey", sp_start_files[i])).convert_alpha()
        scr.blit(bg, (0, 0))
        scr.blit(sp, (0, 0))
        pygame.image.save(scr, os.path.join(out_dir, "frm{:05d}.jpg".format(frame_idx)))
        frame_idx += 1

    print("  Part 2: spider-effect (" + str(len(sp_effect_files)) + " frames)")
    bg_last = pygame.image.load(os.path.join(MAIN, "sun/background", bg_files[-1])).convert()
    for i in range(len(sp_effect_files)):
        scr.blit(bg_last, (0, 0))
        ef = pygame.image.load(os.path.join(MAIN, "spider-effect", sp_effect_files[i])).convert_alpha()
        ew, eh = ef.get_size()
        scale = min(SW / ew, SH / eh)
        if scale < 1:
            ef = pygame.transform.smoothscale(ef, (int(ew * scale), int(eh * scale)))
        ex = (SW - ef.get_width()) // 2
        ey = (SH - ef.get_height()) // 2
        scr.blit(ef, (ex, ey))
        pygame.image.save(scr, os.path.join(out_dir, "frm{:05d}.jpg".format(frame_idx)))
        frame_idx += 1

    output = os.path.join(OUT_MAIN, "start-action.mp4")
    frames_to_mp4(out_dir, output)
    print("  -> " + output + " (" + str(frame_idx) + " frames)")

    import shutil
    if os.path.exists(out_dir):
        shutil.rmtree(out_dir)


if __name__ == "__main__":
    os.makedirs(OUT_MAIN, exist_ok=True)
    os.makedirs(OUT_COST, exist_ok=True)
    generate_start_menu_composites()
    generate_start_action_composite()
    print("\nDone!")
    pygame.quit()
