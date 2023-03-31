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


class CubeModel(CameraWindow):
    aspect_ratio = 16 / 9
    resource_dir = (Path(__file__) / '../../Gears/resources').resolve()
    title = "Cube Model"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.create_gear = False
        self.create_window_is_open = False

        self.wnd.mouse_exclusivity = True
        self.scene = self.load_scene('scenes/myfile.obj')

        self.camera.projection.update(near=0.1, far=1000.0)
        self.camera.velocity = 10.0
        self.camera.mouse_sensitivity = 0.3
        self.gear_param = {"thickness": 10, "name": "Gear_1", "path": "C:\\Users\\Oleg\\Dropbox\\Gears\\resources\\scenes",
                           "location": [0, 0, 0], "a": 3, "b": 3, "alfa": 20, "m": 1, "n_teeth": 18, "shift": 0}
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
        self.Texture = self.load_texture_2d(
            r'texture/watercolor-splash-background.jpg')

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

    def key_event(self, key, action, modifiers):
        keys = self.wnd.keys
        self.imgui.key_event(key, action, modifiers)
        # print("{},{},{},{}".format(key, action, modifiers,keys))
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

    def render(self, time: float, frametime: float):
        self.ctx.clear(*face_color)
        self.ctx.enable_only(moderngl.DEPTH_TEST)
        self.Texture.use()
        translation = Matrix44.from_translation((0, 0, 0))
        rotation = Matrix44.from_eulers((np.pi * 1.5, 0, time))
        model_matrix = translation * rotation

        camera_matrix = self.camera.matrix * self.lookat * model_matrix

        self.P_M.write(self.camera.projection.matrix.astype('f4'))
        self.C_M.write(self.camera.matrix.astype('f4'))
        self.T_M.write(translation.astype('f4'))
        self.viewPos.write(self.camera.position.astype('f4'))

        self.ctx.wireframe = True
        self.switcher.write(grid_color.astype('f4'))
        self.vao_grid.render(moderngl.TRIANGLE_STRIP)
        self.switcher.write(axis_color.astype('f4'))
        self.vao_axis.render(moderngl.LINES)

        self.ctx.wireframe = False

        self.scene.draw(
            projection_matrix=self.camera.projection.matrix,
            camera_matrix=camera_matrix,
            time=time,
        )
        self.render_ui()

    def render_ui(self):
        imgui.new_frame()
        if imgui.begin_main_menu_bar():
            if imgui.begin_menu("File", True):

                clicked_quit, selected_quit = imgui.menu_item("Quit", 'Ctrl+Q', False, True)
                if clicked_quit:
                    exit(1)
                self.create_window_is_open, selected_new = imgui.menu_item('Create new gear', 'Cmd+N',
                                                                           self.create_window_is_open, True)
                clicked_open, selected_open = imgui.menu_item('Open gear', 'Cmd+O', False, True)

                imgui.end_menu()
            imgui.end_main_menu_bar()
        if self.create_window_is_open:
            self.new_gear()

        imgui.show_test_window()
        imgui.render()
        self.imgui.render(imgui.get_draw_data())

    def new_gear(self):
        _, self.create_window_is_open = imgui.begin("Create new gear", True)
        _, self.gear_param["name"] = imgui.input_text("Name", self.gear_param["name"], 30)
        _, self.gear_param["a"] = imgui.input_float("a", self.gear_param["a"], 0.1)
        if imgui.is_item_hovered():
            imgui.begin_tooltip()
            imgui.text("Tooth stem height")
            imgui.end_tooltip()
        _, self.gear_param["b"] = imgui.input_float("b", self.gear_param["b"], 0.1)
        if imgui.is_item_hovered():
            imgui.begin_tooltip()
            imgui.text("Tooth head height")
            imgui.end_tooltip()
        _, self.gear_param["alfa"] = imgui.input_float("alfa", self.gear_param["alfa"], 0.1)
        if imgui.is_item_hovered():
            imgui.begin_tooltip()
            imgui.text("Engagement angle")
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
        _, self.gear_param["thickness"] = imgui.input_float('thickness', self.gear_param["thickness"], 0.1)
        if imgui.is_item_hovered():
            imgui.begin_tooltip()
            imgui.text("Gear thickness")
            imgui.end_tooltip()
        _, self.gear_param["path"] = imgui.input_text("Path", self.gear_param["path"], 60)
        self.create_gear = imgui.button("Create", 100, 20)
        imgui.end()
        if self.create_gear:
            Gear3d(self.gear_param['thickness'], self.gear_param['name'], self.gear_param['path'],
                   self.gear_param['location'], a=self.gear_param['a'], b=self.gear_param['b'],
                   alfa=self.gear_param['alfa'], m=self.gear_param['m'], n_teeth=self.gear_param['n_teeth'],
                   shift=self.gear_param['shift'])


if __name__ == '__main__':
    # moderngl_window.run_window_config(CubeModel)
    CubeModel.run()
