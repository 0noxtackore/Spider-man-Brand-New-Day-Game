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
ORANGE = (255, 149, 0)
DARK_RED = (139, 0, 0)

# Rutas de animaciones
ANIMATION_PATHS = {
    "idle-right": "images-game/characters/Spider-man/idle-right.gif",
    "idle-left": "images-game/characters/Spider-man/idle-left.gif",
    "run-right": "images-game/characters/Spider-man/run-right.gif",
    "run-left": "images-game/characters/Spider-man/run-left.gif",
    "entry-right": "images-game/characters/Spider-man/entry-right.png",
    "entry-left": "images-game/characters/Spider-man/entry-left.png",
    "jump-right": "images-game/characters/Spider-man/jump-right.gif",
    "jump-left": "images-game/characters/Spider-man/jump-left.gif",
    "sit-right": "images-game/characters/Spider-man/sit-right.png",
    "sit-left": "images-game/characters/Spider-man/sit-left.png",
    "sit-center": "images-game/characters/Spider-man/sit-center.png",
    "sit-back": "images-game/characters/Spider-man/sit-back.png"
}

HEALTH_ICON_PATH = "images-game/health-character/Spider-man.png"

# Cargar GIF con PIL
def load_gif_frames(path, scale_factor=1.0):
    """Carga frames de un GIF usando PIL con transparencia y normalizacion de tamaño"""
    frames = []
    if not os.path.exists(path):
        print(f"No encontrado: {path}")
        return frames
    
    try:
        gif = Image.open(path)
        
        # Obtener dimensiones del primer frame como referencia
        gif.seek(0)
        ref_frame = gif.convert('RGBA')
        ref_w = int(ref_frame.width * scale_factor)
        ref_h = int(ref_frame.height * scale_factor)
        
        for frame_num in range(gif.n_frames):
            gif.seek(frame_num)
            # Convertir a RGBA para preservar transparencia
            frame_rgba = gif.convert('RGBA')
            # Escalar al tamaño de referencia (normalizar)
            frame_resized = frame_rgba.resize((ref_w, ref_h), Image.Resampling.LANCZOS)
            frame_data = frame_resized.tobytes()
            frame_surface = pygame.image.fromstring(frame_data, (ref_w, ref_h), 'RGBA')
            frames.append(frame_surface)
        print(f"Cargado: {path} ({len(frames)} frames, {ref_w}x{ref_h})")
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
JUMP_SCALE = 0.25  # Escala más pequeña para jump-left y jump-right

