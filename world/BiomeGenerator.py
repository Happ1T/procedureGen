import random
from ursina import Vec2

class BiomeGenerator:
    def __init__(self, map_size, seed, iterations=2):
        self.biome_types = ['forest', 'lake', 'field', 'mountain']
        print (len(self.biome_types))
        self.map_size = map_size
        self.num_biomes =int( map_size / 16)
        self.iterations = iterations
        self.seed = seed
        random.seed(seed)
        self.biome_centers = [Vec2(random.uniform(0, map_size), random.uniform(0, map_size)) for _ in range(self.num_biomes)]
        self.biome_map = [[None for _ in range(map_size)] for _ in range(map_size)]
        self.relax_centers()
        self.assign_biomes()

    def relax_centers(self):

        for _ in range(self.iterations):
            # Инициализация пустых зон для каждого центра
            regions = [[] for _ in range(self.num_biomes)]
            for x in range(self.map_size):
                for y in range(self.map_size):
                    nearest = min(range(self.num_biomes),
                                  key=lambda i: (Vec2(x, y) - self.biome_centers[i]).length_squared())
                    regions[nearest].append(Vec2(x, y))

            # Пересчитываем центры как центроиды своих регионов
            for i, region in enumerate(regions):
                if region:
                    avg_x = sum(p.x for p in region) / len(region)
                    avg_y = sum(p.y for p in region) / len(region)
                    self.biome_centers[i] = Vec2(avg_x, avg_y)

    def assign_biomes(self):

        for i, center in enumerate(self.biome_centers):
            biome_type = self.biome_types[i % len(self.biome_types)]
            for x in range(self.map_size):
                for y in range(self.map_size):
                    current = Vec2(x, y)
                    nearest = min(range(self.num_biomes),
                                  key=lambda j: (current - self.biome_centers[j]).length_squared())
                    if nearest == i:
                        self.biome_map[x][y] = biome_type

    def get_biome(self, x, z):

        if 0 <= x < self.map_size and 0 <= z < self.map_size:
            return self.biome_map[x][z]
        return 'field'  # биом по умолчанию

    def get_biome_blend_info(self, x, z):
        current = Vec2(x, z)
        dists = sorted([(i, (current - center).length_squared()) for i, center in enumerate(self.biome_centers)], key=lambda t: t[1])
        return dists[0][0], dists[1][0], dists[0][1], dists[1][1]
