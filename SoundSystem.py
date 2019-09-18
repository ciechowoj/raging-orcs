from utilities import *

class SoundEffects:
    """
    Klasa, ktorej statycznymi stalymi sa sciezki odpowiednich dzwiekow - ich wywolywaniem zajmuja sie odpowiednio: dla atakow: AIStates, dla czarow: ich funkcja _add_spell PlayerObject, dla stage'ow gry modul zarzadzajacy zmiana stage'ow z game.py
    """
    GameTheme = [pygame.mixer.Sound("data/music/Game#1.ogg"), pygame.mixer.Sound("data/music/Game#2.ogg")]
    HoFTheme = pygame.mixer.Sound("data/music/HallofFame.ogg")
    MainMenuTheme = pygame.mixer.Sound("data/music/MainMenu.ogg")
    MeleeSound = pygame.mixer.Sound("data/music/Melee.ogg")
    RangedSound = pygame.mixer.Sound("data/music/Ranged.ogg")
    WarnOthersSound = pygame.mixer.Sound("data/music/WarnOthers.ogg")
    SpellSoundDict = {
        "air":pygame.mixer.Sound("data/music/SpellAir.ogg"), 
        "earth":pygame.mixer.Sound("data/music/SpellEarth.ogg"),
        "fire":pygame.mixer.Sound("data/music/SpellFire.ogg"),
        "water":pygame.mixer.Sound("data/music/SpellWater.ogg")}
    
    