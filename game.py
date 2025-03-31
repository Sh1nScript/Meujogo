import pygame
import os
from settings import SCREEN_WIDTH, SCREEN_HEIGHT, FPS, WHITE, BLACK, IMG_DIR, SND_DIR, FONT_DIR, GREEN
from sprites import Player
from level import Level

class Game:
    def __init__(self) -> None:
        pygame.init()
        pygame.mixer.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Doodle Jump")
        self.clock = pygame.time.Clock()
        self.running = True
        
        # Carregar fonte personalizada se existir, senão usar Arial
        self.font_path = os.path.join(FONT_DIR, "game_font.ttf")
        if os.path.exists(self.font_path):
            self.font_name = self.font_path
        else:
            self.font_name = pygame.font.match_font("arial")
            
        # Carregar sons
        self.game_over_sound = pygame.mixer.Sound(os.path.join(SND_DIR, "game_over.wav"))
        self.game_over_sound.set_volume(0.6)
        
        # Carregar música de fundo
        pygame.mixer.music.load(os.path.join(SND_DIR, "background_music.ogg"))
        pygame.mixer.music.set_volume(0.3)
        
        # Carregar imagens para menu
        try:
            self.menu_background = pygame.image.load(os.path.join(IMG_DIR, "background2.png")).convert()
            self.menu_background = pygame.transform.scale(self.menu_background, (SCREEN_WIDTH, SCREEN_HEIGHT))
        except:
            self.menu_background = None
            print("Aviso: background2.png não encontrado. Usando cor sólida.")
    
    def new(self) -> None:
        # Inicializa novos grupos de sprites e cria o player e level
        self.all_sprites = pygame.sprite.Group()
        self.platforms = pygame.sprite.Group()
        self.player = Player()
        self.all_sprites.add(self.player)
        self.level = Level(self.all_sprites, self.platforms)
        self.score = 0
        # Iniciar música
        pygame.mixer.music.play(loops=-1)
        self.run()
    
    def run(self) -> None:
        # Loop principal do jogo
        self.playing = True
        while self.playing:
            self.clock.tick(FPS)
            self.events()
            self.update()
            self.draw()
    
    def update(self) -> None:
        self.all_sprites.update()
        
        # Verifica colisão com plataformas para pulo automático
        if self.player.vy > 0:  # Só verifica colisão se o jogador estiver caindo
            hits = pygame.sprite.spritecollide(self.player, self.platforms, False)
            for platform in hits:
                # Confirma se o jogador está caindo e tocando a parte superior da plataforma
                if self.player.rect.bottom <= platform.rect.top + 10:
                    platform.on_collision(self.player)
                    self.player.rect.bottom = platform.rect.top
                    
                    # Verifica se o jogador estava com power-up e agora pousou em uma plataforma
                    if self.player.was_powered_up and not self.player.powered_up:
                        self.player.was_powered_up = False
                    
                    # Desativa o estado de power-up quando pousa em uma plataforma
                    if self.player.powered_up:
                        self.player.powered_up = False
                    break
        
        # Verificar se o jogador está descendo (após o auge do pulo)
        # Isso desativa o estado powered_up após o auge do pulo
        if self.player.vy > 0 and self.player.powered_up:
            self.player.powered_up = False
        
        # Verificar colisão com inimigos usando o hitbox reduzido
        if hasattr(self.level, 'enemies'):
            for enemy in self.level.enemies:
                # Verificar colisão entre o retângulo do jogador e o hitbox do inimigo
                if self.player.rect.colliderect(enemy.hitbox):
                    # Se o jogador pula em cima do inimigo (está caindo e toca a parte superior)
                    if self.player.vy > 0 and self.player.rect.bottom <= enemy.hitbox.top + 15:
                        # Destrói o inimigo e faz o jogador pular
                        enemy.kill()
                        self.player.jump(boost=1.2)
                    # Se o jogador colide com o inimigo de lado ou por baixo, mas está com power-up ativo
                    # ou já teve power-up mas ainda não pousou em plataforma, ignora o game over
                    elif self.player.powered_up or self.player.was_powered_up:
                        continue
                    else:
                        # O jogador colide com o inimigo de lado ou por baixo - game over
                        self.game_over_sound.play()
                        pygame.mixer.music.stop()
                        self.playing = False
        
        # Atualiza o nível após processar colisões
        self.level.update(self.player)
        
        # Atualizar pontuação usando a pontuação exibida, não a altura total
        self.score = self.level.displayed_score
        
        # Verifica se o jogador caiu
        if self.player.rect.top > SCREEN_HEIGHT:
            self.game_over_sound.play()
            pygame.mixer.music.stop()
            self.playing = False
    
    def events(self) -> None:
        for event in pygame.event.get():
            # Fecha o jogo
            if event.type == pygame.QUIT:
                self.playing = False
                self.running = False
    
    def get_font_size(self, base_size: int) -> int:
        """Calcula um tamanho de fonte proporcional à largura da tela"""
        # Usando 400 como largura de referência (a largura atual da tela)
        scale_factor = SCREEN_WIDTH / 400
        return int(base_size * scale_factor)
    
    def draw(self) -> None:
        # Desenha o fundo
        self.level.draw_background(self.screen)
        
        # Desenha todos os sprites
        self.all_sprites.draw(self.screen)
        
        # Desenha a HUD (pontuação) com fonte Arial
        score_font = pygame.font.SysFont("arial", self.get_font_size(16))
        score_text = score_font.render(f"Pontuação: {self.score}", True, WHITE)
        self.screen.blit(score_text, (10, 10))
        
        pygame.display.flip()
    
    def draw_text(self, text: str, size: int, color: tuple, x: int, y: int, align: str = "midtop") -> None:
        font = pygame.font.Font(self.font_name, size)
        text_surface = font.render(text, True, color)
        text_rect = text_surface.get_rect()
        
        if align == "midtop":
            text_rect.midtop = (x, y)
        elif align == "topleft":
            text_rect.topleft = (x, y)
        elif align == "center":
            text_rect.center = (x, y)
            
        self.screen.blit(text_surface, text_rect)
    
    def show_game_over(self) -> None:
        self.screen.fill(BLACK)
        
        # Centraliza "GAME OVER" mais ao centro da tela
        self.draw_text("GAME OVER", self.get_font_size(36), WHITE, SCREEN_WIDTH//2, SCREEN_HEIGHT * 0.33)
        
        # Cria ambos os textos primeiro para calcular o tamanho total
        font = pygame.font.Font(self.font_name, self.get_font_size(26))
        pontuacao_text = font.render("Pontuação: ", True, WHITE)
        pontuacao_width = pontuacao_text.get_width()
        
        score_font = pygame.font.SysFont("arial", self.get_font_size(26))
        score_text = score_font.render(f"{self.score}", True, WHITE)
        score_width = score_text.get_width()
        
        # Calcula a largura total e a posição inicial para centralizar
        total_width = pontuacao_width + score_width
        start_x = (SCREEN_WIDTH - total_width) // 2
        
        # Posiciona os textos lado a lado a partir da posição inicial
        pontuacao_rect = pontuacao_text.get_rect(topleft=(start_x, SCREEN_HEIGHT * 0.5 - pontuacao_text.get_height() // 2))
        score_rect = score_text.get_rect(topleft=(start_x + pontuacao_width, SCREEN_HEIGHT * 0.5 - score_text.get_height() // 2))
        
        # Exibe os textos
        self.screen.blit(pontuacao_text, pontuacao_rect)
        self.screen.blit(score_text, score_rect)
        
        # Posiciona as instruções mais abaixo
        self.draw_text("Pressione SPACE para jogar novamente", self.get_font_size(18), WHITE, 
                      SCREEN_WIDTH//2, SCREEN_HEIGHT * 0.67)
        self.draw_text("ou ESC para sair", self.get_font_size(18), WHITE, 
                      SCREEN_WIDTH//2, SCREEN_HEIGHT * 0.75)
        
        pygame.display.flip()
        
        waiting = True
        while waiting and self.running:
            self.clock.tick(FPS//2)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    waiting = False
                    self.running = False
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        waiting = False
                    elif event.key == pygame.K_ESCAPE:
                        waiting = False
                        self.running = False
    
    def create_button(self, text, size, color, x, y, width, height, hover_color=None):
        """Cria um botão interativo com efeito hover"""
        button_rect = pygame.Rect(x, y, width, height)
        return {
            'rect': button_rect,
            'text': text,
            'size': size, # Este tamanho será ajustado ao usar o botão
            'color': color,
            'hover_color': hover_color or color,
            'is_hover': False
        }
    
    def draw_button(self, button):
        """Desenha um botão na tela"""
        color = button['hover_color'] if button['is_hover'] else button['color']
        
        # Desenhar fundo do botão com bordas arredondadas
        pygame.draw.rect(self.screen, color, button['rect'], border_radius=10)
        pygame.draw.rect(self.screen, WHITE, button['rect'], 2, border_radius=10)
        
        # Desenhar texto
        font = pygame.font.Font(self.font_name, button['size'])
        text_surf = font.render(button['text'], True, WHITE)
        text_rect = text_surf.get_rect(center=button['rect'].center)
        self.screen.blit(text_surf, text_rect)
    
    def show_start_screen(self) -> None:
        # Criar botões para o menu com fontes proporcionais
        start_button = self.create_button("INICIAR", self.get_font_size(22), GREEN, 
                                         SCREEN_WIDTH//2 - 100, SCREEN_HEIGHT//2, 
                                         200, 50, (120, 220, 120))
        
        exit_button = self.create_button("SAIR", self.get_font_size(22), (200, 100, 100), 
                                        SCREEN_WIDTH//2 - 100, SCREEN_HEIGHT//2 + 70, 
                                        200, 50, (220, 120, 120))
        
        buttons = [start_button, exit_button]
        
        # Carregar possível som de hover
        try:
            hover_sound = pygame.mixer.Sound(os.path.join(SND_DIR, "menu_hover.wav"))
            hover_sound.set_volume(0.2)
            has_hover_sound = True
        except:
            has_hover_sound = False
        
        last_hover_state = {b['text']: False for b in buttons}
        
        waiting = True
        while waiting:
            self.clock.tick(FPS)
            mouse_pos = pygame.mouse.get_pos()
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    waiting = False
                    self.running = False
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        waiting = False
                        self.running = False
                if event.type == pygame.MOUSEBUTTONDOWN:
                    for button in buttons:
                        if button['rect'].collidepoint(mouse_pos):
                            if button['text'] == "INICIAR":
                                waiting = False
                            elif button['text'] == "SAIR":
                                waiting = False
                                self.running = False
            
            # Fundo
            if self.menu_background:
                self.screen.blit(self.menu_background, (0, 0))
            else:
                self.screen.fill(BLACK)
            
            # Título com efeito de sombra - tamanho proporcional
            self.draw_text("DOODLE JUMP", self.get_font_size(38), BLACK, SCREEN_WIDTH//2 + 3, 123)
            self.draw_text("DOODLE JUMP", self.get_font_size(38), WHITE, SCREEN_WIDTH//2, 120)
            
            # Atualizar estado de hover dos botões
            for button in buttons:
                old_hover = button['is_hover']
                button['is_hover'] = button['rect'].collidepoint(mouse_pos)
                
                # Tocar som quando hover começa
                if has_hover_sound and not old_hover and button['is_hover'] and not last_hover_state[button['text']]:
                    hover_sound.play()
                
                last_hover_state[button['text']] = button['is_hover']
                self.draw_button(button)
            
            # Instruções do jogo (agora com cor preta)
            self.draw_text("Use as setas ← → para mover", self.get_font_size(14), BLACK, SCREEN_WIDTH//2, SCREEN_HEIGHT - 100)
            self.draw_text("Pule nas plataformas e não caia!", self.get_font_size(14), BLACK, SCREEN_WIDTH//2, SCREEN_HEIGHT - 70)
            
            pygame.display.flip()
