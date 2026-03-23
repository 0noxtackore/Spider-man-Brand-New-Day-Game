import pygame
import sys
import os

# Intentar importar PIL para GIFs
try:
    from PIL import Image
    PIL_AVAILABLE = True
    print("PIL cargado correctamente")
except ImportError:
    PIL_AVAILABLE = False
    print("PIL no disponible")

# Intentar importar librerías para videos
try:
    from ffpyplayer.player import MediaPlayer
    VIDEO_AVAILABLE = True
    print("ffpyplayer cargado correctamente")
except ImportError:
    VIDEO_AVAILABLE = False
    print("ffpyplayer no instalado. Instala con: pip install ffpyplayer")

# Inicialización
pygame.init()
pygame.mixer.init()

# Pantalla completa
info = pygame.display.Info()
screen_width, screen_height = info.current_w, info.current_h
screen = pygame.display.set_mode((screen_width, screen_height), pygame.FULLSCREEN)
pygame.display.set_caption("Spider-Man - Brand New Day")

# Icono y Logo
def safe_load_image(path):
    try:
        return pygame.image.load(path).convert_alpha()
    except:
        surf = pygame.Surface((100, 100))
        surf.fill((255, 0, 255))
        return surf

game_icon = safe_load_image("images-game/game-icon/icon.png")
pygame.display.set_icon(game_icon)
logo = safe_load_image("images-game/game-logo/logo.png")

# Variables de estado
current_theme = "sun"
game_started = False
frame_index = 0
frame_delay = 40  # 1000ms = 1 segundo entre frames
last_frame_time = pygame.time.get_ticks()
last_theme_change = pygame.time.get_ticks()  # Para cambio automático
theme_change_interval = 5000  # 5 segundos para ps-sun
clock = pygame.time.Clock()
web_sound = None
web_played = False  # Para controlar que solo se reproduzca una vez
laught_sound = None
laught_played = False  # Para controlar que solo se reproduzca una vez

# Rutas de los 4 GIFs
GIF_PATHS = {
    "ps-sun": "images-game/main-game/sun/ps-sun.gif",
    "start-sun": "images-game/main-game/sun/start-sun.gif",
    "ps-night": "images-game/main-game/night/ps-night.gif",
    "start-night": "images-game/main-game/night/start-night.gif"
}

# Variables para GIFs cargados
gif_frames = {}  # Diccionario: nombre -> lista de frames
gif_indices = {}  # Diccionario: nombre -> índice actual
gif_loaded = {}  # Diccionario: nombre -> bool

# Frame calculado para laught.mp3 (70% del GIF de start-sun/start-night)
LAUGHT_FRAME_CALCULATED = 35  # Se calculará dinámicamente al cargar los GIFs

def load_gif_frames(gif_name, gif_path):
    """Carga todos los frames de un GIF usando PIL"""
    global gif_frames, gif_loaded
    
    if not PIL_AVAILABLE:
        return False
    
    if not os.path.exists(gif_path):
        print(f"GIF no encontrado: {gif_path}")
        return False
    
    try:
        gif = Image.open(gif_path)
        frames = []
        
        # Extraer todos los frames del GIF
        for frame_num in range(gif.n_frames):
            gif.seek(frame_num)
            # Convertir a RGB para Pygame
            frame_rgb = gif.convert('RGB')
            # Convertir a surface de pygame
            frame_data = frame_rgb.tobytes()
            frame_surface = pygame.image.fromstring(frame_data, frame_rgb.size, 'RGB')
            # Escalar a pantalla completa
            frame_scaled = pygame.transform.scale(frame_surface, (screen_width, screen_height))
            frames.append(frame_scaled)
        
        gif_frames[gif_name] = frames
        gif_indices[gif_name] = 0
        gif_loaded[gif_name] = True
        print(f"GIF cargado: {gif_name}")
        return len(frames)
        
    except Exception as e:
        print(f"Error cargando GIF {gif_name}: {e}")
        gif_loaded[gif_name] = False
        return 0

