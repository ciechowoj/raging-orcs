"""@package docstring
Moduł zawiera definicje wszystkich obiektów dynamicznych gry. 
"""

from utilities import *
from ObjectSprite import *
from AIStates import *

ELEMENT_COLOR = [( (0, 0, 255, 255), (50, 150, 255, 150) ), ( (255, 255, 0, 255), (255, 0, 0, 150) ), ( (150, 255, 255, 200), (150, 200, 255, 150) ), ( (100, 255, 0, 255), (0, 255, 0, 150) )]
WATER_STARS = create_star_sprites(24, 3, ELEMENT_COLOR[0])
FIRE_STARS = create_star_sprites(24, 3, ELEMENT_COLOR[1])
AIR_STARS = create_star_sprites(24, 3, ELEMENT_COLOR[2])
EARTH_STARS = create_star_sprites(24, 3, ELEMENT_COLOR[3])
WATER_CIRCLES = create_ball_sprites(24, 3, ELEMENT_COLOR[0])
FIRE_CIRCLES = create_ball_sprites(24, 3, ELEMENT_COLOR[1])
AIR_CIRCLES = create_ball_sprites(24, 3, ELEMENT_COLOR[2])
EARTH_CIRCLES = create_ball_sprites(24, 3, ELEMENT_COLOR[3])
WATER_SHIELD = create_shield_sprite(48, ELEMENT_COLOR[0])
FIRE_SHIELD = create_shield_sprite(48, ELEMENT_COLOR[1])
AIR_SHIELD = create_shield_sprite(48, ELEMENT_COLOR[2])
EARTH_SHIELD = create_shield_sprite(48, ELEMENT_COLOR[3])

SHIELD_COST = 0.2
BALL_COST = 0.1
WAVE_COST = 0.4
SHIELD_FACTOR = 0.5

ENERGY_FACTOR = 0.1
HEALTH_FACTOR = 0.1

