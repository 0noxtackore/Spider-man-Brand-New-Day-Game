import pygame
import os
import sys
import time
from ffpyplayer.player import MediaPlayer

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