def get_current_gif_name():
    """Obtiene el nombre del GIF actual según el estado del juego"""
    if game_started:
        return "start-sun" if current_theme == "sun" else "start-night"
    else:
        return "ps-sun" if current_theme == "sun" else "ps-night"

def get_gif_frame(gif_name):
    """Obtiene el siguiente frame del GIF especificado"""
    global gif_indices
    
    if gif_name not in gif_loaded or not gif_loaded[gif_name]:
        return None
    
    frames = gif_frames[gif_name]
    idx = gif_indices.get(gif_name, 0)
    
    # Si es start-sun o start-night y llegamos al final, mantener en último frame (no loop)
    if gif_name in ["start-sun", "start-night"] and idx >= len(frames) - 1:
        return frames[-1]  # Mantener en último frame
    
    # Obtener frame actual
    frame = frames[idx]
    
    # Avanzar índice (solo si no estamos en el último frame de start-sun/start-night)
    if gif_name not in ["start-sun", "start-night"] or idx < len(frames) - 1:
        gif_indices[gif_name] = (idx + 1) % len(frames)
    
    return frame

def reset_gif_index(gif_name):
    """Resetea el índice de un GIF específico"""
    gif_indices[gif_name] = 0

def calculate_laught_frame(gif_name):
    """Calcula el frame para laught.mp3 (75% del GIF aproximadamente)"""
    if gif_name not in gif_frames:
        return 35  # Valor por defecto
    
    total_frames = len(gif_frames[gif_name])
    # Reproducir laught en el 75% del GIF (3/4 del camino)
    laught_frame = int(total_frames * 0.75)
    return max(0, min(laught_frame, total_frames - 1))

# Rutas de carpetas
FOLDER_SUN = "images-game/main-game/sun/ps-sun"
FOLDER_NIGHT = "images-game/main-game/night/ps-night"
FOLDER_START_SUN = "images-game/main-game/sun/start-sun"
FOLDER_START_NIGHT = "images-game/main-game/night/start-night"

# Colores y Fuentes
WHITE, BLACK = (255, 255, 255), (0, 0, 0)
SUN_BG, NIGHT_BG = (135, 206, 235), (25, 25, 112)
font = pygame.font.SysFont("arial", 48, bold=True)

def load_single_frame(folder_path, index):
    """Carga UN SOLO frame, no todos. Esto ahorra RAM."""
    # Intentar con formato fotograma0000.png
    frame_file = f"fotograma{index:04d}.png"
    img_path = os.path.join(folder_path, frame_file)
    
    if os.path.exists(img_path):
        try:
            img = pygame.image.load(img_path)
            return pygame.transform.scale(img, (screen_width, screen_height))
        except:
            return None
    
    # Intentar con formato alternativo
    frame_file_alt = f"fotograma{index}.png"
    img_path_alt = os.path.join(folder_path, frame_file_alt)
    
    if os.path.exists(img_path_alt):
        try:
            img = pygame.image.load(img_path_alt)
            return pygame.transform.scale(img, (screen_width, screen_height))
        except:
            return None
    
    return None

def draw_current_frame():
    """Dibuja solo el frame actual usando GIFs o PNGs como fallback."""
    global frame_index
    
    # Obtener el nombre del GIF actual
    gif_name = get_current_gif_name()
    
    # Si tenemos el GIF cargado, usarlo
    if gif_name in gif_loaded and gif_loaded[gif_name]:
        frame = get_gif_frame(gif_name)
        if frame:
            screen.blit(frame, (0, 0))
            return True
    
    # Fallback: usar imágenes PNG de las carpetas antiguas
    if game_started:
        folder = FOLDER_START_SUN if current_theme == "sun" else FOLDER_START_NIGHT
    else:
        folder = FOLDER_SUN if current_theme == "sun" else FOLDER_NIGHT
    
    frame = load_single_frame(folder, frame_index)
    
    if frame:
        screen.blit(frame, (0, 0))
        return True
    else:
        # Si no hay más frames, resetear o mantener último
        if game_started:
            # Mantener en el último frame
            frame_index = max(0, frame_index - 1)
            frame = load_single_frame(folder, frame_index)
            if frame:
                screen.blit(frame, (0, 0))
                return True
        else:
            # Loop para animación inicial
            frame_index = 0
            frame = load_single_frame(folder, frame_index)
            if frame:
                screen.blit(frame, (0, 0))
                return True
        return False

