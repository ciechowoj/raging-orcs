from utilities import *

class SoundEffects:
    """
    Klasa, ktorej statycznymi stalymi sa sciezki odpowiednich dzwiekow - ich wywolywaniem zajmuja sie odpowiednio: dla atakow: AIStates, dla czarow: ich funkcja _add_spell PlayerObject, dla stage'ow gry modul zarzadzajacy zmiana stage'ow z game.py
    """
    GameTheme = [pygame.mixer.Sound("data/Music/Game#1.ogg"), pygame.mixer.Sound("data/Music/Game#2.ogg")]
    HoFTheme = pygame.mixer.Sound("data/Music/HallOfFame.ogg")
    MainMenuTheme = pygame.mixer.Sound("data/Music/MainMenu.ogg")
    MeleeSound = pygame.mixer.Sound("data/Music/Melee.ogg")
    RangedSound = pygame.mixer.Sound("data/Music/Ranged.ogg")
    WarnOthersSound = pygame.mixer.Sound("data/Music/WarnOthers.ogg")
    SpellSoundDict = {
        "air":pygame.mixer.Sound("data/Music/SpellAir.ogg"),
        "earth":pygame.mixer.Sound("data/Music/SpellEarth.ogg"),
        "fire":pygame.mixer.Sound("data/Music/SpellFire.ogg"),
        "water":pygame.mixer.Sound("data/Music/SpellWater.ogg")}

