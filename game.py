from utilities import *
Issue20891_workaround()
screen = initialize_pygame(vec2(800, 600), False)
from Gameplay import *
from Environment import *

gameplay = Gameplay(screen)
hall_of_fame = HallOfFame(screen)
credits = None
main_menu = MainMenu(screen, gameplay, hall_of_fame, credits)
gameplay.set_main_menu(main_menu)
gameplay.set_hall_of_fame(hall_of_fame)
hall_of_fame.set_main_menu(main_menu)

current_stage = main_menu
while current_stage != None:
    """Przerywa wszystkie ktorych odgrywanie rozpoczal poprzedni stage, nastepnie rozpoczyna nieskonczone odegranie w petli glownego motywu obecnego stage'a"""
    pygame.mixer.stop()
    pygame.mixer.Channel(0).play(current_stage.sound, -1)
    current_stage = current_stage.run()