class DynamicObject:
    """Klasa bazowa obiektów dynamicznych."""
    DEFAULT_HP = 1
    EPSILON = 0.15
    KNOCKBACK = 0.5
    HP_BAR_SPRITES = create_hp_bar_sprites(vec2(64, 4))
    MG_BAR_SPRITES = create_mg_bar_sprites(vec2(64, 4))
    HP_BAR_OFFSET = 8
    DAMAGE_ON_HIT = 5
    VISIBLE_IN_EDITOR = False
    
    def __init__(self):
        self._environment = None
        self._position = vec2()
        self._direction = vec2(0, 1).normal()
        self._velocity = 2.0
        self._radius = 0.5

        self._anim_sprite = None
        self._anim_time = 0.0
        self._anim_loop = False
        self._finished = False

        self._health = 1.0
        self._energy = -1.0
        self._magic = False

        self._spell = False
        self.time = 0
        self._path = []
        self._last_path_point = None
        
        self.DMG_TYPE = "fire"
        self.Resistance = {"fire":0.1,  "water":0.1, "earth":0.1, "air":0.1}


    def update(self, delta, current):
        """Odświeza stan obiektu."""
        self._position += self._direction * self._velocity * delta

    def redraw(self, surface, position, current, frames, pickable):
        """
        Odrysowuje obiekt. W rzeczywistości zwraca pozycje i ramkę animacji która ma być odrysowana,
        ponieważ przed narysowaniem wszystkie obiekty muszą zostać posortowane według osi y.
        """
        if(self._anim_sprite != None):
            
            delta = current - self._anim_time
            if self._anim_loop or delta < self._anim_sprite.get_time():
                self._finished = False
            else:
                delta = self._anim_sprite.get_time() - 0.01
                self._finished = True

            screen_direction = world_to_screen(self._direction).normal()
            screen_direction.y = - screen_direction.y
            angle = angle2(screen_direction)
            frame = self._anim_sprite.get_frame(angle, delta)
            dest = world_to_screen(self._position).floor() - position

            surface_size = vec2(surface.get_size())
            frame_size = self._anim_sprite.get_frame_size()
            dest.y = surface_size.y - dest.y
            hp_dest = dest.copy()
            eg_dest = dest.copy()
            depth = dest.y

            diff = vec2(floor(frame_size.x * 0.5), self._anim_sprite.get_offset())
            dest -= diff
            dest.x += frame[1][0]
            dest.y += frame[1][1]

            p1 = dest
            p2 = dest + vec2(frame[0].get_size())

            if not (p2.x < 0 or p2.y < 0 or surface_size.x < p1.x or surface_size.y < p1.y):
                frames.append((frame, depth, dest.intcpl()))
                pickable.append((self, dest.intcpl() + (frame[1][2], frame[1][3]), depth))
                if self._health >= 0.0:
                    sprite = DynamicObject.HP_BAR_SPRITES[int(self._health * (len(DynamicObject.HP_BAR_SPRITES) - 1))]
                    hp_dest.x -= sprite.get_size()[0] // 2
                    hp_dest.y = dest.y - DynamicObject.HP_BAR_OFFSET
                    frames.append(((sprite, (0, 0) + sprite.get_size()), depth, hp_dest.intcpl()))
                    if self._energy >= 0.0:
                        sprite = DynamicObject.MG_BAR_SPRITES[int(self._energy * (len(DynamicObject.MG_BAR_SPRITES) - 1))]
                        eg_dest.x -= sprite.get_size()[0] // 2
                        eg_dest.y = dest.y - DynamicObject.HP_BAR_OFFSET - sprite.get_size()[1]
                        frames.append(((sprite, (0, 0) + sprite.get_size()), depth, eg_dest.intcpl()))

    def animate(self, sprite, current, loop = True, force = False):
        """
        Ustawia odpowiednią znimacje obiektu.
        """
        if self._anim_sprite != sprite or force:
            self._anim_sprite = sprite
            self._anim_time = current
            self._anim_loop = loop

    def finished(self):
        """Zwraca true jeśli animacja została zakończona."""
        return self._finished

    def get_frame_index(self, time):
        """Zwraca numer aktualnej ramki animacji."""
        return self._anim_sprite.get_frame_i(time - self._anim_time)

    def hit_test(self, position):
        """Zwraca true jeśli pozycja position znajduje się z obszarze obiektu."""
        delta_x = position.x - self._position.x
        delta_y = position.y - self._position.y
        sq_dist = delta_x * delta_x + delta_y * delta_y
        return sq_dist < self._radius

    def get_position(self):
        """Zwraca pozycje obiektu."""
        return self._position

    def set_position(self, position):
        """Ustawia pozycje obiektu."""
        self._position = position

    def get_environment(self):
        """Zwraca środowisko obiektu."""
        return self._environment
        
    def get_direction(self):
        """Zwraca kierunek w którym patrzy obiekt."""
        return self._direction
        
    def set_direction(self, new_direction):
        """Ustawia kierunek obiektu."""
        if new_direction.length() > 0.01:
            self._direction = new_direction.normal()
            
    def set_environment(self, environment):
        """Ustawia środowisko obiektu."""
        self._environment = environment

    def get_icon(size):
        """Zwraca ikone obiektu, dla edytora."""
        return pygame.Surface(size.intcpl(), SRCALPHA)

    def attack(self, object):
        """Atakuje inny obiekt."""
        object.suffer_dmg(self.DAMAGE_ON_HIT, self.DMG_TYPE)
        
    def suffer_dmg(self, amount, type):
        """Zmniejsza "życie" obiektu o amount."""
        self._health -= amount/self.hp * (1-self.Resistance[type])
        
    def is_dead(self):
        """Odpytuje efekt czy jest martwy (umierajacy)"""
        return self._health < 0.0
            
    def get_path(self):
        """Zwraca sciezke ktora podaza obiekt"""
        return self._path
        
    def set_path(self,path):        
        """Ustawia sciezke ktora bedzie podazal obiekt """
        self._path = path
        if path != []:
            self._last_path_point = path[-1]
        
    def get_last_path_point(self):
        """Zwraca ostatni punkt sciezki ktora podaza obiekt"""
        return self._last_path_point
        
    def move_to(self, point, delta):
        """Symuluje ruch obiektu."""
        pos = self.get_position()
        new_direction = point - pos
        
        if new_direction.length() < DynamicObject.EPSILON:
            self.set_position(point)
            return True
        
        self.set_direction(new_direction)
           
        new_position = pos + self._direction * self._velocity * delta
        change = True
        
        for obj in self.get_environment().collidable():
            t = self._radius + obj._radius
            if dist(obj.get_position(), new_position) < t*t and self != obj and not obj._magic:
                change = False
                dest_point = new_position + (rotate2(new_position - obj.get_position(), (random() - 0.5) * 0.1)) * DynamicObject.KNOCKBACK
                self.set_position(dest_point)
                break
                
        if change:
            self.set_position(new_position)
                
        return False
        
    def notify(self, message):
        """Reakcja na bycie poinformowanym o czyms: domyslnie nie rob nic"""
        pass

