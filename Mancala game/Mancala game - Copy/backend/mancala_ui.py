import pygame  # type: ignore
import sys
import time

from game import Game
from play import Play

# Fenêtre
WIDTH, HEIGHT = 1200, 700
BGCOLOR = (20, 120, 40)
PANEL_COLOR = (160, 82, 45)
TITLE_COLOR = (255, 255, 255)
BTN_COLOR = (240, 200, 0)
BTN_HOVER = (255, 230, 80)
TEXT_COLOR = (0, 60, 0)


class MancalaUI:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.setcaption("MANCALA IA - Projet 4")
        self.clock = pygame.time.Clock()
        self.font_big = pygame.font.SysFont("Arial", 60, bold=True)
        self.font_btn = pygame.font.SysFont("Arial", 32, bold=True)
        self.font_small = pygame.font.SysFont("Arial", 24)

        # Navigation entre écrans
        self.state = "TITLE"   # TITLE -> MODE_SELECT -> HEURISTICS -> GAME
        self.selected_mode = None          # "HUMAN_VS_COMP" ou "COMP_VS_COMP"
        self.heuristic_p1 = None          # "simple" ou "strong" (computer Player1)
        self.heuristic_p2 = None          # "simple" ou "strong" (computer Player2)

        # Jeu / IA
        self.game: Game | None = None
        self.play: Play | None = None
        self.current_player = "player1"
        self.last_turn_start = time.time()
        self.time_limit = 15
        self.game_finished = False
        self.final_message = ""
        self.last_ai_move = ""

    # ---------- OUTILS GRAPHIQUES ----------
    def draw_button(self, rect: pygame.Rect, text: str) -> bool:
        mouse_pos = pygame.mouse.get_pos()
        is_hover = rect.collidepoint(mouse_pos)
        color = BTN_HOVER if is_hover else BTN_COLOR
        pygame.draw.rect(self.screen, color, rect, border_radius=15)
        pygame.draw.rect(self.screen, (120, 90, 0), rect, 3, border_radius=15)
        txt = self.font_btn.render(text, True, TEXT_COLOR)
        txt_rect = txt.get_rect(center=rect.center)
        self.screen.blit(txt, txt_rect)
        return is_hover

    # ---------- ÉCRAN 1 : TITRE ----------
    def screen_title(self):
        self.screen.fill(BGCOLOR)
        title = self.font_big.render("MANCALA - Jeu d'Adversaires", True, TITLE_COLOR)
        sub = self.font_small.render(
            "Projet 4 - Minimax Alpha-Bêta (COMPUTER vs HUMAN)", True, TITLE_COLOR
        )
        self.screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 180))
        self.screen.blit(sub, (WIDTH // 2 - sub.get_width() // 2, 250))

        btn_rect = pygame.Rect(0, 0, 260, 70)
        btn_rect.center = (WIDTH // 2, HEIGHT - 120)
        self.draw_button(btn_rect, "JOUER")

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if btn_rect.collidepoint(event.pos):
                    self.state = "MODE_SELECT"

    # ---------- ÉCRAN 2 : CHOIX DU MODE ----------
    def screen_mode_select(self):
        self.screen.fill(BGCOLOR)
        title = self.font_big.render("Choisir le mode de jeu", True, TITLE_COLOR)
        self.screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 120))

        info = self.font_small.render(
            "1. Utilisateur vs Computer    2. Computer vs Computer",
            True,
            TITLE_COLOR,
        )
        self.screen.blit(info, (WIDTH // 2 - info.get_width() // 2, 190))

        btn1 = pygame.Rect(0, 0, 420, 80)
        btn1.center = (WIDTH // 2, 320)
        btn2 = pygame.Rect(0, 0, 420, 80)
        btn2.center = (WIDTH // 2, 430)

        self.draw_button(btn1, "1  Utilisateur  vs  Computer")
        self.draw_button(btn2, "2  Computer  vs  Computer")

        help_text = self.font_small.render(
            "Cliquez sur un mode pour passer au choix des heuristiques.",
            True,
            TITLE_COLOR,
        )
        self.screen.blit(help_text, (WIDTH // 2 - help_text.get_width() // 2, 520))

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if btn1.collidepoint(event.pos):
                    self.selected_mode = "HUMAN_VS_COMP"
                    self.state = "HEURISTICS"
                elif btn2.collidepoint(event.pos):
                    self.selected_mode = "COMP_VS_COMP"
                    self.state = "HEURISTICS"

    # ---------- ÉCRAN 3 : CHOIX DES HEURISTIQUES ----------
    def screen_heuristics(self):
        self.screen.fill(BGCOLOR)
        title = self.font_big.render("Choix des heuristiques IA", True, TITLE_COLOR)
        self.screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 60))

        panel = pygame.Rect(140, 130, WIDTH - 280, 420)
        pygame.draw.rect(self.screen, PANEL_COLOR, panel, border_radius=20)
        pygame.draw.rect(self.screen, (90, 50, 10), panel, 4, border_radius=20)

        if self.selected_mode == "HUMAN_VS_COMP":
            txt1 = self.font_small.render(
                "Mode : Utilisateur (Player1, bas)  vs  Computer (Player2, haut)",
                True,
                TITLE_COLOR,
            )
            txt2 = self.font_small.render(
                "Choisissez l'heuristique du Computer (Player2) :",
                True,
                TITLE_COLOR,
            )
            self.screen.blit(txt1, (panel.x + 40, panel.y + 40))
            self.screen.blit(txt2, (panel.x + 40, panel.y + 90))

            btn_simple = pygame.Rect(panel.x + 80, panel.y + 160, 260, 70)
            btn_strong = pygame.Rect(panel.x + 380, panel.y + 160, 260, 70)

            self.draw_button(btn_simple, "Heuristique FAIBLE (simple)")
            self.draw_button(btn_strong, "Heuristique FORTE (strong)")

            pygame.display.flip()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if btn_simple.collidepoint(event.pos):
                        self.heuristic_p1 = None
                        self.heuristic_p2 = "simple"
                        self.start_game(human_vs_comp=True)
                    elif btn_strong.collidepoint(event.pos):
                        self.heuristic_p1 = None
                        self.heuristic_p2 = "strong"
                        self.start_game(human_vs_comp=True)

        else:  # COMP_VS_COMP
            txt1 = self.font_small.render(
                "Mode : Computer (Player1, bas)  vs  Computer (Player2, haut)",
                True,
                TITLE_COLOR,
            )
            txt2 = self.font_small.render(
                "Choisissez l'heuristique de chaque Computer :",
                True,
                TITLE_COLOR,
            )
            self.screen.blit(txt1, (panel.x + 40, panel.y + 40))
            self.screen.blit(txt2, (panel.x + 40, panel.y + 90))

            lab1 = self.font_small.render(
                "Computer Player1 (bas) :", True, TITLE_COLOR
            )
            self.screen.blit(lab1, (panel.x + 40, panel.y + 140))
            btn_p1_simple = pygame.Rect(panel.x + 80, panel.y + 180, 220, 60)
            btn_p1_strong = pygame.Rect(panel.x + 330, panel.y + 180, 220, 60)
            self.draw_button(btn_p1_simple, "P1  FAIBLE")
            self.draw_button(btn_p1_strong, "P1  FORTE")

            lab2 = self.font_small.render(
                "Computer Player2 (haut) :", True, TITLE_COLOR
            )
            self.screen.blit(lab2, (panel.x + 40, panel.y + 270))
            btn_p2_simple = pygame.Rect(panel.x + 80, panel.y + 310, 220, 60)
            btn_p2_strong = pygame.Rect(panel.x + 330, panel.y + 310, 220, 60)
            self.draw_button(btn_p2_simple, "P2  FAIBLE")
            self.draw_button(btn_p2_strong, "P2  FORTE")

            btn_start = pygame.Rect(panel.centerx - 130, panel.y + 370, 260, 60)
            self.draw_button(btn_start, "Lancer la partie IA vs IA")

            pygame.display.flip()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if btn_p1_simple.collidepoint(event.pos):
                        self.heuristic_p1 = "simple"
                    elif btn_p1_strong.collidepoint(event.pos):
                        self.heuristic_p1 = "strong"
                    elif btn_p2_simple.collidepoint(event.pos):
                        self.heuristic_p2 = "simple"
                    elif btn_p2_strong.collidepoint(event.pos):
                        self.heuristic_p2 = "strong"
                    elif btn_start.collidepoint(event.pos):
                        if self.heuristic_p1 and self.heuristic_p2:
                            self.start_game(human_vs_comp=False)

    # ---------- INITIALISATION DU JEU ----------
    def start_game(self, human_vs_comp: bool):
        if human_vs_comp:
            humanside = "player1"
        else:
            humanside = None

        self.game = Game(humanside=humanside)
        self.play = Play(self.game, max_depth=5, time_limit=15)
        self.current_player = "player1"
        self.last_turn_start = time.time()
        self.state = "GAME"
        self.game_finished = False
        self.final_message = ""
        self.last_ai_move = ""

    # ---------- OUTILS POUR LE PLATEAU ----------
    def get_pit_rects(self):
        rects: dict[str, pygame.Rect] = {}

        # Player1 bas A–F
        for i, name in enumerate(["A", "B", "C", "D", "E", "F"]):
            x = 260 + i * 110
            rects[name] = pygame.Rect(x, 440, 90, 90)

        # Player2 haut G–L
        for i, name in enumerate(["G", "H", "I", "J", "K", "L"]):
            x = 260 + i * 110
            rects[name] = pygame.Rect(x, 170, 90, 90)

        # Magasins
        rects["1"] = pygame.Rect(980, 200, 90, 260)
        rects["2"] = pygame.Rect(130, 200, 90, 260)

        return rects

    def draw_board(self, message: str = ""):
        self.screen.fill(BGCOLOR)
        pygame.draw.rect(
            self.screen,
            PANEL_COLOR,
            (100, 120, WIDTH - 200, 420),
            border_radius=30,
        )
        pygame.draw.rect(
            self.screen,
            (90, 50, 10),
            (100, 120, WIDTH - 200, 420),
            4,
            border_radius=30,
        )

        rects = self.get_pit_rects()
        board = self.game.state.board  # type: ignore[attr-defined]

        for name, r in rects.items():
            if name in ["1", "2"]:
                color = (220, 180, 40)
                pygame.draw.ellipse(self.screen, color, r)
                pygame.draw.ellipse(self.screen, (255, 255, 255), r, 4)
            else:
                color = (255, 215, 0)
                shadow = r.copy()
                shadow.move_ip(4, 4)
                pygame.draw.ellipse(self.screen, (60, 30, 0), shadow)
                pygame.draw.ellipse(self.screen, color, r)
                pygame.draw.ellipse(self.screen, (200, 160, 0), r, 4)

            seeds = board.get(name, 0)
            for i in range(seeds):
                sx = r.centerx + ((i % 3) - 1) * 14
                sy = r.centery + ((i // 3) - 1) * 14
                pygame.draw.circle(
                    self.screen,
                    (200, 50 + 30 * (i % 3), 50 + 80 * ((i + 1) % 3)),
                    (sx, sy),
                    8,
                )

        label1 = self.font_small.render(
            "PLAYER 2 (HAUT) - G à L - magasin 2",
            True,
            TITLE_COLOR,
        )
        label2 = self.font_small.render(
            "PLAYER 1 (BAS)  - A à F - magasin 1",
            True,
            TITLE_COLOR,
        )
        self.screen.blit(label1, (WIDTH // 2 - label1.get_width() // 2, 130))
        self.screen.blit(label2, (WIDTH // 2 - label2.get_width() // 2, 520))

        # Timer
        cx, cy = WIDTH - 120, 90
        pygame.draw.circle(self.screen, (240, 240, 240), (cx, cy), 40)
        pygame.draw.circle(self.screen, (80, 80, 80), (cx, cy), 40, 3)
        remaining = max(0, int(self.time_limit - (time.time() - self.last_turn_start)))
        ttxt = self.font_small.render(str(remaining), True, (200, 0, 0))
        trect = ttxt.get_rect(center=(cx, cy))
        self.screen.blit(ttxt, trect)

        # Messages
        msg = self.font_small.render(message, True, TITLE_COLOR)
        self.screen.blit(msg, (140, 580))

        if self.last_ai_move:
            ai_txt = self.font_small.render(
                f"Dernier coup IA : {self.last_ai_move}", True, TITLE_COLOR
            )
            self.screen.blit(ai_txt, (140, 550))

        pygame.display.flip()

    # ---------- LOGIQUE DU JEU ----------
    def winner_to_text(self, winner: str) -> str:
        if winner == "DRAW":
            return "ÉGALITÉ"

        if self.selected_mode == "HUMAN_VS_COMP":
            if winner == "HUMAN":
                return "UTILISATEUR"
            else:
                return "COMPUTER"
        else:
            if winner == "HUMAN":
                return "COMPUTER 1 (Player1)"
            else:
                return "COMPUTER 2 (Player2)"

    def screen_game(self):
        if self.game_finished:
            self.draw_board(self.final_message)
            return

        message = ""

        # Temps de tour
        elapsed = time.time() - self.last_turn_start
        if elapsed > self.time_limit:
            self.current_player = (
                "player2" if self.current_player == "player1" else "player1"
            )
            self.last_turn_start = time.time()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            # Clic humain
            if (
                self.selected_mode == "HUMAN_VS_COMP"
                and self.current_player == "player1"
                and event.type == pygame.MOUSEBUTTONDOWN
                and event.button == 1
            ):
                pos = event.pos
                rects = self.get_pit_rects()
                clicked = None
                for name, r in rects.items():
                    if r.collidepoint(pos):
                        clicked = name
                        break

                if clicked and clicked in ["A", "B", "C", "D", "E", "F"]:
                    if self.game.state.board.get(clicked, 0) > 0:  # type: ignore[attr-defined]
                        try:
                            _, extra = self.game.state.doMove("player1", clicked)  # type: ignore[attr-defined]
                            self.game.print_board("HUMAN", clicked)  # type: ignore[call-arg]
                            message = f"Vous jouez {clicked}"
                            if not extra:
                                self.current_player = "player2"
                            self.last_turn_start = time.time()
                        except ValueError:
                            message = "Coup invalide"
                    else:
                        message = "Fosse vide, choisissez une autre."

        # Fin de partie après coup humain
        if self.game.gameOver():  # type: ignore[call-arg]
            winner, score = self.game.findWinner()  # type: ignore[call-arg]
            if winner == "DRAW":
                self.final_message = (
                    "GAME OVER : Égalité parfaite entre les deux magasins."
                )
            else:
                nom = self.winner_to_text(winner)
                self.final_message = (
                    f"GAME OVER : {nom} gagne avec {score} graines de plus dans son magasin."
                )
            self.game_finished = True
            self.draw_board(self.final_message)
            return

        # Tours IA
        if not self.game_finished:
            if self.selected_mode == "HUMAN_VS_COMP" and self.current_player == "player2":
                self.play_one_computer_turn("player2", self.heuristic_p2)
                self.current_player = "player1"
                self.last_turn_start = time.time()
            elif self.selected_mode == "COMP_VS_COMP":
                if self.current_player == "player1":
                    self.play_one_computer_turn("player1", self.heuristic_p1)
                    self.current_player = "player2"
                else:
                    self.play_one_computer_turn("player2", self.heuristic_p2)
                    self.current_player = "player1"
                self.last_turn_start = time.time()

        # Fin de partie après coup IA
        if self.game.gameOver():  # type: ignore[call-arg]
            winner, score = self.game.findWinner()  # type: ignore[call-arg]
            if winner == "DRAW":
                self.final_message = (
                    "GAME OVER : Égalité parfaite entre les deux magasins."
                )
            else:
                nom = "UTILISATEUR" if winner == "HUMAN" else "COMPUTER"
                self.final_message = (
                    f"GAME OVER : {nom} gagne avec {score} graines de plus dans son magasin."
                )
            self.game_finished = True
            self.draw_board(self.final_message)
            return

        # Message en bas
        if self.selected_mode == "HUMAN_VS_COMP":
            if self.current_player == "player1":
                msg_turn = "À vous de jouer (Player1, bas)."
            else:
                msg_turn = "Tour du Computer (Player2, haut)."
        else:
            msg_turn = f"Tour de {self.current_player.upper()} (IA vs IA)."

        full_msg = message + "  |  " + msg_turn if message else msg_turn
        self.draw_board(full_msg)

    def play_one_computer_turn(self, player_side: str, heuristic_name: str):
        """
        Joue un coup d'IA pour player_side ('player1' ou 'player2')
        en utilisant l'heuristique 'simple' ou 'strong'.
        """
        # Configurer COMPUTER / HUMAN dans Game
        if player_side == "player1":
            self.game.playerSide["COMPUTER"] = "player1"  # type: ignore[index]
            self.game.playerSide["HUMAN"] = "player2"     # type: ignore[index]
        else:
            self.game.playerSide["COMPUTER"] = "player2"  # type: ignore[index]
            self.game.playerSide["HUMAN"] = "player1"     # type: ignore[index]

        # Choisir l’heuristique
        self.game.currentHeuristic = heuristic_name  # type: ignore[assignment]

        # Profondeur en plus (optionnel)
        if heuristic_name == "strong":
            self.play.max_depth = 7  # type: ignore[assignment]
        else:
            self.play.max_depth = 4  # type: ignore[assignment]

        pit = self.play.computerTurn()  # type: ignore[call-arg]
        if pit is not None:
            self.last_ai_move = pit
            self.game.print_board("COMPUTER", pit)  # type: ignore[call-arg]

        pygame.time.delay(600)

    # ---------- BOUCLE PRINCIPALE ----------
    def run(self):
        while True:
            self.clock.tick(60)
            if self.state == "TITLE":
                self.screen_title()
            elif self.state == "MODE_SELECT":
                self.screen_mode_select()
            elif self.state == "HEURISTICS":
                self.screen_heuristics()
            elif self.state == "GAME":
                self.screen_game()


if __name__ == "__main__":
    ui = MancalaUI()
    ui.run()
