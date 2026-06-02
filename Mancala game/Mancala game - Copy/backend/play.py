# play.py
# Gestion des tours, Minimax Alpha-Bêta, HUMAIN vs IA et IA vs IA

import copy
import math
import time

from game import Game, MAX, MIN   # MAX = +1 (COMPUTER), MIN = -1 (HUMAN)


class Play:
    def __init__(self, game: Game,
                 max_depth_h1: int = 5,
                 max_depth_h2: int = 7,
                 time_limit: int = 15):
        """
        Classe "contrôleur" qui gère :
        - les tours de jeu,
        - les appels à Minimax (avec ou sans alpha-bêta),
        - la limite de profondeur,
        - la limite de temps par tour.

        Paramètres :
        - game         : instance de Game, qui encapsule MancalaBoard + heuristiques.
        - max_depth_h1 : profondeur maximale quand on utilise l'heuristique simple h1.
        - max_depth_h2 : profondeur maximale quand on utilise l'heuristique forte h2.
                         (en général > max_depth_h1 pour donner plus de puissance à h2)
        - time_limit   : temps maximum en secondes pour réfléchir à un coup
                         (utilisé pour arrêter Minimax si nécessaire). [web:178]
        """
        self.game = game
        self.max_depth_h1 = max_depth_h1
        self.max_depth_h2 = max_depth_h2
        self.time_limit = time_limit

    # ------------------- TOUR HUMAIN (console) -------------------
    def humanTurn(self):
        """
        Version console d'un tour HUMAIN (sans Panda3D).

        Boucle :
        - Affiche les fosses disponibles côté HUMAIN.
        - Demande à l'utilisateur une fosse à jouer.
        - Vérifie que la fosse est sur son côté et non vide.
        - Applique doMove() sur le plateau.
        - Gère le cas où l'humain rejoue (extra_turn).
        - Arrête si le temps limite est dépassé ou si la partie est finie.
        """
        side = self.game.playerSide['HUMAN']  # 'player1' ou 'player2'
        pits = self.game.state.p1_pits if side == 'player1' else self.game.state.p2_pits

        start_time = time.time()
        extra_turn = True

        while extra_turn and not self.game.gameOver():
            
            if time.time() - start_time > self.time_limit:
                print("Temps dépassé pour HUMAN, tour perdu.")
                break

            print("Votre côté :", pits)
            move = input("Choisissez une fosse (lettre) : ").strip().upper()

            if time.time() - start_time > self.time_limit:
                print("Temps dépassé pour HUMAN, tour perdu.")
                break

            
            if move not in pits:
                print("Fosse invalide (pas sur votre côté).")
                continue
            if self.game.state.board.get(move, 0) == 0:
                print("Fosse vide, choisissez une autre.")
                continue

            try:
               
               
                _, extra_turn = self.game.state.doMove(side, move)
                self.game.print_board("HUMAN", move)

                if extra_turn and not self.game.gameOver():
                    print("Vous rejouez (dernière graine dans votre magasin).")
            except ValueError as e:
                print("Erreur:", e)
                extra_turn = True

    # ------------------- TOUR COMPUTER (HUMAIN vs IA) -------------------
    def computerTurn(self):
        """
        Réalise un tour de l'ordinateur (COMPUTER) en mode HUMAIN vs IA.

        Le coup est choisi en appliquant Minimax avec alpha-bêta :
        - MAX = COMPUTER, MIN = HUMAN.
        - evaluate() :
            * h1 si currentHeuristic = "simple",
            * h2 si currentHeuristic = "strong".
        - La profondeur de recherche dépend de l'heuristique :
            * max_depth_h1 pour h1,
            * max_depth_h2 pour h2. [web:112][web:178]
        """
        side = self.game.playerSide['COMPUTER']
        start_time = time.time()

        # Choix de la profondeur de recherche en fonction de l'heuristique actuelle
        if self.game.currentHeuristic == "strong":
            depth = self.max_depth_h2
        else:
            depth = self.max_depth_h1

        # Appel de Minimax avec élagage alpha-bêta (COMPUTER = MAX)
        value, bestPit = MinimaxAlphaBetaPruning(
            game=self.game,
            player=MAX,         # COMPUTER = MAX = +1
            depth=depth,
            alpha=-math.inf,
            beta=math.inf,
            start_time=start_time,
            time_limit=self.time_limit
        )

        if bestPit is None:
            # Aucun coup possible (toutes les fosses vides de son côté)
            print("COMPUTER : aucun coup possible.")
            return None

        print(f"COMPUTER joue la fosse {bestPit}")
        _, extra_turn = self.game.state.doMove(side, bestPit)
        self.game.print_board("COMPUTER", bestPit)

        if extra_turn and not self.game.gameOver():
            print("COMPUTER rejoue (dernière graine dans son magasin).")
        return bestPit

    # ------------------- TOUR IA vs IA (IA1 ou IA2) -------------------
    def aiVsAiTurn(self, side: str):
        """
        Joue un coup pour IA1 ou IA2 en mode IA vs IA.

        Paramètre :
        - side :
            'player1' -> IA1 (utilise game.ia1_heuristic : "simple" ou "strong")
            'player2' -> IA2 (utilise game.ia2_heuristic)

        Cette fonction :
        - appelle MinimaxAIvsAI (version negamax avec alpha-bêta),
        - applique le coup trouvé sur le plateau,
        - affiche l'état du jeu en console,
        - indique si l'IA rejoue. [web:126]
        """
        start_time = time.time()

        value, bestPit = MinimaxAIvsAI(
            game=self.game,
            side=side,
            depth=self.max_depth_h1,   # profondeur de base (bonus interne pour "strong")
            alpha=-math.inf,
            beta=math.inf,
            start_time=start_time,
            time_limit=self.time_limit
        )

        if bestPit is None:
            print(f"{side} : aucun coup possible.")
            return None

        print(f"{side} joue la fosse {bestPit}")
        _, extra_turn = self.game.state.doMove(side, bestPit)
        self.game.print_board(side, bestPit)

        if extra_turn and not self.game.gameOver():
            print(f"{side} rejoue (dernière graine dans son magasin).")
        return bestPit


