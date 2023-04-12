import pywavefront

# импорт первой шестеренки из .obj файла
mesh1 = pywavefront.Wavefront('resources/scenes/Gear_1.obj')
# создание объекта шестеренки 1
object1 = create_object(mesh1)

# импорт второй шестеренки из .obj файла
mesh2 = pywavefront.Wavefront('resources/scenes/Gear_2.obj')
# создание объекта шестеренки 2
object2 = create_object(mesh2)

# задание положения и вращения объектов в сцене
object1.set_position([0, 0, 0])
object1.set_rotation([0, 0, 0])

object2.set_position([1, 0, 0])
object2.set_rotation([0, 0, 0])

import pybullet as p

# инициализация симуляции
p.connect(p.GUI)
p.setGravity(0, 0, -10)

# создание тела для первой шестеренки
body1 = p.createCollisionShape(p.GEOM_MESH, vertices=mesh1.vertices, indices=mesh1.mesh_list[0].faces)
object1 = p.createMultiBody(baseMass=10, baseCollisionShapeIndex=body1)

# создание тела для второй шестеренки
body2 = p.createCollisionShape(p.GEOM_MESH, vertices=mesh2.vertices, indices=mesh2.mesh_list[0].faces)
object2 = p.createMultiBody(baseMass=10, baseCollisionShapeIndex=body2)

# задание параметров симуляции
p.setRealTimeSimulation(1)
p.setTimeStep(1/60)

# запуск симуляции
while True:
    p.stepSimulation()

contacts = p.getContactPoints(object1, object2)
if contacts:
    print("Коллизия!")