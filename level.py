import pygame
import random
from settings import SCREEN_WIDTH, SCREEN_HEIGHT, IMG_DIR
from sprites import Platform, MovingPlatform, BreakingPlatform, PowerUp, FlyingEnemy

class Level:
    def __init__(self, all_sprites: pygame.sprite.Group, platforms: pygame.sprite.Group) -> None:
        self.all_sprites = all_sprites
        self.platforms = platforms
        self.powerups = pygame.sprite.Group()
        self.enemies = pygame.sprite.Group()  # Novo grupo para inimigos
        self.max_score = 0
        self.total_height_climbed = 0  # Adiciona contador de altura total escalada
        self.displayed_score = 0  # Novo atributo para controlar a pontuação exibida
        self.background = pygame.image.load(f"{IMG_DIR}/background.png").convert()
        self.background = pygame.transform.scale(self.background, (SCREEN_WIDTH, SCREEN_HEIGHT))
        self.platform_count = 0  # Contador para controlar as primeiras plataformas
        self.difficulty = 0  # Controla a dificuldade do jogo

        # Criar a primeira plataforma diretamente sob o jogador
        p = Platform(SCREEN_WIDTH // 2 - 35, 500)
        self.all_sprites.add(p)
        self.platforms.add(p)
        self.platform_count += 1
        last_y = 500
        last_x = p.rect.x  # Armazena o x da última plataforma

        # Gerar as próximas 10 plataformas
        for i in range(10):
            y = last_y - random.randint(50, 70)
            p = self.create_platform(y, last_x)
            last_y = p.rect.y
            last_x = p.rect.x

    def create_platform(self, y: int, last_x: int = None) -> Platform:
        width = 70
        # Calcula o x baseado no last_x se fornecido, caso contrário, define aleatoriamente
        if last_x is not None:
            delta = random.randint(-50, 50)
            x = last_x + delta
            x = max(0, min(x, SCREEN_WIDTH - width))
        else:
            x = random.randrange(0, SCREEN_WIDTH - width)
        
        # As primeiras 3 plataformas sempre serão normais
        if self.platform_count < 3:
            p = Platform(x, y)
        else:
            platform_type = random.random()
            if platform_type < 0.15 and y < 400:
                p = MovingPlatform(x, y)
            elif platform_type < 0.30 and y < 300:
                p = BreakingPlatform(x, y)
            else:
                p = Platform(x, y)
        
        self.platform_count += 1
        self.all_sprites.add(p)
        self.platforms.add(p)
        
        # Chance de adicionar power-up em plataformas normais
        if self.platform_count >= 3 and random.random() < 0.1 and y < 200:
            pu_type = "spring" if random.random() < 0.7 else "jetpack"
            pu = PowerUp(x + width//2, y, pu_type)
            self.all_sprites.add(pu)
            self.powerups.add(pu)
        
        return p  # Retorna a plataforma criada

    def update(self, player: 'Player') -> None:
        # Se o jogador ultrapassar metade da tela, mover plataformas para baixo
        if player.rect.top <= SCREEN_HEIGHT / 2:
            # Calcular o deslocamento vertical
            offset = abs(player.vy)
            
            # Adiciona a altura escalada ao total de forma mais controlada
            self.total_height_climbed += offset
            
            # Aumenta a dificuldade baseado na altura
            self.difficulty = int(self.total_height_climbed / 1000)
            
            player.rect.y += offset
            for sprite in self.all_sprites.sprites():
                if sprite != player:
                    sprite.rect.y += offset
                    # Remover sprites que saem da tela
                    if sprite.rect.top >= SCREEN_HEIGHT:
                        sprite.kill()
            self.generate_platforms()
            
            # Gerar inimigos com base na dificuldade
            if random.random() < 0.01 + min(0.05, self.difficulty * 0.005):
                self.generate_enemy()
        
        # Calcula a pontuação real (arredondada para baixo)
        real_score = int(self.total_height_climbed)
        
        # Atualiza a pontuação exibida de forma suave (incrementando gradualmente)
        if real_score > self.displayed_score:
            # Incrementa em passos de 1, mais lento e mais estável
            self.displayed_score += 1
        
        # Garante que a pontuação máxima seja sempre a maior até agora
        if self.displayed_score > self.max_score:
            self.max_score = self.displayed_score
        
        # Verificar colisão com power-ups
        powerup_hits = pygame.sprite.spritecollide(player, self.powerups, True)
        for powerup in powerup_hits:
            powerup.apply_effect(player)
    
    def generate_enemy(self) -> None:
        """Gera um novo inimigo voador em uma posição aleatória no topo da tela"""
        x = random.randint(40, SCREEN_WIDTH - 40)
        y = random.randint(-50, 0)  # Ligeiramente acima da tela visível
        
        enemy = FlyingEnemy(x, y)
        self.all_sprites.add(enemy)
        self.enemies.add(enemy)
    
    def generate_platforms(self) -> None:
        # Encontrar a plataforma com menor y (mais alta)
        min_plat = min(self.platforms, key=lambda p: p.rect.y)
        min_y = min_plat.rect.y
        x_hint = min_plat.rect.x
        while len(self.platforms) < 8:
            new_y = min_y - random.randint(50, 70)
            new_plat = self.create_platform(new_y, x_hint)
            min_y = new_plat.rect.y
            x_hint = new_plat.rect.x
            
    def draw_background(self, screen: pygame.Surface) -> None:
        # Desenha o background
        screen.blit(self.background, (0, 0))
