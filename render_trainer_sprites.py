"""Renders looping trainer animations as horizontal sprite sheets:
public/trainers/{male,female}/{pose}.sprite.webp  (FRAMES × 300×400, transparent).

Each pose = base angles from render_trainers.POSES + sine-driven offsets per frame.
Usage: Blender -b --disable-autoexec "Body Mechanics Rigs.blend" --python scripts/blender/render_trainer_sprites.py -- <public/trainers>
"""
import math, os, sys, tempfile
import bpy
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import move_world, reset_pose, rot, setup_scene  # noqa: E402

args = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
out_dir = os.path.abspath(args[0] if args else "public/trainers")
FRAMES, W, H = 12, 300, 400

# Base pose angles (x, y, z) per bone — same vocabulary as render_trainers.py.
BASE = {
    "idle": {"upper_arm_fk.L": (8, 0, -72), "upper_arm_fk.R": (8, 0, 72), "forearm_fk.L": (18, 0, 0), "forearm_fk.R": (18, 0, 0)},
    "hello": {"upper_arm_fk.L": (8, 0, -72), "forearm_fk.L": (15, 0, 0), "upper_arm_fk.R": (10, 0, -45), "forearm_fk.R": (0, 0, -75), "head": (0, 0, -8)},
    "good": {"upper_arm_fk.L": (10, 0, 55), "upper_arm_fk.R": (10, 0, -55), "forearm_fk.L": (0, 0, 20), "forearm_fk.R": (0, 0, -20), "chest": (-6, 0, 0), "head": (-10, 0, 0)},
    "error": {"upper_arm_fk.L": (20, 0, -58), "upper_arm_fk.R": (20, 0, 58), "forearm_fk.L": (25, 0, 85), "forearm_fk.R": (25, 0, -85), "head": (12, 0, 14)},
    "again": {"upper_arm_fk.L": (25, 0, -15), "forearm_fk.L": (10, 0, 100), "upper_arm_fk.R": (8, 0, 72), "forearm_fk.R": (18, 0, 0), "head": (-4, 0, -6)},
}


def anim(pose, ph):
    """Offsets for phase ph in [0, 1). Returns (bone deltas, torso offset, root offset). Root moves the whole rig (jumps)."""
    s, c = math.sin(2 * math.pi * ph), math.cos(2 * math.pi * ph)
    s2 = math.sin(4 * math.pi * ph)
    if pose == "idle":  # weight shift, breathing, small head look-around
        return {"chest": (s * 2, 0, c * 3), "head": (0, 0, s * 6), "upper_arm_fk.L": (s * 4, 0, 0), "upper_arm_fk.R": (-s * 4, 0, 0)}, (0, 0, -0.15 * (1 - abs(c))), (0, 0, 0)
    if pose == "hello":  # big wave
        return {"forearm_fk.R": (0, 0, s * 38), "upper_arm_fk.R": (0, 0, s * 8), "head": (0, 0, s * 6), "chest": (0, 0, -s * 4)}, (0, 0, 0), (0, 0, 0)
    if pose == "good":  # jumping celebration, arms pumping
        hop = max(0.0, s)
        crouch = max(0.0, -s)  # dip before take-off
        return {"upper_arm_fk.L": (0, 0, s * 12), "upper_arm_fk.R": (0, 0, -s * 12), "forearm_fk.L": (0, 0, s * 20), "forearm_fk.R": (0, 0, -s * 20), "head": (-s * 6, 0, 0)}, (0, 0, -crouch * 1.2), (0, 0, hop * 1.6)
    if pose == "error":  # repeated shrug + disappointed head shake
        sh = abs(s)
        return {"upper_arm_fk.L": (0, 0, sh * 12), "upper_arm_fk.R": (0, 0, -sh * 12), "forearm_fk.L": (0, 0, -sh * 10), "forearm_fk.R": (0, 0, sh * 10), "head": (0, 0, s2 * 16)}, (0, 0, -sh * 0.3), (0, 0, 0)
    if pose == "again":  # fist pump "come on!"
        return {"upper_arm_fk.L": (s * 14, 0, s * 12), "forearm_fk.L": (0, 0, s * 20), "chest": (s * 5, 0, 0), "head": (s * 6, 0, 0)}, (0, 0, -max(0.0, -s) * 0.6), (0, 0, max(0.0, s) * 0.5)
    return {}, (0, 0, 0), (0, 0, 0)


tmp = tempfile.mkdtemp()
for gender in ("male", "female"):
    rig = setup_scene(gender, transparent=True, res=(W, H), ortho_scale=28.5, cam_side=False)
    sc = bpy.context.scene
    sc.camera.location.z = 12.4
    sc.render.image_settings.file_format = "PNG"
    sc.render.image_settings.color_mode = "RGBA"
    for pose, base in BASE.items():
        sheet = np.zeros((H, W * FRAMES, 4), dtype=np.float32)
        for f in range(FRAMES):
            reset_pose(rig)
            deltas, torso_off, root_off = anim(pose, f / FRAMES)
            bones = set(base) | set(deltas)
            for b in bones:
                bx, by, bz = base.get(b, (0, 0, 0))
                dx, dy, dz = deltas.get(b, (0, 0, 0))
                rot(rig.pose.bones[b], x=bx + dx, y=by + dy, z=bz + dz)
            move_world(rig, rig.pose.bones["torso"], torso_off)
            move_world(rig, rig.pose.bones["root"], root_off)
            bpy.context.view_layer.update()
            fp = os.path.join(tmp, f"{gender}_{pose}_{f}.png")
            sc.render.filepath = fp
            bpy.ops.render.render(write_still=True)
            im = bpy.data.images.load(fp)
            sheet[:, f * W:(f + 1) * W, :] = np.array(im.pixels[:], dtype=np.float32).reshape(H, W, 4)
            bpy.data.images.remove(im)
        out = bpy.data.images.new(f"{gender}_{pose}", W * FRAMES, H, alpha=True)
        out.pixels[:] = sheet.ravel()
        path = os.path.join(out_dir, gender, f"{pose}.sprite.webp")
        out.filepath_raw = path
        out.file_format = "WEBP"
        sc.render.image_settings.quality = 85
        out.save()
        print("=== saved", path)
