# This code (generate.py) is used to generate the textures, turning them into, well, external pictures.
# This code wil regenerate a random texture every time you run it, so

import os
import math
import random
from PIL import Image

BLOCK_TEXTURE_W = 16
BLOCK_TEXTURE_H = 16

BLOCK_MAP = {
    1: "grass",
    2: "stone",
    3: "sand",
    4: "gravel",
    5: "wood",
    6: "bricks",
    7: "cobblestone",
    8: "water",
    9: "player_head",
    10: "player_body",
    11: "leaves",
    12: "tall_grass"
}

cobbleCracks = [
    0b0000001110000100, 0b0010110010000110, 0b1011100011001110, 0b1110100011110011,
    0b0011000110001001, 0b0001000100001111, 0b0001111110000001, 0b0011001111100110,
    0b1110001000111100, 0b0100010100011000, 0b1000010000011100, 0b0100110000110111,
    0b0011111011000010, 0b1100001010000001, 0b0010000111000011, 0b0000111100111110,
]

def randm(max_val):
    """Mimics the C randm/rand implementation bounded by a max value."""
    if max_val <= 0:
        return 0
    return random.randint(0, max_val - 1)

def dist2d(x1, y1, x2, y2):
    """Calculates Euclidean distance between two points."""
    return math.sqrt((x1 - x2)**2 + (y1 - y2)**2)

def determ2d(x, y):
    """Deterministic pseudorandom noise generator matching your C inline function."""
    return math.fmod(abs(math.tan(9 * float(x) + 1 + float(y))), 1.0)

def hex_to_rgb(hex_val):
    """Converts 0xRRGGBB integer values into individual R, G, B components."""
    r = (hex_val >> 16) & 0xFF
    g = (hex_val >> 8) & 0xFF
    b = hex_val & 0xFF
    return r, g, b

def gen_texture(block_id):
    width = BLOCK_TEXTURE_W
    height = BLOCK_TEXTURE_H * 3
    
    img = Image.new("RGBA", (width, height))
    pixels = img.load()

    brightness = 255 - randm(96)

    for y in range(height):
        for x in range(width):
            baseColor = 0x966C4A
            noiseFloor = 255
            noiseScale = 96

            if block_id == 3:  
                noiseScale = 48
            if block_id == 4:  
                noiseScale = 140

            if block_id == 1 and y < (x * x * (3 + x) * 81 >> 2 & 0x3) + 18:
                baseColor = 0x6AAA40
            elif block_id == 1 and y < (x * x * (3 + x) * 81 >> 2 & 0x3) + 19:
                brightness = int(brightness * 2 / 3)

            needAltNoise = (block_id == 2 or block_id == 8) 
            if not needAltNoise or randm(3) == 0:
                brightness = noiseFloor - randm(noiseScale)

            if block_id == 5:  
                baseColor = 0x675231
                if 0 < x < 15 and (0 < (y & 0xF) < 15 and (y < 15 or 32 <= y < 47)):
                    baseColor = 0xBC9862
                    i6 = x - 7
                    i7 = (y & 0xF) - 7

                    if i6 < 0: i6 = 1 - i6
                    if i7 < 0: i7 = 1 - i7
                    if i7 > i6: i6 = i7

                    brightness = 196 - randm(32) + (i6 % 3) * 32
                elif randm(2) == 0:
                    brightness = int(brightness * (150 - (x & 0x1) * 100) / 100)

            if block_id == 2:    
                baseColor = 0x7F7F7F
            elif block_id == 3:  
                baseColor = 0xD8CE9B
            elif block_id == 4:  
                baseColor = 0xAAAAAA
            elif block_id == 6:  
                baseColor = 0xB53A15
                if (x + (y // 4) * 4) % 8 == 0 or y % 4 == 0:
                    baseColor = 12365733
            elif block_id == 7:  
                baseColor = 0x999999
                brightness -= ((cobbleCracks[y & 0xF] >> x) & 1) * 128
            elif block_id == 8:  
                baseColor = 0x3355EE
            elif block_id == 9:  
                brightness = 255
                if dist2d(x, y % BLOCK_TEXTURE_H, 8, 8) > 6.2 or (y // 16) % 3 == 2:
                    baseColor = 0x000000
                else:
                    baseColor = 0xFFFFFF
                    brightness -= int(dist2d(x, y % BLOCK_TEXTURE_H, 8, 2) * 8)
            elif block_id == 10: 
                brightness = 255
                if (dist2d(x, y % BLOCK_TEXTURE_H, 8, 16) > 12.2 or (y // 16) % 3 != 1) and (y // 16) % 3 != 2:
                    baseColor = 0x000000
                else:
                    baseColor = 0xFFFFFF
                    brightness -= int(dist2d(x, y % BLOCK_TEXTURE_H, 8, 2) * 8)
            elif block_id == 11: 
                baseColor = 0x50D937
                if randm(2) == 0:
                    baseColor = 0  

            elif block_id == 12: 
                baseColor = 0x50D937
                if determ2d(x, y / 3.0) < 0.2 or y < BLOCK_TEXTURE_H or randm(y - BLOCK_TEXTURE_H + 1) < 2:
                    baseColor = 0  

            finalBrightness = brightness
            if y >= BLOCK_TEXTURE_H * 2:
                finalBrightness = int(finalBrightness / 2)

            finalBrightness = max(0, min(255, finalBrightness))

            r, g, b = hex_to_rgb(baseColor)
            
            r = int(r * finalBrightness / 255)
            g = int(g * finalBrightness / 255)
            b = int(b * finalBrightness / 255)

            a = 0 if (baseColor == 0 and block_id in [11, 12]) else 255

            pixels[x, y] = (r, g, b, a)

    return img

def gen_all_textures(seed):
    random.seed(seed)
    os.makedirs("output_textures", exist_ok=True)

    for block_id, name in BLOCK_MAP.items():
        print(f"Generating texture for: {name}...")
        img = gen_texture(block_id)
        
        img.save(f"output_textures/{name}.png")
    
    print("\nGeneration finished! Check the 'output_textures' folder.")

if __name__ == "__main__":
    # socut dugno promits
    generated_seed = random.randint(0, 2**32 - 1)
    print(f"GENERATION SEED: {generated_seed}\n")
    gen_all_textures(generated_seed)