class PlayerObject(DynamicObject):
    """Klasa obiektu gracza."""
    ATTACK = ObjectSprite("data/black mage/attack.png")
    INJURED = ObjectSprite("data/black mage/injured.png")
    CASTING = ObjectSprite("data/black mage/casting.png")
    RUNNING = ObjectSprite("data/black mage/running.png")
    STOPPED = ObjectSprite("data/black mage/paused.png")

    DEFAULT_HP = 100
    VISIBLE_IN_EDITOR = True

    def __init__(self):
        super(PlayerObject, self).__init__()
        self.animate(PlayerObject.RUNNING, 0.0)
        self.hp = PlayerObject.DEFAULT_HP
        self.dead = False

        self._path = []
        self._spell = None
        self._shield = 0.0
        self._shield_time = 10.0
        self._shield_type = WATER_SHIELD
        self._energy = 1.0
        self._score = 0

        self._shield_kind = "fire"
        
        DMG_TYPE = "air"
        Resistance = {"fire":0.2,  "water":0.2, "earth":0.2, "air":0.2}


    def update(self, delta, current):
        """Odświeża stan obiektu."""
        EPSILON = 0.0001
        old_pos = self._position
        new_pos = self._position

        self._health = min(self._health + HEALTH_FACTOR * delta, 1.0)
        self._energy = min(self._energy + ENERGY_FACTOR * delta, 1.0)

        while self._path != [] and EPSILON < delta:
            difference = self._path[-1] - new_pos
            step = self._velocity * delta
            diff = difference.length()
            if diff < step:
                delta = delta * (1.0 - (diff / step))
                new_pos = self._path.pop()
            else:
                new_pos += difference.normal() * self._velocity * delta
                delta = 0.0
            x = new_pos - old_pos
            c = False
            for object in self._environment.collidable():
                if object != self and not isinstance(object, BallEffect) and not isinstance(object, WaveEffect) and check_collision(self.get_position() + x, object.get_position(), self._radius, object._radius):
                    c = True
                    break
            if not c:
                self._position += x
                self._direction = (self._position - old_pos).normal()

            self.animate(PlayerObject.RUNNING, current)
        
        if self._shield != 0.0 and current - self._shield > self._shield_time:
            self._shield = 0.0

        FIRE_FRAME_INDEX = 8
        if self._spell and not self._fired and self.get_frame_index(current) > FIRE_FRAME_INDEX:
            self._add_spell(self._spell, current)
            self._fired = True

        if self._spell and self.finished():
            self._spell = None
       
    def redraw(self, surface, position, current, frames, pickable):
        """Odrysowuje obiekt."""
        if self._spell:
            self.animate(PlayerObject.CASTING, current, False)
        elif self._path == []:
            self.animate(PlayerObject.STOPPED, current)
        super(PlayerObject, self).redraw(surface, position, current, frames, pickable)
        if self._shield != 0.0:
            size = vec2(self._shield_type.get_size())
            dest = world_to_screen(self._position) - position
            dest.y = surface.get_size()[1] - dest.y - 28
            depth = dest.y
            dest -= size // 2
            frames.append(((self._shield_type, (0, 0) + size.intcpl()), depth + 31, dest.intcpl()))

    def goto(self, position):
        """Idzie do podanej pozycji o ile osiągalna."""
        if not self._spell:
            self._path = [vec2(x) for x in self._environment.findPath(position.intcpl(), self._position.intcpl())]
            if self._path != []:
                self._path.pop()
            if self._path != []:
                self._path[0] = position

    def cast(self, spell, enemy):
        """Rzuca zaklęcie."""
        if self._spell == None:
            self._spell = spell
            self._fired = False
            self._path = []
            if enemy != None:
                self.set_direction(enemy.get_position() - self.get_position())

    def suffer_dmg(self, amount, type):
        """Zadaje obiektowi obrażenia."""
        if self._shield != 0.0:
            amount *= SHIELD_FACTOR
            self.Resistance[self._shield_kind] += 0.05
        else:
            self.Resistance[self._shield_kind] = 0.2
        super(PlayerObject, self).suffer_dmg(amount, type)
        

    def get_icon(size):
        """Zwraca ikonę obiektu, musi być przesłonięte w każdej klasie pochodnej."""
        return PlayerObject.STOPPED.get_icon(size)

    def get_score(self):
        """Zwraca punkty gracza."""
        return self._score

    def add_score(self, score):
        """Zwiększa punkty gracza."""
        self._score += score

    def _add_spell(self, spell, current):
        OFFSET_FACTOR = 0.5
        element, type  = spell.split('_')

        if type == "shield":
            if self._energy < SHIELD_COST:
                return
            self._energy -= SHIELD_COST
            self._shield_kind = element
            SoundEffects.SpellSoundDict[element].play()
        elif type == "ball":
            if self._energy < BALL_COST:
                return
            self._energy -= BALL_COST
            SoundEffects.SpellSoundDict[element].play()
        elif type == "wave":
            if self._energy < WAVE_COST:
                return
            self._energy -= WAVE_COST
            SoundEffects.SpellSoundDict[element].play()

        if spell == "water_shield":
            self._shield = current
            self._shield_type = WATER_SHIELD
        elif spell == "fire_shield":
            self._shield = current
            self._shield_type = FIRE_SHIELD
        elif spell == "air_shield":
            self._shield = current
            self._shield_type = AIR_SHIELD
        elif spell == "earth_shield":
            self._shield = current
            self._shield_type = EARTH_SHIELD
        elif spell == "water_ball":
            object = BallEffect()
            object.set_direction(self._direction)
            object.set_position(self._position + self._direction * OFFSET_FACTOR)
            object.set_sprites(WATER_STARS)
            object.set_environment(self._environment)
            self._environment.add_object(object)
        elif spell == "fire_ball":
            object = BallEffect()
            object.set_direction(self._direction)
            object.set_position(self._position + self._direction * OFFSET_FACTOR)
            object.set_sprites(FIRE_STARS)
            object.set_environment(self._environment)
            self._environment.add_object(object)
        elif spell == "air_ball":
            object = BallEffect()
            object.set_direction(self._direction)
            object.set_position(self._position + self._direction * OFFSET_FACTOR)
            object.set_sprites(AIR_STARS)
            object.set_environment(self._environment)
            self._environment.add_object(object)
        elif spell == "earth_ball":
            object = BallEffect()
            object.set_direction(self._direction)
            object.set_position(self._position)
            object.set_sprites(EARTH_STARS)
            object.set_environment(self._environment)
            self._environment.add_object(object)
        elif spell == "water_wave":
            object = WaveEffect()
            object.set_position(self._position)
            object.set_sprites(WATER_CIRCLES)
            object.set_environment(self._environment)
            self._environment.add_object(object)
        elif spell == "fire_wave":
            object = WaveEffect()
            object.set_position(self._position)
            object.set_sprites(FIRE_CIRCLES)
            object.set_environment(self._environment)
            self._environment.add_object(object)
        elif spell == "air_wave":
            object = WaveEffect()
            object.set_position(self._position)
            object.set_sprites(AIR_CIRCLES)
            object.set_environment(self._environment)
            self._environment.add_object(object)
        elif spell == "earth_wave":
            object = WaveEffect()
            object.set_position(self._position)
            object.set_sprites(EARTH_CIRCLES)
            object.set_environment(self._environment)
            self._environment.add_object(object)

