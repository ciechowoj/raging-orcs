from utilities import *
from SoundSystem import SoundEffects

def dist(a,b):
    """Zwraca odległość między punktami a i b."""
    return (a-b).length()
    
class MonsterTypes:
    """Definuje rodzaje potworw wystepujace w grze - dodatkowo sa to stale okreslajace zasieg ich atakow"""
    Melee = 1
    Ranged = 5
    Shaman = 5
   
class _AIStatePrototype:
    """Klasa abstrakcyjna bedaca nadklasa dla wszystkich stanow AI - okresla minimalne metody wymagane by dzialaly - wzorce projektowe Strategia i Pylek"""
    #returns next state and changes object     
    def execute(self, dynamic_object, current, delta):
        """
        Funkcja dla kazdego stanu powinna odpowiednio zmodyfikowac obiekt na rzecz ktorego zostala wywowalana i zwrocic kolejny stan, jaki powinien po niej nastapic
        current i delta to zmienne pozwalajace synchronizowac czas pomiedzy roznymi funkcjami
        """
        pass
        
class AIIdle(_AIStatePrototype):
    """Stan potworka majacego tylko stac w miejscu, bez reakcji na gracza"""
    
    def __init__(self, patrol = True):
        self._patrol_on_next_move = patrol
        
    PATROL_STATE = None
    NORMAL_STATE = None
    
    def get_state(patrol = True):
        """Funkcja statyczna dzialajaca jako fabryka tego stanu"""
        if patrol:
            if AIIdle.PATROL_STATE == None:
                AIIdle.PATROL_STATE = AIIdle()
            return AIIdle.PATROL_STATE
        if AIIdle.NORMAL_STATE == None:
            AIIdle.NORMAL_STATE = AIIdle(False)
        return AIIdle.NORMAL_STATE
        
    def execute(self, dynamic_object, current, delta):
        """Jesli kolejnym stanem powinien byc patrol losuje odpowiednia sciezke sprawdzajac czy jest ona mozliwa do przejscia i zwraca stan odpowiadajacy za patrol, w przeciwnym przypadku upewnia sie ze wyswietlana animacja to stanie w miejscu i zwraca jako kolejny stan samego siebie"""
        if self._patrol_on_next_move:
            pos = dynamic_object.get_position()
            fpath = dynamic_object.get_environment().findPath
            freachable = dynamic_object.get_environment().reachable
            temp = (pos.x + randint(-5,5), pos.y + randint(-5,5))
            while not freachable(vec2(temp)):
                temp = (pos.x + randint(-5,5), pos.y + randint(-5,5))
            path = fpath((pos.x,pos.y),temp)
            for i in range(randint(2,10)):
                x,y = path[-1]
                point_new = (x+randint(-5,5), y+randint(-5,5))
                if freachable(vec2(point_new)):
                    path += fpath((x,y),point_new)
            
            dynamic_object.set_path(path)
            return AIPatrol.get_state()
           
            
        if dynamic_object._anim_sprite != dynamic_object.STOPPED:
            dynamic_object.animate(dynamic_object.STOPPED, current)
        return self
    
    def patrol():
        """Upewnia ze kolejnym stanem po obecnym bedzie patrolowanie z wylosowana autonomicznie droga"""
        self._patrol_on_next_move = True
    
    def not_patrol():
        """Upewnia sie ze kolejnym stanem bedzie nie bedzie patrolowanie, lecz stan identyczny z obecnym"""
        self_patrol_on_next_move = False
        
