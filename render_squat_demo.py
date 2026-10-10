"""Renders a placeholder side-view squat video (public/demo/squat-demo.mp4) from the Jack rig.

10 reps: clean ×5, shallow, torso lean, too fast, clean ×2. Replace with a real recording for the demo.
Usage: Blender -b --disable-autoexec "Body Mechanics Rigs.blend" --python scripts/blender/render_squat_demo.py -- <out.mp4> [male|female]
"""
import os, sys
import bpy

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import key, move_world, reset_pose, rot, setup_scene  # noqa: E402

args = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
out = os.path.abspath(args[0] if args else "public/demo/squat-demo.mp4")
gender = args[1] if len(args) > 1 else "male"
FPS = 24

# (down, back, lean, descent_frames, ascent_frames)
CLEAN = (3.6, 1.2, 20, 30, 22)
REPS = [CLEAN] * 5 + [(1.6, 0.5, 8, 26, 20), (3.6, 1.6, 62, 30, 24), (3.6, 1.2, 20, 7, 20)] + [CLEAN] * 2
HOLD = 14

rig = setup_scene(gender, transparent=False, res=(720, 1280), ortho_scale=28)
sc = bpy.context.scene
cam = sc.camera
cam.location = (60, -1.0, 10.0)
sc.render.fps = FPS
reset_pose(rig)
torso = rig.pose.bones["torso"]


def pose(frame, down, back, lean):
    reset_pose(rig)
    move_world(rig, torso, (0, back, -down))
    rot(torso, x=lean)
    key(torso, frame)


f = 1
pose(f, 0, 0, 0)
for down, back, lean, d, a in REPS:
    f += HOLD
    pose(f, 0, 0, 0)
    f += d
    pose(f, down, back, lean)
    f += a
    pose(f, 0, 0, 0)
f += HOLD * 2
pose(f, 0, 0, 0)

sc.frame_start, sc.frame_end = 1, f
sc.render.image_settings.media_type = "VIDEO" if hasattr(sc.render.image_settings, "media_type") else sc.render.image_settings.file_format
if hasattr(sc.render.image_settings, "media_type"):
    sc.render.image_settings.media_type = "VIDEO"
sc.render.image_settings.file_format = "FFMPEG"
sc.render.ffmpeg.format = "MPEG4"
sc.render.ffmpeg.codec = "H264"
sc.render.ffmpeg.constant_rate_factor = "MEDIUM"
sc.render.ffmpeg.audio_codec = "NONE"
sc.render.filepath = out
os.makedirs(os.path.dirname(out), exist_ok=True)
print(f"=== rendering {f} frames → {out}")
bpy.ops.render.render(animation=True)
