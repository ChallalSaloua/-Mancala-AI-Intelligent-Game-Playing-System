# mancala_board.py

class MancalaBoard:
    def __init__(self):
        """
        Représente uniquement le PLATEAU de Mancala (Kalah) :
        - 12 fosses numérotées par des lettres :
              * Player1 : A, B, C, D, E, F  (rangée du bas dans ton plateau)
              * Player2 : G, H, I, J, K, L  (rangée du haut)
        - 2 magasins :
              * '1' : magasin de Player1
              * '2' : magasin de Player2
        - Configuration initiale : 4 graines dans chaque fosse, magasins vides.
        """
        # Dictionnaire "case -> nombre de graines"
        self.board = {
            'A': 4, 'B': 4, 'C': 4, 'D': 4, 'E': 4, 'F': 4, '1': 0,
            'G': 4, 'H': 4, 'I': 4, 'J': 4, 'K': 4, 'L': 4, '2': 0
        }

        # Tuple des fosses appartenant à chaque joueur.
        # Ces tuples servent à :
        #   - vérifier si un coup est légal,
        #   - tester la fin de partie (toutes les fosses d’un côté vides),
        #   - parcourir les fosses d’un côté.
        self.p1_pits = ('A', 'B', 'C', 'D', 'E', 'F')
        self.p2_pits = ('G', 'H', 'I', 'J', 'K', 'L')

        # Dictionnaire qui donne, pour chaque fosse, la fosse opposée
        # (symétrique de l’autre côté du plateau).
        # Ce mapping est utilisé pour la règle de CAPTURE :
        #   si la dernière graine tombe dans une fosse vide de ton côté
        #   et que la fosse opposée contient des graines, tu captures tout.
        self.opposite = {
            'A': 'L', 'B': 'K', 'C': 'J', 'D': 'I', 'E': 'H', 'F': 'G',
            'G': 'F', 'H': 'E', 'I': 'D', 'J': 'C', 'K': 'B', 'L': 'A'
        }

        # Dictionnaire "case -> case suivante" pour parcourir le plateau
        # en sens ANTIHORAIRE (la direction de distribution des graines).
        #
        # Remarque importante :
        #   - On passe par son propre magasin (1 pour player1, 2 pour player2),
        #   - On passe aussi par le magasin adverse dans cette structure,
        #     MAIS on le saute dans doMove() au moment de déposer une graine.
        #     (règle Kalah : tu ne mets jamais de graine dans le magasin adverse). [web:60][web:66]
        self.next_pit = {
            'A': 'B', 'B': 'C', 'C': 'D', 'D': 'E', 'E': 'F', 'F': '1', '1': 'G',
            'G': 'H', 'H': 'I', 'I': 'J', 'J': 'K', 'K': 'L', 'L': '2', '2': 'A'
        }

    # ------------------- Coups possibles -------------------

    def possibleMoves(self, player: str):
        """
        Renvoie la liste des fosses encore jouables pour un joueur donné.

        Paramètre :
        - player : 'player1' ou 'player2'

        Règle :
        - player1 ne peut jouer que sur A–F,
        - player2 ne peut jouer que sur G–L,
        - et uniquement les fosses qui contiennent AU MOINS 1 graine.

        Cette fonction est utilisée par Minimax pour générer les successeurs :
        on parcourt tous les coups possibles depuis une position. [web:112][web:181]
        """
        if player == 'player1':
            pits = self.p1_pits
        else:
            pits = self.p2_pits

        # On filtre les fosses qui ne sont pas vides.
        return [p for p in pits if self.board[p] > 0]

    # ------------------- Exécution d'un coup -------------------

    def doMove(self, player: str, pit: str):
        """
        Exécute un coup complet pour 'player' en jouant la fosse 'pit',
        et met à jour le plateau self.board EN PLACE.

        Paramètres :
        - player : 'player1' ou 'player2'
        - pit    : lettre de la fosse choisie ('A'..'F' ou 'G'..'L')

        Règles implémentées (Kalah standard) : [web:60][web:49]
        1. Le joueur doit jouer une fosse de SON côté :
           - player1 : A–F
           - player2 : G–L
        2. Il est interdit de jouer une fosse vide.
        3. Il ramasse toutes les graines de la fosse choisie.
        4. Il distribue ces graines une par une dans les cases suivantes
           en suivant self.next_pit, en sens antihoraire.
        5. Il NE DÉPOSE JAMAIS dans le magasin adverse (on saute cette case).
        6. Si la DERNIÈRE graine :
           - tombe dans SON magasin -> il rejoue (extra_turn = True),
           - tombe dans une fosse vide de son côté et que la fosse opposée
             contient des graines -> capture (il prend sa graine + celles de
             la fosse opposée et les met dans son magasin).
        7. Après le coup, si toutes les fosses d’un joueur sont vides,
           l’autre ramasse TOUTES ses graines restantes dans son magasin
           (règle de fin de partie). [web:60]

        Retour :
        - last_pit  : la dernière case où une graine a été déposée
        - extra_turn: booléen, True si le joueur rejoue, False sinon
        """
        # --- 1) Vérifier que la fosse appartient bien au joueur ---
        if player == 'player1':
            if pit not in self.p1_pits:
                raise ValueError("Player1 ne peut jouer que sur les fosses A–F")
            my_pits = self.p1_pits   # fosses appartenant au joueur courant
            my_store = '1'           # magasin du joueur courant
            opp_store = '2'          # magasin de l'adversaire
        else:
            if pit not in self.p2_pits:
                raise ValueError("Player2 ne peut jouer que sur les fosses G–L")
            my_pits = self.p2_pits
            my_store = '2'
            opp_store = '1'

        # Nombre de graines dans la fosse choisie
        seeds = self.board.get(pit, 0)
        if seeds <= 0:
            # On ne peut pas jouer une fosse vide.
            raise ValueError("Fosse vide, coup impossible")

        # --- 2) Ramasser toutes les graines de la fosse choisie ---
        self.board[pit] = 0

        # --- 3) Distribuer les graines une par une ---
        current = pit
        while seeds > 0:
            # passer à la case suivante dans le cycle
            current = self.next_pit[current]

            # Règle Kalah : ne jamais déposer dans le magasin adverse. [web:66][web:155]
            if current == opp_store:
                # on saute directement à la case suivante
                current = self.next_pit[current]

            # On dépose une graine dans la case "current"
            self.board[current] += 1
            seeds -= 1

        # À la fin de la distribution, current = case de la DERNIÈRE graine
        last_pit = current
        extra_turn = False  # valeur par défaut

        # --- 4) Tester les règles spéciales en fonction de last_pit ---

        # Cas 1 : la dernière graine termine dans le magasin du joueur -> il rejoue.
        if last_pit == my_store:
            extra_turn = True

        # Cas 2 : la dernière graine termine dans une fosse VIDE de son côté -> capture.
        # On vérifie :
        #   - que last_pit est bien une de SES fosses,
        #   - que cette fosse contient maintenant EXACTEMENT 1 graine (la graine qu'on vient de poser).
        elif last_pit in my_pits and self.board[last_pit] == 1:
            opp_pit = self.opposite[last_pit]  # fosse opposée
            # Si la fosse opposée contient des graines, on capture.
            if self.board[opp_pit] > 0:
                captured = self.board[opp_pit] + self.board[last_pit]
                # on vide les deux fosses
                self.board[opp_pit] = 0
                self.board[last_pit] = 0
                # on ajoute tout dans le magasin du joueur courant
                self.board[my_store] += captured

        # --- 5) Règle de fin de partie (collecte finale) ---
        # Si, après ce coup, toutes les fosses de Player1 sont vides,
        # Player2 ramasse toutes ses graines restantes dans son magasin '2', et vice versa. [web:60][web:181]
        if all(self.board[p] == 0 for p in self.p1_pits):
            # toutes les fosses de player1 sont vides -> player2 ramasse
            reste = sum(self.board[p] for p in self.p2_pits)
            self.board['2'] += reste
            for p in self.p2_pits:
                self.board[p] = 0

        elif all(self.board[p] == 0 for p in self.p2_pits):
            # toutes les fosses de player2 sont vides -> player1 ramasse
            reste = sum(self.board[p] for p in self.p1_pits)
            self.board['1'] += reste
            for p in self.p1_pits:
                self.board[p] = 0

        return last_pit, extra_turn
