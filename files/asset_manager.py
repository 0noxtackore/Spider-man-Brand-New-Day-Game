import pygame
import os
import time
from ffpyplayer.player import MediaPlayer

ORIG_W, ORIG_H = 1920, 1080
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
VIDEOS_MAIN = os.path.join(BASE_DIR, "images-game", "main-game", "videos-composites")
VIDEOS_COST = os.path.join(BASE_DIR, "images-game", "costumes-section", "videos-composites")

_player = None
_last_frame = None
_loop = False
_eof = False


def open_video(path, loop=True):
    global _player, _last_frame, _loop, _eof
    close_video()
    _player = MediaPlayer(path)
    _loop = loop
    _eof = False
    _last_frame = None
    for _ in range(40):
        frame, val = _player.get_frame()
        if frame:
            _last_frame = _make_surface(frame)
            break
        time.sleep(0.025)
    _player.seek(0, relative=False)
    time.sleep(0.05)
    for _ in range(10):
        frame, val = _player.get_frame()
        if frame:
            _last_frame = _make_surface(frame)
            break
        time.sleep(0.025)


def _make_surface(frame):
    img, pts = frame
    data = img.to_bytearray()[0]
    w, h = img.get_size()
    return pygame.image.frombuffer(data, (w, h), "RGB")


def get_frame(w, h):
    global _last_frame, _eof
    if _player is None:
        return None
    if _eof and not _loop:
        return _last_frame
    frame, val = _player.get_frame()
    if val == "eof":
        _eof = True
        if _loop:
            _player.seek(0, relative=False)
            _eof = False
            frame, val = _player.get_frame()
        else:
            return _last_frame
    if frame is None:
        return _last_frame
    surf = _make_surface(frame)
    if surf.get_size() != (w, h):
        surf = pygame.transform.scale(surf, (w, h))
    _last_frame = surf
    return surf


def seek(pos=0):
    global _eof
    if _player:
        _player.seek(pos, relative=False)
        _eof = False


def is_eof():
    return _eof


def close_video():
    global _player, _last_frame, _eof
    if _player:
        _player.close_player()
        _player = None
    _last_frame = None
    _eof = False


def open_menu_sun(w, h):
    open_video(os.path.join(VIDEOS_MAIN, "start-menu-sun.mp4"), loop=True)


def open_menu_night(w, h):
    open_video(os.path.join(VIDEOS_MAIN, "start-menu-night.mp4"), loop=True)


def open_action(w, h):
    open_video(os.path.join(VIDEOS_MAIN, "start-action.mp4"), loop=False)