# ------------------- MINIMAX ALPHA-BETA (HUMAIN vs IA) -------------------
def MinimaxAlphaBetaPruning(game: Game, player: int, depth: int,
                            alpha: float, beta: float,
                            start_time: float, time_limit: float):
    """
    Implémentation de Minimax avec élagage alpha-bêta pour HUMAIN vs COMPUTER.

    Paramètres :
    - game       : instance de Game (contient l'état + évaluations).
    - player     : MAX (=1, COMPUTER) ou MIN (=-1, HUMAN).
    - depth      : profondeur de recherche restante.
    - alpha, beta: bornes d'élagage (alpha pour MAX, beta pour MIN).
    - start_time : début du calcul du coup.
    - time_limit : limite de temps pour ce coup, en secondes.

    Conditions d'arrêt :
    - game.gameOver() : position terminale (fin de partie),
    - depth == 1      : profondeur maximale atteinte,
    - temps écoulé > time_limit.
    Dans ce cas, on évalue la position avec game.evaluate()
    (h1 ou h2 selon currentHeuristic). [web:137][web:126]
    """
    if game.gameOver() or depth == 1 or (time.time() - start_time > time_limit):
        bestValue = game.evaluate()  # h1 ou h2, toujours du point de vue de COMPUTER
        return bestValue, None

    # Noeud MAX : c'est au joueur COMPUTER de jouer
    if player == MAX:
        bestValue = -math.inf
        bestPit = None
        current_side = game.playerSide['COMPUTER']   # 'player1' ou 'player2'

        # Génération de tous les coups possibles pour COMPUTER
        for pit in game.state.possibleMoves(current_side):
            # On travaille sur une copie profonde de "game" pour ne pas modifier l'original.
            child_game = copy.deepcopy(game)
            # On applique le coup sur l'enfant
            child_game.state.doMove(current_side, pit)

            # On appelle récursivement Minimax pour le joueur MIN (HUMAN)
            value, _ = MinimaxAlphaBetaPruning(
                child_game, MIN, depth - 1, alpha, beta, start_time, time_limit
            )

            # Mise à jour de la meilleure valeur et du meilleur coup
            if value > bestValue:
                bestValue = value
                bestPit = pit

            # Test de coupure beta : si la valeur est déjà >= beta,
            # MIN ne laissera jamais MAX atteindre une valeur aussi bonne.
            if bestValue >= beta:
                break

            # Mise à jour d'alpha (borne inférieure que MAX sait pouvoir atteindre)
            if bestValue > alpha:
                alpha = bestValue

        return bestValue, bestPit

    # Noeud MIN : c'est au joueur HUMAN de jouer
    else:
        bestValue = math.inf
        bestPit = None
        current_side = game.playerSide['HUMAN']     # 'player1' ou 'player2'

        # Génération de tous les coups possibles pour HUMAN
        for pit in game.state.possibleMoves(current_side):
            child_game = copy.deepcopy(game)
            child_game.state.doMove(current_side, pit)

            # Appel récursif pour MAX
            value, _ = MinimaxAlphaBetaPruning(
                child_game, MAX, depth - 1, alpha, beta, start_time, time_limit
            )

            if value < bestValue:
                bestValue = value
                bestPit = pit

            # Test de coupure alpha : si la valeur <= alpha,
            # MAX a déjà un choix meilleur ailleurs.
            if bestValue <= alpha:
                break

            # Mise à jour de beta (borne supérieure que MIN sait pouvoir forcer)
            if bestValue < beta:
                beta = bestValue

        return bestValue, bestPit


