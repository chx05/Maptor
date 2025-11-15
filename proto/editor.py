import pyray as pr
import utils

from multi_sized_font import MultiSizedFont
from time import time
from project import Project
from syntree import *

class Editor:
    def __init__(self) -> None:
        self.bg = pr.Color(11, 10, 7, 255)
        self.fg = pr.Color(240, 236, 87, 255)
        self.txt = pr.Color(244, 245, 248, 255)
        self.dbg_gui_txt = pr.color_alpha(self.txt, 0.4)
        self.op = pr.Color(205, 83, 52, 255)
        self.kw = pr.Color(227, 99, 151, 240)
        self.lit = pr.Color(143, 213, 166, 255)
        self.dot = pr.Color(0, 166, 251, 255)

        self.is_running: bool = True

        # msg + time of logging, in seconds
        self.logs: list[tuple[str, float]] = []

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
        max_decl_width = 100
        
        for i, decl in enumerate(self.prj.decls):
            if self.is_decl_visible(decl):
                self.render_decl(i * max_decl_width, decl)
        
    def is_decl_visible(self, decl: PDecl) -> bool:
        # TODO: render only visible nodes
        return True
    
    def render_decl(self, x: float, decl: PDecl) -> None:
        original_x = x

        dot_radius = 7
        x += dot_radius * 4

        # just a showcase of the colors
        m_name, x = self.render_text(x, 0, decl.name, self.fg)
        _, x = self.render_text(x, 0, " = ", self.op)
        _, x = self.render_text(x, 0, "import ", self.kw)
        _, x = self.render_text(x, 0, "'std'", self.lit)

        dot_pos = pr.Vector2(original_x, 0 + m_name.y // 2)
        dot_gap = 2

        if self.is_mouse_over_box(pr.vector2_add_value(dot_pos, -(dot_radius / 2)), dot_radius):
            dot_radius *= 1.25
            dot_gap = dot_radius

        pr.draw_circle_v(dot_pos, dot_radius, self.dot)
        pr.draw_circle_v(dot_pos, dot_radius - dot_gap, self.bg)

    def is_mouse_over_box(self, pos: pr.Vector2, side_size: float) -> bool:
        m = pr.get_screen_to_world_2d(pr.get_mouse_position(), self.cam)
        self.log(f"m: {m.x},{m.y} | pos: {pos.x},{pos.y}")
        return (
            m.x >= pos.x and m.x <= pos.x + side_size
            and
            m.y >= pos.y and m.y <= pos.y + side_size
        )
    
    def render_text(self, x: float, y: float, text: str, color: pr.Color) -> tuple[pr.Vector2, float]:
        pr.draw_text_ex(
            self.code_font.cur_font,
            text,
            (x, y),
            self.text_size,
            1,
            color
        )

        m = pr.measure_text_ex(
            self.code_font.cur_font, text, self.text_size, 1
        )

        return m, x + m.x

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

        self.code_font: MultiSizedFont = MultiSizedFont(10, 50, step=5)
        self.code_font.load("res/3270.ttf")
        self.text_size: float = 30
        self.refresh_code_font()

        self.gui_font_size: int = 20
        self.gui_font: pr.Font = self.code_font.fonts[self.code_font.get_best_font_from_size(self.gui_font_size)]

        self.prj: Project = Project("res/my_project.mpt")
        self.prj.load()
    
    def unload_stuff(self) -> None:
        self.code_font.unload()
        self.prj.unload()