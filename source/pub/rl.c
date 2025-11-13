#ifndef MPT_RL_C
#define MPT_RL_C

    #include "../libs/raylib/include/raylib.h"
    #include "../libs/raylib/include/raymath.h"
    #include "../libs/raylib/include/rlgl.h"
    #include "base.c"

    static inline Color rgba(uint8_t r, uint8_t g, uint8_t b, uint8_t a)
    {
        return (Color)
        {
            .r = r,
            .g = g,
            .b = b,
            .a = a
        };
    }

    static inline Color rgb(uint8_t r, uint8_t g, uint8_t b)
    {
        return rgba(r, g, b, 255);
    }

    static inline Vector2 vec2(float x, float y)
    {
        return (Vector2)
        {
            .x = x,
            .y = y
        };
    }

#endif