# ------------------- MINIMAX IA vs IA (avec avantage pour h2) -------------------
def MinimaxAIvsAI(game: Game, side: str, depth: int,
                  alpha: float, beta: float,
                  start_time: float, time_limit: float):
    """
    Version spéciale de Minimax (forme negamax) pour le mode IA vs IA.

    Paramètres :
    - side : 'player1' ou 'player2' (côté qui joue à ce noeud).
             * 'player1' = IA1, utilise game.ia1_heuristic
             * 'player2' = IA2, utilise game.ia2_heuristic
    - depth      : profondeur de base. Si le côté courant utilise "strong",
                   on lui donne un bonus de profondeur (depth_effective = depth + 1). [web:126]
    - alpha, beta: bornes de negamax (on inverse signes et bornes à la récursion).
    - start_time, time_limit : contrôle du temps.

    Idee negamax :
      valeur(position, side) = max_{coups} ( - valeur(position', other_side) )
    Ce qui permet d'avoir un seul cas (MAX) en inversant les signes. [web:137]
    """
    # Déterminer l'heuristique utilisée par le côté qui joue (IA1 ou IA2)
    if side == 'player1':
        current_h = game.ia1_heuristic
    else:
        current_h = game.ia2_heuristic

    # Avantage : si ce côté utilise l'heuristique forte "strong" (h2),
    # on augmente sa profondeur effective de recherche.
    if current_h == "strong" and depth > 1:
        depth_effective = depth + 1
    else:
        depth_effective = depth

    # Conditions d'arrêt identiques à la version HUMAIN vs IA,
    # mais on utilise evaluate_for_side(side) pour tenir compte de l'heuristique
    # spécifique à IA1 ou IA2.
    if game.gameOver() or depth_effective == 1 or (time.time() - start_time > time_limit):
        bestValue = game.evaluate_for_side(side)
        return bestValue, None

    bestValue = -math.inf
    bestPit = None

    # On parcourt tous les coups possibles pour ce côté
    for pit in game.state.possibleMoves(side):
        child_game = copy.deepcopy(game)
        child_game.state.doMove(side, pit)

        # Côté suivant (adversaire)
        other_side = 'player2' if side == 'player1' else 'player1'

        # Appel récursif negamax :
        # - on inverse le rôle des bornes alpha/beta (symétrie),
        # - on inversera le signe de la valeur retournée.
        value, _ = MinimaxAIvsAI(
            child_game,
            side=other_side,
            depth=depth_effective - 1,
            alpha=-beta,
            beta=-alpha,
            start_time=start_time,
            time_limit=time_limit
        )
        value = -value  # negamax : on renverse le signe

        # Mise à jour de la meilleure valeur et du meilleur coup
        if value > bestValue:
            bestValue = value
            bestPit = pit

        # Mise à jour d'alpha pour ce point de vue
        if bestValue > alpha:
            alpha = bestValue
        # Test de coupure si alpha dépasse beta
        if alpha >= beta:
            break

    return bestValue, bestPit
