"""Shared helpers for posing the Jack/Jill Rigify rigs in 'Body Mechanics Rigs.blend'.

Characters face -Y, stand at the origin, ~20 units tall. Side view = camera on +X.
"""
import math
import bpy
from mathutils import Euler, Quaternion, Vector

RIGS = {"male": ("Jack Controls", "Jack"), "female": ("Jill Controls", "Jill")}


def setup_scene(gender, transparent=True, res=(768, 1024), ortho_scale=24.0, cam_side=True):
    sc = bpy.context.scene
    # Jill's collections are excluded from the view layer in the source file.
    def walk(lc):
        if lc.name in ("Jack Model", "Jack Rig", "Jill Model", "Jill Rig"):
            lc.exclude = False
        for c in lc.children:
            walk(c)
    walk(bpy.context.view_layer.layer_collection)
    for g, (rig, mesh) in RIGS.items():
        show = g == gender
        for n in (rig, mesh):
            o = bpy.data.objects[n]
            o.hide_render = not show
            o.hide_viewport = not show
    for o in bpy.data.objects:
        if o.name.startswith(("WGT", "metarig")):
            o.hide_render = True
    bpy.data.objects["Background"].hide_render = True
    world = sc.world or bpy.data.worlds.new("World")
    sc.world = world
    world.use_nodes = True
    bg = world.node_tree.nodes.get("Background")
    if bg:
        bg.inputs[0].default_value = (0.55, 0.58, 0.62, 1)
        bg.inputs[1].default_value = 0.6
    sc.render.film_transparent = transparent
    sc.render.resolution_x, sc.render.resolution_y = res
    sc.render.resolution_percentage = 100
    sc.render.engine = "BLENDER_EEVEE" if "BLENDER_EEVEE" in [e.identifier for e in bpy.types.RenderSettings.bl_rna.properties["engine"].enum_items] else "BLENDER_EEVEE_NEXT"
    cam = bpy.data.objects["Camera"]
    cam.data.type = "ORTHO"
    cam.data.ortho_scale = ortho_scale
    if cam_side:
        cam.location = (60, 0, 10.5)
        cam.rotation_euler = (math.radians(90), 0, math.radians(90))
    else:  # 3/4 front view for trainer poses
        cam.location = (28, -52, 12)
        cam.rotation_euler = (math.radians(88), 0, math.radians(28))
    sc.camera = cam
    rig = bpy.data.objects[RIGS[gender][0]]
    # Legs in IK (feet stay planted), arms in FK (pose by rotation).
    for s in ("L", "R"):
        rig.pose.bones[f"thigh_parent.{s}"]["IK_FK"] = 0.0
        rig.pose.bones[f"upper_arm_parent.{s}"]["IK_FK"] = 1.0
    return rig


def reset_pose(rig):
    for pb in rig.pose.bones:
        pb.location = (0, 0, 0)
        pb.rotation_quaternion = (1, 0, 0, 0)
        pb.rotation_euler = (0, 0, 0)
        pb.scale = (1, 1, 1)


def rot(pb, x=0.0, y=0.0, z=0.0):
    """Rotate bone in its local space by Euler degrees."""
    e = Euler((math.radians(x), math.radians(y), math.radians(z)), "XYZ")
    if pb.rotation_mode == "QUATERNION":
        pb.rotation_quaternion = e.to_quaternion()
    else:
        pb.rotation_euler = e


def move_world(rig, pb, delta):
    """Translate a (root-parented) bone by a world-space delta."""
    m = (rig.matrix_world @ pb.bone.matrix_local).to_3x3().normalized()
    pb.location = m.inverted() @ Vector(delta)


def key(pb, frame):
    pb.keyframe_insert("location", frame=frame)
    pb.keyframe_insert("rotation_quaternion" if pb.rotation_mode == "QUATERNION" else "rotation_euler", frame=frame)
