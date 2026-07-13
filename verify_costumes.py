import os
import sys
import tempfile
os.environ['SDL_VIDEODRIVER'] = 'dummy'
import pygame
sys.path.insert(0, os.path.join(os.getcwd(), 'files'))
import costumes

pygame.init()
pygame.display.set_mode((320, 240))
os.chdir(tempfile.gettempdir())
costumes._assets.clear()
costumes.load_fast(None, 320, 240)
print('bg', costumes._assets['bg'].get_size())
print('displays', len(costumes._assets['displays']))
pygame.quit()
