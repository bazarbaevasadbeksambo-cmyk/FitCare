"""Renders trainer pose PNGs (transparent) into public/trainers/{male,female}/{pose}.png.

Usage: Blender -b --disable-autoexec "Body Mechanics Rigs.blend" --python scripts/blender/render_trainers.py -- <public/trainers>
Bone axes (FK arms): L arm z- lowers / z+ raises, x+ forward; R arm mirrored on z. Forearm L z+ bends up.
"""
import os, sys
import bpy

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import move_world, reset_pose, rot, setup_scene  # noqa: E402

args = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
out_dir = os.path.abspath(args[0] if args else "public/trainers")

# pose → {bone: (x, y, z) degrees}
POSES = {
    "idle": {
        "upper_arm_fk.L": (8, 0, -72), "upper_arm_fk.R": (8, 0, 72),
        "forearm_fk.L": (18, 0, 0), "forearm_fk.R": (18, 0, 0),
    },
    "hello": {
        "upper_arm_fk.L": (8, 0, -72), "forearm_fk.L": (15, 0, 0),
        "upper_arm_fk.R": (10, 0, -45), "forearm_fk.R": (0, 0, -75),
        "head": (0, 0, -8),
    },
    "good": {
        "upper_arm_fk.L": (10, 0, 55), "upper_arm_fk.R": (10, 0, -55),
        "forearm_fk.L": (0, 0, 20), "forearm_fk.R": (0, 0, -20),
        "chest": (-6, 0, 0), "head": (-10, 0, 0),
    },
    "error": {  # shrug
        "upper_arm_fk.L": (20, 0, -58), "upper_arm_fk.R": (20, 0, 58),
        "forearm_fk.L": (25, 0, 85), "forearm_fk.R": (25, 0, -85),
        "head": (12, 0, 14),
    },
    "again": {  # "come on, one more": fist up, other hand on the hip side
        "upper_arm_fk.L": (25, 0, -15), "forearm_fk.L": (10, 0, 100),
        "upper_arm_fk.R": (8, 0, 72), "forearm_fk.R": (18, 0, 0),
        "head": (-4, 0, -6),
    },
}

for gender in ("male", "female"):
    rig = setup_scene(gender, transparent=True, res=(600, 800), ortho_scale=26.5, cam_side=False)
    sc = bpy.context.scene
    sc.camera.location.z = 11.6
    for pose, bones in POSES.items():
        reset_pose(rig)
        for b, (x, y, z) in bones.items():
            rot(rig.pose.bones[b], x=x, y=y, z=z)
        if pose == "good":
            move_world(rig, rig.pose.bones["torso"], (0, 0, 0.3))
        bpy.context.view_layer.update()
        path = os.path.join(out_dir, gender, f"{pose}.png")
        os.makedirs(os.path.dirname(path), exist_ok=True)
        sc.render.image_settings.file_format = "PNG"
        sc.render.image_settings.color_mode = "RGBA"
        sc.render.filepath = path
        bpy.ops.render.render(write_still=True)
        print("=== saved", path)
