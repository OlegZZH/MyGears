import glob
import json
import os
from pathlib import Path

import imgui
import moderngl
import numpy as np
from PIL import ImageColor
from pyrr import Matrix44

from base import CameraWindow
from bl_add_gear import Gear3d

face_color = np.array(ImageColor.getcolor("#0071b8", "RGB")) / 255
grid_color = np.array(ImageColor.getcolor("#eeeeee", "RGB")) / 255
axis_color = np.array(ImageColor.getcolor("#FF4D80", "RGB")) / 255
ambient = np.array([0.4125, 0.435, 0.425]).astype('f4')
diffuse = np.array([0.5038, 0.5048, 0.528]).astype('f4')
specular = np.array([0.777, 0.622, 0.6014]).astype('f4')
shininess = 512
light_position = np.array([0, 0, -3], dtype='f4')
light_ambient = np.array([0.2, 0.2, 0.2], dtype='f4')
light_diffuse = np.array([0.8, 0.8, 0.8], dtype='f4')
light_specular = np.array([1.0, 1.0, 1.0], dtype='f4')


def terrain(size):
    vertices = np.dstack(np.mgrid[0:size, 0:size][::-1]) / size
    temp = np.dstack([np.arange(0, size * size - size), np.arange(size, size * size)])
    index = np.pad(temp.reshape(size - 1, 2 * size), [[0, 0], [0, 1]], 'constant', constant_values=-1)
    return vertices, index


def axis():
    buffer = np.array([[0, 10, 0], [0, -10, 0], [-10, 0, 0], [10, 0, 0], [0, 0, 10], [0, 0, -10]])
    return buffer


