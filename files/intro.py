import pygame
import os
import sys
import time
from ffpyplayer.player import MediaPlayer
import asset_manager  # Usamos nuestro nuevo gestor centralizado

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
VIDEO = os.path.join(BASE_DIR, "intro-video", "intro-0noxtackore.mp4")

def play_intro():
    screen = pygame.display.get_surface()
    if screen is None:
        pygame.init()
        pygame.mixer.init()
        info = pygame.display.Info()
        sw, sh = info.current_w, info.current_h
        screen = pygame.display.set_mode((sw, sh), pygame.FULLSCREEN | pygame.SCALED)
        pygame.display.set_caption("Spider-Man - Brand New Day")
    else:
        sw, sh = screen.get_size()

    # --- CONFIGURACIÓN DE LA CARGA PREDICTIVA EN SEGUNDO PLANO ---
    # En vez de cargar todo junto, creamos una lista de tareas (carpetas) para el menú
    carpetas_menu = [
        ("sun/background", "jpg", 80),
        ("night/background", "jpg", 80),
        ("spider-man/ps-spidey", "png", 80),
        ("shadow/spider-man/wait", "png", 80)
    ]
    
    # Generamos una cola con el índice exacto de cada frame individual que necesitamos cargar
    cola_de_carga = []
    for folder, ext, count in carpetas_menu:
        for idx in range(count):
            cola_de_carga.append((folder, ext, idx))
            
    # Agregamos la sombra estática al final de la cola
    sombra_estatica_cargada = False

    player = MediaPlayer(VIDEO)
    player.set_pause(False)
    time.sleep(0.1)

    clock = pygame.time.Clock()

    while True:
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                player.close_player()
                return None
            if e.type == pygame.KEYDOWN and e.key == pygame.K_ESCAPE:
                player.close_player()
                return None

        # ─── TRUCO DE MAGIA: CARGA PREDICTIVA PASO A PASO ───
        # En cada vuelta del bucle del video, cargamos exactamente 2 frames en la RAM.
        # Al procesar solo 2 frames por ciclo, la CPU ni lo nota y el video no da tirones.
        for _ in range(2):
            if cola_de_carga:
                folder, ext, idx = cola_de_carga.pop(0)
                asset_manager.load_one(folder, ext, idx, sw, sh)
            elif not sombra_estatica_cargada:
                asset_manager.load_static("shadow/wait/shadow.png", sw, sh)
                asset_manager.load_light_blur(sw, sh)
                sombra_estatica_cargada = True

        # Renderizado del frame del video
        frame, val = player.get_frame()
        if val == 'eof':
            break
        if frame is not None:
            img, pts = frame
            data = img.to_bytearray()[0]
            w, h = img.get_size()
            surf = pygame.image.frombuffer(data, (w, h), "RGB")
            surf = pygame.transform.scale(surf, (sw, sh))
            screen.blit(surf, (0, 0))
            pygame.display.flip()

        clock.tick(30)

    # Si el video termina antes de completar la precarga, dejamos que el menú siga
    # cargando en segundo plano para que la transición no se quede congelada.
    if cola_de_carga or not sombra_estatica_cargada:
        print("[Intro] Continuando la precarga del menú en segundo plano...")
        asset_manager.preload_fase_menu_async(sw, sh)

    player.close_player()
    return screen

if __name__ == "__main__":
    pygame.init()
    info = pygame.display.Info()
    scr = pygame.display.set_mode((info.current_w, info.current_h), pygame.FULLSCREEN | pygame.SCALED)
    pygame.display.set_caption("Spider-Man - Brand New Day")
    play_intro()
    pygame.quit()
    sys.exit()