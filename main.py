from pathlib import Path

import numpy as np
from PIL import ImageColor
from pyrr import Matrix44

import moderngl
import moderngl_window
from base import CameraWindow
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
        self.wnd.mouse_exclusivity = True
        self.scene = self.load_scene('scenes/myfile.obj')
        self.camera.projection.update(near=0.1, far=1000.0)
        self.camera.velocity = 10.0
        self.camera.mouse_sensitivity = 0.3
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
            (6, 0, 1.0),  # eye
            (0, 0, 1.0),  # target
            (.0, .0, 1.0),  # up
        )
        self.L_M.write(self.lookat.astype('f4'))
        self.shininess.value = shininess
        self.lightPos.write(light_position)
        self.light_ambient.write(light_ambient)
        self.light_diffuse.write(light_diffuse)
        self.light_specular.write(light_specular)

    def render(self, time: float, frametime: float):
        self.ctx.clear(*face_color)
        self.ctx.enable_only(moderngl.DEPTH_TEST )
        self.Texture.use()
        translation = Matrix44.from_translation((0, 0, 0))
        rotation = Matrix44.from_eulers((np.pi*1.5,0,time))
        model_matrix = translation * rotation

        camera_matrix = self.camera.matrix *self.lookat* model_matrix

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


if __name__ == '__main__':
    moderngl_window.run_window_config(CubeModel)