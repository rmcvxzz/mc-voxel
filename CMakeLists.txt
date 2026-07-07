cmake_minimum_required(VERSION 3.10)
project(terram4kc VERSION 0.1.7 LANGUAGES C CXX)
set(CMAKE_EXPORT_COMPILE_COMMANDS ON)

# Options
option(TERRAM4KC_SMALL "Build optimized small binary" OFF)
option(TERRAM4KC_INSTALL "Enable install targets" ON)
option(TERRAM4KC_DISCORD_RPC "Enable Discord Rich Presence" ON)

# Set output directory for all build artifacts
set(CMAKE_RUNTIME_OUTPUT_DIRECTORY ${CMAKE_BINARY_DIR}/output)
set(CMAKE_RUNTIME_OUTPUT_DIRECTORY_DEBUG ${CMAKE_BINARY_DIR}/output)
set(CMAKE_RUNTIME_OUTPUT_DIRECTORY_RELEASE ${CMAKE_BINARY_DIR}/output)
set(CMAKE_RUNTIME_OUTPUT_DIRECTORY_MINSIZEREL ${CMAKE_BINARY_DIR}/output)
set(CMAKE_RUNTIME_OUTPUT_DIRECTORY_RELWITHDEBINFO ${CMAKE_BINARY_DIR}/output)

# SDL2 finding - cross-platform
if(WIN32)
    if(DEFINED ENV{SDL2_DIR})
        set(SDL2_DIR $ENV{SDL2_DIR})
    endif()

    if(EXISTS "${CMAKE_SOURCE_DIR}/win/SDL2/include/SDL2/SDL.h")
        set(SDL2_INCLUDE_DIRS "${CMAKE_SOURCE_DIR}/win/SDL2/include")
        set(SDL2_LIBRARIES
            "${CMAKE_SOURCE_DIR}/win/SDL2/lib/libSDL2.dll.a"
            # "${CMAKE_SOURCE_DIR}/win/SDL2/lib/libSDL2main.a"
        )
        message(STATUS "Using bundled SDL2 from win/SDL2/")
    elseif(SDL2_DIR)
        set(SDL2_INCLUDE_DIRS "${SDL2_DIR}/include")
        find_library(SDL2_LIBRARY SDL2 PATHS "${SDL2_DIR}/lib" "${SDL2_DIR}/lib/x64" NO_DEFAULT_PATH)
        find_library(SDL2MAIN_LIBRARY SDL2main PATHS "${SDL2_DIR}/lib" "${SDL2_DIR}/lib/x64" NO_DEFAULT_PATH)
        set(SDL2_LIBRARIES ${MINGW_DLL_PATH_${MINGW_DLL}} ${SDL2_LIBRARY})
        message(STATUS "Using SDL2 from ${SDL2_DIR}")
    else()
        find_package(SDL2 QUIET)
        if(NOT SDL2_FOUND)
            message(FATAL_ERROR "SDL2 not found. Set SDL2_DIR env var, or place SDL2 in win/SDL2/")
        endif()
    endif()
else()
    find_package(PkgConfig QUIET)
    if(PkgConfig_FOUND)
        pkg_check_modules(SDL2 QUIET sdl2 IMPORTED_TARGET)
    endif()
    if(TARGET PkgConfig::SDL2)
        set(SDL2_LIBRARIES PkgConfig::SDL2)
    else()
        find_package(SDL2 REQUIRED)
    endif()
    if(SDL2_LIBRARIES AND NOT TARGET PkgConfig::SDL2)
        # SDL2main is a Windows/WinMain-entry-point concern - some pkg-config
        # packaging (e.g. Homebrew) lists it as a dependency without actually
        # shipping the archive, breaking the link. Safe to drop outside Windows.
        list(REMOVE_ITEM SDL2_LIBRARIES SDL2main)
    endif()
endif()

