import matplotlib.pyplot as plt
import numpy as np
from transformation import rot_z

fig, ax = plt.subplots()
def circle_involute(a,l):
    t=np.linspace(0,l,20)
    x = a * (t * np.sin(t) + np.cos(t))
    y = a * (np.sin(t) - t * np.cos(t))
    return x, y

def calculate_one_tooth(a, b, alfa, m, n_teeth, shift):
    """

    :param shift: зсув
    :param n_teeth: кількість зубців
    :param m: модуль = pitch_d/teeth
    :param a: висота ніжки зуба
    :param b: висота голівки зуба
    :param alfa: кут зачеплення
    :return: контур одного зуба
    """
    alfa=np.deg2rad(alfa)
    pitch_d= m * n_teeth
    out_d = pitch_d + b  # діаметр вершин зубів окружності
    root_d = pitch_d - a  # діаметр впадин зубів окружності
    pitch_r= pitch_d / 2
    out_r=out_d/2
    root_r=root_d/2
    t=np.linspace(0,2*np.pi)
    pitch_circle_x=pitch_r*np.cos(t)
    pitch_circle_y=pitch_r*np.sin(t)

    out_circle_x=out_r*np.cos(t)
    out_circle_y=out_r*np.sin(t)

    root_circle_x=root_r*np.cos(t)
    root_circle_y=root_r*np.sin(t)

    xt=np.array([-3,3])
    yt=-np.tan(alfa)*xt+pitch_r
    yrt=xt/np.tan(alfa)
    xi=pitch_r/((1/np.tan(alfa))+np.tan(alfa))
    yi=xi/np.tan(alfa)
    base_r=np.sqrt(xi*xi+yi*yi)
    base_circle_x=base_r*np.cos(t)
    base_circle_y=base_r*np.sin(t)
    tip_r= (pitch_d + 2 * m * (1 + shift)) / 2
    l= np.sqrt(tip_r * tip_r / base_r / base_r - 1)
    tooth=np.array(circle_involute(base_r,l))

    fTipPressureAngle = np.rad2deg(np.arccos((base_r*2) / (tip_r*2)))
    fInvAlpha = np.tan(alfa) - alfa
    fInvAlphaA = np.tan(fTipPressureAngle * np.pi / 180) - fTipPressureAngle * np.pi / 180
    fTopThickness = np.pi / (2 * n_teeth) + (2 * shift * np.tan(alfa)) / n_teeth + fInvAlpha - fInvAlphaA

    x1 = base_r
    y1 = 0
    x2 = base_r * (np.cos(l) + l * np.sin(l))
    y2 = base_r * (np.sin(l) - l * np.cos(l))
    d = np.sqrt((x1 - x2) **2 + (y1 - y2) **2)
    cosx = (base_r **2 + tip_r**2 - d **2) / 2 / base_r / tip_r
    tooth_thickness = 2 * np.rad2deg(fTopThickness) + 2 * np.rad2deg(np.arccos(cosx))
    rot=rot_z(np.c_[tooth[0],-tooth[1]],-tooth_thickness)
    tooth=np.c_[tooth,np.flip(rot.T,1)]

    ax.plot(pitch_circle_x, pitch_circle_y, color="r")
    ax.plot(out_circle_x, out_circle_y, color="g")
    ax.plot(root_circle_x, root_circle_y, color="c")
    ax.plot(xt,yt)
    ax.plot(xt,yrt)
    ax.plot(xi,yi,"o")
    # ax.plot(*tooth)

    ax.plot(base_circle_x, base_circle_y, color="b")


    return tooth

def generate_teeth(tooth,n_teeth):
    angle=360/n_teeth
    teeth=np.array([rot_z(tooth.T,angle*i).T for i in range (n_teeth)])
    for i in teeth:
        ax.plot(*i)
    return teeth
if __name__ == '__main__':
    a=3
    b=3
    alfa=20
    m=1
    n_teeth=18
    shift=0
    generate_teeth(calculate_one_tooth(a, b, alfa, m, n_teeth, shift),n_teeth)
    plt.gca().set_aspect("equal")
    plt.show()