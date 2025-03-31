import pygame
from settings import IMG_DIR, SND_DIR, GRAVITY, SCREEN_WIDTH, SCREEN_HEIGHT, WHITE
import random

class Player(pygame.sprite.Sprite):
    def __init__(self) -> None:
        super().__init__()
        # Carrega e redimensiona a imagem do jogador para 40x40
        original_image = pygame.image.load(f"{IMG_DIR}/player.png").convert_alpha()
        self.image = pygame.transform.scale(original_image, (40, 40))
        self.rect = self.image.get_rect()
        self.rect.midbottom = (200, 500)
        self.vx = 0
        self.vy = 0
        self.is_jumping = False
        # Sons de pulo
        self.jump_sound = pygame.mixer.Sound(f"{SND_DIR}/jump.wav")
        self.jump_sound.set_volume(0.3)
        # Novo estado para power-up
        self.powered_up = False
        self.was_powered_up = False
        
    def update(self) -> None:
        # Movimento horizontal baseado no input
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            self.vx = -5
        elif keys[pygame.K_RIGHT]:
            self.vx = 5
        else:
            self.vx = 0
        self.rect.x += self.vx
        # Atualizar posição vertical
        self.vy += GRAVITY
        self.rect.y += self.vy
        # Corrigir atravessar as laterais
        if self.rect.left > SCREEN_WIDTH:
            self.rect.right = 0
        if self.rect.right < 0:
            self.rect.left = SCREEN_WIDTH
        
    def jump(self, boost: float = 1.0) -> None:
        # Define pulo, utilizando som ou power-up se desejar
        self.vy = -11 * boost  # Aumentado de -10 para -11 para garantir alcance
        self.jump_sound.play()
        self.is_jumping = True

class Platform(pygame.sprite.Sprite):
    def __init__(self, x: int, y: int, image_name: str = "platform_green.png") -> None:
        super().__init__()
        # Carrega e redimensiona a imagem da plataforma para 70x20
        original_image = pygame.image.load(f"{IMG_DIR}/{image_name}").convert_alpha()
        self.image = pygame.transform.scale(original_image, (70, 20))
        self.rect = self.image.get_rect(topleft=(x, y))
        self.type = "normal"
        
    def update(self) -> None:
        pass
        
    def on_collision(self, player: 'Player') -> bool:
        """O que acontece quando o jogador colide com esta plataforma"""
        # Só fazer o jogador pular se ele estiver caindo
        if player.vy > 0:
            player.jump()
            return True  # Plataforma permanece após colisão
        return True

class MovingPlatform(Platform):
    def __init__(self, x: int, y: int) -> None:
        super().__init__(x, y, "platform_blue_moving.png")
        self.type = "moving"
        self.vx = random.choice([-2, 2])
        
    def update(self) -> None:
        self.rect.x += self.vx
        # Inverter direção quando atingir os limites da tela
        if self.rect.right > SCREEN_WIDTH or self.rect.left < 0:
            self.vx *= -1

class BreakingPlatform(Platform):
    def __init__(self, x: int, y: int) -> None:
        super().__init__(x, y, "platform_brown_breaking_1.png")
        self.type = "breaking"
        self.breaking = False
        self.break_time = 0
        self.break_sound = pygame.mixer.Sound(f"{SND_DIR}/platform_break.wav")
        self.break_sound.set_volume(0.4)
        
    def update(self) -> None:
        if self.breaking:
            self.break_time += 1
            if self.break_time >= 10:  # 10 frames até quebrar
                self.kill()
                
    def on_collision(self, player: 'Player') -> bool:
        if not self.breaking:
            player.jump()
            self.breaking = True
            self.break_sound.play()
            # Muda imagem para plataforma quebrada
            original_image = pygame.image.load(f"{IMG_DIR}/platform_brown_breaking_2.png").convert_alpha()
            self.image = pygame.transform.scale(original_image, (70, 20))
        return True  # Mantém no grupo até que a atualização a remova

class PowerUp(pygame.sprite.Sprite):
    def __init__(self, x: int, y: int, type: str = "spring") -> None:
        super().__init__()
        self.type = type
        if type == "spring":
            original_image = pygame.image.load(f"{IMG_DIR}/spring.png").convert_alpha()
            self.image = pygame.transform.scale(original_image, (20, 20))
        elif type == "jetpack":
            original_image = pygame.image.load(f"{IMG_DIR}/jetpack.png").convert_alpha()
            self.image = pygame.transform.scale(original_image, (30, 30))
        self.rect = self.image.get_rect(midbottom=(x, y))
        self.pickup_sound = pygame.mixer.Sound(f"{SND_DIR}/powerup_pickup.wav")
        self.pickup_sound.set_volume(0.5)
        
    def apply_effect(self, player: 'Player') -> None:
        self.pickup_sound.play()  # Aqui o som é tocado quando o power-up é coletado
        player.powered_up = True  # Ativa o estado de power-up
        player.was_powered_up = True  # Marca que o jogador pegou um power-up
        if self.type == "spring":
            player.jump(boost=1.5)  # Pulo mais alto
        elif self.type == "jetpack":
            player.jump(boost=3.0)  # Pulo muito mais alto

class FlyingEnemy(pygame.sprite.Sprite):
    def __init__(self, x: int, y: int) -> None:
        super().__init__()
        # Carrega e redimensiona a imagem do inimigo voador (reduzido o tamanho)
        try:
            original_image = pygame.image.load(f"{IMG_DIR}/enemy_fly.png").convert_alpha()
            self.image = pygame.transform.scale(original_image, (30, 20))  # Reduzido de 40x30 para 30x20
        except:
            # Fallback caso a imagem não exista
            self.image = pygame.Surface((30, 20))  # Reduzido tamanho
            self.image.fill((255, 0, 0))
            pygame.draw.circle(self.image, (0, 0, 0), (15, 10), 4)  # Ajustado o círculo também
            
        self.rect = self.image.get_rect(center=(x, y))
        # Criando um hitbox menor (75% do tamanho original)
        self.hitbox = pygame.Rect(0, 0, self.rect.width * 0.75, self.rect.height * 0.75)
        self.hitbox.center = self.rect.center
        
        self.vx = random.choice([-2, -1, 1, 2])  # Velocidade horizontal aleatória
        self.vy = random.uniform(-0.5, 0.5)  # Pequena flutuação vertical
        
    def update(self) -> None:
        # Movimento horizontal
        self.rect.x += self.vx
        
        # Pequeno movimento vertical para simular voo
        self.rect.y += self.vy
        
        # Atualizar a posição do hitbox para acompanhar a imagem
        self.hitbox.center = self.rect.center
        
        # Inverter direção horizontal quando bater na borda da tela
        if self.rect.right > SCREEN_WIDTH:
            self.vx = -abs(self.vx)
        elif self.rect.left < 0:
            self.vx = abs(self.vx)
            
        # Inverter flutuação vertical em intervalos aleatórios
        if random.random() < 0.02:
            self.vy *= -1
