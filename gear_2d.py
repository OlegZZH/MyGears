import matplotlib.pyplot as plt
import numpy as np

from transformation import rot_z


class Gear2d:
    def __init__(self, a, b, alfa, m, n_teeth, shift):
        """
        :param shift: зсув
        :param n_teeth: кількість зубців
        :param m: модуль = pitch_d/teeth
        :param a: висота ніжки зуба
        :param b: висота голівки зуба
        :param alfa: кут зачеплення
        :return: контур одного зуба
        """
        self.edges = None
        self.arc_y = None
        self.arc_x = None
        self.base_circle_y = None
        self.base_circle_x = None
        self.yi = None
        self.xi = None
        self.yrt = None
        self.yt = None
        self.xt = None
        self.root_circle_y = None
        self.root_circle_x = None
        self.out_circle_y = None
        self.out_circle_x = None
        self.pitch_circle_y = None
        self.pitch_circle_x = None
        self.tooth = None
        self.gear = None
        self.a = a
        self.b = b
        self.alfa = np.deg2rad(alfa)
        self.m = m
        self.n_teeth = n_teeth
        self.shift = shift

        self.pitch_d = self.m * self.n_teeth
        self.out_d = self.pitch_d + self.b  # діаметр вершин зубів окружності
        self.root_d = self.pitch_d - self.a  # діаметр впадин зубів окружності
        self.pitch_r = self.pitch_d / 2
        self.out_r = self.out_d / 2
        self.root_r = self.root_d / 2

        self.calculate_one_tooth()
        self.generate_gear()
        self.create_edges()

    def calculate_one_tooth(self):
        t = np.linspace(0, 2 * np.pi)
        self.pitch_circle_x = self.pitch_r * np.cos(t)
        self.pitch_circle_y = self.pitch_r * np.sin(t)

        self.out_circle_x = self.out_r * np.cos(t)
        self.out_circle_y = self.out_r * np.sin(t)

        self.root_circle_x = self.root_r * np.cos(t)
        self.root_circle_y = self.root_r * np.sin(t)

        self.xt = np.array([-3, 3])
        self.yt = -np.tan(self.alfa) * self.xt + self.pitch_r
        self.yrt = self.xt / np.tan(self.alfa)
        self.xi = self.pitch_r / ((1 / np.tan(self.alfa)) + np.tan(self.alfa))
        self.yi = self.xi / np.tan(self.alfa)
        base_r = np.sqrt(self.xi * self.xi + self.yi * self.yi)
        self.base_circle_x = base_r * np.cos(t)
        self.base_circle_y = base_r * np.sin(t)
        tip_r = (self.pitch_d + 2 * self.m * (1 + self.shift)) / 2
        l = np.sqrt(tip_r * tip_r / base_r / base_r - 1)
        tooth = np.array(self.circle_involute(base_r, l))

        fTipPressureAngle = np.rad2deg(np.arccos((base_r * 2) / (tip_r * 2)))
        fInvAlpha = np.tan(self.alfa) - self.alfa
        fInvAlphaA = np.tan(fTipPressureAngle * np.pi / 180) - fTipPressureAngle * np.pi / 180
        fTopThickness = np.pi / (2 * self.n_teeth) + (
                    2 * self.shift * np.tan(self.alfa)) / self.n_teeth + fInvAlpha - fInvAlphaA

        x1 = base_r
        y1 = 0
        x2 = base_r * (np.cos(l) + l * np.sin(l))
        y2 = base_r * (np.sin(l) - l * np.cos(l))
        d = np.sqrt((x1 - x2) ** 2 + (y1 - y2) ** 2)
        cox = (base_r ** 2 + tip_r ** 2 - d ** 2) / 2 / base_r / tip_r
        tooth_thickness = 2 * np.rad2deg(fTopThickness) + 2 * np.rad2deg(np.arccos(cox))
        rot = rot_z(np.c_[tooth[0], -tooth[1]], -tooth_thickness)
        tooth = np.c_[tooth, np.flip(rot.T, 1)]
        second_tooth = rot_z(tooth.T, 360 / self.n_teeth).T
        arc_r = np.sqrt((tooth[0, 0] - second_tooth[0, -1]) ** 2 + (tooth[1, 0] - second_tooth[1, -1]) ** 2) / 2
        arc_center = [(tooth[0, 0] + second_tooth[0, -1]) / 2, (tooth[1, 0] + second_tooth[1, -1]) / 2]
        t2 = np.linspace(1.5 * np.pi - np.deg2rad(tooth_thickness / 2), np.pi / 2)
        self.arc_x = arc_r * np.cos(t2) + arc_center[0]
        self.arc_y = arc_r * np.sin(t2) + arc_center[1]
        self.tooth = np.flip(np.concatenate((np.array([self.arc_x, self.arc_y]), tooth), axis=1), 0)

    @staticmethod
    def circle_involute(r, l):
        t = np.linspace(0, l, 20)
        x = r * (t * np.sin(t) + np.cos(t))
        y = r * (np.sin(t) - t * np.cos(t))
        return x, y

    def generate_gear(self):
        angle = 360 / self.n_teeth
        self.gear = np.array([rot_z(self.tooth.T, angle * i) for i in range(self.n_teeth)]).reshape(-1, 2)

    def create_edges(self):
        self.edges = np.roll(np.repeat(np.array([i for i in range(len(self.gear))]), 2), -1).reshape(-1, 2)

    def show_gear(self):
        fig, ax = plt.subplots()
        ax.plot(self.pitch_circle_x, self.pitch_circle_y, color="r")
        ax.plot(self.out_circle_x, self.out_circle_y, color="g")
        ax.plot(self.root_circle_x, self.root_circle_y, color="c")
        ax.plot(self.xt, self.yt)
        ax.plot(self.xt, self.yrt)
        ax.plot(self.xi, self.yi, "o")
        # ax.plot(*self.tooth)
        # ax.plot(self.arc_x,self.arc_y)

        ax.plot(self.base_circle_x, self.base_circle_y, color="b")
        ax.plot(self.gear[:, 0], self.gear[:, 1])
        plt.gca().set_aspect("equal")
        plt.show()


if __name__ == '__main__':
    a = 3
    b = 3
    alfa = 20
    m = 1
    n_teeth = 18
    shift = 0
    gear = Gear_2d(a, b, alfa, m, n_teeth, shift)
    gear.show_gear()
