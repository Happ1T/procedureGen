from ursina import *
from ursina.prefabs.first_person_controller import FirstPersonController
from perlin_noise import PerlinNoise
from concurrent.futures import ThreadPoolExecutor
import math
import random
from PIL import Image as PILImage

app = Ursina()

# === Параметры ===
MAP_SIZE = 80
CHUNK_SIZE = 16
RENDER_DISTANCE = 3
MAX_HEIGHT = 12
PERLIN_SCALE = 35
CENTER_X = MAP_SIZE // 2
CENTER_Z = MAP_SIZE // 2

noise = PerlinNoise(octaves=5, seed=23125)
loaded_chunks = {}

def distance_mask(x, z):
    dx = x - CENTER_X
    dz = z - CENTER_Z
    distance = math.sqrt(dx ** 2 + dz ** 2)
    max_dist = math.sqrt((MAP_SIZE / 2) ** 2 + (MAP_SIZE / 2) ** 2)
    return 1 - (distance / max_dist)

def generate_chunk(cx, cz):
    if (cx, cz) in loaded_chunks:
        return

    chunk_entities = []

    def generate_block(x, z):
        world_x = cx * CHUNK_SIZE + x
        world_z = cz * CHUNK_SIZE + z

        if world_x >= MAP_SIZE or world_z >= MAP_SIZE:
            return None

        noise_val = noise([world_x / PERLIN_SCALE, world_z / PERLIN_SCALE])
        mask_val = distance_mask(world_x, world_z)
        height = int((noise_val + 1) / 2 * mask_val * MAX_HEIGHT)

        blocks = []
        for y in range(height):
            if height < 2:
                c = color.rgb(30, 120, 250)
            elif y < 3:
                c = color.rgb(80, 200, 80)
            elif y < 6:
                c = color.rgb(100, 160, 60)
            else:
                c = color.rgb(120, 120, 120)

            blocks.append(Entity(
                model='cube',
                color=c,
                texture='white_cube',
                position=(world_x, y, world_z),
                scale=1,
                collider='box'
            ))

        return blocks

    with ThreadPoolExecutor() as executor:
        future_blocks = []
        for x in range(CHUNK_SIZE):
            for z in range(CHUNK_SIZE):
                future_blocks.append(executor.submit(generate_block, x, z))

        for future in future_blocks:
            blocks = future.result()
            if blocks:
                chunk_entities.extend(blocks)

    loaded_chunks[(cx, cz)] = chunk_entities

def destroy_chunk(cx, cz):
    for e in loaded_chunks[(cx, cz)]:
        destroy(e)
    del loaded_chunks[(cx, cz)]

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

        if held_keys['space']:
            self.controller.y += time.dt * 5
        if held_keys['left shift']:
            self.controller.y -= time.dt * 5
        if held_keys['escape']:
            application.quit()

        # обновляем миникарту раз в 2 секунды
        global minimap_timer
        minimap_timer -= time.dt
        if minimap_timer <= 0:
            self.minimap.texture = generate_minimap()
            minimap_timer = 2

        self.minimap.enabled = True

        self.minimap.position = window.top_left + Vec2(0.22, -0.1)
        self.minimap.scale = (0.4, 0.4)

        self.minimap.z = -100

    def input(self, key):
        pass

def generate_minimap():
    size = MAP_SIZE
    scale = 4
    img_size = size * scale
    img = PILImage.new('RGBA', (img_size, img_size), (0, 0, 0, 0))
    pixels = img.load()

    for (cx, cz), entities in loaded_chunks.items():
        for e in entities:
            x = int(e.x)
            z = int(e.z)
            color_rgb = (int(e.color.r * 255), int(e.color.g * 255), int(e.color.b * 255))

            for dx in range(scale):
                for dz in range(scale):
                    px = x * scale + dx
                    pz = z * scale + dz
                    if 0 <= px < img_size and 0 <= pz < img_size:
                        pixels[px, pz] = (*color_rgb, 255)

    return Texture(img)

# === Камера ===
camera_entity = FreeCam()
minimap_timer = 0

# создаём сам объект миникарты
camera_entity.minimap = Entity(
    parent=camera.ui,
    model='quad',
    scale=(0.4, 0.4),
    position=window.top_right - Vec2(0.22, -0.1),
    texture=generate_minimap(),
    z=-100
)

# свет, небо
DirectionalLight().look_at(Vec3(1, -1, -1))
Sky()

app.run()
