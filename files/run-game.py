import os
import sys
import pygame

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

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
if "bg" not in costumes._assets:
    costumes.load_fast(screen, sw, sh)
costumes.main_loop(screen, sw, sh)

pygame.quit()
sys.exit()
