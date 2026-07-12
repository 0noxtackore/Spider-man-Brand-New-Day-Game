import pygame
import os
import sys
import json
import threading

ORIG_W, ORIG_H = 1920, 1080
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BASE = os.path.join(BASE_DIR, "images-game", "main-game")

_frame_cache = {}


def preload_fase_menu_async(w, h):
    thread = threading.Thread(target=preload_fase_menu, args=(w, h), daemon=True)
    thread.start()
    return thread

def preload_fase_accion_async(w, h):
    thread = threading.Thread(target=preload_fase_accion, args=(w, h), daemon=True)
    thread.start()
    return thread

def get_cached_frame(key):
    return _frame_cache.get(key, None)

def load_one(folder, ext, idx, w, h):
    key = (folder, ext, idx, w, h)
    if key in _frame_cache:
        return _frame_cache[key]
    path = os.path.join(BASE, folder, "frm{:04d}.{}".format(idx, ext))
    try:
        surf = pygame.image.load(path)
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
        path = os.path.join(BASE, folder, "frm{:04d}.{}".format(i, ext))
        try:
            surf = pygame.image.load(path)
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
        surf = pygame.image.load(path).convert_alpha()
        if surf.get_width() != w or surf.get_height() != h:
            surf = pygame.transform.scale(surf, (w, h))
        _frame_cache[key] = surf
    except:
        _frame_cache[key] = pygame.Surface((w, h))
    return _frame_cache[key]

def preload_fase_menu(w, h):
    print("[Preload] Cargando interfaz de menu en segundo plano...")
    load_seq("sun/background", "jpg", 80, w, h)
    load_seq("night/background", "jpg", 80, w, h)
    load_seq("spider-man/ps-spidey", "png", 80, w, h)
    load_seq("shadow/spider-man/wait", "png", 80, w, h)
    load_static("shadow/wait/shadow.png", w, h)
    load_light_blur(w, h)
    print("[Preload] Menu listo!")

def preload_fase_accion(w, h):
    print("[Preload] Cargando recursos de accion del juego...")
    load_seq("spider-man/start-spidey", "png", 80, w, h)
    load_seq("shadow/spider-man/start", "png", 80, w, h)
    load_seq("spider-effect", "png", 40, w, h)
    load_static("shadow/start/shadow.png", w, h)
    print("[Preload] Accion lista!")

def preload_costumes(screen, w, h):
    try:
        import costumes
        costumes.load_fast(screen, w, h)
    except ImportError:
        print("[Error] No se pudo encontrar el modulo 'costumes'")

def preload_costumes_async(screen, w, h):
    thread = threading.Thread(target=preload_costumes, args=(screen, w, h), daemon=True)
    thread.start()
    return thread
