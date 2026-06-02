from mancala_board import MancalaBoard

# Constantes pour Minimax (cf. énoncé du projet) :
# MAX : joueur qui maximise la fonction d'évaluation (COMPUTER).
# MIN : joueur qui minimise (HUMAN).
MAX = 1   # COMPUTER
MIN = -1  # HUMAN


class Game:
    def __init__(self, humanside=None):
        """
        Représente l'état logique du jeu Mancala (Kalah) pour l'algorithme Minimax.

        - self.state : instance de MancalaBoard, qui contient le plateau (graines dans chaque fosse + magasins).
        - humanside :
            * 'player1'  -> l'utilisateur contrôle le côté A–F (magasin '1').
            * 'player2'  -> l'utilisateur contrôle le côté G–L (magasin '2').
            * None       -> mode IA vs IA (aucun humain), on fixe par convention :
                           HUMAN = player1, COMPUTER = player2.
        """
        # Plateau avec 12 fosses + 2 magasins, et règles de distribution/capture implémentées dans MancalaBoard.
        self.state = MancalaBoard()

        # Association logique HUMAN / COMPUTER -> player1 / player2
        if humanside is None:
            # Mode IA vs IA : convention fixe
            self.playerSide = {
                'HUMAN': 'player1',
                'COMPUTER': 'player2'
            }
        else:
            if humanside == 'player1':
                self.playerSide = {
                    'HUMAN': 'player1',
                    'COMPUTER': 'player2'
                }
            else:
                self.playerSide = {
                    'HUMAN': 'player2',
                    'COMPUTER': 'player1'
                }

        # Heuristique utilisée par evaluate() en mode HUMAIN vs IA :
        # "simple" = h1 (équation (1) du projet, basée uniquement sur les magasins),
        # "strong" = h2 (heuristique avancée que tu ajoutes).
        self.currentHeuristic = "simple"

        # Heuristiques utilisées en mode IA vs IA :
        # IA1 = player1, IA2 = player2, chacune peut utiliser "simple" ou "strong".
        self.ia1_heuristic = "simple"
        self.ia2_heuristic = "simple"

    # ---------- Choix des heuristiques IA1 / IA2 (IA vs IA) ----------

    def set_ia1_heuristic(self, h: str):
        """
        Fixe l'heuristique de l'IA1 (côté player1) pour le mode IA vs IA.
        h doit être "simple" (h1) ou "strong" (h2).
        """
        if h not in ("simple", "strong"):
            raise ValueError("Heuristique inconnue pour IA1 (simple/strong)")
        self.ia1_heuristic = h

    def set_ia2_heuristic(self, h: str):
        """
        Fixe l'heuristique de l'IA2 (côté player2) pour le mode IA vs IA.
        h doit être "simple" (h1) ou "strong" (h2).
        """
        if h not in ("simple", "strong"):
            raise ValueError("Heuristique inconnue pour IA2 (simple/strong)")
        self.ia2_heuristic = h

    # ---------- Fin de partie / gagnant ----------

    def gameOver(self) -> bool:
        """
        Renvoie True si la partie est terminée.

        La fin de partie a lieu quand toutes les fosses d'un des joueurs sont vides.
        À ce moment, MancalaBoard.doMove ramasse automatiquement les graines restantes
        de l'autre côté et les place dans le magasin correspondant. [web:60][web:180]
        """
        p1empty = all(self.state.board[p] == 0 for p in self.state.p1_pits)
        p2empty = all(self.state.board[p] == 0 for p in self.state.p2_pits)
        return p1empty or p2empty

    def findWinner(self):
        """
        Calcule le gagnant à la fin de la partie.

        Compare le contenu des deux magasins, puis renvoie :
          - 'HUMAN'     si le magasin du joueur HUMAIN est plus rempli,
          - 'COMPUTER'  si le magasin du joueur COMPUTER est plus rempli,
          - 'DRAW'      s'ils contiennent le même nombre de graines.

        Le score retourné est la différence absolue de graines entre les deux magasins.
        """
        humanside = self.playerSide['HUMAN']
        compside  = self.playerSide['COMPUTER']

        # Magasin associé à chaque côté : player1 -> '1', player2 -> '2'.
        human_store = '1' if humanside == 'player1' else '2'
        comp_store  = '1' if compside  == 'player1' else '2'

        human_score = self.state.board[human_store]
        comp_score  = self.state.board[comp_store]

        if human_score > comp_score:
            return 'HUMAN', human_score - comp_score
        elif comp_score > human_score:
            return 'COMPUTER', comp_score - human_score
        else:
            return 'DRAW', 0

    # ---------- Heuristique h1 = projet (équation 1) ----------

    def heuristic_simple(self) -> int:
        """
        h1 : heuristique "simple" demandée dans le projet (équation (1)).

        Elle ne dépend QUE des magasins des deux joueurs :
            value(n) = nbSeedsStore(playerSide[COMPUTER])
                       - nbSeedsStore(playerSide[HUMAN])

        Autrement dit, la valeur est positive si COMPUTER mène en nombre de graines
        dans son magasin, négative s'il est en retard. [web:112][web:125]
        """
        compside  = self.playerSide['COMPUTER']
        humanside = self.playerSide['HUMAN']

        comp_store  = '1' if compside  == 'player1' else '2'
        human_store = '1' if humanside == 'player1' else '2'

        return self.state.board[comp_store] - self.state.board[human_store]

    # ---------- Heuristique h2 = forte, très avantageuse ----------

    def heuristic_strong(self) -> int:
        """
        h2 : heuristique avancée (plus "forte") vue du point de vue de COMPUTER (MAX).

        Idée : on enrichit h1 avec plusieurs termes stratégiques inspirés des heuristiques
        classiques pour Mancala/Kalah : [web:120][web:177]

        - Différence de graines dans les magasins (score direct).
        - Différence de graines sur les fosses (contrôle du plateau).
        - Mobilité : nombre de coups encore possibles.
        - Opportunités de tour supplémentaire (cases proches du magasin).
        - Opportunités de capture sur le côté de COMPUTER et du côté adverse.

        Les coefficients (15, 4, 3, 2, 1, ...) pondèrent l'importance de chaque terme.
        """
        board = self.state.board
        max_side = self.playerSide['COMPUTER']   # 'player1' ou 'player2'

        # Sélection des fosses et magasins correspondant au "MAX" (COMPUTER)
        if max_side == 'player1':
            my_pits  = self.state.p1_pits
            op_pits  = self.state.p2_pits
            my_store, op_store = '1', '2'
        else:
            my_pits  = self.state.p2_pits
            op_pits  = self.state.p1_pits
            my_store, op_store = '2', '1'

        # 1) Différence magasins (score direct, très important)
        store_diff = board[my_store] - board[op_store]

        # 2) Différence de graines sur les fosses (contrôle matériel du plateau)
        my_side = sum(board[p] for p in my_pits)
        op_side = sum(board[p] for p in op_pits)
        side_diff = my_side - op_side

        # 3) Mobilité (nombre de fosses jouables de chaque côté)
        my_moves = sum(1 for p in my_pits if board[p] > 0)
        op_moves = sum(1 for p in op_pits if board[p] > 0)
        mobility = my_moves - op_moves

        # 4) Opportunités de tour supplémentaire pour COMPUTER :
        # on approxime : fosses proches du magasin sont favorables (peu de cases à parcourir).
        extra_turn_chances = 0
        # pour player1, fosses proches du magasin : E, F ; pour player2 : G, H
        if max_side == 'player1':
            near_store_pits = ('E', 'F')
        else:
            near_store_pits = ('G', 'H')
        for p in near_store_pits:
            if board[p] >= 1:
                extra_turn_chances += 1

        # 5) Opportunités de capture (positionnelles, approximatives)
        capture_chances_me = 0
        capture_chances_opp = 0
        opp_map = self.state.opposite

        # a) Cases où une capture semble possible pour COMPUTER :
        #    -> fosses vides de son côté avec une fosse opposée non vide.
        for p in my_pits:
            if board[p] == 0:
                opp_p = opp_map[p]
                if board[opp_p] > 0:
                    capture_chances_me += 1

        # b) Idem pour l'adversaire (on pénalise ces positions)
        for p in op_pits:
            if board[p] == 0:
                opp_p = opp_map[p]
                if board[opp_p] > 0:
                    capture_chances_opp += 1

        # Combinaison linéaire des différents termes.
        return (
            15 * store_diff +         # favoriser fortement un avantage au score
            4  * side_diff +          # favoriser plus de graines sur son côté
            1  * mobility +           # plus de coups possibles
            2  * extra_turn_chances + # plus d'opportunités de rejouer
            3  * capture_chances_me - # favoriser des captures potentielles
            2  * capture_chances_opp  # pénaliser les captures pour l'adversaire
        )

    # ---------- Fonction d’évaluation (HUMAIN vs IA) ----------

    def evaluate(self) -> int:
        """
        Fonction d’évaluation principale utilisée par Minimax Alpha‑Bêta
        en mode HUMAIN vs IA (COMPUTER = MAX = +1). [web:126][web:178]

        Selon self.currentHeuristic, on utilise :
          - "simple" : h1 (équation (1) du projet),
          - "strong" : h2 (heuristique avancée).
        La valeur retournée est toujours vue du point de vue de COMPUTER :
        > 0 : position favorable à COMPUTER, < 0 : favorable à HUMAN.
        """
        if self.currentHeuristic == "strong":
            return self.heuristic_strong()
        else:
            return self.heuristic_simple()

    # ---------- Évaluation pour IA vs IA ----------

    def evaluate_for_side(self, side: str) -> int:
        """
        Fonction d'évaluation utilisée uniquement en mode IA vs IA.

        - side = 'player1' -> on évalue la position avec l'heuristique de IA1.
        - side = 'player2' -> on évalue la position avec l'heuristique de IA2.

        Techniquement, on change temporairement self.currentHeuristic pour réutiliser
        evaluate(), puis on restaure l'ancienne valeur. La valeur renvoyée reste
        interprétée comme "vue du point de vue de COMPUTER". [web:126]
        """
        if side == 'player1':
            h = self.ia1_heuristic
        else:
            h = self.ia2_heuristic

        old = self.currentHeuristic
        self.currentHeuristic = h
        v = self.evaluate()
        self.currentHeuristic = old
        return v

    # ---------- Affichage console (debug) ----------

    def print_board(self, last_move_player: str, last_move_pit: str):
        """
        Affiche dans le terminal l'état courant du plateau.
        Utile pour débugger la logique sans l'interface Panda3D.
        """
        b = self.state.board
        print("--------------------------------------------------")
        print(f"Coup joué par {last_move_player} sur la fosse {last_move_pit}")
        print(f"Magasin 1 (Player1) = {b['1']}  |  Magasin 2 (Player2) = {b['2']}")
        print("Fosses Player1 (A–F) : ", end="")
        print(" ".join(f"{p}:{b[p]}" for p in self.state.p1_pits))
        print("Fosses Player2 (G–L) : ", end="")
        print(" ".join(f"{p}:{b[p]}" for p in self.state.p2_pits))
        print("--------------------------------------------------")