# SDL2_net finding - bundled in win/
if(WIN32)
    if(EXISTS "${CMAKE_SOURCE_DIR}/win/SDL2_net/include/SDL2/SDL_net.h")
        set(SDL2_NET_INCLUDE_DIRS "${CMAKE_SOURCE_DIR}/win/SDL2_net/include")
        if(EXISTS "${CMAKE_SOURCE_DIR}/win/SDL2_net/lib/libSDL2_net.dll.a")
            set(SDL2_NET_LIBRARIES "${CMAKE_SOURCE_DIR}/win/SDL2_net/lib/libSDL2_net.dll.a")
            message(STATUS "Using bundled SDL2_net (MinGW) from win/SDL2_net/")
        elseif(EXISTS "${CMAKE_SOURCE_DIR}/win/SDL2_net/lib/SDL2_net.lib")
            set(SDL2_NET_LIBRARIES "${CMAKE_SOURCE_DIR}/win/SDL2_net/lib/SDL2_net.lib")
            message(STATUS "Using bundled SDL2_net (MSVC) from win/SDL2_net/")
        else()
            message(FATAL_ERROR "SDL2_net headers found but no libraries in win/SDL2_net/lib/")
        endif()
    else()
        message(FATAL_ERROR "SDL2_net not found in win/SDL2_net/. Download from https://github.com/libsdl-org/SDL_net/releases")
    endif()
else()
    find_package(PkgConfig QUIET)
    if(PkgConfig_FOUND)
        pkg_check_modules(SDL2_NET QUIET SDL2_net IMPORTED_TARGET)
    endif()
    if(TARGET PkgConfig::SDL2_NET)
        set(SDL2_NET_LIBRARIES PkgConfig::SDL2_NET)
    else()
        find_library(SDL2_NET_LIBRARY SDL2_net)
        find_path(SDL2_NET_INCLUDE_DIR SDL_net.h PATH_SUFFIXES SDL2)
        if(SDL2_NET_LIBRARY AND SDL2_NET_INCLUDE_DIR)
            set(SDL2_NET_LIBRARIES ${SDL2_NET_LIBRARY})
            set(SDL2_NET_INCLUDE_DIRS ${SDL2_NET_INCLUDE_DIR})
            set(SDL2_NET_FOUND TRUE)
        else()
            message(FATAL_ERROR "SDL2_net not found. Install libsdl2-net-dev or similar.")
        endif()
    endif()
endif()

if(WIN32)
    if(EXISTS "${CMAKE_SOURCE_DIR}/win/SDL2_image/include/SDL2/SDL_image.h")
        set(SDL2_IMAGE_INCLUDE_DIRS "${CMAKE_SOURCE_DIR}/win/SDL2_image/include")
        if(EXISTS "${CMAKE_SOURCE_DIR}/win/SDL2_image/lib/libSDL2_image.dll.a")
            set(SDL2_IMAGE_LIBRARIES "${CMAKE_SOURCE_DIR}/win/SDL2_image/lib/libSDL2_image.dll.a")
            message(STATUS "Using bundled SDL2_image (MinGW) from win/SDL2_image/")
        else()
            message(FATAL_ERROR "SDL2_image headers found but no library in win/SDL2_image/lib/")
        endif()
    else()
        message(FATAL_ERROR "SDL2_image not found in win/SDL2_image.")
    endif()
else()
    find_package(PkgConfig QUIET)
    if(PkgConfig_FOUND)
        pkg_check_modules(SDL2_IMAGE QUIET SDL2_image IMPORTED_TARGET)
    endif()
    if(TARGET PkgConfig::SDL2_IMAGE)
        set(SDL2_IMAGE_LIBRARIES PkgConfig::SDL2_IMAGE)
    else()
        find_library(SDL2_IMAGE_LIBRARY SDL2_image)
        find_path(SDL2_IMAGE_INCLUDE_DIR SDL_image.h PATH_SUFFIXES SDL2)
        if(SDL2_IMAGE_LIBRARY AND SDL2_IMAGE_INCLUDE_DIR)
            set(SDL2_IMAGE_LIBRARIES ${SDL2_IMAGE_LIBRARY})
            set(SDL2_IMAGE_INCLUDE_DIRS ${SDL2_IMAGE_INCLUDE_DIR})
        else()
            message(FATAL_ERROR "SDL2_image not found. Install libsdl2-image-dev or similar.")
        endif()
    endif()
