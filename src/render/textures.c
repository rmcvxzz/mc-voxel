#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <SDL2/SDL_image.h>
#include "textures.h"

int textures[TEXTURES_SIZE] = { 0 };

static const char* blockFileNames[NUMBER_OF_BLOCKS] = {
    [BLOCK_AIR]         = NULL,
    [BLOCK_STONE]       = "stone.png",
    [BLOCK_SAND]        = "sand.png",
    [BLOCK_GRAVEL]      = "gravel.png",
    [BLOCK_BRICKS]      = "bricks.png",
    [BLOCK_COBBLESTONE] = "cobblestone.png",
    [BLOCK_WATER]       = "water.png",
    [BLOCK_WOOD]        = "wood.png",
    [BLOCK_GRASS]       = "grass.png",
    [BLOCK_LEAVES]      = "leaves.png",
    [BLOCK_TALL_GRASS]  = "tall_grass.png",
    [BLOCK_PLAYER_HEAD] = "player_head.png",
    [BLOCK_PLAYER_BODY] = "player_body.png"
};

void genTextures (unsigned int seed) {
        (void)seed;
        char path[256];

        for (Block blockId = 1; blockId < NUMBER_OF_BLOCKS; blockId++) {
                if (!blockFileNames[blockId]) continue;

                snprintf(path, sizeof(path), "assets/textures/blocks/%s", blockFileNames[blockId]);

                SDL_Surface* loadedSurface = IMG_Load(path);
                if (!loadedSurface) {
                        fprintf(stderr, "[Texture Error] SDL_image failed to load %s: %s\n", path, IMG_GetError());
                        continue;
                }

                SDL_Surface* rgbaSurface = SDL_ConvertSurfaceFormat(loadedSurface, SDL_PIXELFORMAT_RGBA32, 0);
                SDL_FreeSurface(loadedSurface);

                if (!rgbaSurface) {
                        fprintf(stderr, "[Texture Error] Conversion failed for %s: %s\n", path, SDL_GetError());
                        continue;
                }

                int width = rgbaSurface->w;
                int height = rgbaSurface->h;
                uint32_t* pixels = (uint32_t*)rgbaSurface->pixels;

                for (int y = 0; y < height; y++) {
                for (int x = 0; x < width; x++) {
                        uint32_t pixel = pixels[x + y * width];

                        uint8_t r, g, b, a;
                        SDL_GetRGBA(pixel, rgbaSurface->format, &r, &g, &b, &a);

                        int finalColor = 0;
                        if (a > 0) {
                                finalColor = (r << 16) | (g << 8) | b;
                        }

                        textures[x + y * BLOCK_TEXTURE_H + blockId * BLOCK_TEXTURE_W * BLOCK_TEXTURE_H * 3] = finalColor;
                }
                }

                SDL_FreeSurface(rgbaSurface);
        }
}