# Cargar todas las animaciones
animations = {
    "idle-right": load_gif_frames(ANIMATION_PATHS["idle-right"], PLAYER_SCALE),
    "idle-left": load_gif_frames(ANIMATION_PATHS["idle-left"], PLAYER_SCALE),
    "run-right": load_gif_frames(ANIMATION_PATHS["run-right"], RUN_SCALE),
    "run-left": load_gif_frames(ANIMATION_PATHS["run-left"], RUN_SCALE),
    "entry-right": [load_single_image(ANIMATION_PATHS["entry-right"], PLAYER_SCALE)],
    "entry-left": [load_single_image(ANIMATION_PATHS["entry-left"], PLAYER_SCALE)],
    "jump-right": load_gif_frames(ANIMATION_PATHS["jump-right"], PLAYER_SCALE),
    "jump-left": load_gif_frames(ANIMATION_PATHS["jump-left"], PLAYER_SCALE),
    "sit-right": [load_single_image(ANIMATION_PATHS["sit-right"], PLAYER_SCALE)],
    "sit-left": [load_single_image(ANIMATION_PATHS["sit-left"], PLAYER_SCALE)],
    "sit-center": [load_single_image(ANIMATION_PATHS["sit-center"], PLAYER_SCALE)],
    "sit-back": [load_single_image(ANIMATION_PATHS["sit-back"], PLAYER_SCALE)]
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
        
        # Salto (jump animation sin bucle)
        self.is_jumping = False
        self.jump_played = False  # Para controlar que solo se reproduzca una vez
        
        # Animación de aterrizaje (sit -> idle)
        self.is_sitting = False
        self.sit_timer = 0
        self.sit_duration = 4  # frames para animación sit (< 1s a 60fps)
        
        # Volteo (transición)
        self.is_turning = False
        self.turn_timer = 0
        self.turn_duration = 8  # frames para entry
        
        # Agacharse (sit-left/sit-right mantenido)
        self.is_crouching = False
        self.crouch_turning = False  # Para transición sit-center/sit-back
        self.crouch_turn_timer = 0
        self.crouch_turn_duration = 6
        
        # Vida
        self.max_health = 100
        self.health = 100
        
        # Suelo (posición Y del suelo invisible)
        self.ground_y = screen_height - 40
    
    def update(self, keys):
        # Movimiento horizontal
        moving_left = keys[pygame.K_LEFT] or keys[pygame.K_a]
        moving_right = keys[pygame.K_RIGHT] or keys[pygame.K_d]
        moving_down = keys[pygame.K_DOWN] or keys[pygame.K_s]
        
        # Prioridad: si ambas teclas, mantener dirección actual (quieto)
        if moving_right and moving_left:
            self.vel_x = 0
            # Mantener animación idle en la dirección actual (si no está en transición)
            if not self.is_turning and not self.is_sitting and not self.is_crouching:
                self.current_animation = "idle-right" if self.facing_right else "idle-left"
            # No hacer return aquí para permitir que la física continúe
        
        # Manejar animación de agacharse
        if self.is_crouching:
            self.vel_x = 0  # No moverse horizontalmente mientras se agacha
            
            # Si está en transición de volteo en crouch
            if self.crouch_turning:
                self.crouch_turn_timer -= 1
                if self.crouch_turn_timer <= 0:
                    self.crouch_turning = False
                    # Al terminar transición, ir al sit correspondiente
                    self.current_animation = "sit-right" if self.facing_right else "sit-left"
                    self.frame_index = 0
            else:
                # Detectar cambio de dirección mientras está agachado
                if moving_right and not self.facing_right:
                    # Voltear de izquierda a derecha
                    self.crouch_turning = True
                    self.crouch_turn_timer = self.crouch_turn_duration
                    self.current_animation = "sit-back"
                    self.facing_right = True
                    self.frame_index = 0
                elif moving_left and self.facing_right:
                    # Voltear de derecha a izquierda
                    self.crouch_turning = True
                    self.crouch_turn_timer = self.crouch_turn_duration
                    self.current_animation = "sit-center"
                    self.facing_right = False
                    self.frame_index = 0
        
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
        
        # Detectar tecla abajo para agacharse (solo en suelo y no saltando)
        if moving_down and self.on_ground and not self.is_jumping and not self.is_crouching:
            self.is_crouching = True
            self.crouch_turning = False
            # Seleccionar animación según dirección actual
            self.current_animation = "sit-right" if self.facing_right else "sit-left"
            self.frame_index = 0
        
        # Detectar tecla arriba para salir de agacharse (solo flecha arriba)
        moving_up = keys[pygame.K_UP]
        if self.is_crouching and moving_up:
            self.is_crouching = False
            self.crouch_turning = False
            self.current_animation = "idle-right" if self.facing_right else "idle-left"
            self.frame_index = 0
        
        # Movimiento normal (no está volteando ni sentándose ni agachándose ni en transición de crouch)
        if not self.is_crouching and not self.is_turning and not self.is_sitting:
            if not self.is_jumping and not self.is_sitting:
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
            else:
                # Si está saltando, actualizar velocidad y detectar cambio de dirección
                if moving_right:
                    self.current_speed += (self.max_speed - self.current_speed) * self.acceleration
                    self.vel_x = self.current_speed
                    # Cambiar animación de salto si voltea a la derecha
                    if not self.facing_right:
                        self.facing_right = True
                        self.current_animation = "jump-right"
                        self.frame_index = 0  # Resetear frame
                elif moving_left:
                    self.current_speed += (self.max_speed - self.current_speed) * self.acceleration
                    self.vel_x = -self.current_speed
                    # Cambiar animación de salto si voltea a la izquierda
                    if self.facing_right:
                        self.facing_right = False
                        self.current_animation = "jump-left"
                        self.frame_index = 0  # Resetear frame
                else:
                    self.vel_x = 0
        
        # Salto (solo con SPACE, no UP ni W) - puede interrumpir sit
        if keys[pygame.K_SPACE] and self.on_ground and not self.is_jumping:
            # Cancelar cualquier animación de sit si está activa
            if self.is_sitting:
                self.is_sitting = False
                self.sit_timer = 0
            self.vel_y = self.jump_power
            self.on_ground = False
            self.is_jumping = True
            self.jump_played = False  # Resetear para reproducir animación
            self.frame_index = 0  # Resetear frame para animación de salto
            # Seleccionar animación de salto según dirección
            if self.facing_right:
                self.current_animation = "jump-right"
            else:
                self.current_animation = "jump-left"
        
        # Aplicar gravedad
        self.vel_y += self.gravity
        
        # Actualizar posición
        self.x += self.vel_x
        self.y += self.vel_y
        
        # Colisión con suelo invisible
        if self.y + self.height > self.ground_y:
            self.y = self.ground_y - self.height
            self.vel_y = 0
            was_in_air = not self.on_ground  # Verificar si venía del aire
            self.on_ground = True
            # Si acaba de aterrizar, verificar si está corriendo
            if was_in_air and self.is_jumping:
                self.is_jumping = False
                moving_right = keys[pygame.K_RIGHT] or keys[pygame.K_d]
                moving_left = keys[pygame.K_LEFT] or keys[pygame.K_a]
                
                # Si está corriendo, ir directamente a run, sino hacer sit -> idle
                if moving_right:
                    self.current_animation = "run-right"
                    self.facing_right = True
                elif moving_left:
                    self.current_animation = "run-left"
                    self.facing_right = False
                else:
                    # No está corriendo, iniciar animación sit -> idle
                    self.is_sitting = True
                    self.sit_timer = self.sit_duration
                    self.current_animation = "sit-right" if self.facing_right else "sit-left"
                    self.frame_index = 0
        
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
            
            # Manejar animación de agacharse (sit-center/sit-back transiciones)
            if self.is_crouching:
                # Solo manejar transiciones de volteo en crouch
                if self.crouch_turning:
                    self.crouch_turn_timer -= 1
                    if self.crouch_turn_timer <= 0:
                        self.crouch_turning = False
                        # Al terminar transición, ir al sit correspondiente
                        self.current_animation = "sit-right" if self.facing_right else "sit-left"
                        self.frame_index = 0
                return
            
            # Manejar animación de sentarse (sit -> idle)
            if self.is_sitting:
                self.sit_timer -= 1
                if self.sit_timer <= 0:
                    self.is_sitting = False
                    # Al terminar sit, ir a idle
                    self.current_animation = "idle-right" if self.facing_right else "idle-left"
                    self.frame_index = 0
                # Las animaciones sit son estáticas (un solo frame)
                return
            
            # Si es animación de salto, no hacer bucle (reproducir una sola vez)
            if self.current_animation in ["jump-right", "jump-left"]:
                # Avanzar frame solo si no hemos llegado al final
                if self.frame_index < len(anim_frames) - 1:
                    self.frame_index += 1
                # Si llegamos al final, mantener el último frame
            else:
                # Otras animaciones hacen bucle normal
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
            
            # Offset horizontal para animaciones de salto (centrar visualmente)
            if self.current_animation == "jump-right":
                frame_rect.x -= 0  # Mover un poco a la izquierda
            elif self.current_animation == "jump-left":
                frame_rect.x += 0  # Mover un poco a la derecha
            
            surface.blit(frame, frame_rect)
        
        # Debug: dibujar hitbox (comentar para ocultar)
        # pygame.draw.rect(surface, RED, (int(self.x), int(self.y), self.width, self.height), 2)
    
    def draw_health(self, surface):
        # Configuracion barra de vida
        bar_width = 320
        bar_height = 20
        
        # Icono a la izquierda, barra al lado centrada verticalmente
        if health_icon:
            icon_x = 10
            icon_y = 15
            surface.blit(health_icon, (icon_x, icon_y))
            # Barra al lado del icono, centrada verticalmente
            icon_center_y = icon_y + health_icon.get_height() // 2
            bar_x = icon_x + health_icon.get_width()  # Justo al lado del icono
            bar_y = icon_center_y - bar_height // 2  # Centrada vertical con icono
        else:
            bar_x = 60
            bar_y = 25
        
        # Fondo de barra (negro)
        pygame.draw.rect(surface, BLACK, (bar_x - 2, bar_y - 2, bar_width + 4, bar_height + 4))
        
        # Barra de vida - color segun porcentaje
        health_width = int((self.health / self.max_health) * bar_width)
        health_percent = self.health / self.max_health
        
        if health_percent >= 0.5:
            bar_color = ORANGE
        else:
            bar_color = RED  
        
        pygame.draw.rect(surface, bar_color, (bar_x, bar_y, health_width, bar_height))
        
        # Texto SPIDER-MAN con efecto de contraste dinamico
        font = pygame.font.SysFont("arial", 16, bold=True)
        text_str = "SPIDER-MAN"
        
        # Renderizamos dos versiones del texto
        text_white = font.render(text_str, True, WHITE)
        text_black = font.render(text_str, True, BLACK)
        
        text_x = bar_x + bar_width // 2 - text_white.get_width() // 2
        text_y = bar_y + bar_height // 2 - text_white.get_height() // 2
        
        # A. Dibujamos la version BLANCA primero (se vera donde NO hay barra de vida)
        surface.blit(text_white, (text_x, text_y))
        
        # B. Dibujamos la version NEGRA, pero solo dentro del area de la barra actual
        current_bar_rect = pygame.Rect(bar_x, bar_y, health_width, bar_height)
        surface.set_clip(current_bar_rect)
        surface.blit(text_black, (text_x, text_y))
        
        # C. Resetear el clip
        surface.set_clip(None)

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
        "SPACE: Saltar",
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