endif()


# Discord RPC setup
if(TERRAM4KC_DISCORD_RPC)
    if(WIN32)
        if(EXISTS "${CMAKE_SOURCE_DIR}/discord-rpc/include/discord_rpc.h")
            set(DISCORD_RPC_INCLUDE_DIRS "${CMAKE_SOURCE_DIR}/discord-rpc/include")
            if(EXISTS "${CMAKE_SOURCE_DIR}/discord-rpc/lib/libdiscord-rpc.dll.a")
                set(DISCORD_RPC_LIBRARIES "${CMAKE_SOURCE_DIR}/discord-rpc/lib/libdiscord-rpc.dll.a")
                set(DISCORD_RPC_DLL "${CMAKE_SOURCE_DIR}/discord-rpc/bin/discord-rpc.dll")
                message(STATUS "Using bundled Discord RPC (MinGW) from discord-rpc/")
            elseif(EXISTS "${CMAKE_SOURCE_DIR}/discord-rpc/lib/discord-rpc.lib")
                set(DISCORD_RPC_LIBRARIES "${CMAKE_SOURCE_DIR}/discord-rpc/lib/discord-rpc.lib")
                set(DISCORD_RPC_DLL "${CMAKE_SOURCE_DIR}/discord-rpc/bin/discord-rpc.dll")
                message(STATUS "Using bundled Discord RPC (MSVC) from discord-rpc/")
            else()
                message(WARNING "Discord RPC headers found but no libraries. Disabling Discord RPC.")
                set(TERRAM4KC_DISCORD_RPC OFF)
            endif()
        else()
            message(WARNING "Discord RPC not found in discord-rpc/ folder. Disabling Discord RPC.")
            set(TERRAM4KC_DISCORD_RPC OFF)
        endif()
    else()
        find_package(PkgConfig QUIET)
        if(PkgConfig_FOUND)
            pkg_check_modules(DISCORD_RPC QUIET discord-rpc IMPORTED_TARGET)
        endif()
        if(TARGET PkgConfig::DISCORD_RPC)
            set(DISCORD_RPC_LIBRARIES PkgConfig::DISCORD_RPC)
        else()
            find_library(DISCORD_RPC_LIBRARY discord-rpc)
            find_path(DISCORD_RPC_INCLUDE_DIR discord_rpc.h PATH_SUFFIXES discord-rpc)
            if(DISCORD_RPC_LIBRARY AND DISCORD_RPC_INCLUDE_DIR)
                set(DISCORD_RPC_LIBRARIES ${DISCORD_RPC_LIBRARY})
                set(DISCORD_RPC_INCLUDE_DIRS ${DISCORD_RPC_INCLUDE_DIR})
                set(DISCORD_RPC_FOUND TRUE)
            else()
                message(WARNING "Discord RPC not found. Disabling Discord RPC.")
                set(TERRAM4KC_DISCORD_RPC OFF)
            endif()
        endif()
    endif()
endif()

# Source files
set(SOURCES
    src/main.c
    src/audio/audio.c
    src/discord/discord_presence.c
    src/data/data.c
    src/core/gameloop.c
    src/render/gui.c
    src/data/inputbuffer.c
    src/ui/menus.c
    src/render/minecraftfont.c
    src/data/options.c
    src/core/player.c
    src/core/player_model.c
    src/net/net.c
    src/core/terrain.c
    src/render/textures.c
    src/util/utility.c
    src/ui/imgui_renderer.cpp
    src/data/loc.c
    src/render/gl_renderer.c
    src/net/mcpi.c
    glad/src/glad.c
)

