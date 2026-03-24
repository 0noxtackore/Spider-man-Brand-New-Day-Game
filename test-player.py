import pygame
import sys
import os
from PIL import Image

# Inicialización
pygame.init()
pygame.mixer.init()

# Pantalla en ventana (no fullscreen)
screen_width, screen_height = 1280, 720
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Spider-Man - Test Player")

# Colores
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
DARK_RED = (139, 0, 0)  # Rojo oscuro para barra de vida

# Rutas de animaciones
ANIMATION_PATHS = {
    "idle-right": "images-game/characters/Spider-man/idle-right.gif",
    "idle-left": "images-game/characters/Spider-man/idle-left.gif",
    "run-right": "images-game/characters/Spider-man/run-right.gif",
    "run-left": "images-game/characters/Spider-man/run-left.gif",
    "entry-right": "images-game/characters/Spider-man/entry-right.png",
    "entry-left": "images-game/characters/Spider-man/entry-left.png"
}

HEALTH_ICON_PATH = "images-game/health-character/Spider-man.png"

# Cargar GIF con PIL
def load_gif_frames(path, scale_factor=1.0):
    """Carga frames de un GIF usando PIL con transparencia"""
    frames = []
    if not os.path.exists(path):
        print(f"No encontrado: {path}")
        return frames
    
    try:
        gif = Image.open(path)
        for frame_num in range(gif.n_frames):
            gif.seek(frame_num)
            # Convertir a RGBA para preservar transparencia
            frame_rgba = gif.convert('RGBA')
            frame_data = frame_rgba.tobytes()
            frame_surface = pygame.image.fromstring(frame_data, frame_rgba.size, 'RGBA')
            # Escalar con suavizado (anti-aliasing)
            new_w = int(frame_surface.get_width() * scale_factor)
            new_h = int(frame_surface.get_height() * scale_factor)
            frame_scaled = pygame.transform.smoothscale(frame_surface, (new_w, new_h))
            frames.append(frame_scaled)
        print(f"Cargado: {path} ({len(frames)} frames)")
    except Exception as e:
        print(f"Error cargando {path}: {e}")
    
    return frames

def load_single_image(path, scale_factor=1.0):
    """Carga una imagen PNG/JPG"""
    if not os.path.exists(path):
        print(f"No encontrado: {path}")
        return None
    
    try:
        img = pygame.image.load(path).convert_alpha()
        new_w = int(img.get_width() * scale_factor)
        new_h = int(img.get_height() * scale_factor)
        return pygame.transform.smoothscale(img, (new_w, new_h))
    except Exception as e:
        print(f"Error cargando {path}: {e}")
        return None

# Escala del personaje (más pequeño para ventana)
PLAYER_SCALE = 0.3
RUN_SCALE = 0.25  # Escala más pequeña para run-left y run-right

# Cargar todas las animaciones
animations = {
    "idle-right": load_gif_frames(ANIMATION_PATHS["idle-right"], PLAYER_SCALE),
    "idle-left": load_gif_frames(ANIMATION_PATHS["idle-left"], PLAYER_SCALE),
    "run-right": load_gif_frames(ANIMATION_PATHS["run-right"], RUN_SCALE),  # Más pequeño
    "run-left": load_gif_frames(ANIMATION_PATHS["run-left"], RUN_SCALE),   # Más pequeño
    "entry-right": [load_single_image(ANIMATION_PATHS["entry-right"], PLAYER_SCALE)],
    "entry-left": [load_single_image(ANIMATION_PATHS["entry-left"], PLAYER_SCALE)]
}

# Cargar icono de vida (más grande, 0.25 en lugar de 0.15)
health_icon = load_single_image(HEALTH_ICON_PATH, 0.29)