class Orc(DynamicObject):
    """Podstawowa klasa potworow"""
    ATTACK = ObjectSprite("data/ice troll/attack.png")
    INJURED = ObjectSprite("data/ice troll/disintegrate.png")
    RUNNING = ObjectSprite("data/ice troll/walking.png")
    STOPPED = ObjectSprite("data/ice troll/paused.png")
    INJ_ANIM_TIME = 2
    VICTORY_SCORE = 1
    DAMAGE_ON_HIT = 10
    HP = 30
    VISIBLE_IN_EDITOR = True

    def __init__(self, state = None):
        super(Orc, self).__init__()
        if state == None:
            state = AIIdle.get_state()
        self._state = state
        self.animate(self.STOPPED, 0.0)
        self.hp = Orc.HP
        self.dead = False
        self._monster_type = MonsterTypes.Melee
        
    def get_monster_type(self):
        """Zwraca typ potwora (z powodu braku silnego typowania jest to po prostu liczba"""
        return self._monster_type
   
    def update(self, delta, current):
        """Sprawdza i odpowiednio reaguje jesli potwor jest umierajacy i wykonuje strategie dana w stanie AI"""
        if self.dead:
            if self.finished():
                for player in self.get_environment().get_players():
                    player.add_score(self.VICTORY_SCORE)
                return True
            return False
        self._state = self._state.execute(self, current, delta)
        if self._health < 0:
            self.animate(self.INJURED, current, False)
            self.dead = True
        return False
    
    def get_icon(size):
        """Zwraca ikone potwora (dla edytora)."""
        return Orc.STOPPED.get_icon(size)

    def set_State(self,state):
        """Ustawia aktualny stan AI na dany"""
        self._state = state
        
    def get_State(self):
        """Zwraca aktualny stan AI"""
        return self._state
    
    def notify(self, state):
        """Reakcja na bycie poinformowanym zeby zmienic stan na dany jest odpowiednia zmiana stanu
            Kod ten mozna rozbudowac, by stworzyc bardziej skomplikowane AI"""
        self.set_State(state)