set(HEADERS
    src/core/blocks.h
    src/util/compat.h
    src/core/coords.h
    src/data/data.h
    src/core/gameloop.h
    src/render/gui.h
    src/data/inputbuffer.h
    src/main.h
    src/ui/menus.h
    src/render/minecraftfont.h
    src/data/options.h
    src/core/player.h
    src/core/player_model.h
    src/net/net.h
    src/core/terrain.h
    src/render/textures.h
    src/util/utility.h
    src/audio/audio.h
    src/discord/discord_presence.h
    src/ui/imgui_renderer.h
    src/data/loc.h
    src/render/gl_renderer.h
    src/net/mcpi.h
)

# Dear ImGui (SDL2 + SDLRenderer2 backends)
set(IMGUI_DIR "${CMAKE_SOURCE_DIR}/imgui")

add_library(imgui STATIC
    ${IMGUI_DIR}/imgui.cpp
    ${IMGUI_DIR}/imgui_draw.cpp
    ${IMGUI_DIR}/imgui_tables.cpp
    ${IMGUI_DIR}/imgui_widgets.cpp
    ${IMGUI_DIR}/backends/imgui_impl_sdl2.cpp
    ${IMGUI_DIR}/backends/imgui_impl_sdlrenderer2.cpp
    ${IMGUI_DIR}/backends/imgui_impl_opengl3.cpp
)

target_include_directories(imgui PUBLIC
    ${IMGUI_DIR}
    ${IMGUI_DIR}/backends
    ${SDL2_INCLUDE_DIRS}
    ${SDL2_INCLUDE_DIRS}/SDL2
)

set_target_properties(imgui PROPERTIES LINKER_LANGUAGE CXX)

add_executable(m4kc ${SOURCES} ${HEADERS})

target_include_directories(m4kc PRIVATE
    ${SDL2_INCLUDE_DIRS}
    ${SDL2_INCLUDE_DIRS}/SDL2
    ${SDL2_NET_INCLUDE_DIRS}
    ${SDL2_NET_INCLUDE_DIRS}/SDL2
    ${SDL2_IMAGE_INCLUDE_DIRS}
    ${SDL2_IMAGE_INCLUDE_DIRS}/SDL2
    src
    src/core
    src/render
    src/ui
    src/net
    src/audio
    src/data
    src/discord
    src/util
    glad/include)
target_link_libraries(m4kc PRIVATE imgui ${SDL2_LIBRARIES} ${SDL2_NET_LIBRARIES} ${SDL2_IMAGE_LIBRARIES})

# OpenGL
if(WIN32)
    target_link_libraries(m4kc PRIVATE opengl32)
else()
    find_package(OpenGL REQUIRED)
    target_link_libraries(m4kc PRIVATE OpenGL::GL)
endif()

# Discord RPC compile definitions and linking
if(TERRAM4KC_DISCORD_RPC)
    target_compile_definitions(m4kc PRIVATE TERRAM4KC_DISCORD_RPC=1)
    target_include_directories(m4kc PRIVATE ${DISCORD_RPC_INCLUDE_DIRS})
    target_link_libraries(m4kc PRIVATE ${DISCORD_RPC_LIBRARIES})
    message(STATUS "Discord RPC enabled")
else()
    message(STATUS "Discord RPC disabled")
endif()

