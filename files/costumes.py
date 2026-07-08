import pygame
import sys
import os
import threading
import numpy as np
from PIL import Image

ASSETS = "images-game/costumes-section"
ORIG_W, ORIG_H = 1920, 1080

def load_png(path, w, h, do_scale=True):
    try:
        img = pygame.image.load(os.path.join(ASSETS, path)).convert_alpha()
        if do_scale and img.get_size() != (w, h):
            img = pygame.transform.scale(img, (w, h))
        return img
    except:
        surf = pygame.Surface((w, h) if do_scale else (ORIG_W, ORIG_H), pygame.SRCALPHA)
        surf.fill((0, 0, 0, 0))
        return surf

def load_gif_frames(path, w, h, result_dict=None, key=None):
    frames_data = []
    full = os.path.join(ASSETS, path)
    if not os.path.exists(full):
        if result_dict is not None and key is not None:
            result_dict[key] = []
        return frames_data
    try:
        gif = Image.open(full)
        for i in range(gif.n_frames):
            gif.seek(i)
            frame = gif.convert("RGBA")
            raw = frame.tobytes()
            frames_data.append((frame.size, raw))
    except Exception as e:
        print(f"Error loading {path}: {e}")
    if result_dict is not None and key is not None:
        result_dict[key] = frames_data
    return frames_data

def make_multiply_surface(surf):
    out = surf.copy()
    arr = pygame.surfarray.pixels3d(out)
    alpha = pygame.surfarray.pixels_alpha(out)
    mask = alpha == 0
    arr[mask] = [255, 255, 255]
    del arr, alpha
    return out

def crop_content(surf):
    w, h = surf.get_size()
    raw = pygame.image.tostring(surf, "RGBA")
    pil_img = Image.frombytes("RGBA", (w, h), raw)
    bbox = pil_img.getbbox()
    if not bbox:
        return surf, None
    cropped = pil_img.crop(bbox)
    raw2 = cropped.tobytes()
    return pygame.image.fromstring(raw2, cropped.size, "RGBA"), bbox

SUIT_BBOXES = {
    1: (105, 225, 243, 1069),
    2: (174, 227, 305, 1078),
    3: (238, 227, 369, 1078),
    4: (314, 226, 445, 1078),
}

_assets = {}
_assets_loaded = False

def load_fast(screen, w, h):
    global _assets
    sx = w / ORIG_W; sy = h / ORIG_H
    crops = {}
    for i in range(1, 5):
        full = load_png(f"suits/{i}.png", ORIG_W, ORIG_H, do_scale=False)
        cropped, _ = crop_content(full)
        crops[i] = cropped
    keys = {}
    for name in ["left", "right", "x", "z", "p", "a", "esc"]:
        p = os.path.join("images-game/key button", f"{name}.png")
        try: keys[name] = pygame.image.load(p).convert_alpha()
        except: keys[name] = pygame.Surface((40, 40), pygame.SRCALPHA)
    arrows = {i: load_png(f"arrow/{i}.png", w, h) for i in range(1, 5)}
    spidey_path = "images-game/notification-icon/spidey-icon.png"
    try: spidey = pygame.image.load(spidey_path).convert_alpha()
    except: spidey = pygame.Surface((64, 64), pygame.SRCALPHA)
    sfx_dir = "sound-game/costumes"
    def ls(name):
        try: return pygame.mixer.Sound(os.path.join(sfx_dir, f"{name}.mp3"))
        except: return None
    sfx = {"move": ls("move-costume"), "quit": ls("quit-game"), "select": ls("select-costume"), "other": ls("other")}
    bg = load_png("backgroung.png", w, h)
    displays = {}
    for i in range(1, 5):
        bx1, by1, bx2, by2 = SUIT_BBOXES[i]
        ow = bx2 - bx1; oh = by2 - by1
        dw = max(1, int(ow * sx)); dh = max(1, int(oh * sy))
        displays[i] = {"surf": pygame.transform.scale(crops[i], (dw, dh)), "x": int(bx1 * sx), "y": int(by1 * sy), "w": dw, "h": dh}
    cf = pygame.font.SysFont("arial", 16, bold=True)
    ctrl = []
    for label_text, key_name in [("QUIT", "esc"), ("BACK", "a"), ("LEFT", "left"), ("RIGHT", "right"), ("SELECT", "x"), ("MAP", "z"), ("SWING TIME", "p")]:
        ki = keys[key_name]
        kw = ki.get_width(); kh = ki.get_height()
        ks = pygame.transform.smoothscale(ki, (48, int(48 * kh / kw)))
        lb = cf.render(label_text, True, (255, 255, 255))
        ls = cf.render(label_text, True, (0, 0, 0))
        ctrl.append((lb, ls, ks, lb.get_width() + 6 + ks.get_width()))
    tw = sum(d[3] for d in ctrl) + 20 * (len(ctrl) - 1)
    qf = pygame.font.SysFont("arial", 24, bold=True)
    qt = qf.render("ARE YOU SURE YOU WANT TO QUIT?", True, (255, 255, 255))
    of = pygame.font.SysFont("arial", 22, bold=True)
    icon = pygame.transform.smoothscale(spidey, (100, 100))
    _assets = {
        "sx": sx, "sy": sy, "bg": bg,
        "displays": displays, "arrows": arrows,
        "ctrl_data": ctrl, "cx": w - 20 - tw, "cy": h - 20,
        "qf": qf, "qt": qt, "of": of, "icon": icon, "sfx": sfx,
    }
    load_gifs_parallel(screen, w, h)