class GreyTroll(Orc):
    """Klasa szarego trolla."""
    ATTACK = ObjectSprite("data/grey troll/attack.png")
    INJURED = ObjectSprite("data/grey troll/disintegrate.png")
    RUNNING = ObjectSprite("data/grey troll/walking.png")
    STOPPED = ObjectSprite("data/grey troll/paused.png")
    INJ_ANIM_TIME = 2
    VICTORY_SCORE = 1
    DAMAGE_ON_HIT = 10
    HP = 30
    VISIBLE_IN_EDITOR = True
        
    def __init__(self, state = None):
        super(GreyTroll, self).__init__(state)
        
    def get_icon(size):
        return GreyTroll.STOPPED.get_icon(size)

class Swampthing(Orc):
    """Klasa potwora z bagien."""
    ATTACK = ObjectSprite("data/swampthing/attack.png")
    INJURED = ObjectSprite("data/swampthing/tipping.png")
    RUNNING = ObjectSprite("data/swampthing/running.png")
    STOPPED = ObjectSprite("data/swampthing/paused.png")
    INJ_ANIM_TIME = 2
    VICTORY_SCORE = 1
    DAMAGE_ON_HIT = 10
    HP = 30
    VISIBLE_IN_EDITOR = True
        
    def __init__(self, state = None):
        super(Swampthing, self).__init__(state)
        
    def get_icon(size):
        return Swampthing.STOPPED.get_icon(size)

class GreenZombie(Orc):
    """Klasa zielonego zombie."""
    ATTACK = ObjectSprite("data/green zombie/attack.png")
    INJURED = ObjectSprite("data/green zombie/disintegrate.png")
    RUNNING = ObjectSprite("data/green zombie/walking.png")
    STOPPED = ObjectSprite("data/green zombie/knit.png")
    INJ_ANIM_TIME = 2
    VICTORY_SCORE = 1
    DAMAGE_ON_HIT = 10
    HP = 30
    VISIBLE_IN_EDITOR = True
        
    def __init__(self, state = None):
        super(GreenZombie, self).__init__(state)
        
    def get_icon(size):
        return GreenZombie.STOPPED.get_icon(size)