# Platform-specific
if(WIN32)
    # set_target_properties(m4kc PROPERTIES WIN32_EXECUTABLE TRUE)

    # Copy SDL2.dll
    if(EXISTS "${CMAKE_SOURCE_DIR}/win/SDL2.dll")
        add_custom_command(TARGET m4kc POST_BUILD
            COMMAND ${CMAKE_COMMAND} -E copy_if_different
            "${CMAKE_SOURCE_DIR}/win/SDL2.dll"
            ${CMAKE_RUNTIME_OUTPUT_DIRECTORY}
            COMMENT "Copying SDL2.dll"
        )
    endif()
    if(EXISTS "${CMAKE_SOURCE_DIR}/win/SDL2/bin/SDL2.dll")
        add_custom_command(TARGET m4kc POST_BUILD
            COMMAND ${CMAKE_COMMAND} -E copy_if_different
            "${CMAKE_SOURCE_DIR}/win/SDL2/bin/SDL2.dll"
            ${CMAKE_RUNTIME_OUTPUT_DIRECTORY}
            COMMENT "Copying SDL2.dll from bin"
        )
    endif()

    # Copy SDL2_net.dll
    if(EXISTS "${CMAKE_SOURCE_DIR}/win/SDL2_net/include/SDL2/SDL_net.h")
        add_custom_command(TARGET m4kc POST_BUILD
            COMMAND ${CMAKE_COMMAND} -E copy_if_different
            "${CMAKE_SOURCE_DIR}/win/SDL2_net/bin/SDL2_net.dll"
            ${CMAKE_RUNTIME_OUTPUT_DIRECTORY}
            COMMENT "Copying SDL2_net.dll"
        )
    endif()

    if(EXISTS "${CMAKE_SOURCE_DIR}/win/SDL2_image/include/SDL2/SDL_image.h")
        add_custom_command(TARGET m4kc POST_BUILD
            COMMAND ${CMAKE_COMMAND} -E copy_if_different
            "${CMAKE_SOURCE_DIR}/win/SDL2_image/bin/SDL2_image.dll"
            ${CMAKE_RUNTIME_OUTPUT_DIRECTORY}
            COMMENT "Copying SDL2_image.dll"
        )
    endif()

    # SDL2_image finding - bundled in win/
    if(WIN32)
        if(EXISTS "${CMAKE_SOURCE_DIR}/win/SDL2_image/include/SDL2/SDL_image.h")
            set(SDL2_IMAGE_INCLUDE_DIRS "${CMAKE_SOURCE_DIR}/win/SDL2_image/include")
            if(EXISTS "${CMAKE_SOURCE_DIR}/win/SDL2_image/lib/libSDL2_image.dll.a")
                set(SDL2_IMAGE_LIBRARIES "${CMAKE_SOURCE_DIR}/win/SDL2_image/lib/libSDL2_image.dll.a")
                message(STATUS "Using bundled SDL2_image (MinGW) from win/SDL2_image/")
            else()
                message(FATAL_ERROR "SDL2_image headers found but no library in win/SDL2_image/lib/")
            endif()
        else()
            message(FATAL_ERROR "SDL2_image not found in win/SDL2_image/. Download from https://github.com/libsdl-org/SDL_image/releases")
        endif()
    else()
        find_package(PkgConfig QUIET)
        if(PkgConfig_FOUND)
            pkg_check_modules(SDL2_IMAGE QUIET SDL2_image IMPORTED_TARGET)
        endif()
        if(TARGET PkgConfig::SDL2_IMAGE)
            set(SDL2_IMAGE_LIBRARIES PkgConfig::SDL2_IMAGE)
        else()
            find_library(SDL2_IMAGE_LIBRARY SDL2_image)
            find_path(SDL2_IMAGE_INCLUDE_DIR SDL_image.h PATH_SUFFIXES SDL2)
            if(SDL2_IMAGE_LIBRARY AND SDL2_IMAGE_INCLUDE_DIR)
                set(SDL2_IMAGE_LIBRARIES ${SDL2_IMAGE_LIBRARY})
                set(SDL2_IMAGE_INCLUDE_DIRS ${SDL2_IMAGE_INCLUDE_DIR})
            else()
                message(FATAL_ERROR "SDL2_image not found. Install libsdl2-image-dev or similar.")
            endif()
        endif()
    endif()

    # Copy Discord RPC DLL if enabled
    if(TERRAM4KC_DISCORD_RPC AND EXISTS "${DISCORD_RPC_DLL}")
        add_custom_command(TARGET m4kc POST_BUILD
            COMMAND ${CMAKE_COMMAND} -E copy_if_different
            "${DISCORD_RPC_DLL}"
            ${CMAKE_RUNTIME_OUTPUT_DIRECTORY}
            COMMENT "Copying discord-rpc.dll"
        )
    endif()

    # Copy MinGW runtime DLLs (needed when linking C++)
    foreach(MINGW_DLL
        libgcc_s_seh-1.dll
        libstdc++-6.dll
        libwinpthread-1.dll
    )
        find_file(MINGW_DLL_PATH_${MINGW_DLL} ${MINGW_DLL}
            PATHS
            "C:/msys64/mingw64/bin"
            "C:/mingw64/bin"
            "C:/mingw/bin"
            NO_DEFAULT_PATH
        )
        if(MINGW_DLL_PATH_${MINGW_DLL})
            add_custom_command(TARGET m4kc POST_BUILD
                COMMAND ${CMAKE_COMMAND} -E copy_if_different
                "${MINGW_DLL_PATH_${MINGW_DLL}}"
                ${CMAKE_RUNTIME_OUTPUT_DIRECTORY}
                COMMENT "Copying ${MINGW_DLL}"
            )
        endif()
    endforeach()
