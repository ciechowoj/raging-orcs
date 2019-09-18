from GameStage import *
import pickle

SPACING = 1.5

class MainMenu(GameStage):
    """Klasa menu głównego."""
    def __init__(self, screen, gameplay, hall_of_fame, credits):
        super(MainMenu, self).__init__(screen)
        ACTIVE_COLOR = (255, 100, 0)
        INACTIVE_COLOR = (200, 0, 0)
        TEXT_LABELS = ["CONTINUE", "NEW GAME", "HALL OF FAME", "EXIT"]
        self._position = 0
        self._CONTINUE = 0
        self._NEW_GAME = 1
        self._HALL_OF_FAME = 2
        self._EXIT = 3
        self._ACTIVE_LABELS = [FONT_BIG.render(text, True, ACTIVE_COLOR) for text in TEXT_LABELS]
        self._INACTIVE_LABELS = [FONT_BIG.render(text, True, INACTIVE_COLOR) for text in TEXT_LABELS]
        self._gameplay = gameplay
        self._hall_of_fame = hall_of_fame
        self._credits = credits
        
        self.sound = SoundEffects.MainMenuTheme

    def on_event(self, event):
        """Obsługuje zdarzenia menu głównego."""
        if event.type == KEYDOWN:
            if event.key == K_UP:
                self._position = (self._position - 1) % len(self._ACTIVE_LABELS)
            elif event.key == K_DOWN:
                self._position = (self._position + 1) % len(self._ACTIVE_LABELS)
            elif event.key == K_RETURN:
                if self._position == self._CONTINUE:
                    if not self._gameplay.is_ingame():
                        self._gameplay.new_game("data/level.dat")
                    self.set_next_stage(self._gameplay)
                    return True
                elif self._position == self._NEW_GAME:
                    self._gameplay.new_game("data/level.dat")
                    self.set_next_stage(self._gameplay)
                    return True
                elif self._position == self._HALL_OF_FAME:
                    self.set_next_stage(self._hall_of_fame)
                    return True
                elif self._position == self._CREDITS:
                    pass
                elif self._position == self._EXIT:
                    self.set_next_stage(None)
                    return True
            elif event.key == K_ESCAPE:
                self._position = self._EXIT
        return False

    def on_redraw(self, surface, delta, current):
        """Odrysowuje menu główne."""
        i, s = 0, len(self._ACTIVE_LABELS)
        spacing = int(self._ACTIVE_LABELS[0].get_size()[1] * SPACING)
        yoffset = spacing * s
        yoffset = (surface.get_size()[1] - yoffset) // 2
        
        while i < s:
            if i == self._position:
                xoffset = (surface.get_size()[0] - self._ACTIVE_LABELS[i].get_size()[0]) // 2
                surface.blit(self._ACTIVE_LABELS[i], (xoffset, i * spacing + yoffset))
            else:
                xoffset = (surface.get_size()[0] - self._INACTIVE_LABELS[i].get_size()[0]) // 2
                surface.blit(self._INACTIVE_LABELS[i], (xoffset, i * spacing + yoffset))
            i += 1

class HallOfFame(GameStage):
    """Klasa tabeli najwyższych wyników."""
    ACTIVE_COLOR = (255, 100, 0)
    INACTIVE_COLOR = (200, 0, 0)
    def __init__(self, screen):
        super(HallOfFame, self).__init__(screen)
        self._position = -1
        self._entries = []
        try:
            self._entries = pickle.load(open("data/scores.dat", "rb"))
        except:
            self._entries = [("Unknown", 0) for x in range(6)]
        
        self._labels = [HallOfFame._prepare_surface(entry, HallOfFame.INACTIVE_COLOR) for entry in self._entries]
        
        self.sound = SoundEffects.HoFTheme

    def add_score(self, name, score):
        """Dodaje nowy wynik."""
        i, s = 0, len(self._entries)
        while i < s:
            if self._entries[i][1] < score:
                break
            i += 1
        if i < s:
            j = s - 1
            while j > i:
                self._entries[j] = self._entries[j - 1]
                self._labels[j] = self._labels[j - 1]
                j -= 1
            self._entries[i] = name, score
            self._labels[i] = HallOfFame._prepare_surface(self._entries[i], HallOfFame.ACTIVE_COLOR)
            self._position = i

    def on_event(self, event):
        """Obsługuje zdarzenia tabeli wyników."""
        if event.type == KEYDOWN:
            if event.key == K_RETURN:
                if self._position >= 0:
                    self._labels[self._position] = HallOfFame._prepare_surface(self._entries[self._position], HallOfFame.INACTIVE_COLOR)
                    self._position = -1
            elif event.key == K_ESCAPE:
                pickle.dump(self._entries, open("data/scores.dat", "wb+"))
                self.set_next_stage(self._main_menu)
                if self._position >= 0:
                    self._labels[self._position] = HallOfFame._prepare_surface(self._entries[self._position], HallOfFame.INACTIVE_COLOR)
                    self._position = -1
                return True
            elif self._position >= 0 and event.unicode != "" and (ord("A") <= ord(event.unicode) and ord(event.unicode) <= ord("Z") or ord("a") <= ord(event.unicode) and ord(event.unicode) <= ord("z") or event.unicode == " "):
                self._entries[self._position] = self._entries[self._position][0] + event.unicode, self._entries[self._position][1]
                self._labels[self._position] = HallOfFame._prepare_surface(self._entries[self._position], HallOfFame.ACTIVE_COLOR)
            elif self._position >= 0 and event.key == K_BACKSPACE and self._entries[self._position][0] != "":
                self._entries[self._position] = self._entries[self._position][0][:-1], self._entries[self._position][1]
                self._labels[self._position] = HallOfFame._prepare_surface(self._entries[self._position], HallOfFame.ACTIVE_COLOR)

        return False

    def on_redraw(self, surface, delta, current):
        """Odrysowuje tabele wyników."""
        i, s = 0, len(self._labels)
        spacing = int(self._labels[0].get_size()[1])
        yoffset = spacing * s
        yoffset = (surface.get_size()[1] - yoffset) // 2
        
        while i < s:
            xoffset = (surface.get_size()[0] - self._labels[i].get_size()[0]) // 2
            surface.blit(self._labels[i], (xoffset, i * spacing + yoffset))
            i += 1

    def set_main_menu(self, main_menu):
        """Ustawia referencje do menu głównego (potrzeban do powrotu)."""
        self._main_menu = main_menu

    def _prepare_surface(data, color, width = 600):
        name = FONT_BIG.render(data[0], True, color) 
        score = FONT_BIG.render(str(data[1]), True, color)
        surface = pygame.Surface((width, name.get_size()[1]))
        surface.blit(name, (0, 0))
        surface.blit(score, (surface.get_size()[0] - score.get_size()[0], 0))
        return surface
