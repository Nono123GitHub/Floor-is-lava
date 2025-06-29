from ursina import *
from ursina.prefabs.first_person_controller import FirstPersonController
import random

# --- App & player -----------------------------------------------------------
app = Ursina(borderless=False)
player = FirstPersonController(collider='box', speed=6)
mouse.locked = True

# --- Environment -----------------------------------------------------------
ground = Entity(model='plane', scale=64, texture='grass', texture_scale=(64, 64), collider='box')
lava = Entity(model='plane', scale=64, texture='noise', color=color.red.tint(-0.1), y=-20, collider='box')
lava_speed = 1  # units per second – tweak for difficulty

# --- Goals -----------------------------------------------------------------
goal_count = 3
goals = []
for _ in range(goal_count):
    g = Entity(
        model='cube',
        color=color.green,
        scale=2,
        collider='box',
        position=(random.randint(-15, 15), random.randint(3, 15), random.randint(-15, 15))
    )
    goals.append(g)

# --- UI --------------------------------------------------------------------
goal_counter = Text(text=f'Goals left: {len(goals)}', origin=(-3, .45), scale=1.5, background=True)
timer_text   = Text(text='Time: 0.0', origin=(-.95, .4), background=True)

# --- Helpers ----------------------------------------------------------------

def flash(col=color.white, duration=.15):
    """Quick full‑screen flash helper."""
    overlay = Entity(parent=camera.ui, model='quad', color=col, scale=2, z=-1)
    destroy(overlay, delay=duration)

blocks = []  # user‑placed blocks

# --- Input -----------------------------------------------------------------

def input(key):
    # Placement – left mouse on ground or an existing block
    if key == 'left mouse down' and mouse.world_point is not None:
        if mouse.hovered_entity in (ground, *blocks):
            p = mouse.world_point
            # snap to 2×2×2 grid so blocks line up neatly
            p = Vec3(round(p.x / 2) * 2, round(p.y / 2) * 2 + 1, round(p.z / 2) * 2)
            # Prevent exact overlap with another block
            if not any((b.position - p).length() < .1 for b in blocks):
                b = Entity(model='cube', texture='brick', color=color.gray, scale=2,
                            position=p, collider='box')
                blocks.append(b)
    # Removal – right mouse on an existing block
    if key == 'right mouse down' and mouse.hovered_entity in blocks:
        b = mouse.hovered_entity
        blocks.remove(b)
        destroy(b)

# --- Game update -----------------------------------------------------------
elapsed = 0

def update():
    global elapsed
    # Timer
    elapsed += time.dt
    timer_text.text = f'Time: {elapsed:.1f}'

    # Lava rises smoothly with frame‑rate independence
    lava.y += lava_speed * time.dt

    # If player touches lava – lose condition
    if player.y < lava.y + 1:
        lose()

    # Check for goal pickup
    hit_info = player.intersects()
    if hit_info.hit and hit_info.entity in goals:
        goals.remove(hit_info.entity)
        destroy(hit_info.entity)
        flash(color.lime)
        goal_counter.text = f'Goals left: {len(goals)}'
        if not goals:
            win()

# --- Win / Lose ------------------------------------------------------------

def win():
    flash(color.azure, duration=.3)
    Text(text='YOU WIN!', scale=3, origin=(0, 0), background=True, color=color.cyan)
    application.pause()
    mouse.locked = False


def lose():
    flash(color.red, duration=.3)
    Text(text='YOU LOST!', scale=3, origin=(0, 0), background=True, color=color.white)
    application.pause()
    mouse.locked = False

# --- Extras ----------------------------------------------------------------
Sky()
app.run()
