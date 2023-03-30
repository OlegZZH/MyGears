import os
import sys

import bpy
from math import *

import numpy as np
from matplotlib import pyplot as plt

# this is optional and allows you to call the functions without specifying the package name
from gear_2d import Gear

def createMeshFromData(name, origin, verts, edges):
    # Create mesh and object
    mesh_gear = bpy.data.meshes.new(name+'Mesh')
    object_gear = bpy.data.objects.new(name, mesh_gear)
    object_gear.location = origin
    object_gear.show_name = False

    gears_collection = bpy.data.collections.new('gears_collection')
    bpy.context.scene.collection.children.link(gears_collection)

    # bpy.context.collection.objects.link(ob)

    gears_collection.objects.link(object_gear)
    object_gear.select_set(True)


    mesh_gear.from_pydata(verts, edges, [])
    mesh_gear.update()
    bpy.context.view_layer.objects.active = object_gear
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.normals_make_consistent(inside=False)

    #bpy.ops.wm.tool_set_by_id(name="builtin.extrude_region")
    bpy.ops.mesh.extrude_context_move(MESH_OT_extrude_context={"use_normal_flip":False, "use_dissolve_ortho_edges":False, "mirror":False}, TRANSFORM_OT_translate={"value":(0, 0, 10), "orient_axis_ortho":'X', "orient_type":'GLOBAL', "orient_matrix":((1, 0, 0), (0, 1, 0), (0, 0, 1)), "orient_matrix_type":'GLOBAL', "constraint_axis":(True, True, True), "mirror":False, "use_proportional_edit":False, "proportional_edit_falloff":'SMOOTH', "proportional_size":1, "use_proportional_connected":False, "use_proportional_projected":False, "snap":False, "snap_elements":{'INCREMENT'}, "use_snap_project":False, "snap_target":'CLOSEST', "use_snap_self":True, "use_snap_edit":True, "use_snap_nonedit":True, "use_snap_selectable":False, "snap_point":(0, 0, 0), "snap_align":False, "snap_normal":(0, 0, 0), "gpencil_strokes":False, "cursor_transform":False, "texture_space":False, "remove_on_cancel":False, "view2d_edge_pan":False, "release_confirm":True, "use_accurate":False, "use_automerge_and_split":False})
    # bpy.ops.mesh.loopcut_slide(MESH_OT_loopcut={"number_cuts":10, "smoothness":0, "falloff":'INVERSE_SQUARE', "object_index":0, "edge_index":4692, "mesh_select_mode_init":(True, False, False)}, TRANSFORM_OT_edge_slide={"value":0, "single_side":False, "use_even":False, "flipped":False, "use_clamp":True, "mirror":True, "snap":False, "snap_elements":{'INCREMENT'}, "use_snap_project":False, "snap_target":'CLOSEST', "use_snap_self":True, "use_snap_edit":True, "use_snap_nonedit":True, "use_snap_selectable":False, "snap_point":(0, 0, 0), "correct_uv":True, "release_confirm":True, "use_accurate":False})
    # bpy.ops.view3d.snap_cursor_to_selected()
    bpy.ops.mesh.primitive_circle_add(vertices=1620, radius=3, enter_editmode=False, align='WORLD',location=(-2.15173e-06, -5.18045e-08, 10), scale=(1, 1, 1))
    bpy.ops.mesh.select_mode(type="VERT")
    bpy.ops.mesh.select_all(action='DESELECT')
    bpy.ops.object.mode_set(mode='OBJECT')

    obj = bpy.context.active_object
    for i in obj.data.vertices[1620:]:
        i.select=True
    # obj.data.vertices[0].select = True
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.bridge_edge_loops()

    bpy.ops.mesh.select_all(action='DESELECT')
    bpy.ops.object.mode_set(mode='OBJECT')
    for i in obj.data.vertices[3240:]:
        i.select = True
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.extrude_context_move(MESH_OT_extrude_context={"use_normal_flip":False, "use_dissolve_ortho_edges":False, "mirror":False}, TRANSFORM_OT_translate={"value":(-0, -0, -10), "orient_axis_ortho":'X', "orient_type":'GLOBAL', "orient_matrix":((1, 0, 0), (0, 1, 0), (0, 0, 1)), "orient_matrix_type":'GLOBAL', "constraint_axis":(True, True, True), "mirror":False, "use_proportional_edit":False, "proportional_edit_falloff":'SMOOTH', "proportional_size":1, "use_proportional_connected":False, "use_proportional_projected":False, "snap":False, "snap_elements":{'INCREMENT'}, "use_snap_project":False, "snap_target":'CLOSEST', "use_snap_self":True, "use_snap_edit":True, "use_snap_nonedit":True, "use_snap_selectable":False, "snap_point":(0, 0, 0), "snap_align":False, "snap_normal":(0, 0, 0), "gpencil_strokes":False, "cursor_transform":False, "texture_space":False, "remove_on_cancel":False, "view2d_edge_pan":False, "release_confirm":True, "use_accurate":False, "use_automerge_and_split":False})
    bpy.ops.object.mode_set(mode='OBJECT')
    for i in obj.data.vertices[:1620]:
        i.select=True
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.bridge_edge_loops()


    bpy.ops.export_scene.obj(filepath=r'C:\Users\Oleg\Dropbox\Gears\gears\myfile.obj')

    return object_gear


if __name__ == '__main__':

    a = 3
    b = 3
    alfa = 20
    m = 1
    n_teeth = 18
    shift = 0
    gear = Gear(a, b, alfa, m, n_teeth, shift)
    createMeshFromData("gear18",[0,0,0],np.c_[gear.gear,np.zeros(len(gear.gear))],gear.edges)

