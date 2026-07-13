import os
import sys
import tempfile
import unittest

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

ROOT_DIR = os.path.dirname(os.path.dirname(__file__))
FILES_DIR = os.path.join(ROOT_DIR, "files")
sys.path.insert(0, FILES_DIR)

import pygame
import costumes


class CostumesPathResolutionTests(unittest.TestCase):
    def setUp(self):
        pygame.init()
        pygame.display.set_mode((320, 240))

    def tearDown(self):
        pygame.quit()

    def test_load_fast_uses_project_assets_when_cwd_changes(self):
        costumes._assets.clear()
        old_cwd = os.getcwd()
        try:
            os.chdir(tempfile.gettempdir())
            costumes.load_fast(None, 320, 240)
        finally:
            os.chdir(old_cwd)

        bg = costumes._assets["bg"]
        suit = costumes._assets["displays"][1]["surf"]

        self.assertTrue(self._has_visible_pixels(bg))
        self.assertTrue(self._has_visible_pixels(suit))

    def _has_visible_pixels(self, surface):
        for y in range(surface.get_height()):
            for x in range(surface.get_width()):
                r, g, b, a = surface.get_at((x, y))
                if a > 0:
                    return True
        return False


if __name__ == "__main__":
    unittest.main()
