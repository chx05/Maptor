import pyray as pr
from multi_sized_font import MultiSizedFont

class Editor:
    def __init__(self) -> None:
        self.bg = pr.Color(11, 10, 7, 255)
        self.fg = pr.Color(240, 236, 87, 255)
        self.txt = pr.Color(244, 245, 248, 255)

        self.is_running: bool = True
    
    @property
    def screen_size(self) -> tuple[int, int]:
        return (pr.get_screen_width(), pr.get_screen_height())
    
    @property
    def screen_center(self) -> tuple[float, float]:
        return (self.screen_size[0] / 2, self.screen_size[1] / 2)
    
    @property
    def zoom_size(self) -> int:
        # TODO: resize this to self.font.min_sz/max_sz range
        return self.cam.zoom
    
    def refresh_running_state(self) -> None:
        if pr.window_should_close():
            self.is_running = False
        
        ctrl = pr.is_key_down(pr.KeyboardKey.KEY_LEFT_CONTROL)
        q = pr.is_key_pressed(pr.KeyboardKey.KEY_Q)
        if ctrl and q:
            self.is_running = False

    def launch(self) -> None:
        pr.init_window(0, 0, "Maptor [proto | beta]")
        pr.toggle_fullscreen()
        pr.set_target_fps(pr.get_monitor_refresh_rate(pr.get_current_monitor()))
        
        self.load_stuff()
        
        while self.is_running:
            self.inputs()

            pr.begin_drawing()
            pr.clear_background(self.bg)

            pr.begin_mode_2d(self.cam)
            self.canvas()
            pr.end_mode_2d()
            
            self.gui()
            pr.end_drawing()

            self.refresh_running_state()
        
        self.unload_stuff()
        pr.close_window()
    
    def canvas(self) -> None:
        pr.draw_text_ex(self.font, "x: u8 = 10", (190, 200), self.font_sz, 2, self.fg)

    def gui(self) -> None:
        pr.draw_fps(20, 20)

    def inputs(self) -> None:
        mouse_dx_btn = pr.is_mouse_button_down(pr.MouseButton.MOUSE_BUTTON_RIGHT)
        if mouse_dx_btn:
            delta = pr.get_mouse_delta()
            delta = pr.vector2_scale(delta, -1 / self.cam.zoom)
            self.cam.target = pr.vector2_add(self.cam.target, delta)
        
        mouse_scroll = pr.get_mouse_wheel_move()
        if mouse_scroll != 0:
            saved_zoom = self.cam.zoom
            self.cam.zoom += mouse_scroll * 0.25

            self.cap_zoom(saved_zoom)
            print(mouse_scroll, self.cam.zoom)
    
    def cap_zoom(self, old_zoom: float) -> None:
        MIN_ZOOM = 0.1
        MAX_ZOOM = 5.0
        if self.cam.zoom < MIN_ZOOM or self.cam.zoom > MAX_ZOOM:
            self.cam.zoom = old_zoom

    def init_usable_font(self) -> None:
        self.usable_font: pr.Font = self.font.get_best_font_from_size(self.zoom_size)

    def load_stuff(self) -> None:
        self.cam: pr.Camera2D = pr.Camera2D(
            self.screen_center,
            (0, 0),
            0,
            1
        )

        self.font: MultiSizedFont = MultiSizedFont(10, 50)
        self.font.load("res/3270.ttf")

        self.init_usable_font()
    
    def unload_stuff(self) -> None:
        self.font.unload()