def load_gifs_parallel(screen, w, h):
    global _assets
    result_dict = {}
    items = [("shadow", "shadow.gif")] + [(f"suit-pose-{i}", f"suit-pose/{i}.gif") for i in range(1, 5)]
    threads = []
    for key, path in items:
        t = threading.Thread(target=load_gif_frames, args=(path, w, h, result_dict, key))
        t.start()
        threads.append(t)
    for t in threads:
        t.join()
    shadow_data = result_dict.get("shadow", [])
    if shadow_data:
        shadow_surfs = []
        for size, raw_bytes in shadow_data:
            surf = pygame.image.fromstring(raw_bytes, size, "RGBA")
            if surf.get_size() != (w, h):
                surf = pygame.transform.scale(surf, (w, h))
            shadow_surfs.append(surf)
        _assets["shadow"] = [make_multiply_surface(f) for f in shadow_surfs]
    else:
        _assets["shadow"] = []
    suit_pose = {}
    for i in range(1, 5):
        data = result_dict.get(f"suit-pose-{i}", [])
        if data:
            frames = []
            for size, raw_bytes in data:
                surf = pygame.image.fromstring(raw_bytes, size, "RGBA")
                if surf.get_size() != (w, h):
                    surf = pygame.transform.scale(surf, (w, h))
                frames.append(surf)
            suit_pose[i] = frames
        else:
            suit_pose[i] = suit_pose.get(i - 1, [])
    _assets["suit_pose"] = suit_pose

def load_assets(screen, w, h):
    global _assets_loaded
    load_fast(screen, w, h)
    _assets_loaded = True

