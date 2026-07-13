import pygame
import os
import sys
import subprocess
import imageio_ffmpeg
from PIL import Image

pygame.init()
scr = pygame.display.set_mode((1920, 1080))

FFMPEG = imageio_ffmpeg.get_ffmpeg_exe()
BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
COST = os.path.join(BASE, "images-game", "costumes-section")
OUT_COST = os.path.join(COST, "videos-composites")
TMP_COST = os.path.join(COST, "_tmp_frames")

SW, SH = 1920, 1080


def frames_to_mp4(frame_dir, output, fps=24):
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


def gif_frames_to_surfaces(gif_path):
    gif = Image.open(gif_path)
    n_frames = getattr(gif, "n_frames", 1)
    surfaces = []
    for i in range(n_frames):
        gif.seek(i)
        frame = gif.convert("RGBA")
        data = frame.tobytes()
        w, h = frame.size
        surf = pygame.image.frombuffer(data, (w, h), "RGBA")
        surfaces.append(surf)
    return surfaces


def pil_to_surface(img):
    data = img.tobytes()
    w, h = img.size
    return pygame.image.frombuffer(data, (w, h), "RGBA")


def generate_costume_composites():
    print("=== COSTUME COMPOSITES ===")

    bg_path = os.path.join(COST, "backgroung.png")
    bg_pil = Image.open(bg_path).convert("RGBA")
    bg_surf = pil_to_surface(bg_pil)

    shadow_path = os.path.join(COST, "shadow.gif")
    print("Loading shadow GIF frames...")
    shadow_surfs = gif_frames_to_surfaces(shadow_path)
    print("  " + str(len(shadow_surfs)) + " shadow frames, size=" + str(shadow_surfs[0].get_size()))

    for suit_num in range(1, 19):
        pose_path = os.path.join(COST, "suit-pose", "{}.gif".format(suit_num))
        print("[{}/18] costume-{}.mp4".format(suit_num, suit_num))

        pose_surfs = gif_frames_to_surfaces(pose_path)
        print("  pose frames: " + str(len(pose_surfs)))

        out_dir = os.path.join(TMP_COST, "costume_{}".format(suit_num))
        os.makedirs(out_dir, exist_ok=True)

        n_frames = max(len(shadow_surfs), len(pose_surfs))
        for i in range(n_frames):
            scr.fill((255, 255, 255))
            scr.blit(bg_surf, (0, 0))

            shadow_frame = shadow_surfs[i % len(shadow_surfs)]
            shadow_copy = pygame.transform.scale(shadow_frame, (SW, SH))
            white_shadow = pygame.Surface((SW, SH))
            white_shadow.fill((255, 255, 255))
            white_shadow.blit(shadow_copy, (0, 0))
            scr.blit(white_shadow, (0, 0), special_flags=pygame.BLEND_RGB_MULT)

            pose_frame = pose_surfs[i % len(pose_surfs)]
            pose_copy = pygame.transform.scale(pose_frame, (SW, SH))
            scr.blit(pose_copy, (0, 0))

            pygame.image.save(scr, os.path.join(out_dir, "frm{:05d}.jpg".format(i)))

        output = os.path.join(OUT_COST, "costume-{}.mp4".format(suit_num))
        frames_to_mp4(out_dir, output)
        print("  -> " + output)

        import shutil
        if os.path.exists(out_dir):
            shutil.rmtree(out_dir)

    print("\nDone!")


if __name__ == "__main__":
    os.makedirs(OUT_COST, exist_ok=True)
    generate_costume_composites()
    pygame.quit()
