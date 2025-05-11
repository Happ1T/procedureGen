from ursina import *
from perlin_noise import PerlinNoise
import math

from ursina.prefabs.first_person_controller import FirstPersonController

app = Ursina()

# === Настройки ===
CHUNK_SIZE = 8
RENDER_DISTANCE = 3  # количество чанков от игрока по каждому направлению
TERRAIN_HEIGHT = 10
PERLIN_PERIOD = 30
PERLIN_AMP = TERRAIN_HEIGHT
noise = PerlinNoise(octaves=2, seed=42132)

loaded_chunks = {}

# === Генерация одного чанка ===
def generate_chunk(cx, cz):
    if (cx, cz) in loaded_chunks:
        return

    chunk_entities = []

    for x in range(CHUNK_SIZE):
        for z in range(CHUNK_SIZE):
            world_x = cx * CHUNK_SIZE + x
            world_z = cz * CHUNK_SIZE + z

            raw = noise([world_x / PERLIN_PERIOD, world_z / PERLIN_PERIOD])
            height = int((raw + 1) / 2 * PERLIN_AMP)

            for y in range(height):
                # Цвет по высоте
                if y < 2:
                    block_color = color.rgb(0, 150, 255)     # вода
                elif y < 3:
                    block_color = color.rgb(50, 200, 50)     # равнина
                elif y < 5:
                    block_color = color.rgb(150, 75, 0)      # холмы
                else:
                    block_color = color.rgb(130, 130, 130)   # горы

                e = Entity(
                    model='cube',
                    texture='white_cube',
                    color=block_color,
                    position=(world_x, y, world_z),
                    scale=1,
                    collider='box'
                )
                chunk_entities.append(e)

    loaded_chunks[(cx, cz)] = chunk_entities

# === Удаление чанка ===
def destroy_chunk(cx, cz):
    for e in loaded_chunks[(cx, cz)]:
        destroy(e)
    del loaded_chunks[(cx, cz)]

# === Управление камерой ===
class FreeCamera(Entity):
    def __init__(self):
        super().__init__()
        self.controller = FirstPersonController()
        self.controller.gravity = 0
        self.controller.cursor.visible = False
        self.controller.speed = 5
        self.prev_chunk = None

    def update(self):
        pos = self.controller.position
        chunk_x = int(pos.x) // CHUNK_SIZE
        chunk_z = int(pos.z) // CHUNK_SIZE
        current_chunk = (chunk_x, chunk_z)

        # Генерация чанков рядом
        for dx in range(-RENDER_DISTANCE, RENDER_DISTANCE + 1):
            for dz in range(-RENDER_DISTANCE, RENDER_DISTANCE + 1):
                generate_chunk(chunk_x + dx, chunk_z + dz)

        # Удаление далеких чанков
        if self.prev_chunk != current_chunk:
            to_remove = []
            for (cx, cz) in loaded_chunks:
                if abs(cx - chunk_x) > RENDER_DISTANCE or abs(cz - chunk_z) > RENDER_DISTANCE:
                    to_remove.append((cx, cz))
            for chunk in to_remove:
                destroy_chunk(*chunk)
            self.prev_chunk = current_chunk

        # Подъем / спуск
        if held_keys['space']:
            self.controller.y += time.dt * 5
        if held_keys['left shift']:
            self.controller.y -= time.dt * 5
        if held_keys['escape']:
            application.quit()

camera_controller = FreeCamera()

# Свет и небо
DirectionalLight().look_at(Vec3(1, -1, -1))
Sky()

app.run()
