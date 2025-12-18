import pyray as pr
import utils
import string

from typing import Callable, cast
from multi_sized_font import MultiSizedFont
from project import Project
from syntree import *
from editable import *


class Editor:
    def __init__(self) -> None:
        #self.light_mode()
        self.dark_mode()

        self.is_running: bool = True
        self.parallel_view_mode: bool = False
        # no nid->editable dict because i need temporal sorting
        self.editables: list[Editable] = []
        # original_base_x, original_y, previous_max_x, final_y
        self.parallel_contexts: list[tuple[float, float, float, float]] = []
        # nid
        self.under_edit: int | None = None
        self.under_edit_cursor_idx: int = 0

        self.logs: dict[str, str] = {}

        self.gui_padding: int = 20
        self.interline_gap: float = 0.25
        self.interdecl_gap: float = 25
        self.indent_level_step: float = 0.5
        self.fn_call_par_gap: float = 0.25
        self.stmt_side_padding: float = 2
        self.codewire_left_padding: float = 0.5
        self.shapewire_thick: float = 0.2

        self.x: float
        self.y: float
        self.max_x: float
        self.base_x: float
        self.indent_level: float

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
    
    @property
    def cur_under_edit(self) -> Editable:
        assert self.under_edit != None
        return self.get_editable(self.under_edit)
    
    def light_mode(self) -> None:
        self.bg = pr.Color(244, 245, 248, 255)
        self.tc_typing = pr.Color(139, 38, 53, 255)
        self.tc_normal = pr.Color(11, 10, 7, 255)
        self.tc_wire = pr.color_alpha(self.tc_normal, 0.3)
        self.tc_shapewire = pr.color_alpha(self.tc_wire, 0.15)
        self.tc_dbg_gui = pr.color_alpha(self.tc_normal, 0.4)
        self.tc_kw = pr.Color(216, 49, 91, 255)
        self.tc_lit = pr.Color(6, 167, 125, 255)
        self.tc_fn_name = pr.Color(130, 106, 237, 255)
        self.tc_cursor = pr.Color(0, 71, 119, 255)

    def dark_mode(self) -> None:
        self.bg = pr.Color(20, 22, 28, 255)
        self.tc_typing = pr.Color(255, 121, 140, 255)
        self.tc_normal = pr.Color(224, 225, 232, 255)
        self.tc_wire = pr.color_alpha(self.tc_normal, 0.25)
        self.tc_shapewire = pr.color_alpha(self.tc_wire, 0.15)
        self.tc_dbg_gui = pr.color_alpha(self.tc_normal, 0.35)
        self.tc_kw = pr.Color(255, 98, 151, 255)
        self.tc_lit = pr.Color(90, 247, 190, 255)
        self.tc_fn_name = pr.Color(150, 180, 255, 255)
        self.tc_cursor = pr.Color(120, 200, 255, 255)

    def get_editable(self, nid: int) -> Editable:
        for e in self.editables:
            if e.node.nid == nid:
                return e
        
        raise ValueError(nid)

    def set_editable(self, e: Editable) -> None:
        for i, a in enumerate(self.editables):
            if a.node.nid == e.node.nid:
                self.editables[i] = e
                return
        
        self.editables.append(e)
    
    def get_editables_keys(self) -> list[int]:
        return list(map(lambda e: e.node.nid, self.editables))
    
    def refresh_running_state(self) -> None:
        ctrl = pr.is_key_down(pr.KeyboardKey.KEY_LEFT_CONTROL)

        if pr.window_should_close():
            self.is_running = False
        
        q = pr.is_key_pressed(pr.KeyboardKey.KEY_Q)
        if ctrl and q:
            self.is_running = False

    def launch(self) -> None:
        pr.init_window(0, 0, "Maptor [proto | beta]")
        pr.set_exit_key(pr.KeyboardKey.KEY_NULL)
        pr.toggle_fullscreen()
        #pr.set_target_fps(pr.get_monitor_refresh_rate(pr.get_current_monitor()))
        
        self.load_stuff()
        
        while self.is_running:
            pr.begin_drawing()
            pr.clear_background(self.bg)

            pr.begin_mode_2d(self.cam)
            self.editables.clear()
            self.canvas()
            self.handle_editables()
            self.render_cursor()
            # must be the last one
            self.inputs()
            pr.end_mode_2d()
            
            self.gui()
            pr.end_drawing()

            self.refresh_running_state()
        
        self.unload_stuff()
        pr.close_window()

    def handle_editables(self) -> None:
        mouse_pos = pr.get_screen_to_world_2d(pr.get_mouse_position(), self.cam)
        mouse_click = pr.is_mouse_button_down(pr.MouseButton.MOUSE_BUTTON_LEFT)
        
        for e in self.editables:
            bounding_box = self.editable_bounding_box(e)
            
            hover = pr.check_collision_point_rec(mouse_pos, bounding_box)
            if hover:
                pr.draw_rectangle_rec(bounding_box, self.tc_shapewire)

                if mouse_click:
                    self.change_under_edit_to(e.node.nid)

    def editable_bounding_box(self, e: Editable) -> pr.Rectangle:
        x_offset = 0
        w_offset = 0
        if e.is_quoted_lit():
            x_offset = self.adjust(-1)
            w_offset = 2

        return pr.Rectangle(
            e.x + x_offset, e.y,
            self.adjust(e.content_len() + w_offset),
            self.text_size
        )

    def render_cursor(self) -> None:
        if self.under_edit == None:
            return
        
        e = self.cur_under_edit
        if e.field_name == None:
            cursor = self.editable_bounding_box(e)
            pr.draw_rectangle_rec(cursor, self.tc_shapewire)
        else:
            cursor_x_pos = e.x + self.adjust(self.under_edit_cursor_idx)
            cursor = pr.Rectangle(
                cursor_x_pos, e.y,
                self.adjust(0.2), self.text_size
            )
            pr.draw_rectangle_rec(cursor, self.tc_cursor)

    def canvas(self) -> None:
        self.x = 0
        self.y = 0
        self.max_x = 0
        self.base_x = 0
        self.indent_level = 0

        for decl in self.prj.decls:
            if not self.is_decl_visible(decl):
                continue

            self.decl(decl)
            # flushing last line
            self.flat_carry()

            self.indent_level = 0
            self.base_x = self.max_x + self.adjust(self.interdecl_gap)
            self.x = self.base_x
            self.y = 0
        
    def is_decl_visible(self, decl: DeclNode) -> bool:
        # TODO: render only visible nodes
        return True
    
    def decl(self, decl: DeclNode) -> None:
        if decl.doc != "":
            self.doc(decl.doc)
            self.flat_carry()
        
        self.editable(decl, "name", self.tc_fn_name)
        
        match decl.value:
            case FnNode():
                self.fn_node(decl.value)

            case _:
                raise NotImplementedError(decl.value.__class__)

    def doc(self, s: str) -> None:
        lines = s.split("\n")
        height = self.vadjust(1) * len(lines) + self.vadjust(self.interline_gap) * (len(lines)-1)
        self.y -= height
        self.codewire(self.y + height)
        
        self.stmt_left_pad()
        
        for i, l in enumerate(lines):
            is_last_line = i != len(lines) - 1

            pieces = l.split("`")
            for j, p in enumerate(pieces):
                is_highlighted_piece = j % 2 == 1
                if is_highlighted_piece:
                    self.text(p, pr.color_alpha(self.tc_wire, 0.65))
                else:
                    self.text(p, self.tc_wire)

            if is_last_line:
                self.flat_carry()
        
        self.stmt_left_unpad()

    def adjust(self, length: float) -> float:
        # +1 and -1 are the spacings, we need length-1 of them (the last char doesn't have right spacing)
        return (self.code_font.widths[self.code_font.cur_idx] + 1) * length - 1
    
    def vadjust(self, height: float) -> float:
        return self.text_size * height
    
    def gap(self, length: float) -> None:
        self.x += self.adjust(length)

    def fn_node_head(self, fn: FnNode) -> None:
        self.gap(self.fn_call_par_gap)
        self.wire("(")

        if len(fn.ins) + len(fn.outs) == 0:
            self.wire(")")
            self.flat_carry()
            self.flat_carry()
            return

        param_left_padding = 2
        self.indent(param_left_padding)
        self.icarry()
        
        for p in fn.ins:
            self.editable(p, "name", self.tc_normal)
            self.typing_note_wire()
            self.expr(p.typing)

            self.icarry()
        
        for o in fn.outs:
            self.text("out", self.tc_kw)
            self.one()
            self.editable(o, "name", self.tc_normal)
            self.typing_note_wire()
            self.expr(o.typing)

            self.icarry()

        self.unindent(param_left_padding)
        self.wire(")")

        self.flat_carry()
        self.flat_carry()

    def fn_node(self, fn: FnNode) -> None:
        self.fn_node_head(fn)
        self.body(fn.body)
    
    def body(self, sts: list[StmtNode]) -> None:
        if len(sts) == 0:
            return

        for i, s in enumerate(sts):
            is_last = i == len(sts) - 1
            self.codewire_auto(s, is_last)
            
            self.stmt_left_pad()
            self.stmt(s)
            self.stmt_left_unpad()
            self.icarry()

    def codewire_auto(self, s: StmtNode, is_last: bool) -> None:
        if is_last or hasattr(s, "body"):
            self.codewire_flowstop(1)
        else:
            self.codewire(self.y + self.vadjust(1 + self.interline_gap))

    def codewire_flowstop(self, wire_len) -> None:
        y_end = self.y + self.vadjust(wire_len)/2
        self.codewire(y_end)
        left_padding = self.adjust(self.codewire_left_padding)
        pr.draw_line_ex(
            (left_padding + self.x, y_end),
            (left_padding + self.x + self.adjust(0.75), y_end),
            self.adjust(self.shapewire_thick),
            self.tc_shapewire)

    def stmt_left_pad(self):
        self.indent(self.stmt_side_padding)
        
    def stmt_left_unpad(self) -> None:
        self.unindent(self.stmt_side_padding)

    def stmt(self, s: StmtNode) -> None:
        match s:
            case ReturnNode():
                self.editable_solid("return", s, self.tc_kw)
            
            case CallNode():
                assert isinstance(s.callee, IdentNode)
                assert len(s.ins) <= 1
                assert len(s.outs) == 0

                self.editable(s.callee, "name", self.tc_fn_name)
                self.gap(self.fn_call_par_gap)
                self.wire("(")
                if len(s.ins) > 0:
                    self.expr(s.ins[0])
                self.wire(")")
            
            case IfNode():
                self.text("if", self.tc_kw)
                self.one()
                self.expr(s.expr)
                self.scope_indent()
                self.icarry()
                self.body(s.body)
                self.scope_unindent()
            
            case ElseNode():
                if not self.parallel_view_mode:
                    self.stmt(s.ifnode)
                    self.render_else_node_only(s.body)
                else:
                    self.begin_parallel()
                    self.stmt(s.ifnode)

                    self.new_column()

                    self.render_else_node_only(s.body)
                    self.end_parallel()
            
            case AssignNode():
                self.expr(s.assignee)
                self.one()
                self.text("=", self.tc_kw)
                self.one()
                self.expr(s.assigner)
            
            case StmtBufferNode():
                self.editable(s, "value", self.tc_normal)

            case _:
                raise NotImplementedError(s.__class__)
    
    def begin_parallel(self) -> None:
        original_base_x = self.base_x
        original_y = self.y
        previous_max_x = self.begin_local_max_x()
        self.parallel_contexts.append((original_base_x, original_y, previous_max_x, 0))

    def new_column(self) -> None:
        # temporarely popping context
        original_base_x, original_y, previous_max_x, final_y = self.parallel_contexts.pop()
        local_max_x = self.end_local_max_x(previous_max_x)
        final_y = final_y if final_y > self.y else self.y
        self.y = original_y
        self.use_local_max_x(local_max_x)

        # repush context with updated info
        self.parallel_contexts.append((original_base_x, original_y, previous_max_x, final_y))

    def end_parallel(self) -> None:
        original_base_x, _, _, _ = self.parallel_contexts.pop()
        self.base_x = original_base_x

    def render_else_node_only(self, body: list[StmtNode]) -> None:
        self.text("else", self.tc_kw)
        self.scope_indent()
        self.icarry()
        self.body(body)
        self.scope_unindent()

    def use_local_max_x(self, local_max_x: float) -> None:
        self.base_x = local_max_x + self.adjust(5)
        self.x = self.base_x

    def end_local_max_x(self, old_max_x: float) -> float:
        self.x = self.base_x
        local_max_x = self.max_x
        self.max_x = old_max_x
        return local_max_x

    def begin_local_max_x(self) -> float:
        old_max_x = self.max_x
        self.max_x = self.x
        return old_max_x

    def expr(self, e: ExprNode) -> None:
        match e:
            case IdentNode():
                starts_with_capital = len(e.name) > 0 and e.name[0] in string.ascii_uppercase
                if starts_with_capital or e.name in PRIMITIVE_IDENTS:
                    self.editable(e, 'name', self.tc_typing)
                else:
                    self.editable(e, 'name', self.tc_normal)
            
            case LitChrNode():
                assert isinstance(e.value, str)
                self.editable_custom_render(
                    "'" + repr('"' + e.value).removeprefix("'\"").replace("\\\\", "\\"),
                    self.x + self.adjust(1),
                    e,
                    "value",
                    self.tc_lit
                )

            case LitNode():
                match e.value:
                    case None:
                        self.editable_solid("null", e, self.tc_lit)
                    case bool():
                        self.editable_solid("true" if e.value else "false", e, self.tc_lit)
                    case str():
                        self.editable_custom_render(
                            '"' + repr("'" + e.value).removeprefix('"\'').replace("\\\\", "\\"),
                            self.x + self.adjust(1),
                            e,
                            "value",
                            self.tc_lit
                        )
                    case _:
                        self.text(repr(e.value), self.tc_lit)
            
            case BinaryNode():
                # TODO add parenthesis when exprs must have implicit precedence
                # or maybe just add EnclosedNode
                self.expr(e.l)
                self.one()
                self.text(e.op, self.tc_kw)
                self.one()
                self.expr(e.r)

            case PlaceholderNode():
                self.text("_", self.tc_wire)

            case _:
                raise NotImplementedError(e.__class__)

    def one(self, n: int = 1) -> None:
        self.text(" " * n, self.tc_normal)

    def update_xmax(self, max_x: float) -> float:
        if self.x > max_x:
            return self.x
        
        return max_x

    def typing_note_wire(self) -> None:
        self.text(": ", self.tc_wire)
    
    def borderwire(self, end_x: float) -> None:
        self.flat_carry()
        pr.draw_line_ex((self.x, self.y), (end_x, self.y), self.adjust(self.shapewire_thick), self.tc_shapewire)
        self.flat_carry()
    
    def codewire(self, end_y: float) -> None:
        left_padding = self.adjust(self.codewire_left_padding)
        pr.draw_line_ex((left_padding + self.x, self.y), (left_padding + self.x, end_y), self.adjust(self.shapewire_thick), self.tc_shapewire)

    def wire(self, txt: str) -> None:
        self.text(txt, self.tc_wire)

    def flat_carry(self) -> None:
        if self.x > self.max_x:
            self.max_x = self.x
        
        self.x = self.base_x
        self.y += self.text_size + self.vadjust(self.interline_gap)
    
    def icarry(self) -> None:
        self.flat_carry()
        self.x += self.adjust(self.indent_level)
    
    def carry_at(self, desired_x: float) -> None:
        self.flat_carry()
        self.x = desired_x
    
    def indent(self, length: float, sign: int = +1) -> None:
        self.base_x += sign*self.adjust(length)
        self.x += sign*self.adjust(length)

    def unindent(self, length: float) -> None:
        self.indent(length, -1)
    
    def scope_indent(self) -> None:
        self.indent(self.indent_level_step)

    def scope_unindent(self) -> None:
        self.unindent(self.indent_level_step)
    
    def text(self, text: str, color: pr.Color) -> None:
        pr.draw_text_ex(
            self.code_font.cur_font,
            text,
            (self.x, self.y),
            self.text_size,
            1,
            color
        )

        m = pr.measure_text_ex(
            self.code_font.cur_font, text, self.text_size, 1
        )

        self.x += m.x
    
    def editable(self, node: Node, field_name: str, color: pr.Color) -> None:
        self.set_editable(Editable(node, field_name, self.x, self.y))
        self.text(getattr(node, field_name), color)
        #txt = cast(str, getattr(node, field_name)).split("_")
        #for i, t in enumerate(txt):
        #    self.text(t, color)
        #    if i != len(txt) - 1:
        #        self.text("_", self.tc_wire)
    
    def editable_custom_render(self, rendering_text: str, x: float, node: Node, field_name: str, color: pr.Color) -> None:
        self.set_editable(Editable(node, field_name, x, self.y))
        self.text(rendering_text, color)

    def editable_solid(self, rendering_text: str, node: Node, color: pr.Color) -> None:
        self.set_editable(Editable(node, None, self.x, self.y, SolidContent(len(rendering_text))))
        self.text(rendering_text, color)

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
            self.tc_dbg_gui
        )
    
    def display_logs(self) -> None:
        for i, (tag, msg) in enumerate(self.logs.items()):
            content = f"{tag}: {msg}"
            measure = pr.measure_text_ex(self.gui_font, content, self.gui_font_size, 1)

            pr.draw_text_ex(
                self.gui_font,
                content,
                (
                    self.w - measure.x - self.gui_padding,
                    self.gui_padding + (measure.y + self.gui_padding) * i
                ),
                self.gui_font_size,
                1,
                self.tc_dbg_gui
            )

    def log(self, tag: str, msg: object) -> None:
        self.logs[tag] = repr(msg)

    def inputs(self) -> None:
        ctrl = pr.is_key_down(pr.KeyboardKey.KEY_LEFT_CONTROL)
        shift = pr.is_key_down(pr.KeyboardKey.KEY_LEFT_SHIFT)

        mouse_dx_btn = pr.is_mouse_button_down(pr.MouseButton.MOUSE_BUTTON_RIGHT)
        if mouse_dx_btn or shift:
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
            self.handle_zoom(mouse_scroll)

        if ctrl and pr.is_key_pressed(pr.KeyboardKey.KEY_P):
            self.parallel_view_mode = not self.parallel_view_mode
        
        if self.under_edit != None:
            if pr.is_key_pressed(pr.KeyboardKey.KEY_TAB):
                ks = self.get_editables_keys()
                ki = ks.index(self.under_edit)
                if shift:
                    self.change_under_edit_to(ks[ki-1 if ki-1 >= 0 else 0])
                else:
                    self.change_under_edit_to(ks[ki+1 if ki+1 < len(ks) else len(ks)-1])
            
            if pr.is_key_pressed(pr.KeyboardKey.KEY_ESCAPE):
                self.change_under_edit_to(None)

            if pr.is_key_pressed(pr.KeyboardKey.KEY_ENTER):
                nid = self.add_node_below()
                self.change_under_edit_to(nid, new_one_born_on_this_frame=True)
                # we can't continue because that nid
                # will be valid starting from the next frame
                return

            if self.cur_under_edit.field_name == None:
                self.handle_solid_editing_inputs(ctrl)
            else:
                self.handle_editing_inputs(ctrl)
    
    def find_room_below(self, node: Node | None) -> tuple[list[Node], Node, Node]:
        assert node != None, "Node type not found"

        match node:
            case IncomeNode():
                assert isinstance(node.parent, FnNode)
                return cast(list[Node], node.parent.ins), node, IncomeNode("new_income", IdentNode("i32"))
            case OutcomeNode():
                assert isinstance(node.parent, FnNode)
                return cast(list[Node], node.parent.outs), node, OutcomeNode("new_outcome", IdentNode("i32"))
            case StmtNode():
                body = getattr(node.parent, "body")
                return cast(list[Node], body), node, StmtBufferNode()
            case _:
                return self.find_room_below(node.parent)

    def add_node_below(self) -> int:
        node = self.cur_under_edit.node
        seq, cur, new_node = self.find_room_below(node)

        new_node.parent = cur.parent
        seq.insert(utils.index_of(seq, cur) + 1, new_node)

        return new_node.nid

    def handle_editing_inputs(self, ctrl: bool) -> None:
        assert self.under_edit != None
        e = self.cur_under_edit
        
        if pr.is_key_pressed(pr.KeyboardKey.KEY_LEFT):
            if ctrl:
                self.cursor_skip_word(direction=-1)
            else:
                if self.under_edit_cursor_idx > 0:
                    self.under_edit_cursor_idx -= 1

        if pr.is_key_pressed(pr.KeyboardKey.KEY_RIGHT):
            if ctrl:
                self.cursor_skip_word(direction=+1)
            else:
                if self.under_edit_cursor_idx < e.content_len():
                    self.under_edit_cursor_idx += 1
        
        key_begin = pr.KeyboardKey.KEY_KP_7
        if pr.is_key_pressed(key_begin):
            self.under_edit_cursor_idx = 0

        key_end = pr.KeyboardKey.KEY_KP_1
        if pr.is_key_pressed(key_end):
            self.under_edit_cursor_idx = self.cur_under_edit.content_len()
            
        keychar = chr(pr.get_char_pressed())
        if self.cur_under_edit.supports_char(keychar):
            idx = self.under_edit_cursor_idx
            content = e.content()
            e.set_content(content[:idx] + keychar + content[idx:])
            self.under_edit_cursor_idx += 1
            
        if pr.is_key_pressed(pr.KeyboardKey.KEY_BACKSPACE):
            idx = self.under_edit_cursor_idx
            if ctrl:
                content = e.content()
                self.cursor_skip_word(direction=-1)
                delta = abs(idx - self.under_edit_cursor_idx)
                e.set_content(content[:idx-delta] + content[idx:])
            else:
                if idx > 0:
                    content = e.content()
                    e.set_content(content[:idx-1] + content[idx:])
                    self.under_edit_cursor_idx -= 1
    
    def cursor_skip_word(self, direction: int) -> None:
        self.cursor_skip_while(direction, lambda c: c not in IDENT_CHARS)
        self.cursor_skip_while(direction, lambda c: c in IDENT_CHARS)

    def cursor_skip_while(self, direction: int, predicate: Callable[[str], bool]) -> None:
        skip_count = 0
        content = self.cur_under_edit.content()
        i = self.under_edit_cursor_idx
        
        match direction:
            case -1:
                offset = -1
                has_left = lambda: i > 0
                has_right = lambda: i <= len(content)
            case 1:
                offset = 0
                has_left = lambda: i >= 0
                has_right = lambda: i < len(content)
            case _:
                raise ValueError()

        while has_left() and has_right():
            c = content[i + offset]

            if predicate(c):
                skip_count += 1
                i += direction
            else:
                if skip_count == 0:
                    i += direction
                
                break
        
        self.under_edit_cursor_idx = i

    def get_tmp_node_for(self, node: Node) -> Node:
        match node:
            case StmtNode():
                return StmtBufferNode()
            case ExprNode():
                return IdentNode("")
            case _:
                return PlaceholderNode()

    def handle_solid_editing_inputs(self, ctrl: bool) -> None:
        assert self.under_edit != None
        e = self.cur_under_edit
        assert e.solid_content != None
            
        if pr.is_key_pressed(pr.KeyboardKey.KEY_BACKSPACE):
            assert e.node.parent != None
            new_node = self.get_tmp_node_for(e.node)
            new_node.parent = e.node.parent

            self.change_under_edit_to(new_node.nid, new_one_born_on_this_frame=True)

            e.node.parent.set_child(e.node.nid, new_node)
            e.node = new_node
            e.field_name = "name"
            e.solid_content = None

    def change_under_edit_to(self, new_one: int | None, new_one_born_on_this_frame: bool = False) -> None:
        if self.under_edit != None:
            if self.cur_under_edit.content_len() == 0 and not self.cur_under_edit.is_quoted_lit():
                self.cur_under_edit.set_content("_")

        self.under_edit = new_one
        if self.under_edit != None and not new_one_born_on_this_frame:
            self.under_edit_cursor_idx = self.cur_under_edit.content_len()
        else:
            self.under_edit_cursor_idx = 0

    def handle_zoom(self, mouse_scroll: float) -> None:
        world_mouse_x = self.cam.target.x
        world_mouse_y = self.cam.target.y

        anchor_x = world_mouse_x / self.text_size
        anchor_y = world_mouse_y / self.text_size

        self.text_size += mouse_scroll
        self.cap_text_size()
        self.refresh_code_font()

        # moving camera to anchor point (center of viewport)
        new_world_mouse_x = anchor_x * self.text_size
        new_world_mouse_y = anchor_y * self.text_size
        self.cam.target.x = new_world_mouse_x
        self.cam.target.y = new_world_mouse_y
    
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
        #self.code_font.load("res/3270.ttf")
        self.code_font.load("res/hurmit.otf")
        #self.code_font.load("res/agave.ttf")
        #self.code_font.load("res/jetbrains.ttf")
        self.text_size: float = 20
        self.refresh_code_font()

        self.gui_font_size: int = 20
        self.gui_font: pr.Font = self.code_font.fonts[self.code_font.get_best_font_from_size(self.gui_font_size)]

        m = pr.measure_text_ex(self.code_font.cur_font, " ", self.text_size, 1)
        self.font_h_to_w_ratio = m.x / m.y

        self.prj: Project = Project("res/my_project.mpt")
        self.prj.load()
    
    def unload_stuff(self) -> None:
        self.code_font.unload()
        self.prj.unload()
