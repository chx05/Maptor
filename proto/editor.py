import pyray as pr
import utils

from multi_sized_font import MultiSizedFont
from typing import Callable
from time import time


class Tween:
    def __init__(self, prop_name: str, increment_value: float, speed: float, on_complete: Callable) -> None:
        self.prop_name: str = prop_name
        self.target_value: float = increment_value
        self.speed: float = speed
        self.on_complete: Callable = on_complete


class Editor:
    def __init__(self) -> None:
        self.bg = pr.Color(11, 10, 7, 255)
        self.fg = pr.Color(240, 236, 87, 255)
        self.txt = pr.Color(244, 245, 248, 255)
        self.dbg_gui_txt = pr.color_alpha(self.txt, 0.4)

        self.is_running: bool = True

        # msg + time of logging, in seconds
        self.logs: list[tuple[str, float]] = []
        self.tweens: list[Tween] = []

        self.gui_padding: int = 20
    
    @property
    def w(self) -> int:
        return pr.get_screen_width()
    
    @property
    def h(self) -> int:
        return pr.get_screen_height()

    @property
    def screen_size(self) -> tuple[int, int]:
        return (self.w, self.h)
    
    @property
    def screen_center(self) -> tuple[float, float]:
        return (self.w / 2, self.h / 2)
    
    def refresh_running_state(self) -> None:
        ctrl = pr.is_key_down(pr.KeyboardKey.KEY_LEFT_CONTROL)

        if pr.is_key_pressed(pr.KeyboardKey.KEY_M):
            pr.minimize_window()

        if pr.window_should_close():
            self.is_running = False
        
        q = pr.is_key_pressed(pr.KeyboardKey.KEY_Q)
        if ctrl and q:
            self.is_running = False

    def launch(self) -> None:
        pr.init_window(0, 0, "Maptor [proto | beta]")
        pr.toggle_fullscreen()
        pr.set_target_fps(pr.get_monitor_refresh_rate(pr.get_current_monitor()))
        
        self.load_stuff()
        
        while self.is_running:
            self.step_tweens()
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

    def step_tweens(self) -> None:
        i = 0
        while i < len(self.tweens):
            tw = self.tweens[i]
            step = tw.speed * pr.get_frame_time()
            setattr(self, tw.prop_name, getattr(self, tw.prop_name) + step)

            cur_val = getattr(self, tw.prop_name)

            if step > 0 and cur_val >= tw.target_value:
                tw.on_complete()
                self.tweens.pop(i)
                continue

            if step < 0 and cur_val <= tw.target_value:
                tw.on_complete()
                self.tweens.pop(i)
                continue
            
            i += 1

    def canvas(self) -> None:
        pr.draw_text_ex(self.code_font.cur_font, "x: u8 = 10", (190, 200), self.text_size, 2, self.fg)

    def gui(self) -> None:
        self.display_fps()
        self.display_logs()
    
    def display_fps(self) -> None:
        fps_text = str(pr.get_fps())
        pr.draw_text_ex(
            self.gui_font,
            fps_text,
            (self.gui_padding, self.gui_padding),
            self.gui_font_size,
            1,
            self.dbg_gui_txt
        )
    
    def display_logs(self) -> None:
        for i, (msg, _) in enumerate(reversed(self.logs)):
            measure = pr.measure_text_ex(self.gui_font, msg, self.gui_font_size, 1)

            pr.draw_text_ex(
                self.gui_font,
                msg,
                (
                    self.w - measure.x - self.gui_padding,
                    self.gui_padding + (measure.y + self.gui_padding) * i
                ),
                self.gui_font_size,
                1,
                pr.color_alpha(
                    self.dbg_gui_txt,
                    1 - i / len(self.logs)
                )
            )

        # i remove all the old messages (they expire after N seconds)
        expiration_time = 5
        t = time()
        self.logs = list(filter(lambda l: t < l[1] + expiration_time, self.logs))

    def log(self, msg: str) -> None:
        max_capacity = 10
        if len(self.logs) >= max_capacity:
            self.logs.pop(0)

        self.logs.append((msg, time()))

    def inputs(self) -> None:
        ctrl = pr.is_key_down(pr.KeyboardKey.KEY_LEFT_CONTROL)

        mouse_dx_btn = pr.is_mouse_button_down(pr.MouseButton.MOUSE_BUTTON_RIGHT)
        if mouse_dx_btn:
            delta = pr.get_mouse_delta()
            delta = pr.vector2_scale(delta, -1 / self.cam.zoom)
            self.cam.target = pr.vector2_add(self.cam.target, delta)
        
        mouse_scroll = pr.get_mouse_wheel_move()

        KEY_PLUS = 93
        if mouse_scroll > 0 or (ctrl and pr.is_key_pressed(KEY_PLUS)):
            mouse_scroll = +self.code_font.step

        KEY_MINUS = 47
        if mouse_scroll < 0 or (ctrl and pr.is_key_pressed(KEY_MINUS)):
            mouse_scroll = -self.code_font.step

        if mouse_scroll != 0:
            self.text_size += mouse_scroll
            self.cap_text_size()
            self.refresh_code_font()
            self.log(f"text_size: {self.text_size} | cur_font_idx: {self.code_font.cur_idx} ({self.code_font.sizes[self.code_font.cur_idx]})")
    
    def cap_text_size(self) -> None:
        val = self.text_size
        minsz = self.code_font.min_sz
        maxsz = self.code_font.max_sz

        if val < minsz:
            val = minsz
        
        if val > maxsz:
            val = maxsz
        
        self.text_size = val

    def refresh_code_font(self) -> None:
        self.code_font.refresh_most_suitable_font(int(self.text_size))

    def load_stuff(self) -> None:
        self.cam: pr.Camera2D = pr.Camera2D(
            self.screen_center,
            (0, 0),
            0,
            1
        )

        self.code_font: MultiSizedFont = MultiSizedFont(10, 50, step=10)
        self.code_font.load("res/3270.ttf")
        self.text_size: float = 30
        self.refresh_code_font()

        self.gui_font_size: int = 20
        self.gui_font: pr.Font = self.code_font.fonts[self.code_font.get_best_font_from_size(self.gui_font_size)]
    
    def unload_stuff(self) -> None:
        self.code_font.unload()