class Player:
    def __init__(self):
        self.x = screen_width // 2
        self.y = screen_height - 150
        self.width = 60
        self.height = 90
        self.vel_x = 0
        self.vel_y = 0
        self.base_speed = 3    # Velocidad base (lenta)
        self.max_speed = 17    # Velocidad maxima (con tecla)
        self.current_speed = 3   # Velocidad actual (interpolada)
        self.acceleration = 0.8  # Suavidad de aceleracion
        self.gravity = 0.6
        self.jump_power = -30
        self.on_ground = False
        
        # Animación
        self.current_animation = "idle-right"
        self.frame_index = 0
        self.frame_delay = 4
        self.frame_counter = 0
        self.facing_right = True
        
        # Volteo (transición)
        self.is_turning = False
        self.turn_timer = 0
        self.turn_duration = 8  # frames para entry
        
        # Vida
        self.max_health = 100
        self.health = 100
        
        # Suelo (posición Y del suelo invisible)
        self.ground_y = screen_height - 40
    
    def update(self, keys):
        # Movimiento horizontal
        moving_left = keys[pygame.K_LEFT] or keys[pygame.K_a]
        moving_right = keys[pygame.K_RIGHT] or keys[pygame.K_d]
        
        # Prioridad: si ambas teclas, mantener dirección actual (quieto)
        if moving_right and moving_left:
            self.vel_x = 0
            # Mantener animación idle en la dirección actual
            if not self.is_turning:
                self.current_animation = "idle-right" if self.facing_right else "idle-left"
            return  # Salir, no procesar más
        
        # Manejar animación de volteo
        if self.is_turning:
            self.vel_x = 0
            self.turn_timer -= 1
            if self.turn_timer <= 0:
                self.is_turning = False
                # Al terminar volteo, determinar siguiente animación
                if self.facing_right:
                    self.current_animation = "run-right" if moving_right else "idle-right"
                else:
                    self.current_animation = "run-left" if moving_left else "idle-left"
            return  # No procesar más durante volteo
        
        # Movimiento normal (no está volteando)
        if moving_right:
            # Acelerar hacia velocidad maxima
            self.current_speed += (self.max_speed - self.current_speed) * self.acceleration
            self.vel_x = self.current_speed
            if not self.facing_right:
                # Volteando de izquierda a derecha
                self.is_turning = True
                self.turn_timer = self.turn_duration
                self.current_animation = "entry-right"
                self.facing_right = True
            else:
                self.current_animation = "run-right"
        elif moving_left:
            # Acelerar hacia velocidad maxima
            self.current_speed += (self.max_speed - self.current_speed) * self.acceleration
            self.vel_x = -self.current_speed
            if self.facing_right:
                # Volteando de derecha a izquierda
                self.is_turning = True
                self.turn_timer = self.turn_duration
                self.current_animation = "entry-left"
                self.facing_right = False
            else:
                self.current_animation = "run-left"
        else:
            # No se mueve - desacelerar hacia velocidad base
            self.current_speed += (self.base_speed - self.current_speed) * self.acceleration
            self.vel_x = 0
            self.current_animation = "idle-right" if self.facing_right else "idle-left"
        
        # Salto
        if (keys[pygame.K_SPACE] or keys[pygame.K_UP] or keys[pygame.K_w]) and self.on_ground:
            self.vel_y = self.jump_power
            self.on_ground = False
        
        # Aplicar gravedad
        self.vel_y += self.gravity
        
        # Actualizar posición
        self.x += self.vel_x
        self.y += self.vel_y
        
        # Colisión con suelo invisible
        if self.y + self.height > self.ground_y:
            self.y = self.ground_y - self.height
            self.vel_y = 0
            self.on_ground = True
        
        # Limitar a pantalla
        if self.x < 0:
            self.x = 0
        if self.x + self.width > screen_width:
            self.x = screen_width - self.width
        
        # Actualizar animación
        self.update_animation()
    
    def update_animation(self):
        anim_frames = animations.get(self.current_animation, [])
        if not anim_frames:
            return
        
        self.frame_counter += 1
        if self.frame_counter >= self.frame_delay:
            self.frame_counter = 0
            self.frame_index = (self.frame_index + 1) % len(anim_frames)
    
    def draw(self, surface):
        # Obtener frame actual
        anim_frames = animations.get(self.current_animation, [])
        if anim_frames and len(anim_frames) > 0:
            frame = anim_frames[self.frame_index % len(anim_frames)]
            # Centrar frame en la posición del jugador
            frame_rect = frame.get_rect()
            frame_rect.centerx = int(self.x + self.width // 2)
            frame_rect.bottom = int(self.y + self.height)
            surface.blit(frame, frame_rect)
        
        # Debug: dibujar hitbox (comentar para ocultar)
        # pygame.draw.rect(surface, RED, (int(self.x), int(self.y), self.width, self.height), 2)
    
    def draw_health(self, surface):
        # Configuracion barra de vida - mas ancha
        bar_width = 285
        bar_height = 20
        
        # Icono de Spider-man a la izquierda
        if health_icon:
            icon_x = 10
            icon_y = 15
            surface.blit(health_icon, (icon_x, icon_y))
            # Barra al lado del icono, centrada verticalmente con el icono
            icon_center_y = icon_y + health_icon.get_height() // 2
            bar_x = icon_x + health_icon.get_width()  # Justo al lado, sin espacio
            bar_y = icon_center_y - bar_height // 2  # Centrada vertical con icono
        else:
            bar_x = 60
            bar_y = 25
        
        # Fondo de barra (negro) - sin margen izquierdo extra
        pygame.draw.rect(surface, BLACK, (bar_x, bar_y - 2, bar_width + 4, bar_height + 4))
        
        # Barra de vida (rojo oscuro)
        health_width = int((self.health / self.max_health) * bar_width)
        pygame.draw.rect(surface, DARK_RED, (bar_x, bar_y, health_width, bar_height))
        
        # Texto de vida
        font = pygame.font.SysFont("arial", 18, bold=True)
        health_text = font.render(f"{self.health}/{self.max_health}", True, WHITE)
        text_x = bar_x + bar_width // 2 - health_text.get_width() // 2
        text_y = bar_y + bar_height // 2 - health_text.get_height() // 2
        surface.blit(health_text, (text_x, text_y))

# Instanciar jugador
player = Player()

# Bucle principal
clock = pygame.time.Clock()
running = True

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False
            # Teclas para ajustar vida (testing)
            if event.key == pygame.K_1:
                player.health = max(0, player.health - 10)
            if event.key == pygame.K_2:
                player.health = min(player.max_health, player.health + 10)
    
    # Obtener teclas presionadas
    keys = pygame.key.get_pressed()
    
    # Actualizar jugador
    player.update(keys)
    
    # Dibujar
    screen.fill(RED)  # Fondo rojo
    
    # Dibujar suelo invisible (línea blanca)
    pygame.draw.line(screen, WHITE, (0, player.ground_y), (screen_width, player.ground_y), 2)
    
    # Dibujar jugador
    player.draw(screen)
    
    # Dibujar barra de vida
    player.draw_health(screen)
    
    # Instrucciones
    font_small = pygame.font.SysFont("arial", 16)
    instructions = [
        "Flechas/A,D: Moverse",
        "Espacio/W/Arriba: Saltar",
        "ESC: Salir",
        "1: Daño | 2: Curar"
    ]
    for i, text in enumerate(instructions):
        surf = font_small.render(text, True, WHITE)
        screen.blit(surf, (10, screen_height - 100 + i * 20))
    
    # Debug info
    debug_font = pygame.font.SysFont("arial", 14)
    debug_text = f"Anim: {player.current_animation} | Frame: {player.frame_index} | Facing Right: {player.facing_right} | Turning: {player.is_turning}"
    debug_surf = debug_font.render(debug_text, True, WHITE)
    screen.blit(debug_surf, (10, screen_height - 30))
    
    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()
