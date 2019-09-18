from TerrainGrid import *
from ObjectSprite import *
from DynamicObject import *
from StaticObjects import *

class LevelLoader:
    """Klasa bazowa loadera map. Implementuje wzorzec fabryka. Buduje środowisko gry na podstawie zadanego pliku z mapą."""
    def __init__(self):
        self._terrain_grid_sprites = []
        self._static_object_sprites = []
        self._terrain_grid = None
        self._static_objects = None
        self._dynamic_objects = []

    def load(self, file_name):
        """Wczytuje mapę."""
        return None

    def save(self, file_name):
        """Zapisuje mapę."""
        pass

    def get_terrain_grid_sprites(self):
        """Zwraca "duszki" kafli podłoża."""
        return self._terrain_grid_sprites

    def get_static_object_sprites(self):
        """Zwraca "duszki" obiektów statycznych."""
        return self._static_object_sprites

    def get_terrain_grid(self):
        """Zwraca podłoża."""
        return self._terrain_grid

    def get_static_objects(self):
        """Zwraca kolekcje obiektów statycznych."""
        self._static_objects.set_sprites(self._static_object_sprites)
        return self._static_objects

    def get_dynamic_objects(self):
        """Zwraca listę obiektów dynamicznych."""
        return self._dynamic_objects
    
    def set_terrain_grid(self, terrain_grid):
        """Ustawia podłoże."""
        terrain_grid_sprites = dict()
        for v in area(terrain_grid.get_size()):
            tile = terrain_grid.get_tile(v)
            terrain_grid_sprites[tile.get_file_name()] = tile
        self._terrain_grid_sprites = list(terrain_grid_sprites.values())
        self._terrain_grid = terrain_grid

    def set_static_objects(self, static_objects):
        """Ustawia kolekcje obiektów statycznych."""
        self._static_object_sprites = static_objects.get_sprites()
        self._static_objects = static_objects

    def set_dynamic_objects(self, dynamic_objects):
        """Ustawia listę obiektów dynamicznych."""
        self._dynamic_objects = dynamic_objects

class TxtLevelLoader(LevelLoader):
    """Implementuje tekstowy format mapy gry."""
    def load(self, file_name):
        # vr <version>
        # pp <width> <height>
        # ts <file_name>
        # os <file_name>
        # t <x> <y> <flags> <tile_sprite>
        # s <x> <y> <t> <static_sprite>
        # d <class_name> <x> <y>
        self._dynamic_objects = []
        file = open(file_name, "r")
        for line in file.readlines():
            if line.startswith("pp"):
                self._terrain_grid = TerrainGrid()
                self._static_objects = StaticObjects()
                width, height = int(line.split()[1].strip()), int(line.split()[2].strip())
                self._terrain_grid.set_size(vec2(width, height))
                self._static_objects.set_size(vec2(width, height))
            elif line.startswith("ts"):
                self._terrain_grid_sprites.append(TileSprite(line.split()[1].strip()))
            elif line.startswith("os"):
                self._static_object_sprites.append(ObjectSprite(line.split()[1].strip()))
            elif line.startswith("t"):
                split = [x.strip() for x in line.split()]
                position = vec2(int(split[1]), int(split[2]))
                flags, sprite = split[3] == "True", int(split[4])
                self._terrain_grid.set_tile(position, self._terrain_grid_sprites[sprite])
                self._terrain_grid.set_flags(position, flags)
            elif line.startswith("s"):
                split = [x.strip() for x in line.split()]
                position = vec2(int(split[1]) * 0.01, int(split[2]) * 0.01)
                num_frame = int(split[3])
                sprite = int(split[4])
                sector = (position / SECTOR_SIZE).floor()
                self._static_objects.get_sector(vec2(int(position.x), int(position.y)) // SECTOR_SIZE).append((position, num_frame, self._static_object_sprites[sprite]))
            elif line.startswith("d"):
                split = [x.strip() for x in line.split()]
                class_name = split[1]
                position = vec2(int(split[2]) * 0.01, int(split[3]) * 0.01)
                object = eval(class_name + "()")
                object.set_position(position)
                self._dynamic_objects.append(object)

    def save(self, file_name):
        terrain_grid_sprites = dict()
        for i in range(len(self._terrain_grid_sprites)):
            terrain_grid_sprites[self._terrain_grid_sprites[i].get_file_name()] = i
        static_objects_sprites = dict()
        for i in range(len(self._static_object_sprites)):
            static_objects_sprites[self._static_object_sprites[i]] = i
        file = open(file_name, "w+")
        file.write("RapingOrcsWithGreatMagic v0.1\n")
        file.write("pp " + str(self._terrain_grid.get_size().x) + " " + str(self._terrain_grid.get_size().x) + "\n")
        for x in self._terrain_grid_sprites:
            file.write("ts " + x.get_file_name() + "\n")

        for x in self._static_object_sprites:
            file.write("os " + x.get_file_name() + "\n")

        for v in area(self._terrain_grid.get_size()):
            flags = self._terrain_grid.get_flags(v)
            sprite = self._terrain_grid.get_tile(v)
            file.write("t " + str(v.x) + " " + str(v.y) + " " + str(flags) + " " + str(terrain_grid_sprites[sprite.get_file_name()]) + "\n")

        for o in self._dynamic_objects:
            position = o.get_position()
            class_name = o.__class__.__name__
            x = str(floor(position.x * 100))
            y = str(floor(position.y * 100))
            file.write("d " + class_name + " " + x + " " + y + "\n")

        size_in_sectors = self._static_objects.get_size()
        for y in range(size_in_sectors.y):
            for x in range(size_in_sectors.x):
                for i in self._static_objects.get_sector(vec2(x, y)):
                    xp = str(floor(i[0].x * 100))
                    yp = str(floor(i[0].y * 100))
                    rt = str(i[1])
                    sprite = str(static_objects_sprites[i[2]])
                    file.write("s " + xp + " " + yp + " " + rt + " " + sprite + "\n")
