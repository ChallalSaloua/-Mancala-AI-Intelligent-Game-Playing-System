# main.py

from game import Game
from play import Play

if __name__ == "__main__":
    mode = input(
        "Choisissez le mode :\n"
        "  1) HUMAIN vs COMPUTER\n"
        "  2) COMPUTER vs COMPUTER (IA1 vs IA2)\n"
        "Votre choix (1/2) : "
    ).strip()

    # ------------------ MODE 1 : HUMAIN vs COMPUTER ------------------
    if mode == "1":
        human_side = input("Voulez-vous être player1 (A–F) ou player2 (G–L) ? (1/2) : ").strip()
        human_side = 'player1' if human_side == '1' else 'player2'

        game = Game(humanside=human_side)        # -> param 'humanside'
        play = Play(game, max_depth=5, time_limit=15)

        # choix heuristique pour l'IA
        h = input("Heuristique IA (s = simple, f = forte) ? (s/f) : ").strip().lower()
        game.currentHeuristic = "strong" if h == "f" else "simple"

        current_player = 'HUMAN'   # on décide que HUMAN commence

        while not game.gameOver():
            print("\n--------------- Nouveau tour ---------------")
            if current_player == 'HUMAN':
                print("Tour de l'utilisateur (HUMAN)")
                play.humanTurn()
                current_player = 'COMPUTER'
            else:
                print("Tour de l'ordinateur (COMPUTER)")
                play.computerTurn()
                current_player = 'HUMAN'

        winner, score = game.findWinner()
        print("\n=== Fin de partie ===")
        print("Board final :", game.state.board)
        print("Gagnant :", winner, "avec un avantage de", score, "graines.")

    # ------------------ MODE 2 : COMPUTER vs COMPUTER ------------------
    else:
        print("Mode COMPUTER vs COMPUTER (IA1 vs IA2)")
        # IA1 = player1, IA2 = player2
        game = Game(humanside=None)
        play = Play(game, max_depth=5, time_limit=15)

        h1 = input("Heuristique IA1 (player1) ? simple (s) / forte (f) : ").strip().lower()
        h2 = input("Heuristique IA2 (player2) ? simple (s) / forte (f) : ").strip().lower()
        game.ia1_heuristic = "strong" if h1 == "f" else "simple"
        game.ia2_heuristic = "strong" if h2 == "f" else "simple"

        current_side = 'player1'   # IA1 commence

        while not game.gameOver():
            print("\n--------------- Nouveau tour ---------------")
            if current_side == 'player1':
                print("Tour IA1 (player1)")
            else:
                print("Tour IA2 (player2)")

            play.aiVsAiTurn(current_side)
            current_side = 'player2' if current_side == 'player1' else 'player1'

        winner, score = game.findWinner()
        print("\n=== Fin de partie IA vs IA ===")
        print("Board final :", game.state.board)
        print("Gagnant :", winner, "avec un avantage de", score, "graines.")
