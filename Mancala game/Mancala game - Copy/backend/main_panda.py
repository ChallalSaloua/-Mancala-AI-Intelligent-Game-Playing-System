# mancala_title_app.py
from direct.showbase.ShowBase import ShowBase
from direct.gui.DirectGui import DirectLabel, DirectButton
from direct.gui.OnscreenImage import OnscreenImage
from direct.interval.IntervalGlobal import Sequence, Wait, Func, LerpFunc, Parallel
from direct.filter.CommonFilters import CommonFilters
from panda3d.core import TransparencyAttrib, TextNode, WindowProperties
from direct.gui import DirectGuiGlobals as DGG
from direct.task import Task
import time

from game import Game
from play import Play


class MancalaTitleApp(ShowBase):
    def __init__(self):
        ShowBase.__init__(self)

        # -------- Fenêtre --------
        props = WindowProperties()
        props.setSize(1280, 720)
        props.setOrigin(50, 50)
        self.win.requestProperties(props)

        # --- variables générales ---
        self.font_title = None
        self.font_dialog_title = None
        self.font_dialog_buttons = None
        self.widgets_screen1 = []
        self.widgets_screen2 = []
        self.ia1_heuristic = None

        # Pointeurs
        self.h1_img = self.h1_simple = None
        self.h2_img = self.h2_strong = None
        self.h3_img = self.h3_simple = None
        self.h4_img = self.h4_strong = None

        # --- variables plateau ---
        self.current_game = None
        self.current_play = None
        self.current_player = None
        self.time_limit = 15
        self.turn_start_time = None
        self.timer_label = None
        self.turn_label = None
        self.board_bg = None
        self.holes_buttons = {}
        self.seed_images = {}
        self.pit_centers = {}
        self.store1_label = None
        self.store2_label = None
        self.game_finished = False
        self.final_message_label = None

        # magasins (images de graines)
        self.store_centers = {}
        self.store_seed_images = {'1': [], '2': []}

        # modes
        self.mode = "HUMAN_VS_IA"     # ou "IA_VS_IA"
        self.current_ai_side = None   # 'player1' ou 'player2' en IA vs IA

        # --- chargement des polices ---
        self.font_title = loader.loadFont("Bloody Stump.ttf")
        self.font_dialog_title = loader.loadFont("DSSnowfall.ttf")
        self.font_dialog_buttons = self.font_dialog_title

        # -------- Écran 1 : fond + titre ----------
        ratio = self.getAspectRatio()
        self.bg = OnscreenImage(
            image="p1.gif",
            pos=(0, 0, 0),
            scale=(ratio * 1.2, 1, 1.2),
            parent=render2d
        )
        self.bg.setTransparency(TransparencyAttrib.M_alpha)

        self.title = DirectLabel(
            text="MANCALA",
            text_fg=(0.0, 0.10, 0.0, 1),
            text_align=TextNode.ACenter,
            text_scale=0.40,
            text_font=self.font_title,
            frameColor=(0, 0, 0, 0),
            pos=(0, 0, 0.25)
        )
        self.title.setScale(0.12)

        self.filters = CommonFilters(self.win, self.cam)
        self.filters.setBloom(
            blend=(0.3, 0.3, 0.3, 1),
            mintrigger=0.7,
            desat=0.0,
            intensity=1.2,
            size="small"
        )

        self.zoom_seq = Sequence(
            self.title.scaleInterval(5.0, 0.9, startScale=0.12),
            Wait(1.0),
            Func(self.show_play_button)
        )
        self.zoom_seq.start()

    # ---------- ÉCRAN 1 ----------
    def show_play_button(self):
        self.widgets_screen1.extend([self.bg, self.title])

        self.play_button = DirectButton(
            text="JOUER",
            text_font=self.font_title,
            text_fg=(1, 1, 1, 1),
            text_scale=0.16,
            text_align=TextNode.ACenter,
            frameColor=(0, 0, 0, 0),
            relief=DGG.FLAT,
            pos=(0, 0, -0.75),
            command=self.start_transition
        )
        self.widgets_screen1.append(self.play_button)

    def start_transition(self):
        def fade_out(t):
            alpha = 1.0 - t
            for w in self.widgets_screen1:
                w.setColorScale(1, 1, 1, alpha)

        self.fade_seq = Sequence(
            LerpFunc(fade_out, fromData=0.0, toData=1.0, duration=0.7),
            Func(self.setup_screen2),
            Func(self.play_screen2_intro)
        )
        self.fade_seq.start()

    # ---------- ÉCRAN 2 ----------
    def setup_screen2(self):
        for w in self.widgets_screen1:
            w.hide()

        self.widgets_screen2 = []
        ratio = self.getAspectRatio()

        self.bg2 = OnscreenImage(
            image="p2.jpg",
            pos=(0, 0, 0),
            scale=(ratio * 1.2, 1, 1.2),
            parent=render2d
        )
        self.bg2.setTransparency(TransparencyAttrib.M_alpha)
        self.widgets_screen2.append(self.bg2)

        self.title_img = OnscreenImage(
            image="titre.png",
            pos=(0, 0, 0.95),
            scale=(0.6, 1, 0.12)
        )
        self.title_img.setTransparency(TransparencyAttrib.M_alpha)
        self.widgets_screen2.append(self.title_img)

        self.welcome_label = DirectLabel(
            text="Bienvenue a MANCALA",
            text_font=self.font_title,
            text_fg=(1, 1, 1, 1),
            text_scale=0.70,
            text_align=TextNode.ACenter,
            frameColor=(0, 0, 0, 0),
            pos=(0, 0, 0.70)
        )
        self.widgets_screen2.append(self.welcome_label)

        self.choose_img = OnscreenImage(
            image="img3.png",
            pos=(0, 0, 0.20),
            scale=(1.10, 1, 0.25)
        )
        self.choose_img.setTransparency(TransparencyAttrib.M_alpha)
        self.widgets_screen2.append(self.choose_img)

        self.choose_label = DirectLabel(
            text="Choisissez une méthode ",
            text_font=self.font_dialog_title,
            text_fg=(1, 1, 1, 1),
            text_scale=0.17,
            text_align=TextNode.ACenter,
            frameColor=(0, 0, 0, 0),
            pos=(0, 0, 0.13)
        )
        self.widgets_screen2.append(self.choose_label)

        self.user_vs_comp_img = OnscreenImage(
            image="img3.png",
            pos=(0, 0, -0.40),
            scale=(1.10, 1, 0.25)
        )
        self.user_vs_comp_img.setTransparency(TransparencyAttrib.M_alpha)
        self.widgets_screen2.append(self.user_vs_comp_img)

        self.user_vs_comp_button = DirectButton(
            text="Utilisateur vs Computer",
            text_font=self.font_dialog_title,
            text_fg=(1, 1, 1, 1),
            text_scale=0.17,
            text_align=TextNode.ACenter,
            frameColor=(0, 0, 0, 0),
            relief=DGG.FLAT,
            pos=(0, 0, -0.48),
            command=self.on_user_vs_comp_clicked
        )
        self.widgets_screen2.append(self.user_vs_comp_button)

        self.comp_vs_comp_img = OnscreenImage(
            image="img3.png",
            pos=(0, 0, -0.70),
            scale=(1.10, 1, 0.25)
        )
        self.comp_vs_comp_img.setTransparency(TransparencyAttrib.M_alpha)
        self.widgets_screen2.append(self.comp_vs_comp_img)

        self.comp_vs_comp_button = DirectButton(
            text="Computer vs Computer",
            text_font=self.font_dialog_title,
            text_fg=(1, 1, 1, 1),
            text_scale=0.17,
            text_align=TextNode.ACenter,
            frameColor=(0, 0, 0, 0),
            relief=DGG.FLAT,
            pos=(0, 0, -0.78),
            command=self.on_comp_vs_comp_clicked
        )
        self.widgets_screen2.append(self.comp_vs_comp_button)

        self.back_img = OnscreenImage(
            image="img3.png",
            pos=(0.9, 0, -0.95),
            scale=(0.4, 1, 0.10)
        )
        self.back_img.setTransparency(TransparencyAttrib.M_alpha)
        self.widgets_screen2.append(self.back_img)

        self.back_button = DirectButton(
            text="Retour",
            text_font=self.font_dialog_title,
            text_fg=(1, 1, 1, 1),
            text_scale=0.10,
            text_align=TextNode.ACenter,
            frameColor=(0, 0, 0, 0),
            relief=DGG.FLAT,
            pos=(0.9, 0, -0.99),
            command=self.back_to_screen1
        )
        self.widgets_screen2.append(self.back_button)

        for w in self.widgets_screen2:
            w.setTransparency(TransparencyAttrib.M_alpha)
            w.setColorScale(1, 1, 1, 0)

        self.float_seq = Sequence(
            Parallel(
                self.choose_img.posInterval(1.5, (0, 0, 0.22), startPos=(0, 0, 0.20)),
                self.user_vs_comp_img.posInterval(1.5, (0, 0, -0.38), startPos=(0, 0, -0.40)),
                self.comp_vs_comp_img.posInterval(1.5, (0, 0, -0.68), startPos=(0, 0, -0.70)),
            ),
            Parallel(
                self.choose_img.posInterval(1.5, (0, 0, 0.20), startPos=(0, 0, 0.22)),
                self.user_vs_comp_img.posInterval(1.5, (0, 0, -0.40), startPos=(0, 0, -0.38)),
                self.comp_vs_comp_img.posInterval(1.5, (0, 0, -0.70), startPos=(0, 0, -0.68)),
            )
        )
        self.float_seq.loop()

        self.user_vs_comp_button.bind(DGG.ENTER, self._on_hover_enter, extraArgs=[self.user_vs_comp_button])
        self.user_vs_comp_button.bind(DGG.EXIT, self._on_hover_exit, extraArgs=[self.user_vs_comp_button])
        self.comp_vs_comp_button.bind(DGG.ENTER, self._on_hover_enter, extraArgs=[self.comp_vs_comp_button])
        self.comp_vs_comp_button.bind(DGG.EXIT, self._on_hover_exit, extraArgs=[self.comp_vs_comp_button])

    def play_screen2_intro(self):
        def fade_in(t):
            for w in self.widgets_screen2:
                w.setColorScale(1, 1, 1, t)

        title_move = self.title_img.posInterval(1.0, (0, 0, 0.75), startPos=(0, 0, 0.95))
        title_scale = self.title_img.scaleInterval(1.0, (0.9, 1, 0.18), startScale=(0.6, 1, 0.12))
        text_move = self.welcome_label.posInterval(1.0, (0, 0, 0.70), startPos=(0, 0, 0.95))
        text_scale = self.welcome_label.scaleInterval(1.0, 0.18, startScale=0.65)

        intro_seq = Sequence(
            Parallel(
                LerpFunc(fade_in, fromData=0.0, toData=1.0, duration=0.8),
                title_move,
                title_scale,
                text_move,
                text_scale
            )
        )
        intro_seq.start()

    def back_to_screen1(self):
        for w in self.widgets_screen2:
            w.hide()

        for widget in [self.h1_img, self.h1_simple, self.h2_img, self.h2_strong,
                       self.h3_img, self.h3_simple, self.h4_img, self.h4_strong]:
            if widget is not None:
                widget.hide()

        for w in self.widgets_screen1:
            w.show()
            w.setColorScale(1, 1, 1, 1)

    def _on_hover_enter(self, button, *_):
        button['text_fg'] = (1, 0.9, 0.6, 1)

    def _on_hover_exit(self, button, *_):
        button['text_fg'] = (1, 1, 1, 1)

    # ---------- choix modes ----------
    def on_user_vs_comp_clicked(self):
        for w in [self.user_vs_comp_img, self.user_vs_comp_button,
                  self.comp_vs_comp_img, self.comp_vs_comp_button]:
            w.hide()
        self.show_heuristic_choice_user_vs_comp()

    def on_comp_vs_comp_clicked(self):
        for w in [self.user_vs_comp_img, self.user_vs_comp_button,
                  self.comp_vs_comp_img, self.comp_vs_comp_button]:
            w.hide()
        self.show_heuristic_choice_ia1()

    def show_heuristic_choice_user_vs_comp(self):
        self.h1_img = OnscreenImage(
            image="img3.png",
            pos=(0, 0, -0.40),
            scale=(1.10, 1, 0.25)
        )
        self.h1_img.setTransparency(TransparencyAttrib.M_alpha)

        self.h1_simple = DirectButton(
            text="EASY Level",
            text_font=self.font_dialog_title,
            text_fg=(1, 1, 1, 1),
            text_scale=0.17,
            text_align=TextNode.ACenter,
            frameColor=(0, 0, 0, 0),
            relief=DGG.FLAT,
            pos=(0, 0, -0.48),
            command=self.on_heuristic_user_vs_comp,
            extraArgs=["simple"]
        )

        self.h2_img = OnscreenImage(
            image="img3.png",
            pos=(0, 0, -0.70),
            scale=(1.10, 1, 0.25)
        )
        self.h2_img.setTransparency(TransparencyAttrib.M_alpha)

        self.h2_strong = DirectButton(
            text="HARD Level",
            text_font=self.font_dialog_title,
            text_fg=(1, 1, 1, 1),
            text_scale=0.17,
            text_align=TextNode.ACenter,
            frameColor=(0, 0, 0, 0),
            relief=DGG.FLAT,
            pos=(0, 0, -0.78),
            command=self.on_heuristic_user_vs_comp,
            extraArgs=["strong"]
        )

    def on_heuristic_user_vs_comp(self, heuristic_name):
        print("Lancement Utilisateur vs Computer avec heuristique :", heuristic_name)
        game = Game(humanside='player1')
        game.currentHeuristic = heuristic_name
        # profondeur de base pour h1, plus grande pour h2 dans Play
        play = Play(game, max_depth_h1=5, max_depth_h2=7, time_limit=15)
        self.mode = "HUMAN_VS_IA"
        self.start_panda_board(game, play)

    def show_heuristic_choice_ia1(self):
        self.h1_img = OnscreenImage(
            image="img3.png",
            pos=(0, 0, -0.40),
            scale=(1.10, 1, 0.25)
        )
        self.h1_img.setTransparency(TransparencyAttrib.M_alpha)

        self.h1_simple = DirectButton(
            text="IA1 : EASY Level ",
            text_font=self.font_dialog_title,
            text_fg=(1, 1, 1, 1),
            text_scale=0.17,
            text_align=TextNode.ACenter,
            frameColor=(0, 0, 0, 0),
            relief=DGG.FLAT,
            pos=(0, 0, -0.48),
            command=self.on_heuristic_ia1_chosen,
            extraArgs=["simple"]
        )

        self.h2_img = OnscreenImage(
            image="img3.png",
            pos=(0, 0, -0.70),
            scale=(1.10, 1, 0.25)
        )
        self.h2_img.setTransparency(TransparencyAttrib.M_alpha)

        self.h2_strong = DirectButton(
            text="IA1 : HARD Level",
            text_font=self.font_dialog_title,
            text_fg=(1, 1, 1, 1),
            text_scale=0.17,
            text_align=TextNode.ACenter,
            frameColor=(0, 0, 0, 0),
            relief=DGG.FLAT,
            pos=(0, 0, -0.78),
            command=self.on_heuristic_ia1_chosen,
            extraArgs=["strong"]
        )

    def on_heuristic_ia1_chosen(self, heuristic_name):
        self.ia1_heuristic = heuristic_name
        print("IA1 heuristique :", heuristic_name)
        for w in [self.h1_img, self.h1_simple, self.h2_img, self.h2_strong]:
            w.hide()
        self.show_heuristic_choice_ia2()

    def show_heuristic_choice_ia2(self):
        self.h3_img = OnscreenImage(
            image="img3.png",
            pos=(0, 0, -0.40),
            scale=(1.10, 1, 0.25)
        )
        self.h3_img.setTransparency(TransparencyAttrib.M_alpha)

        self.h3_simple = DirectButton(
            text="IA2 : EASY Level",
            text_font=self.font_dialog_title,
            text_fg=(1, 1, 1, 1),
            text_scale=0.17,
            text_align=TextNode.ACenter,
            frameColor=(0, 0, 0, 0),
            relief=DGG.FLAT,
            pos=(0, 0, -0.48),
            command=self.on_heuristic_ia2_chosen,
            extraArgs=["simple"]
        )

        self.h4_img = OnscreenImage(
            image="img3.png",
            pos=(0, 0, -0.70),
            scale=(1.10, 1, 0.25)
        )
        self.h4_img.setTransparency(TransparencyAttrib.M_alpha)

        self.h4_strong = DirectButton(
            text="IA2 : HARD Level",
            text_font=self.font_dialog_title,
            text_fg=(1, 1, 1, 1),
            text_scale=0.17,
            text_align=TextNode.ACenter,
            frameColor=(0, 0, 0, 0),
            relief=DGG.FLAT,
            pos=(0, 0, -0.78),
            command=self.on_heuristic_ia2_chosen,
            extraArgs=["strong"]
        )

    def on_heuristic_ia2_chosen(self, heuristic_name):
        print("IA1 heuristique :", self.ia1_heuristic)
        print("IA2 heuristique :", heuristic_name)

        game = Game(humanside=None)
        game.set_ia1_heuristic(self.ia1_heuristic)
        game.set_ia2_heuristic(heuristic_name)

        play = Play(game, max_depth_h1=5, max_depth_h2=7, time_limit=15)
        self.mode = "IA_VS_IA"
        self.start_panda_board(game, play)

    # ================== ÉCRAN PLATEAU ==================
    def start_panda_board(self, game: Game, play: Play):
        for w in self.widgets_screen2:
            w.hide()
        for w in [self.h1_img, self.h1_simple, self.h2_img, self.h2_strong,
                  self.h3_img, self.h3_simple, self.h4_img, self.h4_strong]:
            if w is not None:
                w.hide()

        self.current_game = game
        self.current_play = play
        self.game_finished = False

        if self.mode == "IA_VS_IA":
            self.current_player = "IA"
            self.current_ai_side = 'player1'
            turn_text = "Tour : IA1"
        else:
            self.current_player = "HUMAN"
            self.current_ai_side = None
            turn_text = "Tour : HUMAIN"

        ratio = self.getAspectRatio()

        # Plateau
        self.board_bg = OnscreenImage(
            image="plateau.png",
            pos=(0, 0, 0),
            scale=(ratio, 1, 1),
            parent=aspect2d
        )
        self.board_bg.setTransparency(TransparencyAttrib.M_alpha)

        # Centres des trous
        self.pit_centers = {
            'A': (-0.47 * ratio, -0.21),
            'B': (-0.27 * ratio, -0.21),
            'C': (-0.08 * ratio, -0.21),
            'D': (0.12 * ratio, -0.21),
            'E': (0.32 * ratio, -0.21),
            'F': (0.52 * ratio, -0.21),
            'L': (-0.47 * ratio, 0.21),
            'K': (-0.27 * ratio, 0.21),
            'J': (-0.08 * ratio, 0.21),
            'I': (0.12 * ratio, 0.21),
            'H': (0.32 * ratio, 0.21),
            'G': (0.52 * ratio, 0.21),
        }

        # Centres des magasins
        self.store_centers = {
            '1': (0.72 * ratio, 0.02),
            '2': (-0.72 * ratio, -0.02),
        }
        self.store_seed_images = {'1': [], '2': []}

        # Timer + tour
        self.timer_label = DirectLabel(
            text="Temps restant : 15 s",
            text_font=self.font_dialog_title,
            text_fg=(1, 1, 0, 1),
            text_scale=0.10,
            text_align=TextNode.ACenter,
            frameColor=(0, 0, 0, 0.6),
            pos=(-0.75 * ratio, 0, 0.85)
        )

        self.turn_label = DirectLabel(
            text=turn_text,
            text_font=self.font_dialog_title,
            text_fg=(1, 1, 1, 1),
            text_scale=0.10,
            text_align=TextNode.ACenter,
            frameColor=(0, 0, 0, 0.6),
            pos=(0.75 * ratio, 0, 0.85)
        )

        xs = [-0.78 * ratio, -0.47 * ratio, -0.16 * ratio,
              0.16 * ratio, 0.47 * ratio, 0.78 * ratio]
        z_bottom = -0.26
        z_top = 0.24
        z_store_bottom = -0.90
        z_store_top = 0.90

        self.holes_buttons = {}
        self.seed_images = {}

        button_scale = 0.20

        top_pits = ['L', 'K', 'J', 'I', 'H', 'G']
        for pit, x in zip(top_pits, xs):
            btn = DirectButton(
                text="",
                frameColor=(0, 0, 0, 0),
                relief=DGG.FLAT,
                pos=(x, 0, z_top),
                scale=button_scale,
                command=self.on_pit_clicked,
                extraArgs=[pit]
            )
            self.holes_buttons[pit] = btn
            self.seed_images[pit] = []

        bottom_pits = ['A', 'B', 'C', 'D', 'E', 'F']
        for pit, x in zip(bottom_pits, xs):
            btn = DirectButton(
                text="",
                frameColor=(0, 0, 0, 0),
                relief=DGG.FLAT,
                pos=(x, 0, z_bottom),
                scale=button_scale,
                command=self.on_pit_clicked,
                extraArgs=[pit]
            )
            self.holes_buttons[pit] = btn
            self.seed_images[pit] = []

        # Magasins (texte)
        self.store1_label = DirectLabel(
            text=f"Magasin bas : {self.current_game.state.board['1']}",
            text_font=self.font_dialog_title,
            text_fg=(1, 1, 1, 1),
            text_scale=0.05,
            text_align=TextNode.ACenter,
            frameColor=(0, 0, 0, 0.5),
            pos=(0, 0, z_store_bottom)
        )
        self.store2_label = DirectLabel(
            text=f"Magasin haut : {self.current_game.state.board['2']}",
            text_font=self.font_dialog_title,
            text_fg=(1, 1, 1, 1),
            text_scale=0.05,
            text_align=TextNode.ACenter,
            frameColor=(0, 0, 0, 0.5),
            pos=(0, 0, z_store_top)
        )

        self.final_message_label = DirectLabel(
            text="",
            text_font=self.font_dialog_title,
            text_fg=(1, 1, 1, 1),
            text_scale=0.05,
            text_align=TextNode.ACenter,
            frameColor=(0, 0, 0, 0),
            pos=(0, 0, -0.99)
        )

        self.refresh_seeds()
        self.turn_start_time = time.time()
        taskMgr.add(self.update_timer_task, "updateTimerTask")
        if self.mode == "IA_VS_IA":
            taskMgr.doMethodLater(1.0, self.ai_vs_ai_task, "aiVsAi", appendTask=True)

    def refresh_seeds(self):
        # nettoyer graines des trous
        for pit, imgs in self.seed_images.items():
            for img in imgs:
                img.removeNode()
        self.seed_images = {pit: [] for pit in self.holes_buttons.keys()}

        # nettoyer graines des magasins
        for s, imgs in self.store_seed_images.items():
            for img in imgs:
                img.removeNode()
        self.store_seed_images = {'1': [], '2': []}

        b = self.current_game.state.board

        offsets = [
            (-0.05,  0.05), (0.0,  0.05), (0.05,  0.05),
            (-0.03,  0.0),  (0.0,  0.0),  (0.03,  0.0),
            (-0.03, -0.03), (0.0, -0.03), (0.03, -0.03),
        ]

        colors = [
            (1, 0.3, 0.3, 1),
            (0.3, 1, 0.3, 1),
            (0.3, 0.3, 1, 1),
            (1, 1, 0.3, 1),
            (1, 0.3, 1, 1),
            (0.3, 1, 1, 1),
        ]

        # graines dans les trous
        for pit in self.holes_buttons.keys():
            n = b.get(pit, 0)
            if n <= 0:
                continue

            cx, cz = self.pit_centers[pit]
            for i in range(n):
                ox, oz = offsets[i % len(offsets)]
                color = colors[i % len(colors)]

                seed = DirectButton(
                    image="seed.png",
                    frameColor=(0, 0, 0, 0),
                    relief=DGG.FLAT,
                    pos=(cx + ox, 0, cz + oz),
                    scale=0.08,
                    command=self.on_pit_clicked,
                    extraArgs=[pit]
                )
                seed.setTransparency(TransparencyAttrib.M_alpha)
                seed['image_color'] = color

                self.seed_images[pit].append(seed)

        # graines dans les magasins
        cols = 4
        dx = 0.045
        dz = 0.045
        scale_store_seed = 0.05

        for store_id in ['1', '2']:
            n = b.get(store_id, 0)
            if n <= 0:
                continue

            cx, cz = self.store_centers[store_id]
            rows = (n + cols - 1) // cols

            for i in range(n):
                row = i // cols
                col = i % cols

                offset_x = (col - (cols - 1) / 2.0) * dx
                offset_z = (rows / 2.0 - 0.5 - row) * dz

                color = colors[i % len(colors)]

                seed = OnscreenImage(
                    image="seed.png",
                    pos=(cx + offset_x, 0, cz + offset_z),
                    scale=scale_store_seed,
                    parent=aspect2d
                )
                seed.setTransparency(TransparencyAttrib.M_alpha)
                seed.setColor(*color)
                self.store_seed_images[store_id].append(seed)

        self.store1_label['text'] = f"Magasin bas : {b['1']}"
        self.store2_label['text'] = f"Magasin haut : {b['2']}"

    # ---------- Animation de distribution ----------
    def compute_path_pits(self, player, start_pit, seeds):
        """
        Recalcule le chemin de distribution visuelle, en respectant la règle :
        on saute le magasin adverse (comme dans MancalaBoard.doMove).
        """
        path = []
        current = start_pit

        if player == 'player1':
            opp_store = '2'
        else:
            opp_store = '1'

        for _ in range(seeds):
            current = self.current_game.state.next_pit[current]
            if current == opp_store:
                current = self.current_game.state.next_pit[current]
            path.append(current)
        return path

    def animate_move(self, path_pits, callback=None):
        intervals = []
        jump_up = 0.08
        duration = 0.70

        for pit in path_pits:
            if pit not in self.pit_centers:
                intervals.append(Wait(0.2))
                continue

            cx, cz = self.pit_centers[pit]

            start_pos = (cx, 0, cz)
            mid_pos   = (cx, 0, cz + jump_up)
            end_pos   = (cx, 0, cz)

            seed = OnscreenImage(
                image="seed.png",
                pos=start_pos,
                scale=0.06,
                parent=aspect2d
            )
            seed.setTransparency(TransparencyAttrib.M_alpha)
            seed.setColor(1, 1, 1, 1)

            up_ival = seed.posInterval(duration * 0.5, mid_pos, startPos=start_pos)
            down_ival = seed.posInterval(duration * 0.5, end_pos, startPos=mid_pos)

            one_jump = Sequence(up_ival, down_ival, Func(seed.removeNode))
            intervals.append(one_jump)
            intervals.append(Wait(0.12))

        seq = Sequence(*intervals)
        if callback is not None:
            seq.append(Func(callback))
        seq.start()

    # ---------- Clic HUMAIN ----------
    def on_pit_clicked(self, pit):
        if self.game_finished or self.current_game is None:
            return
        if self.mode != "HUMAN_VS_IA":
            return
        if self.current_player != "HUMAN":
            return

        humanside = self.current_game.playerSide['HUMAN']
        pits_allowed = (
            self.current_game.state.p1_pits if humanside == 'player1'
            else self.current_game.state.p2_pits
        )
        if pit not in pits_allowed:
            return
        if self.current_game.state.board.get(pit, 0) == 0:
            return

        b = self.current_game.state.board
        seeds = b[pit]

        try:
            last_pit, extra = self.current_game.state.doMove(humanside, pit)
        except ValueError:
            return

        path = self.compute_path_pits(humanside, pit, seeds)

        def after_anim():
            print("HUMAN joue", pit)
            self.current_game.print_board("HUMAN", pit)
            self.refresh_seeds()

            if self.current_game.gameOver():
                self.show_final_result()
                return

            if extra:
                self.turn_label['text'] = "Tour : HUMAIN (rejoue)"
                self.turn_start_time = time.time()
            else:
                self.current_player = "COMPUTER"
                self.turn_label['text'] = "Tour : IA"
                self.turn_start_time = time.time()
                taskMgr.doMethodLater(0.8, self.computer_move_task, "compMove")

        self.animate_move(path, callback=after_anim)

    # ---------- Tour IA (HUMAIN vs IA) ----------
    def computer_move_task(self, task):
        if self.game_finished or self.current_game is None:
            return Task.done

        side = self.current_game.playerSide['COMPUTER']
        possible = self.current_game.state.possibleMoves(side)
        if not possible:
            return Task.done

        pit = self.current_play.computerTurn()
        if pit is None:
            self.turn_label['text'] = "IA : aucun coup"
            self.current_player = "HUMAN"
            self.turn_start_time = time.time()
            return Task.done

        self.refresh_seeds()
        if self.current_game.gameOver():
            self.show_final_result()
            return Task.done

        self.current_player = "HUMAN"
        self.turn_label['text'] = "Tour : HUMAIN"
        self.turn_start_time = time.time()
        return Task.done

    # ---------- IA vs IA ----------
    def ai_vs_ai_task(self, task):
        if self.game_finished or self.current_game is None:
            return Task.done

        side = self.current_ai_side
        name = "IA1" if side == 'player1' else "IA2"
        self.turn_label['text'] = f"Tour : {name}"

        pit = self.current_play.aiVsAiTurn(side)
        if pit is None:
            other = 'player2' if side == 'player1' else 'player1'
            if any(self.current_game.state.board[p] > 0
                   for p in (self.current_game.state.p1_pits if other == 'player1'
                             else self.current_game.state.p2_pits)):
                self.current_ai_side = other
                task.delayTime = 1.0
                return Task.again
            else:
                self.show_final_result()
                return Task.done

        self.refresh_seeds()
        if self.current_game.gameOver():
            self.show_final_result()
            return Task.done

        self.current_ai_side = 'player2' if side == 'player1' else 'player1'
        task.delayTime = 1.0
        return Task.again

    # ---------- Fin + écran de résultat ----------
    def show_final_result(self):
        self.game_finished = True
        winner, score = self.current_game.findWinner()

        if self.mode == "IA_VS_IA":
            if winner == "DRAW":
                msg = "IA1 et IA2 sont à égalité."
            elif winner == "HUMAN":
                msg = f"IA1 gagne avec {score} graines de plus."
            else:
                msg = f"IA2 gagne avec {score} graines de plus."
        else:
            if winner == "DRAW":
                msg = "Égalité parfaite."
            else:
                nom = "UTILISATEUR" if winner == "HUMAN" else "COMPUTER"
                msg = f"{nom} gagne avec {score} graines de plus."

        self.final_message_label['text'] = ""
        self.turn_label['text'] = ""

        ratio = self.getAspectRatio()
        scale_x = 0.9 * ratio
        scale_z = 0.7

        self.result_bg = OnscreenImage(
            image="resultat.png",
            pos=(0, 0, 0),
            scale=(scale_x, 1, scale_z),
            parent=aspect2d
        )
        self.result_bg.setTransparency(TransparencyAttrib.M_alpha)
        self.result_bg.setColorScale(1, 1, 1, 0)

        self.result_label = DirectLabel(
            text=msg,
            text_font=self.font_dialog_title,
            text_fg=(1, 1, 1, 1),
            text_scale=0.10,
            text_align=TextNode.ACenter,
            frameColor=(0, 0, 0, 0),
            pos=(0, 0, -0.05)
        )
        self.result_label.setTransparency(TransparencyAttrib.M_alpha)
        self.result_label.setColorScale(1, 1, 1, 0)

        self.result_button = DirectButton(
            text="Retour au menu",
            text_font=self.font_dialog_title,
            text_fg=(1, 1, 1, 1),
            text_scale=0.08,
            text_align=TextNode.ACenter,
            frameColor=(0, 0, 0, 0.7),
            relief=DGG.FLAT,
            pos=(0, 0, -0.45),
            command=self.back_to_screen1_from_gameover
        )
        self.result_button.setTransparency(TransparencyAttrib.M_alpha)
        self.result_button.setColorScale(1, 1, 1, 0)

        anim = Sequence(
            Parallel(
                self.result_bg.colorScaleInterval(
                    0.6, (1, 1, 1, 1), startColorScale=(1, 1, 1, 0)
                ),
                self.result_bg.scaleInterval(
                    0.6,
                    (scale_x, 1, scale_z),
                    startScale=(scale_x * 0.8, 1, scale_z * 0.8)
                )
            ),
            Parallel(
                self.result_label.colorScaleInterval(
                    0.4, (1, 1, 1, 1), startColorScale=(1, 1, 1, 0)
                ),
                self.result_button.colorScaleInterval(
                    0.4, (1, 1, 1, 1), startColorScale=(1, 1, 1, 0)
                )
            )
        )
        anim.start()

    def back_to_screen1_from_gameover(self):
        for w in [getattr(self, 'result_bg', None),
                  getattr(self, 'result_label', None),
                  getattr(self, 'result_button', None)]:
            if w is not None:
                w.removeNode()

        if self.board_bg is not None:
            self.board_bg.removeNode()
        for btn in self.holes_buttons.values():
            btn.removeNode()
        if self.store1_label is not None:
            self.store1_label.removeNode()
        if self.store2_label is not None:
            self.store2_label.removeNode()
        if self.timer_label is not None:
            self.timer_label.removeNode()
        if self.turn_label is not None:
            self.turn_label.removeNode()
        if self.final_message_label is not None:
            self.final_message_label.removeNode()

        for w in self.widgets_screen1:
            w.show()
            w.setColorScale(1, 1, 1, 1)

    def update_timer_task(self, task):
        if self.current_game is None or self.turn_start_time is None or self.game_finished:
            return Task.cont

        if self.mode == "IA_VS_IA":
            self.timer_label['text'] = "Mode IA vs IA"
            return Task.cont

        elapsed = time.time() - self.turn_start_time
        remaining = max(0, self.time_limit - int(elapsed))
        self.timer_label['text'] = f"Temps restant : {remaining} s"

        if remaining <= 0 and self.mode == "HUMAN_VS_IA":
            if self.current_player == "HUMAN":
                self.current_player = "COMPUTER"
                self.turn_label['text'] = "Temps HUMAIN écoulé → Tour IA"
                self.turn_start_time = time.time()
                taskMgr.doMethodLater(0.8, self.computer_move_task, "compMove")
            else:
                self.current_player = "HUMAN"
                self.turn_label['text'] = "Temps IA écoulé → Tour HUMAIN"
                self.turn_start_time = time.time()

        return Task.cont


if __name__ == "__main__":
    app = MancalaTitleApp()
    app.run()
