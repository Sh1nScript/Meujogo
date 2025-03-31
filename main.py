from game import Game

if __name__ == "__main__":
    g = Game()
    g.show_start_screen()  # nova tela de início para Start/Sair
    
    while g.running:
        g.new()
        if g.running:  # Verifica se não saiu durante o jogo
            g.show_game_over()