class AIAttack(_AIStatePrototype):    
    """Stan reprezentujacy potworka atakujacego zadanego gracza"""
    SEARCH_PATH_DIST = 4
    SEARCH_RADIUS = 100
    ATTACK_RADIUS = 1.5
    CLOSE_COMBAT_RAD = 4
    COOLDOWN = 0.9
    
    def __init__(self, player):
        self.player = player
        
    def execute(self, dynamic_object, current, delta):
        """Upewnia sie, ze potworek podaza droga lub atakuje, wyswietlajaca odpowiednia animacje, zaleznie od tego czy gracz jest w zasiegu ataku"""
        dynamic_object.time -= delta
        player_pos = self.player.get_position()
        distance = dist(dynamic_object.get_position(), player_pos)
        path = dynamic_object.get_path()
        
        if path == [] or dist(self.player.get_position(), vec2(dynamic_object.get_last_path_point())) > AIAttack.SEARCH_PATH_DIST:
            obj_pos = dynamic_object.get_position()
            obj_pos += player_pos.normal()        
            obj_pos = obj_pos.intcpl()
            player_pos = player_pos.intcpl()
            path = dynamic_object.get_environment().findPath(obj_pos, player_pos)
            path = path[1:]
          
            dynamic_object.set_path(path)
           
        if distance > AIAttack.ATTACK_RADIUS*dynamic_object.get_monster_type():
            if path != []:
                got_there = dynamic_object.move_to(vec2(path[0]), delta)
                if got_there:
                    path = path[1:]
                    dynamic_object.set_path(path)    
                if dynamic_object._anim_sprite != dynamic_object.RUNNING:
                    dynamic_object.animate(dynamic_object.RUNNING, current)
        else:
                dynamic_object.set_direction( self.player.get_position() - dynamic_object.get_position())
                
                if dynamic_object._anim_sprite != dynamic_object.ATTACK:
                    dynamic_object.animate(dynamic_object.ATTACK, current)
                if dynamic_object.time <= 0:
                    dynamic_object.time = self.COOLDOWN
                    if dynamic_object.get_monster_type() == MonsterTypes.Ranged:
                        dynamic_object.shoot()
                        SoundEffects.RangedSound.play()
                    else: 
                        dynamic_object.attack(self.player)
                        SoundEffects.MeleeSound.play()
            
        return self;
        
class AIPatrol(_AIStatePrototype):
    """Stan reprezentujacy potworka patrolujacego dana sciezke"""
    SPOT_RADIUS = 10
    STATE = None
    
    def __init__(self):
        pass
    
    def get_state():
        if AIPatrol.STATE == None:
            AIPatrol.STATE = AIPatrol()
        return AIPatrol.STATE
            
    def execute(self, dynamic_object, current, delta):
        """Upewnia sie ze potworek wyswietla odpowiednia animacje, nastepnie wykonuje ruch w strone kolejnego wezla sciezki i zapetla ja"""
        if dynamic_object._anim_sprite != dynamic_object.RUNNING:
            dynamic_object.animate(dynamic_object.RUNNING, current)
        
            
        for player in dynamic_object.get_environment().get_players():
            if dist(player.get_position(), dynamic_object.get_position()) < AIPatrol.SPOT_RADIUS:
                return AIWarnOthers(player)

        path = dynamic_object.get_path()
        if path != []:
            got_there = dynamic_object.move_to(vec2(path[0]), delta)        
            if got_there:
                path.append(path[0])
                path = path[1:]
                dynamic_object.set_path(path)
                
        return self
        
class AIWarnOthers(_AIStatePrototype):
    """Stan reprezentujacy potworka powiadamiajacego pozostale o zauwazonym graczu"""
    WARNING_TIMEOUT = 5
    WARNING_CHANCE = 10
   
    def __init__(self, player):
        self.player = player
        self.time = 0
       
    def execute(self, dynamic_object, current, delta):
        """Odgrywa dzwiek zawiadamiania i przy uzyciu notify przekazuje pozostalym potworkom referencje do zauwazonego obiektu-gracza (dokladniej: nowy stan AI do wykonywania: atakowanie wskazanego gracza)"""
        SoundEffects.WarnOthersSound.play()
        if dynamic_object._anim_sprite != dynamic_object.STOPPED:
            dynamic_object.animate(dynamic_object.STOPPED, current)
        self.time+=delta
        if self.time + randint(-2,4) >= AIWarnOthers.WARNING_TIMEOUT:
            dynamic_object.set_path([])
            return AIAttack(self.player)
        if randint(0, AIWarnOthers.WARNING_CHANCE) == 0:
            dynamic_object.get_environment().notify(AIAttack(self.player), dynamic_object.get_position())
        return self
     