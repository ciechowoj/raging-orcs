from ObjectSprite import *
from TerrainGrid import *
from StaticObjects import *
from DynamicObject import *
from LevelLoader import *
from IMGUI import *
from queue import PriorityQueue

EMPTY_TILE = 0
MARGIN_SIZE = vec2(TILE_SIZE.x * 4, TILE_SIZE.y * 4)
MAX_OBJECT_SIZE = 128
UPDATE_OBJECT_RANGE = 64
REDRAW_OBJECT_RADIUS = 20

class Environment:
    """Klasa reprezentująca środowisko gry."""

    FIND_PATH_MAX_DIST = 200
    WARN_DISTANCE = 100
    """
    Stala okreslajaca jaka najdluzsza droge moze zwrocic findPath (Poprawia wydajnosc - nizsza stala = mniej szukania)
    """
    
    def __init__(self, tile_size = TILE_SIZE):
        # environment
        self._terrain_grid = TerrainGrid(tile_size)
        self._static_objects = StaticObjects()
        self._dynamic_objects = []

        # buffers for drawing
        self._previous_buffer = None
        self._current_buffer = None
        self._prev_viewport_pos = vec2(-0xfffffff, -0xfffffff)

        # surface cache
        self._PAGE_SIZE = vec2(320, 240)
        self._cache_size = 0
        self._cache_pages = []
        self._frame_number = 0
        self._visible_objects = []
        self._pickable_objects = []
        self._players = []

        self.resize(vec2(50, 50))
        
    def load(self, loader):
        """Wczytuje mapę z podanego loadera."""
        self._terrain_grid = loader.get_terrain_grid()
        self._static_objects = loader.get_static_objects()
        self._dynamic_objects = loader.get_dynamic_objects()
        self._players = []
        for x in self._dynamic_objects:
            if isinstance(x, PlayerObject):
                self._players.append(x)
            x.set_environment(self)

    def save(self, loader):
        """Zapisuje mapę do podenego loadera."""
        loader.set_terrain_grid(self._terrain_grid)
        loader.set_static_objects(self._static_objects)
        loader.set_dynamic_objects(self._dynamic_objects)

    def resize(self, size):
        """Zmienia rozmiar środowiska."""
        self._terrain_grid.set_size(size)
        self._static_objects.set_size(size)
        i, s = 0, len(self._dynamic_objects)
        while i < s:
            position = self._dynamic_objects[i].get_position()
            if position.x < 0 or position.y < 0 or size.x <= position.x or size.y <= position.y:
                del self._dynamic_objects[i]
                s -= 1
            else:
                i += 1

    def notify(self, message, position):
        """Powiadamia wszystkie obiekty o czyms"""
        for object in self._dynamic_objects:
            if dist(object.get_position(), position) < Environment.WARN_DISTANCE:
                object.notify(message)
            
    def reachable(self, point):
        """Okresla czy do danego punktu (kwadratu) terenu da sie wejsc - identyczna z is_reachable"""
        return not self._terrain_grid.get_flags(point.ifloor())

    def update(self, delta, current):
        """Odświeża stan środowiska."""
        update_radius_sq = UPDATE_OBJECT_RANGE * UPDATE_OBJECT_RANGE
        position = vec2()
        if self._players != []:
            position = self._players[0].get_position()
        i, s = 0, len(self._dynamic_objects)
        while i < s:
            d_pos = position - self._dynamic_objects[i].get_position()
            radius_sq = d_pos.lengthsq()
            if radius_sq < update_radius_sq:
                if self._dynamic_objects[i].update(delta, current):
                    self._dynamic_objects[i] = self._dynamic_objects[-1]
                    self._dynamic_objects.pop()
                    s -= 1
                else:
                    i += 1
            else:
                i += 1

    def redraw(self, surface, position, time, collisions = False):
        """Odrysowywuje środowisko."""
        self._create_buffers(surface)
        
        surface_size = vec2(surface.get_size())
        viewport_pos = (world_to_screen(position) - surface_size / 2).floor()
        displacement = self._prev_viewport_pos - viewport_pos
        displacement.y = -displacement.y

        self._current_buffer.fill((0, 0, 255, 0))
        self._current_buffer.blit(self._previous_buffer, displacement.intcpl())

        self._terrain_grid.redraw(self._current_buffer, viewport_pos - MARGIN_SIZE, time, collisions)

        surface.blit(self._current_buffer, (-MARGIN_SIZE).intcpl())

        first = viewport_pos // self._PAGE_SIZE
        last = (viewport_pos + surface_size) // self._PAGE_SIZE + vec2(1, 1)

        self._visible_objects = []
        self._pickable_objects = []
        self._static_objects.redraw(surface, viewport_pos, self._visible_objects)

        self._prev_viewport_pos = viewport_pos

        # cull invisible objects
        redraw_radius_sq = REDRAW_OBJECT_RADIUS * REDRAW_OBJECT_RADIUS
        for object in self._dynamic_objects:
            d_pos = position - object.get_position()
            radius_sq = d_pos.lengthsq()
            if radius_sq < redraw_radius_sq:
                object.redraw(surface, viewport_pos, time, self._visible_objects, self._pickable_objects)
        
        self._visible_objects.sort(key = lambda x: x[1])
        for object in self._visible_objects:
            surface.blit(object[0][0], object[2], object[0][1])

        self._swap_buffers()

    def pick(self, position):
        """Zwraca listę obiektów na danej pozycji."""
        result = []
        for object in self._pickable_objects:
            region = object[1]
            if region_hit(region, position):
                result.append(object[0])
        return result

    def get_players(self):
        """Zwraca obiekty gracza (zwykle jeden)."""
        return self._players

    def add_object(self, object):
        """Dodaje obiekt do środowiska."""
        self._dynamic_objects.append(object)

    def collidable(self):
        """Zwraca obiekty ktore wchodzą w kolizje."""
        return self._dynamic_objects

    def is_reachable(self, position):
        """Sprawdza czy dana pozycja jest osiągalna, czy da się tam wejść."""
        return not self._terrain_grid.get_flags(position)

    def is_clear(self):
        return len(self._dynamic_objects) == 1

    def _create_buffers(self, surface):
        surface_size = vec2(surface.get_size())
        required_size = surface_size + MARGIN_SIZE * 2
        if self._previous_buffer == None:
            self._previous_buffer = pygame.Surface(required_size.intcpl())
            self._previous_position = vec2(-0xfffffff, -0xfffffff)
        if self._current_buffer == None:
            self._current_buffer = pygame.Surface(required_size.intcpl())
    
    def _swap_buffers(self):
        tmp = self._current_buffer
        self._current_buffer = self._previous_buffer
        self._previous_buffer = tmp

    #returns table with points (nodes) to go through
    def findPath(self, startPoint, endPoint):
        """
        Zwraca droge z punktu startowego do koncowego omijajaca wszystkie niedostepne statyczne czesci terenu.
        NIE OMIJA OBIEKTOW DYNAMICZNYCH
        W przypadku braku drogi zwraca liste pusta
        Stala srodowiska FIND_PATH_MAX_DIST okresla jaka najdluzsza droge findPath bedzie rozwazal, przestaje szukac i zwraca liste pusta w przypadku gdy przewidywana dlugosc trasy przekroczy ta stala.
        Jesli punkt startowy lub koncowy sa nieosiagalne stara sie znalezc osiagalny punkt w ich sasiedztwie.
        Zwraca [] i wypisuje na konsole blad jesli nie znajdzie
        """
        def pairPlus(pair1, pair2):
            a1,b1 = pair1
            a2,b2 = pair2
            return (a1+a2, b1+b2)
    
        def manhattanDis(pair1, pair2):
            a1,b1 = pair1
            a2,b2 = pair2
            t0 = a2-a1
            t1 = b2-b1
            return ((t0*t0+t1*t1))
        
        def seqPlus(table, pair):
            tableNew = table[:]
            tableNew.append(pair)
            return tableNew

        def filter(f, table):
            newTable = []
            for obj in table:
                if f(obj):
                    newTable.append(obj)
            return newTable
         
        def findPathAux(self, startPoint, endPoint):
            reached = set()
            unchecked = PriorityQueue()
            
            moves = {(i,j) for i in [-1,0,1] for j in [-1,0,1]}
            moves.remove((0,0))
            
            count=0
            unchecked.put((0,startPoint,[]))
            while not unchecked.empty():
                prior, point, seq = unchecked.get()
      
                if point == endPoint:
                    return seq
                
                #odcinaj jesli przewidywana droga bedzie zbyt dluga
                if prior > self.FIND_PATH_MAX_DIST:
                    return []
                              
                if not point in reached:
                    reached.add(point)
                    for move in moves:
                        pointNew = pairPlus(point, move)
                        if self.reachable(vec2(pointNew)):
                            seqNew = seqPlus(seq, move)
                            unchecked.put((manhattanDis(pointNew, endPoint), pointNew, seqNew))
        startPointVec = vec2(startPoint)
        if not self.reachable(startPointVec):
            rpoints = filter(self.reachable, [startPointVec + vec2(i,j) for i in [-1,0,1] for j in [-1,0,1]])
            if rpoints != []:
                startPoint = rpoints[0].couple()
            else:
                print("FindPath Error: startPoint unreachable and has not reachable neighbours")
                return []
        endPointVec = vec2(endPoint)
        if not self.reachable(endPointVec):
            rpoints = filter(self.reachable, [endPointVec + vec2(i,j) for i in [-1,0,1] for j in [-1,0,1]])
            if rpoints != []:
                endPoint = rpoints[0].couple()
            else:
                print("FindPath Error: endPoint unreachable and has not reachable neighbours")
                return []
                
        seq = findPathAux(self, startPoint, endPoint)
        if seq == None: 
            print("FindPath Error: None path of given length exists")
            return []
        seqNew = []
        acc = last = startPoint
        for move in seq:
            if move == last:
                acc = pairPlus(acc, last)
            else:
                seqNew = seqPlus(seqNew, acc)
                last = move
                acc = pairPlus(acc,move)
        seqNew = seqPlus(seqNew, endPoint)
        return [(x[0] + 0.49, x[1] + 0.49) for x in seqNew]
        #return seqNew

    def redraw_path(self, surface, position, path):
        """Funkcja pomocnicza rysuje ścieżkę na mapie. Przydatna przy debugowaniu."""
        surface_size = vec2(surface.get_size())
        i, s = 0, len(path) - 1
        while i < s:
            first = world_to_screen(vec2(path[i]) + vec2(0.5, 0.5))
            second = world_to_screen(vec2(path[i + 1]) + vec2(0.5, 0.5))
            first -= position
            second -= position
            first.y = surface_size.y - first.y
            second.y = surface_size.y - second.y
            pygame.draw.line(surface, (255, 0, 0), first.intcpl(), second.intcpl())
            i += 1
