from ursina import *
from perlin_noise import PerlinNoise
import math

from ursina.prefabs.first_person_controller import FirstPersonController

app = Ursina()

# === Параметры острова ===
MAP_SIZE = 80
CHUNK_SIZE = 16
RENDER_DISTANCE = 3
MAX_HEIGHT = 12
PERLIN_SCALE = 35
CENTER_X = MAP_SIZE // 2
CENTER_Z = MAP_SIZE // 2

noise = PerlinNoise(octaves=3, seed=2023131)
loaded_chunks = {}

# === Маска расстояния от центра ===
def distance_mask(x, z):
    dx = x - CENTER_X
    dz = z - CENTER_Z
    distance = math.sqrt(dx**2 + dz**2)
    max_dist = math.sqrt((MAP_SIZE / 2)**2 + (MAP_SIZE / 2)**2)
    return 1 - (distance / max_dist)  # ближе к центру — выше

# === Генерация чанка ===
def generate_chunk(cx, cz):
    if (cx, cz) in loaded_chunks:
        return

    chunk_entities = []

    for x in range(CHUNK_SIZE):
        for z in range(CHUNK_SIZE):
            world_x = cx * CHUNK_SIZE + x
            world_z = cz * CHUNK_SIZE + z

            if world_x >= MAP_SIZE or world_z >= MAP_SIZE:
                continue

            noise_val = noise([world_x / PERLIN_SCALE, world_z / PERLIN_SCALE])
            mask_val = distance_mask(world_x, world_z)
            height = int((noise_val + 1) / 2 * mask_val * MAX_HEIGHT)

            for y in range(height):
                if height < 2:
                    c = color.rgb(30, 120, 250)  # вода
                elif y < 3:
                    c = color.rgb(80, 200, 80)  # берег
                elif y < 6:
                    c = color.rgb(100, 160, 60)  # холмы
                else:
                    c = color.rgb(120, 120, 120)  # скалы

                e = Entity(
                    model='cube',
                    color=c,
                    texture='white_cube',
                    position=(world_x, y, world_z),
                    scale=1,
                    collider='box'
                )
                chunk_entities.append(e)

    loaded_chunks[(cx, cz)] = chunk_entities

def destroy_chunk(cx, cz):
    for e in loaded_chunks[(cx, cz)]:
        destroy(e)
    del loaded_chunks[(cx, cz)]

# === Камера ===
class FreeCam(Entity):
    def __init__(self):
        super().__init__()
        self.controller = FirstPersonController()
        self.controller.gravity = 0
        self.controller.cursor.visible = False
        self.prev_chunk = None
        self.controller.speed = 5

    def update(self):
        pos = self.controller.position
        chunk_x = int(pos.x) // CHUNK_SIZE
        chunk_z = int(pos.z) // CHUNK_SIZE
        current_chunk = (chunk_x, chunk_z)

        for dx in range(-RENDER_DISTANCE, RENDER_DISTANCE + 1):
            for dz in range(-RENDER_DISTANCE, RENDER_DISTANCE + 1):
                generate_chunk(chunk_x + dx, chunk_z + dz)

        if self.prev_chunk != current_chunk:
            to_remove = []
            for (cx, cz) in list(loaded_chunks):
                if abs(cx - chunk_x) > RENDER_DISTANCE or abs(cz - chunk_z) > RENDER_DISTANCE:
                    to_remove.append((cx, cz))
            for chunk in to_remove:
                destroy_chunk(*chunk)
            self.prev_chunk = current_chunk

        # управление вверх/вниз
        if held_keys['space']:
            self.controller.y += time.dt * 5
        if held_keys['left shift']:
            self.controller.y -= time.dt * 5
        if held_keys['escape']:
            application.quit()

camera = FreeCam()

# свет и небо
DirectionalLight().look_at(Vec3(1, -1, -1))
Sky()

app.run()
