import os
import sys
import unittest

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import pygame
import asset_manager


class AssetManagerAsyncPreloadTests(unittest.TestCase):
    def setUp(self):
        pygame.init()
        pygame.display.set_mode((320, 240))

    def tearDown(self):
        pygame.quit()

    def test_preload_fase_menu_async_starts_and_caches_assets(self):
        asset_manager._frame_cache.clear()

        thread = asset_manager.preload_fase_menu_async(320, 240)
        self.assertIsNotNone(thread)
        thread.join(timeout=5)

        cached = asset_manager.get_cached_frame(("sun/background", "jpg", 0, 320, 240))
        self.assertIsNotNone(cached)


if __name__ == "__main__":
    unittest.main()
