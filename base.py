import moderngl_window as mglw
import imgui
from moderngl_window.integrations.imgui import ModernglWindowRenderer
from moderngl_window.scene.camera import KeyboardCamera, OrbitCamera


class CameraWindow(mglw.WindowConfig):
    """Base class with built in 3D camera support"""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.camera = KeyboardCamera(self.wnd.keys, aspect_ratio=self.wnd.aspect_ratio)
        self.camera_enabled = True
        imgui.create_context()
        self.imgui = ModernglWindowRenderer(self.wnd)
        self.wnd.ctx.error






    def mouse_position_event(self, x: int, y: int, dx, dy):
        if self.camera_enabled:
            self.camera.rot_state(-dx, -dy)

    def resize(self, width: int, height: int):
        self.camera.projection.update(aspect_ratio=self.wnd.aspect_ratio)
        self.imgui.resize(width, height)

    def mouse_drag_event(self, x, y, dx, dy):
        self.imgui.mouse_drag_event(x, y, dx, dy)

    def mouse_release_event(self, x: int, y: int, button: int):
        self.imgui.mouse_release_event(x, y, button)

    def mouse_press_event(self, x, y, button):
        self.imgui.mouse_press_event(x, y, button)

    def mouse_scroll_event(self, x_offset, y_offset):
        self.imgui.mouse_scroll_event(x_offset, y_offset)
    def unicode_char_entered(self, char):
        self.imgui.unicode_char_entered(char)


class OrbitCameraWindow(mglw.WindowConfig):
    """Base class with built in 3D orbit camera support

    Move the mouse to orbit the camera around the view point.
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.camera = OrbitCamera(aspect_ratio=self.wnd.aspect_ratio)
        self.camera_enabled = True

    def key_event(self, key, action, modifiers):
        keys = self.wnd.keys


        if action == keys.ACTION_PRESS:
            if key == keys.C:
                self.camera_enabled = not self.camera_enabled
                self.wnd.mouse_exclusivity = self.camera_enabled
                self.wnd.cursor = not self.camera_enabled
            if key == keys.SPACE:
                self.timer.toggle_pause()

    def mouse_position_event(self, x: int, y: int, dx, dy):
        if self.camera_enabled:
            self.camera.rot_state(dx, dy)

    def mouse_scroll_event(self, x_offset: float, y_offset: float):
        if self.camera_enabled:
            self.camera.zoom_state(y_offset)

    def resize(self, width: int, height: int):
        self.camera.projection.update(aspect_ratio=self.wnd.aspect_ratio)


class OrbitDragCameraWindow(mglw.WindowConfig):
    """Base class with drag-based 3D orbit support

    Click and drag with the left mouse button to orbit the camera around the view point.
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.camera = OrbitCamera(aspect_ratio=self.wnd.aspect_ratio)

    def key_event(self, key, action, modifiers):
        keys = self.wnd.keys

        if action == keys.ACTION_PRESS:
            if key == keys.SPACE:
                self.timer.toggle_pause()

    def mouse_drag_event(self, x: int, y: int, dx, dy):
        self.camera.rot_state(dx, dy)

    def mouse_scroll_event(self, x_offset: float, y_offset: float):
        self.camera.zoom_state(y_offset)

    def resize(self, width: int, height: int):
        self.camera.projection.update(aspect_ratio=self.wnd.aspect_ratio)