endif()

# Temporary console mode
if(MINGW)
    target_link_options(m4kc PRIVATE -mconsole)
endif()

# Copy assets folder to output directory
if(EXISTS "${CMAKE_SOURCE_DIR}/assets")
    add_custom_command(TARGET m4kc POST_BUILD
        COMMAND ${CMAKE_COMMAND} -E copy_directory
        "${CMAKE_SOURCE_DIR}/assets"
        ${CMAKE_RUNTIME_OUTPUT_DIRECTORY}/assets
        COMMENT "Copying assets folder"
    )
endif()

if(EXISTS "${CMAKE_SOURCE_DIR}/lang")
    add_custom_command(TARGET m4kc POST_BUILD
        COMMAND ${CMAKE_COMMAND} -E copy_directory
        "${CMAKE_SOURCE_DIR}/lang"
        ${CMAKE_RUNTIME_OUTPUT_DIRECTORY}/lang
        COMMENT "Copying lang folder"
    )
endif()

# Compiler flags
if(MSVC)
    target_compile_options(m4kc PRIVATE /W4)
    if(TERRAM4KC_SMALL)
        target_compile_options(m4kc PRIVATE /O1 /GL)
        target_link_options(m4kc PRIVATE /LTCG)
    endif()
else()
    target_compile_options(m4kc PRIVATE -Wall -Wextra)
    if(TERRAM4KC_SMALL)
        target_compile_options(m4kc PRIVATE
            -Os -g0
            -fno-stack-protector
            -fno-unwind-tables
            -fno-asynchronous-unwind-tables
        )
        target_compile_definitions(m4kc PRIVATE small)
        target_link_options(m4kc PRIVATE -s)
        if(NOT WIN32)
            add_custom_command(TARGET m4kc POST_BUILD
                COMMAND strip $<TARGET_FILE:m4kc>
                -S --strip-unneeded
                --remove-section=.note.gnu.gold-version
                --remove-section=.comment
                --remove-section=.note
                --remove-section=.note.gnu.build-id
                --remove-section=.note.ABI-tag
                COMMENT "Stripping binary"
            )
        endif()
    else()
        target_compile_options(m4kc PRIVATE -g)
    endif()
endif()

# Install
if(TERRAM4KC_INSTALL AND NOT WIN32)
    include(GNUInstallDirs)
    install(TARGETS m4kc DESTINATION ${CMAKE_INSTALL_PREFIX}/games)
    install(FILES m4kc.desktop DESTINATION ${CMAKE_INSTALL_PREFIX}/share/applications)
    install(FILES icons/icon.png DESTINATION ${CMAKE_INSTALL_PREFIX}/share/icons/hicolor/256x256/apps RENAME m4kc.png)
endif()

# CPack
set(CPACK_PACKAGE_NAME "TerraM4KC")
set(CPACK_PACKAGE_VERSION ${PROJECT_VERSION})
set(CPACK_GENERATOR "ZIP")
include(CPack)