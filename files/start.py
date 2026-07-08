import pygame
import sys
import os
import asset_manager  # Migrado a tu gestor centralizado optimizado

ORIG_W, ORIG_H = 1920, 1080
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BASE = os.path.join(BASE_DIR, "images-game", "main-game")

SUN_BG, NIGHT_BG = (135, 206, 235), (25, 25, 112)
WHITE, BLACK = (255, 255, 255), (0, 0, 0)

_seq_counts = {
    "sun/background": 80,
    "night/background": 80,
    "spider-man/ps-spidey": 80,
    "spider-man/start-spidey": 80,
    "shadow/spider-man/wait": 80,
    "shadow/spider-man/start": 80,
    "spider-effect": 40,
}

_fallback = None

def _get_seq(folder, ext, idx, w, h):
    global _fallback
    if _fallback is None:
        _fallback = pygame.Surface((w, h))
    key = (folder, ext, idx, w, h)
    
    # Intentamos obtenerlo directo del caché global optimizado
    surf = asset_manager.get_cached_frame(key)
    if surf is not None:
        return surf
        
    # Si por alguna razón no se precargó en la intro, lo cargamos de forma segura y optimizada
    return asset_manager.load_one(folder, ext, idx, w, h)


def _get_static(filepath, w, h):
    global _fallback
    if _fallback is None:
        _fallback = pygame.Surface((w, h))
    key = (filepath, w, h)
    
    # Intentamos obtenerlo del caché global optimizado
    surf = asset_manager.get_cached_frame(key)
    if surf is not None:
        return surf
        
    # Fallback de carga estática optimizada
    return asset_manager.load_static(filepath, w, h)


def _render(screen, frame_idx, w, h, theme, started, sp_active, sp_consumed, sp_idx, character_surface):
    if started:
        bg_seq = "sun/background" if theme == "sun" else "night/background"
        shadow_bg = "shadow/start/shadow.png"
        sm_seq = "spider-man/start-spidey"
        shadow_sm = "shadow/spider-man/start"
    else:
        bg_seq = "sun/background" if theme == "sun" else "night/background"
        shadow_bg = "shadow/wait/shadow.png"
        sm_seq = "spider-man/ps-spidey"
        shadow_sm = "shadow/spider-man/wait"

    bg_ext = "jpg"
    sm_ext = "png"

    screen.blit(_get_seq(bg_seq, bg_ext, frame_idx % _seq_counts[bg_seq], w, h), (0, 0))
    screen.blit(_get_static(shadow_bg, w, h), (0, 0))

    character_surface.fill((0, 0, 0, 0))

    if started:
        sm_idx = min(frame_idx, _seq_counts[sm_seq] - 1)
    else:
        sm_idx = frame_idx % _seq_counts[sm_seq]
    character_surface.blit(_get_seq(sm_seq, sm_ext, sm_idx, w, h), (0, 0))

    screen.blit(character_surface, (0, 0))

    if theme == "night":
        light_surf = _get_static("light/light.png", w, h)
        if light_surf is not None and light_surf.get_size() != (1, 1):
            screen.blit(light_surf, (0, 0))

    if started:
        if not sp_active and not sp_consumed:
            total_sm = _seq_counts[sm_seq]
            if frame_idx >= total_sm - 1:
                sp_active = True
                sp_idx = 0
        if sp_active and not sp_consumed:
            sp_frames = _seq_counts["spider-effect"]
            if sp_idx < sp_frames:
                s = _get_seq("spider-effect", "png", sp_idx, w, h)
                screen.blit(s, (0, 0))
                sp_idx += 1
            else:
                s = _get_seq("spider-effect", "png", sp_frames - 1, w, h)
                screen.blit(s, (0, 0))
                sp_consumed = True

    return sp_active, sp_consumed, sp_idx