class GreenArcher(Orc):
    """Klasa zielonego łucznika."""
    ATTACK = ObjectSprite("data/green archer/shooting.png")
    INJURED = ObjectSprite("data/green archer/tipping.png")
    RUNNING = ObjectSprite("data/green archer/running.png")
    STOPPED = ObjectSprite("data/green archer/paused.png")
    DAMAGE_ON_HIT = 2
    HP = 20
    VISIBLE_IN_EDITOR = True

    def __init__(self, state = AIIdle()):
        super(GreenArcher, self).__init__(state)
        self.hp = GreenArcher.HP
        self._monster_type = MonsterTypes.Ranged
        self._velocity = 3.0

    def shoot(self):
        """Wykonuje strzał."""
        arrow = ArrowEffect()
        arrow.set_position(self.get_position()+self.get_direction()*2)
        arrow.set_direction(self.get_direction())
        self.get_environment().add_object(arrow)
        arrow.set_environment(self.get_environment())
   
    def get_icon(size):
        return GreenArcher.STOPPED.get_icon(size)

class RedArcher(GreenArcher):
    """Klasa czerwonego łucznika."""
    ATTACK = ObjectSprite("data/red archer/shooting.png")
    INJURED = ObjectSprite("data/red archer/tipping.png")
    RUNNING = ObjectSprite("data/red archer/running.png")
    STOPPED = ObjectSprite("data/red archer/paused.png")
    DAMAGE_ON_HIT = 2
    HP = 20
    VISIBLE_IN_EDITOR = True

    def __init__(self, state = AIIdle()):
        super(RedArcher, self).__init__(state)
        self.hp = RedArcher.HP
        self._monster_type = MonsterTypes.Ranged
        self._velocity = 4.0
   
    def get_icon(size):
        return RedArcher.STOPPED.get_icon(size)

class BallEffect(DynamicObject):
    """Klasa efektu kuli żywiołu."""
    TIMEOUT = 0.20
    VELOCITY = 1.5
    DAMAGE_ON_HIT = 15
    
    class Particle:
        def __init__(self):
            self.reset(-BallEffect.TIMEOUT)

        def reset(self, current):
            self.time = current + (random() - 0.5) * 0.2
            self.dir = rotate2(vec2(0.0, 1.0), random() * pi * 2) * BallEffect.VELOCITY
            self.pos = vec2(0.0, 0.0)

    def __init__(self, number = 48):
        super(BallEffect, self).__init__()
        self._particles = [BallEffect.Particle() for x in range(number)]
        self._old_time = 0.0
        self._velocity = 6.0
        self._longevity = 2.0
        self._sprites = WATER_STARS
        self._magic = True

    def set_sprites(self, sprites):
        """Ustawia "duszki" cząsteczek."""
        self._sprites = sprites

    def set_longevity(longevity):
        """Ustawia czas trwania efektu."""
        self._longevity = longevity

    def update(self, delta, current):
        """Odświeża stan efektu."""
        self._longevity -= delta
        for obj in self.get_environment().collidable():
            t = self._radius + obj._radius
            if dist(obj.get_position(), self.get_position()) < t and self != obj and not isinstance(obj, PlayerObject) and not obj._magic:
                obj.suffer_dmg(self.DAMAGE_ON_HIT, self.DMG_TYPE)
                return True
        if self._longevity < 0:
            return True
        else:
            return super(BallEffect, self).update(delta, current)

    def redraw(self, surface, position, current, frames, pickable):
        """Odrysowuje efekt."""
        delta = current - self._old_time
        self._old_time = current
        real_size = self._sprites[0].get_size()
        half_size = vec2(real_size) // 2
        i, s = 0, len(self._particles)
        while i < s:
            if current - self._particles[i].time > BallEffect.TIMEOUT:
                self._particles[i].reset(current)
            else:
                self._particles[i].pos += self._particles[i].dir * delta
            dest = world_to_screen(self._particles[i].pos + self._position) - position - half_size 
            index = int(clamp((current - self._particles[i].time) / BallEffect.TIMEOUT, 0.0, 0.99) * len(self._sprites))
            dest.y = surface.get_size()[1] - dest.y - 32
            frames.append(((self._sprites[index], (0, 0) + real_size), dest.y + 16, dest.intcpl()))
            i += 1

