import os
import sys
import pygame

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT_DIR)
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    import protect_assets
    protect_assets.protect_all()
except Exception:
    pass

pygame.init()
pygame.mixer.init()

info = pygame.display.Info()
sw, sh = info.current_w, info.current_h
screen = pygame.display.set_mode((sw, sh), pygame.FULLSCREEN | pygame.SCALED)
pygame.display.set_caption("Spider-Man - Brand New Day")

import intro
import start
import costumes

intro.play_intro()
saved_frame = start.main_loop(screen, sw, sh)
if saved_frame:
    screen.blit(saved_frame, (0, 0))
    pygame.display.flip()
costumes.main_loop(screen, sw, sh)

pygame.quit()
sys.exit()