def _ui(screen, w, h, theme, logo, blur, font, press, to, key_scaled):
    log_w = int(w * 0.45)
    log_h = int(logo.get_height() * (log_w / logo.get_width()))
    s = pygame.transform.scale(logo, (log_w, log_h))
    r = s.get_rect(centerx=w // 2 + 40, top=40)
    if theme == "night" and blur:
        screen.blit(pygame.transform.scale(blur, (log_w, log_h)), r)
    screen.blit(s, r)
    pw, kw, tw = press.get_width(), 100, to.get_width()
    sx = w // 2 - (pw + kw + tw) // 2
    cy = h - 120
    for dx, dy in [(-2, -2), (2, -2), (-2, 2), (2, 2)]:
        screen.blit(font.render("PRESS ", True, BLACK), (sx + dx, cy - press.get_height() // 2 + dy))
        ks = pygame.Surface((kw, 46))
        ks.fill(BLACK)
        ks.set_alpha(160)
        screen.blit(ks, (sx + pw + dx, cy - 23 + dy))
        screen.blit(font.render(" TO START", True, BLACK), (sx + pw + kw + dx, cy - to.get_height() // 2 + dy))
    screen.blit(press, (sx, cy - press.get_height() // 2))
    screen.blit(key_scaled, (sx + pw, cy - 23))
    screen.blit(to, (sx + pw + kw, cy - to.get_height() // 2))


def _img(path):
    full_path = os.path.join(BASE_DIR, path)
    try:
        return pygame.image.load(full_path).convert_alpha()
    except:
        return pygame.Surface((1, 1))


def main_loop(s, sw, sh):
    screen = s
    w, h = sw, sh

    logo = _img("images-game/game-logo/logo.png")
    blur = _img("images-game/game-logo/blur.png")
    enter_key = _img("images-game/key button/enter.png")
    preload_thread = asset_manager.preload_fase_menu_async(w, h)
    try:
        pygame.display.set_icon(_img("images-game/game-icon/icon.png"))
    except:
        pass
    font = pygame.font.SysFont("arial", 24, bold=True)
    press_surf = font.render("PRESS ", True, WHITE)
    to_surf = font.render(" TO START", True, WHITE)
    key_scaled = pygame.transform.scale(enter_key, (100, 46))

    try:
        pygame.mixer.music.load(os.path.join(BASE_DIR, "soundtrack-game", "main-theme.mp3"))
        pygame.mixer.music.set_volume(0.7)
        pygame.mixer.music.play(-1)
        c = pygame.mixer.Sound(os.path.join(BASE_DIR, "sound-game", "city.mp3"))
        c.set_volume(0.5)
        c.play(-1)
        web_snd = pygame.mixer.Sound(os.path.join(BASE_DIR, "sound-game", "web.mp3"))
        web_snd.set_volume(0.6)
        laugh_snd = pygame.mixer.Sound(os.path.join(BASE_DIR, "sound-game", "laught.mp3"))
        laugh_snd.set_volume(0.6)
    except:
        web_snd = laugh_snd = None

    # ESTRATEGIA PREDICTIVA: Precargamos costumes de forma fluida mientras el jugador está inactivo en el menú
    try:
        asset_manager.preload_costumes_async(screen, w, h)
    except:
        pass

    character_surface = pygame.Surface((w, h), pygame.SRCALPHA)

    theme = "sun"
    started = False
    sp_active = False
    sp_consumed = False
    sp_idx = 0
    frame_idx = 0
    last_theme_swap = pygame.time.get_ticks()
    web_played = False
    laugh_played = False
    clock = pygame.time.Clock()
    running = True

    while running:
        now = pygame.time.get_ticks()
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                return None
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_ESCAPE:
                    return None
                if e.key == pygame.K_RETURN and not started:
                    # PRECARGA AL INSTANTE: Cargamos la fase de acción optimizada en menos de 0.2 segundos
                    asset_manager.preload_fase_accion_async(w, h)
                    
                    started = True
                    frame_idx = 0
                    sp_active = False
                    sp_consumed = False
                    sp_idx = 0
                if e.key == pygame.K_TAB and not started:
                    theme = "night" if theme == "sun" else "sun"
                    frame_idx = 0
                    last_theme_swap = now

        if not started and now - last_theme_swap > 5000:
            theme = "night" if theme == "sun" else "sun"
            frame_idx = 0
            last_theme_swap = now

        screen.fill(NIGHT_BG if theme == "night" else SUN_BG)
        sp_active, sp_consumed, sp_idx = _render(
            screen, frame_idx, w, h, theme, started,
            sp_active, sp_consumed, sp_idx, character_surface
        )

        if not started:
            _ui(screen, w, h, theme, logo, blur, font, press_surf, to_surf, key_scaled)

        pygame.display.flip()
        clock.tick(30)
        frame_idx += 1

        if started:
            if frame_idx == 1 and web_snd and not web_played:
                web_snd.play()
                web_played = True
            if frame_idx == 30 and laugh_snd and not laugh_played:
                laugh_snd.play()
                laugh_played = True
            if sp_consumed:
                saved = screen.copy()
                return saved

    return None


if __name__ == "__main__":
    pygame.init()
    pygame.mixer.init()
    info = pygame.display.Info()
    scr = pygame.display.set_mode((info.current_w, info.current_h), pygame.FULLSCREEN | pygame.SCALED)
    pygame.display.set_caption("Spider-Man - Brand New Day")
    r = main_loop(scr, info.current_w, info.current_h)
    pygame.quit()
    sys.exit()