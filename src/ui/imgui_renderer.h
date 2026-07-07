#pragma once

#include <SDL2/SDL.h>

#ifdef __cplusplus
extern "C" {
#endif

typedef struct {
    int    fps;
    int    blockSelected;
    int    blockX, blockY, blockZ;
    int    headInWater;
    int    feetInWater;
    double velFB;
    double velLR;
} ImguiDebugState;

extern ImguiDebugState g_imgui_debug;

/* SDL_Renderer backend - used when running without --opengl */
void imgui_init(SDL_Window *window, SDL_Renderer *renderer);

/* OpenGL3 backend - used when running with --opengl */
void imgui_init_gl(SDL_Window *window, SDL_GLContext gl_context);

void imgui_shutdown(void);
void imgui_process_event(SDL_Event *event);
void imgui_new_frame(void);
void imgui_render(void);
int  imgui_wants_mouse(void);
int  imgui_wants_keyboard(void);

#ifdef __cplusplus
}
#endif