import pygame
import os
import sys
import threading

ORIG_W, ORIG_H = 1920, 1080
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BASE = os.path.join(BASE_DIR, "images-game", "main-game")

# Caché global en memoria RAM compartido para todos los archivos del juego
_frame_cache = {}


def preload_fase_menu_async(w, h):
    """Carga el menú en segundo plano sin bloquear el bucle principal."""
    thread = threading.Thread(target=preload_fase_menu, args=(w, h), daemon=True)
    thread.start()
    return thread


def preload_fase_accion_async(w, h):
    """Carga los recursos de acción en segundo plano sin bloquear el juego."""
    thread = threading.Thread(target=preload_fase_accion, args=(w, h), daemon=True)
    thread.start()
    return thread

def get_cached_frame(key):
    """Devuelve un frame si existe, de lo contrario None."""
    return _frame_cache.get(key, None)

def load_one(folder, ext, idx, w, h):
    key = (folder, ext, idx, w, h)
    if key in _frame_cache:
        return _frame_cache[key]
    path = os.path.join(BASE, folder, f"frm{idx:04d}.{ext}")
    try:
        surf = pygame.image.load(path)
        # CRÍTICO: Primero optimizar formato en RAM, luego escalar
        surf = surf.convert_alpha() if ext == "png" else surf.convert()
        if surf.get_width() != w or surf.get_height() != h:
            surf = pygame.transform.scale(surf, (w, h))
        _frame_cache[key] = surf
    except:
        _frame_cache[key] = pygame.Surface((w, h))
    return _frame_cache[key]

def load_seq(folder, ext, count, w, h):
    for i in range(count):
        key = (folder, ext, i, w, h)
        if key in _frame_cache:
            continue
        path = os.path.join(BASE, folder, f"frm{i:04d}.{ext}")
        try:
            surf = pygame.image.load(path)
            # CRÍTICO: .convert() antes de .scale() ahorra muchísima CPU
            surf = surf.convert_alpha() if ext == "png" else surf.convert()
            if surf.get_width() != w or surf.get_height() != h:
                surf = pygame.transform.scale(surf, (w, h))
            _frame_cache[key] = surf
        except:
            _frame_cache[key] = pygame.Surface((w, h))

def load_static(filepath, w, h):
    key = (filepath, w, h)
    if key in _frame_cache:
        return _frame_cache[key]
    path = os.path.join(BASE, filepath)
    try:
        surf = pygame.image.load(path).convert_alpha()
        if surf.get_width() != w or surf.get_height() != h:
            surf = pygame.transform.scale(surf, (w, h))
        _frame_cache[key] = surf
    except:
        _frame_cache[key] = pygame.Surface((w, h))
    return _frame_cache[key]

def load_light_blur(w, h):
    key = ("light/light_blur.png", w, h)
    if key in _frame_cache:
        return _frame_cache[key]
    path = os.path.join(BASE, "light/light.png")
    try:
        # Optimizado para evitar tirones de procesamiento de smoothscale redundantes
        surf = pygame.image.load(path).convert_alpha()
        if surf.get_width() != w or surf.get_height() != h:
            surf = pygame.transform.scale(surf, (w, h))
        _frame_cache[key] = surf
    except:
        _frame_cache[key] = pygame.Surface((w, h))
    return _frame_cache[key]

# --- ESTRATEGIA DE PRECARGA PREDICTIVA (FASES SUAVES) ---

def preload_fase_menu(w, h):
    """
    LLAMAR DESDE: intro.py (mientras corre la intro).
    Carga instantáneamente solo lo necesario para renderizar el menú 'start'.
    """
    print("[Preload] Cargando interfaz de menú en segundo plano...")
    load_seq("sun/background", "jpg", 80, w, h)
    load_seq("night/background", "jpg", 80, w, h)
    load_seq("spider-man/ps-spidey", "png", 80, w, h)
    load_seq("shadow/spider-man/wait", "png", 80, w, h)
    load_static("shadow/wait/shadow.png", w, h)
    load_light_blur(w, h)
    print("[Preload] ¡Menú listo!")

def preload_fase_accion(w, h):
    """
    LLAMAR DESDE: start.py (inmediatamente al pulsar ENTER).
    Carga la animación de ataque y los efectos especiales.
    """
    print("[Preload] Cargando recursos de acción del juego...")
    load_seq("spider-man/start-spidey", "png", 80, w, h)
    load_seq("shadow/spider-man/start", "png", 80, w, h)
    load_seq("spider-effect", "png", 40, w, h)
    load_static("shadow/start/shadow.png", w, h)
    print("[Preload] ¡Acción lista!")

def preload_costumes(screen, w, h):
    """
    LLAMAR DESDE: start.py (mientras el usuario navega o selecciona opciones).
    """
    try:
        import costumes
        costumes.load_fast(screen, w, h)
    except ImportError:
        print("[Error] No se pudo encontrar el módulo 'costumes'")


def preload_costumes_async(screen, w, h):
    """Carga los trajes en segundo plano sin bloquear el menú."""
    thread = threading.Thread(target=preload_costumes, args=(screen, w, h), daemon=True)
    thread.start()
    return thread