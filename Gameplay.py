from MenuStages import *
from Environment import *

SPELL_NAMES = ["water_ball", "fire_ball", "air_ball", "earth_ball", "water_wave", "fire_wave", "air_wave", "earth_wave"]

class Gameplay(GameStage):
    """Klasa stadium rozgrywki. Główna klasa gry."""
    def __init__(self, screen):
        super(Gameplay, self).__init__(screen)
        self._environment = Environment()
        self._level_file_name = ""
        self.sound = SoundEffects.GameTheme[randint(0,1)]

    def on_event(self, event):
        """Obsługuje zdarzenia wejścia, wydając odpowiednie polecenia obiektowi gracza."""
        if event.type == MOUSEBUTTONDOWN: 
            if event.button == 1:
                pos = vec2(event.pos)
                pos.y = self._screen.get_size()[1] - pos.y
                world = screen_to_world(self._get_screen_pos() + pos)
                if self._environment.is_reachable(world.ifloor()):
                    self._player.goto(world)
            elif event.button == 3:
                picked = self._environment.pick(vec2(event.pos))
                if picked != []:
                    pressed = pygame.key.get_pressed()
                    mask = 0
                    if pressed[K_q]:
                        mask |= 1
                    if pressed[K_w]:
                        mask |= 2
                    if pressed[K_e]:
                        mask |= 4
                    self._player.cast(SPELL_NAMES[mask], picked[0])
        elif event.type == KEYDOWN and event.key == K_ESCAPE:
            self.set_next_stage(self._main_menu)
            return True
        elif event.type == KEYDOWN:
            if event.key == K_1:
                self._player.cast("water_shield", None)
            elif event.key == K_2:
                self._player.cast("fire_shield", None)
            elif event.key == K_3:
                self._player.cast("air_shield", None)
            elif event.key == K_4:
                self._player.cast("earth_shield", None)
        return False

    def on_update(self, delta, current):
        """Odświeża stan gry."""
        if self._player.is_dead() or self._environment.is_clear():
            self.set_next_stage(self._hall_of_fame)
            self._hall_of_fame.add_score("", self._player.get_score())
            self._level_file_name = ""
            return True
        self._environment.update(delta, current)

    def on_redraw(self, surface, delta, current):
        """Odrysowuje grę."""
        self._environment.redraw(surface, self._player.get_position(), current, False)
        score = FONT_SMALL.render("score: " + str(self._player.get_score()), True, (255, 255, 0))
        surface.blit(score, ((surface.get_size()[0] - score.get_size()[0]) // 2, 0))

    def new_game(self, file):
        """Inicjalizuje nową rozgrywkę."""
        loader = TxtLevelLoader()
        loader.load(file)
        self._environment.load(loader)
        self._player = self._environment.get_players()[0]
        self._level_file_name = file

    def is_ingame(self):
        """Sprawdza czy rozgrywka jest zainicjalizowana."""
        return self._level_file_name != ""

    def set_main_menu(self, main_menu):
        """Ustawia referencje do menu głównego gry."""
        self._main_menu = main_menu

    def set_hall_of_fame(self, hall_of_fame):
        """Ustawia referencje do tabeli najwyższych wynikow gry."""
        self._hall_of_fame = hall_of_fame

    def _get_screen_pos(self):
        return world_to_screen(self._player.get_position()) - vec2(self._screen.get_size()) * 0.5
