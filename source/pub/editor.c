#ifndef MPT_EDITOR_C
#define MPT_EDITOR_C

    #include "base.c"
    #include "rl.c"
    #include "project.c"

    typedef struct
    {
        bool is_running;
        uint16_t w;
        uint16_t h;

        Color bg;
        Color fg;
        Color txt;

        uint8_t font_sz;
        uint8_t font_spacing;
        Font font;

        prj_t prj;
    } mpt_t;

    // region HEADER

        void mpt_init(mpt_t* m, uint16_t w, uint16_t h);

        void mpt_deinit(mpt_t* m);

        void mpt_run(mpt_t* m);

        void rl_set_best_fps();

        void mpt_load_assets(mpt_t* m);

        void mpt_unload_assets(mpt_t* m);

        void mpt_loop(mpt_t* m);

        void mpt_gui(mpt_t* m);

        void mpt_update(mpt_t* m);
    
    // endregion HEADER

    // region SOURCE

        void mpt_init(mpt_t* m, uint16_t w, uint16_t h)
        {
            m->is_running = true;
            m->w = w;
            m->h = h;

            m->bg = rgb(11, 10, 7);
            m->fg = rgb(240, 236, 87);
            // inverse of m->bg, for now, if permanent choice remember to use invert() instead
            m->txt = rgb(244, 245, 248);
        }

        void mpt_deinit(mpt_t* m)
        {
            (void)m;
        }

        void mpt_run(mpt_t* m)
        {
            InitWindow(m->w, m->h, "Maptor [beta]");
            rl_set_best_fps();

            mpt_load_assets(m);
            mpt_loop(m);
            mpt_unload_assets(m);
        }

        void rl_set_best_fps()
        {
            SetTargetFPS(
                GetMonitorRefreshRate(GetCurrentMonitor())
            );
        }

        void mpt_load_assets(mpt_t* m)
        {
            m->font_sz = 64;
            m->font_spacing = 4;
            m->font = LoadFontEx("res/3270.ttf", m->font_sz, NULL, 0);
        }

        void mpt_unload_assets(mpt_t* m)
        {
            UnloadFont(m->font);
        }

        void mpt_loop(mpt_t* m)
        {
            while (m->is_running)
            {
                mpt_gui(m);
                mpt_update(m);
            }
        }

        void mpt_gui(mpt_t* m)
        {
            BeginDrawing();
            {
                ClearBackground(m->bg);
                
            }
            EndDrawing();
        }

        void mpt_update(mpt_t* m)
        {
            m->is_running = !WindowShouldClose();
        }

    // endregion SOURCE

#endif