class GearGenerator(CameraWindow):
    aspect_ratio = 16 / 9
    resource_dir = (Path(__file__) / '../../Gears/resources').resolve()
    title = "Cube Model"
    fullscreen = True
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.remove_gear = None
        self.add_gear = None
        self.enable_profile = True
        self.s = None
        self.create_gear = False
        self.load = False
        self.create_window_is_open = False
        self.clicked_load = False
        self.selected = np.full(10, 0)

        self.wnd.mouse_exclusivity = True

        self.gear_collation = []
        self.scene = Scene()
        # self.scene.add_obj(self.load_scene("scenes\\myfile.obj"),Matrix44.from_translation((0, 0, 0)).astype('f4'))

        self.camera.projection.update(near=0.1, far=1000.0)
        self.camera.velocity = 10.0
        self.camera.mouse_sensitivity = 0.3
        self.gear_param = {"thickness": 3, "name": "Gear_1",
                           "path": "C:\\Users\\Oleg\\Dropbox\\Gears\\resources\\scenes",
                           "location": [0, 0, 0], "a": 2.5, "b": 2, "alfa": 20, "m": 1, "n_teeth": 10, "shift": 0}
        self.prog = self.load_program(vertex_shader=r"programs\vertex_shader.glsl",
                                      fragment_shader=r"programs\fragment_shader.glsl")
        self.P_M = self.prog["prog"]
        self.C_M = self.prog["cam"]
        self.L_M = self.prog["lookat"]
        self.T_M = self.prog["trans"]
        self.switcher = self.prog["switcher"]
        self.viewPos = self.prog["viewPos"]
        self.shininess = self.prog["material.shininess"]
        self.lightPos = self.prog["light.position"]
        self.light_ambient = self.prog["light.ambient"]
        self.light_diffuse = self.prog["light.diffuse"]
        self.light_specular = self.prog["light.specular"]

        self.previwe = {n: self.load_preview_texture(n) for n in ["a", "b", "angle"]}

        vertices, ind = terrain(30)
        vertices[:, :, :] -= 0.5
        vertices *= 100

        self.vbo_grid = self.ctx.buffer(vertices.astype('f4'))
        self.ibo_g = self.ctx.buffer(ind.astype('i4'))
        self.vbo_axis = self.ctx.buffer(axis().astype('f4'))

        self.vao_grid = self.ctx.vertex_array(self.prog, [(self.vbo_grid, '2f', 'in_vert')], self.ibo_g)
        self.vao_axis = self.ctx.vertex_array(self.prog, self.vbo_axis, 'in_vert')

        self.lookat = Matrix44.look_at(
            (15, 0, 1.0),  # eye
            (0, 0, 1.0),  # target
            (.0, .0, 1.0),  # up
        )
        self.L_M.write(self.lookat.astype('f4'))
        self.shininess.value = shininess
        self.lightPos.write(light_position)
        self.light_ambient.write(light_ambient)
        self.light_diffuse.write(light_diffuse)
        self.light_specular.write(light_specular)

        io = imgui.get_io()
        self.new_font = io.fonts.add_font_from_file_ttf(
            "Semi-Coder-Regular.ttf", 30,
        )
        self.imgui.refresh_font_texture()

    def key_event(self, key, action, modifiers):
        keys = self.wnd.keys
        self.imgui.key_event(key, action, modifiers)

        if self.camera_enabled:
            self.camera.key_input(key, action, modifiers)

        if action == keys.ACTION_PRESS:
            if key == keys.C:
                self.camera_enabled = not self.camera_enabled
                self.wnd.mouse_exclusivity = self.camera_enabled
                self.wnd.cursor = not self.camera_enabled
            if key == keys.SPACE:
                self.timer.toggle_pause()
            if modifiers.ctrl == True and key == keys.Q:
                self.wnd.close()
            if modifiers.ctrl == True and key == keys.N:
                self.create_window_is_open = True

    def load_preview_texture(self, name):
        texture = self.load_texture_2d(f'texture/{name}.png', flip_y=False)

        self.imgui.register_texture(texture)
        return texture

    def render(self, time: float, frametime: float):
        self.ctx.clear(*face_color)
        self.ctx.enable_only(moderngl.DEPTH_TEST)

        self.P_M.write(self.camera.projection.matrix.astype('f4'))
        self.C_M.write(self.camera.matrix.astype('f4'))
        self.T_M.write(Matrix44.from_translation((0, 0, 0)).astype('f4'))
        self.viewPos.write(self.camera.position.astype('f4'))

        self.ctx.wireframe = True
        self.switcher.write(grid_color.astype('f4'))
        self.vao_grid.render(moderngl.TRIANGLE_STRIP)
        self.switcher.write(axis_color.astype('f4'))
        self.vao_axis.render(moderngl.LINES)

        self.ctx.wireframe = False
        for n, obj in enumerate(self.scene.scene):
            if n > 0:
                speed = (self.scene.scene[0].gear_info["pitch_d"] / obj.gear_info["pitch_d"])
                if obj.gear_info["n_teeth"] % 2 == 0:
                    obj.angle = 180 / obj.gear_info["n_teeth"] - obj.gear_info["tooth_thickness"] - self.scene.scene[
                        n - 1].angle
                else:
                    obj.angle = 360 / obj.gear_info["n_teeth"] - obj.gear_info["tooth_thickness"] - self.scene.scene[
                        n - 1].angle
                if n % 2 != 0:
                    speed *= -1
            else:
                speed = 1

            rotation = Matrix44.from_x_rotation(np.pi * 1.5, dtype="f4") @ Matrix44.from_z_rotation(time * speed,
                                                                                                    dtype="f4") @ Matrix44.from_z_rotation(
                np.deg2rad(obj.angle), dtype="f4") @ obj.model_matrix
            obj.gear_3d_obj.draw(
                projection_matrix=self.camera.projection.matrix,
                camera_matrix=self.camera.matrix * self.lookat * rotation,
                time=time,

            )

        self.render_ui()

    def render_ui(self):
        imgui.new_frame()

        imgui.push_style_color(imgui.COLOR_WINDOW_BACKGROUND, *face_color*0.7)
        imgui.push_style_var(imgui.STYLE_ALPHA, 0.9)

        imgui.push_style_color(imgui.COLOR_TEXT, *grid_color)
        imgui.push_style_color(imgui.COLOR_FRAME_BACKGROUND, *face_color*0.7)
        imgui.push_style_color(imgui.COLOR_TITLE_BACKGROUND, *face_color*0.7)
        imgui.push_style_color(imgui.COLOR_TITLE_BACKGROUND_ACTIVE, *face_color*0.7)
        imgui.push_style_var(imgui.STYLE_GRAB_ROUNDING, 10.0)
        imgui.push_style_var(imgui.STYLE_FRAME_ROUNDING, 10.0)
        imgui.push_font(self.new_font)

        if imgui.begin_main_menu_bar():
            if imgui.begin_menu("File", True):

                clicked_quit, selected_quit = imgui.menu_item("Quit", 'Ctrl+Q', False, True)
                if clicked_quit:
                    exit(1)
                self.create_window_is_open, selected_new = imgui.menu_item('Create new gear', 'Cmd+N',
                                                                           self.create_window_is_open, True)
                self.clicked_load, selected_load = imgui.menu_item('Load file', 'Cmd+O', self.clicked_load, True)

                imgui.end_menu()
            imgui.end_main_menu_bar()
        if self.create_window_is_open:
            self.new_gear()
        if self.clicked_load:
            self.load_file_window()

        imgui.begin("Gear Generator")
        for obj in self.scene.scene:
            if imgui.tree_node(obj.gear_info["name"]):
                imgui.text("Number of teeth - {}".format(obj.gear_info["n_teeth"]))
                imgui.text("a - {}".format(obj.gear_info["a"]))
                imgui.text("b - {}".format(obj.gear_info["b"]))
                imgui.text("Profile shift - {}".format(obj.gear_info["shift"]))
                imgui.text("Engagement angle - {}".format(obj.gear_info["alfa"]))
                imgui.text("Module - {}".format(obj.gear_info["m"]))
                imgui.text("Gear thickness - {}".format(obj.gear_info["thickness"]))
                imgui.text("Pitch Diameter - {}".format(obj.gear_info["pitch_d"]))
                imgui.text("Tip Diameter - {}".format(obj.gear_info["out_d"]))
                imgui.text("Root Diameter - {}".format(obj.gear_info["root_d"]))
                imgui.text("Base Diameter - {}".format(obj.gear_info["base_r"] * 2))
                imgui.text("Tooth thickness - {}".format(obj.gear_info["tooth_thickness"]))
                imgui.tree_pop()
        self.add_gear = imgui.button("+ Add gear")
        imgui.same_line()
        self.remove_gear = imgui.button("- Remove gear")
        if self.add_gear:
            imgui.open_popup("Choose how to add")
        imgui.same_line()
        if imgui.begin_popup("Choose how to add"):
            if imgui.selectable("Create new gear")[1]: self.create_window_is_open = True
            if imgui.selectable("Load file")[1]: self.clicked_load = True
            imgui.end_popup()
        if self.remove_gear and self.scene.scene:
            self.scene.remove()
        imgui.end()

        imgui.pop_font()
        imgui.pop_style_color()
        imgui.pop_style_color()
        imgui.pop_style_color()
        imgui.pop_style_color()
        imgui.pop_style_color()
        imgui.pop_style_var()
        imgui.pop_style_var()
        imgui.pop_style_var()
        # imgui.show_test_window()
        imgui.render()
        self.imgui.render(imgui.get_draw_data())

    def new_gear(self):
        _, self.create_window_is_open = imgui.begin("Create new gear_3d_obj", True)
        _, self.gear_param["name"] = imgui.input_text("Name", f"Gear_{len(self.scene.scene)}", 30)
        _, self.gear_param["shift"] = imgui.slider_float("Profile shift", self.gear_param["shift"], 0, 1)
        if imgui.is_item_hovered():
            imgui.begin_tooltip()
            imgui.text("If you use a shift then the following 2 parameters will be ignored")
            imgui.end_tooltip()
        _, self.gear_param["a"] = imgui.input_float("a", self.gear_param["a"], 0.1)
        if imgui.is_item_hovered():
            imgui.begin_tooltip()
            imgui.text("Tooth stem height")
            imgui.image(self.previwe["a"].glo, self.previwe["a"].width, self.previwe["a"].height)
            imgui.end_tooltip()
        _, self.gear_param["b"] = imgui.input_float("b", self.gear_param["b"], 0.1)
        if imgui.is_item_hovered():
            imgui.begin_tooltip()
            imgui.text("Tooth head height")
            imgui.image(self.previwe["b"].glo, self.previwe["b"].width, self.previwe["b"].height)
            imgui.end_tooltip()
        _, self.gear_param["alfa"] = imgui.input_float("alfa", self.gear_param["alfa"], 0.1)
        if imgui.is_item_hovered():
            imgui.begin_tooltip()
            imgui.text("Engagement angle")
            imgui.image(self.previwe["angle"].glo, self.previwe["angle"].width, self.previwe["angle"].height)
            imgui.end_tooltip()
        _, self.gear_param["m"] = imgui.input_float('m', self.gear_param["m"], 0.1)
        if imgui.is_item_hovered():
            imgui.begin_tooltip()
            imgui.text("Module m = diameter / n_teeth")
            imgui.end_tooltip()
        _, self.gear_param["n_teeth"] = imgui.input_int('Number of teeth', self.gear_param["n_teeth"])
        if imgui.is_item_hovered():
            imgui.begin_tooltip()
            imgui.text("Number of teeth")
            imgui.end_tooltip()
        _, self.gear_param["thickness"] = imgui.input_int('thickness', self.gear_param["thickness"], 0.1)
        if imgui.is_item_hovered():
            imgui.begin_tooltip()
            imgui.text("Gear thickness")
            imgui.end_tooltip()
        _, self.gear_param["path"] = imgui.input_text("Path", self.gear_param["path"], 60)
        self.create_gear = imgui.button("Create", 100, 40)
        imgui.end()

        if self.create_gear:
            g = Gear3d(self.gear_param['thickness'], self.gear_param['name'], self.gear_param['path'],
                       self.gear_param['location'], a=self.gear_param['a'], b=self.gear_param['b'],
                       alfa=self.gear_param['alfa'], m=self.gear_param['m'], n_teeth=self.gear_param['n_teeth'],
                       shift=self.gear_param['shift'])
            self.add2scene(os.path.join(self.gear_param['path'], '{}.obj'.format(self.gear_param['name'])), g.__dict__)

    def load_file_window(self):
        _, self.clicked_load = imgui.begin("Load file", True)
        _, self.gear_param["path"] = imgui.input_text("Path", self.gear_param["path"], 60)
        imgui.same_line()
        self.load = imgui.button("Change Directory", 220, 40)
        files = glob.glob(self.gear_param["path"] + "\*.obj")
        for n, i in enumerate(files):
            _, self.selected[n] = imgui.selectable(f"{n}. {os.path.basename(i)}", self.selected[n])
            if self.selected[n]:
                self.selected = np.full(len(self.selected), False)
                self.selected[n] = True
                self.s = i

        self.load = imgui.button("Load", 100, 40)
        if self.load:
            name = os.path.splitext(os.path.basename(self.s))[0]
            with open(os.path.join(self.gear_param["path"], f'{name}.json'), 'r') as f:
                loaded_gear = json.load(f)
            self.add2scene(self.s, loaded_gear)
        imgui.end()

    def add2scene(self, gear_path: str, gear_dict: dict):
        if not self.scene.scene:
            model_matrix = Matrix44.from_translation((0, 0, 0), dtype='f4')
        else:
            shift = sum(i.gear_info['pitch_d'] for i in self.scene.scene[1:]) + self.scene.scene[0].gear_info['pitch_r']
            model_matrix = Matrix44.from_translation((0, shift + gear_dict['pitch_r'], 0), dtype='f4')
        obj = self.load_scene(gear_path)

        self.scene.add_obj(obj, model_matrix, gear_dict, 0)


class Object:
    def __init__(self, gear, model_matrix, gear_info, angle):
        self.gear_3d_obj = gear
        self.model_matrix = model_matrix
        self.gear_info = gear_info
        self.angle = angle


class Scene:
    def __init__(self):
        self.scene = []

    def add_obj(self, gear, model, gear_info, angle):
        self.scene.append(Object(gear, model, gear_info, angle))

    def remove(self):
        self.scene.pop()


if __name__ == '__main__':
    # moderngl_window.run_window_config(GearGenerator)
    GearGenerator.run()