def main_loop(screen, screen_width, screen_height):
    global _assets
    if "bg" not in _assets:
        load_fast(screen, screen_width, screen_height)
    a = _assets

    current_suit = 4
    active_pose_suit = 4
    gif_idx = 0
    gif_timer = 0
    gif_speed = 3
    clock = pygame.time.Clock()
    running = True
    show_quit_modal = False
    modal_choice = 0

    sfx = a["sfx"]
    while running:
        dt = clock.tick(60)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if show_quit_modal:
                    if event.key == pygame.K_LEFT:
                        modal_choice = 0
                    if event.key == pygame.K_RIGHT:
                        modal_choice = 1
                    if event.key == pygame.K_RETURN:
                        if modal_choice == 0:
                            if sfx["other"]: sfx["other"].play()
                            running = False
                        else:
                            if sfx["other"]: sfx["other"].play()
                            show_quit_modal = False
                    if event.key == pygame.K_ESCAPE:
                        if sfx["other"]: sfx["other"].play()
                        show_quit_modal = False
                else:
                    if event.key == pygame.K_ESCAPE:
                        show_quit_modal = True
                        modal_choice = 0
                        if sfx["quit"]: sfx["quit"].play()
                    if event.key == pygame.K_LEFT:
                        current_suit = 4 if current_suit == 1 else current_suit - 1
                        if sfx["move"]: sfx["move"].play()
                    if event.key == pygame.K_RIGHT:
                        current_suit = 1 if current_suit == 4 else current_suit + 1
                        if sfx["move"]: sfx["move"].play()
                    if event.key == pygame.K_x:
                        active_pose_suit = current_suit
                        gif_idx = 0
                        if sfx["select"]: sfx["select"].play()
                    if event.key == pygame.K_RETURN:
                        if sfx["other"]: sfx["other"].play()
                        running = False

        shadow_frames = a.get("shadow", [])
        suit_pose = a.get("suit_pose", {})
        gif_timer += 1
        if gif_timer >= gif_speed:
            gif_timer = 0
            pf = suit_pose.get(active_pose_suit, [])
            total = max(len(shadow_frames), len(pf), 1)
            gif_idx = (gif_idx + 1) % total

        screen.fill((0, 0, 0))
        screen.blit(a["bg"], (0, 0))

        if shadow_frames:
            screen.blit(shadow_frames[gif_idx % len(shadow_frames)], (0, 0), special_flags=pygame.BLEND_RGB_MULT)

        pose_frames = suit_pose.get(active_pose_suit, [])
        if pose_frames:
            screen.blit(pose_frames[gif_idx % len(pose_frames)], (0, 0))

        for i in range(1, 5):
            if i != current_suit:
                d = a["displays"][i]
                screen.blit(d["surf"], (d["x"], d["y"]))

        d = a["displays"][current_suit]
        scale = 1.15
        sw = int(d["w"] * scale)
        sh = int(d["h"] * scale)
        big = pygame.transform.scale(d["surf"], (sw, sh))
        bx = d["x"] - (sw - d["w"]) // 2
        by = d["y"] - (sh - d["h"]) // 2
        screen.blit(big, (bx, by))

        screen.blit(a["arrows"][current_suit], (0, 0))

        x = a["cx"]
        for lbl, lbl_shadow, k_scaled, seg_w in a["ctrl_data"]:
            lh = lbl.get_height()
            kh = k_scaled.get_height()
            center_y = a["cy"] - max(lh, kh) // 2
            text_y = center_y - lh // 2
            key_y = center_y - kh // 2
            for dx, dy in [(-1, -1), (1, -1), (-1, 1), (1, 1)]:
                screen.blit(lbl_shadow, (x + dx, text_y + dy))
            screen.blit(lbl, (x, text_y))
            screen.blit(k_scaled, (x + lbl.get_width() + 6, key_y))
            x += seg_w + 20

        if show_quit_modal:
            overlay = pygame.Surface((screen_width, screen_height), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 180))
            screen.blit(overlay, (0, 0))

            modal_w = 500
            modal_h = 280
            mx = (screen_width - modal_w) // 2
            my = (screen_height - modal_h) // 2
            pygame.draw.rect(screen, (20, 20, 40), (mx, my, modal_w, modal_h), border_radius=12)
            pygame.draw.rect(screen, (100, 100, 180), (mx, my, modal_w, modal_h), 3, border_radius=12)

            ix = mx + (modal_w - 100) // 2
            iy = my + 20
            screen.blit(a["icon"], (ix, iy))

            qx = mx + (modal_w - a["qt"].get_width()) // 2
            qy = iy + 100 + 15
            screen.blit(a["qt"], (qx, qy))

            opt_spacing = 120
            opt_center_x = mx + modal_w // 2
            opt_y = qy + 45

            for idx, text in enumerate(["YES", "NO"]):
                color = (255, 50, 50) if idx == modal_choice else (180, 180, 180)
                label = a["of"].render(text, True, color)
                lx = opt_center_x - opt_spacing // 2 + idx * opt_spacing - label.get_width() // 2
                screen.blit(label, (lx, opt_y))
                if idx == modal_choice:
                    underline = pygame.Surface((label.get_width() + 10, 3))
                    underline.fill((255, 50, 50))
                    screen.blit(underline, (lx - 5, opt_y + label.get_height() + 4))

        pygame.display.flip()

if __name__ == "__main__":
    pygame.init()
    pygame.mixer.init()
    info = pygame.display.Info()
    sw, sh = info.current_w, info.current_h
    screen = pygame.display.set_mode((sw, sh), pygame.FULLSCREEN | pygame.SCALED)
    pygame.display.set_caption("Spider-Man - Costumes")
    main_loop(screen, sw, sh)
    pygame.quit()
    sys.exit()