def draw_ui():
    if not game_started:
        # Logo - muy arriba de la pantalla
        log_w = int(screen_width * 0.45)  # 25% del ancho (más pequeño)
        log_h = int(logo.get_height() * (log_w / logo.get_width()))
        scaled_logo = pygame.transform.scale(logo, (log_w, log_h))
        # Posición logo: usar Rect para colocar en el borde superior
        logo_rect = scaled_logo.get_rect()
        logo_rect.centerx = screen_width // 2
        logo_rect.top = 0  # Borde superior exacto
        screen.blit(scaled_logo, logo_rect)
        
        # Texto "PRESS START" mejorado con efecto de sombra y brillo
        current_time = pygame.time.get_ticks()
        if (current_time // 400) % 2 == 0:  # Parpadeo más rápido (400ms)
            # Posición del texto
            text_x = screen_width // 2
            text_y = screen_height - 120    
            # Borde negro grueso
            border_font = pygame.font.SysFont("arial", 32, bold=True)
            for dx, dy in [(-2, -2), (2, -2), (-2, 2), (2, 2), (0, -2), (0, 2), (-2, 0), (2, 0)]:
                border = border_font.render("PRESS START", True, BLACK)
                border_rect = border.get_rect(center=(text_x + dx, text_y + dy))
                screen.blit(border, border_rect)
            
            # Texto principal blanco brillante
            main_text = border_font.render("PRESS START", True, WHITE)
            text_rect = main_text.get_rect(center=(text_x, text_y))
            screen.blit(main_text, text_rect)

def play_video(video_path):
    """Reproduce un video MP4 usando ffpyplayer con audio"""
    if not VIDEO_AVAILABLE:
        print(f"ffpyplayer no disponible, saltando video: {video_path}")
        return
    
    if not os.path.exists(video_path):
        print(f"Video no encontrado: {video_path}")
        return
    
    try:
        print(f"Reproduciendo video con audio: {video_path}")
        player = MediaPlayer(video_path, ffopts={'paused': False, 'an': False, 'vn': False})
        
        while True:
            frame, val = player.get_frame()
            
            if val == 'eof':
                break
            
            if frame is not None:
                img, t = frame
                # Convertir a surface de pygame
                img_data = img.to_bytearray()[0]
                img_size = img.get_size()
                frame_surface = pygame.image.frombuffer(img_data, img_size, "RGB")
                # Escalar a pantalla completa
                frame_scaled = pygame.transform.scale(frame_surface, (screen_width, screen_height))
                screen.blit(frame_scaled, (0, 0))
                pygame.display.flip()
            
            # Manejar eventos
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    player.close_player()
                    return False
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE or event.key == pygame.K_SPACE:
                        player.close_player()
                        return True
            
            # Controlar velocidad
            pygame.time.wait(30)
        
        player.close_player()
        print(f"Video terminado: {video_path}")
        return True
        
    except Exception as e:
        print(f"Error reproduciendo video {video_path}: {e}")
        import traceback
        traceback.print_exc()
        return True

def start_music():
    """Inicia la música del juego después de los videos"""
    global web_sound, laught_sound
    try:
        # Música principal
        pygame.mixer.music.load("soundtrack-game/main-theme.mp3")
        pygame.mixer.music.set_volume(0.7)
        pygame.mixer.music.play(-1)
        
        # Sonido ambiental de ciudad en bucle
        city_sound = pygame.mixer.Sound("sound-game/city.mp3")
        city_sound.set_volume(0.5)
        city_sound.play(-1)  # En bucle infinito
        
        # Sonido de web (cargado pero no reproducido aún)
        web_sound = pygame.mixer.Sound("sound-game/web.mp3")
        web_sound.set_volume(0.6)
        
        # Sonido de laught (cargado pero no reproducido aún)
        laught_sound = pygame.mixer.Sound("sound-game/laught.mp3")
        laught_sound.set_volume(0.6)
    except:
        pass

# Cargar los 4 GIFs ANTES de los videos (así están listos cuando terminen)
if PIL_AVAILABLE:
    for gif_name, gif_path in GIF_PATHS.items():
        load_gif_frames(gif_name, gif_path)
    
    # Calcular frame para laught.mp3 basado en el GIF de start-sun
    if "start-sun" in gif_frames:
        LAUGHT_FRAME_CALCULATED = calculate_laught_frame("start-sun")
    elif "start-night" in gif_frames:
        LAUGHT_FRAME_CALCULATED = calculate_laught_frame("start-night")

# Reproducir videos introductorios antes del juego
if VIDEO_AVAILABLE:
    # Pantalla negra entre videos
    screen.fill((0, 0, 0))
    pygame.display.flip()
    
    # Reproducir PS4 intro
    play_video("game-intro/ps4-intro.mp4")
    
    # Pequeña pausa entre videos
    pygame.time.wait(500)
    
    # Reproducir Marvel intro
    play_video("game-intro/marvel-intro.mp4")
    
    # Pausa final antes del juego
    pygame.time.wait(500)
else:
    print("Saltando videos introductorios (ffpyplayer no instalado)")

# Iniciar música DESPUÉS de los videos (los GIFs ya están cargados y listos)
start_music()

# Bucle Principal
running = True

while running:
    current_time = pygame.time.get_ticks()
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False
            if event.key == pygame.K_TAB and not game_started:
                current_theme = "night" if current_theme == "sun" else "sun"
                frame_index = 0
                web_played = False
                laught_played = False
                # Resetear índices de GIFs
                reset_gif_index("ps-sun")
                reset_gif_index("ps-night")
                reset_gif_index("start-sun")
                reset_gif_index("start-night")
                last_frame_time = pygame.time.get_ticks()
                last_theme_change = pygame.time.get_ticks()
            if event.key == pygame.K_RETURN and not game_started:
                game_started = True
                frame_index = 0
                # Resetear índices de GIFs al iniciar el juego
                reset_gif_index("ps-sun")
                reset_gif_index("ps-night")
                reset_gif_index("start-sun")
                reset_gif_index("start-night")
                last_frame_time = current_time

    # Cambio automático de tema cada 10 segundos
    if not game_started and current_time - last_theme_change > theme_change_interval:
        current_theme = "night" if current_theme == "sun" else "sun"
        frame_index = 0
        web_played = False
        laught_played = False
        # Resetear índices de GIFs
        reset_gif_index("ps-sun")
        reset_gif_index("ps-night")
        reset_gif_index("start-sun")
        reset_gif_index("start-night")
        last_theme_change = current_time

    # Dibujar
    screen.fill(SUN_BG if current_theme == "sun" else NIGHT_BG)
    
    draw_current_frame()
    
    draw_ui()
    
    pygame.display.flip()
    
    # Esperar antes del siguiente frame (controla velocidad de GIFs)
    pygame.time.wait(frame_delay)
    
    # Actualizar frame para sonidos
    frame_index += 1
    
    # Reproducir web.mp3 a 1 segundo (frame 1) solo en start-sun y start-night
    if frame_index == 1 and web_sound and not web_played and game_started:
        web_sound.play()
        web_played = True
    
    # Reproducir laught.mp3 a 0.5 segundos (frame 10) solo en start-sun y start-night
    if frame_index == 30 and laught_sound and not laught_played and game_started:
        laught_sound.play()
        laught_played = True

pygame.quit()
sys.exit()