class WaveEffect(DynamicObject):
    """Klasa efektu fali żywiołu."""
    VELOCITY = 6.0
    DAMAGE_ON_HIT = 1
    
    class Particle:
        def reset(self, direction):
            self.dir = direction

    def __init__(self, number = 96):
        super(WaveEffect, self).__init__()
        self._particles = [WaveEffect.Particle() for x in range(number)]
        self._radius = 0.25
        self._max_radius = 5.0
        self.set_sprites(FIRE_CIRCLES)
        self._magic = True
        
    def set_sprites(self, sprites):
        """Ustawia "duszki" cząsteczek."""
        i, s = 0, len(self._particles)
        while i < s:
            self._particles[i].reset(rotate2(vec2(0.0, 1.0), random() * pi * 2))
            i += 1
        self._sprites = sprites
        self._velocity = 0.0

    def set_max_radius(self, max_radius):
        """Ustawia maxymalny zasięg."""
        self._max_radius = max_radius

    def update(self, delta, current):
        """Odświeża stan efektu."""
        self._radius += delta * WaveEffect.VELOCITY
        for obj in self.get_environment().collidable():
            t = self._radius + obj._radius
            m = abs(self._radius - obj._radius)
            distance = dist(obj.get_position(), self.get_position())
            if self != obj and distance < t and distance > m and not isinstance(obj, PlayerObject) and not obj._magic:
                obj.suffer_dmg(self.DAMAGE_ON_HIT, self.DMG_TYPE)
      
        if self._radius > self._max_radius:
            return True
        else:
            return super(WaveEffect, self).update(delta, current)

    def redraw(self, surface, position, current, frames, pickable):
        """Odrysowuje obiekt."""
        real_size = self._sprites[0].get_size()
        half_size = vec2(real_size) // 2

        i, s = 0, len(self._particles)
        while i < s:
            dest = world_to_screen(self._particles[i].dir * self._radius + self._position) - position
            index = int(clamp(self._radius / self._max_radius, 0.0, 0.99) * len(self._sprites))
            dest.y = surface.get_size()[1] - dest.y
            frames.append(((self._sprites[index], (0, 0) + real_size), dest.y + 16, dest.intcpl()))
            i += 1

class ArrowEffect(DynamicObject):
    """Klasa strzały."""
    TIMEOUT = 0.20
    VELOCITY = 1.5
    DAMAGE_ON_HIT = 5
    SPRITE = ObjectSprite("data/arrow.png")

    def __init__(self, number = 48):
        super(ArrowEffect, self).__init__()
        self._velocity = 7.0
        self._longevity = 2.0
        self._health = -1
        self.animate(ArrowEffect.SPRITE, 0.0)
        self._magic = True

    def set_sprites(self, sprites):
        """Ustawia duszka strzały."""
        self._sprites = sprites

    def set_longevity(longevity):
        """Ustawia czas życia strzały."""
        self._longevity = longevity

    def update(self, delta, current):
        """Odświeża stan strzały."""
        self._longevity -= delta
        for obj in self.get_environment().collidable():
            t = self._radius + obj._radius
            if dist(obj.get_position(), self.get_position()) < t and self != obj and not obj._magic:
                obj.suffer_dmg(self.DAMAGE_ON_HIT, self.DMG_TYPE)
                return True
        if self._longevity < 0:
            return True
        else:
            return super(ArrowEffect, self).update(delta, current)

DYNAMIC_OBJECTS = [x[1] for x in getmembers(modules[__name__], lambda member: isclass(member) and member.__module__ == __name__) if x[1].VISIBLE_IN_EDITOR]
