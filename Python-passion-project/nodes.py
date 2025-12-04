import pygame
import cv2
from effects import trigger_node_effect, update_node_effects

pygame.mixer.init()

nodes = [
    {"x":200, "y":200, "radius":40, "sound":pygame.mixer.Sound("note1.wav"),
     "touched":False, "pulse_r":0, "glow_alpha":0, "shockwave_r":0, "particles":[]},

    {"x":400, "y":300, "radius":40, "sound":pygame.mixer.Sound("note2.wav"),
     "touched":False, "pulse_r":0, "glow_alpha":0, "shockwave_r":0, "particles":[]},

    {"x":600, "y":150, "radius":40, "sound":pygame.mixer.Sound("note3.wav"),
     "touched":False, "pulse_r":0, "glow_alpha":0, "shockwave_r":0, "particles":[]}
]

# green node
node_x = 300
node_y = 450
node_radius = 60
sound_main = pygame.mixer.Sound("note.wav")
touched_main = False

# green node effects
main_effect = {"pulse_r":0, "glow_alpha":0, "shockwave_r":0}
main_particles = []


def handle_blue_collisions(img, hand_points, effect_mode):
    """
    Checks collision with blue nodes.
    Also triggers their visual effect + sound.
    """
    for node in nodes:
        hit = False

        for (hx, hy) in hand_points:
            if ((hx - node["x"])**2 + (hy - node["y"])**2)**0.5 < node["radius"]:
                hit = True
                if not node["touched"]:
                    node["sound"].play()
                    trigger_node_effect(node, effect_mode)
                    node["touched"] = True

        if not hit:
            node["touched"] = False

        col = (0,255,0) if node["touched"] else (255,0,0)
        cv2.circle(img, (node["x"], node["y"]), node["radius"], col, -1)

        update_node_effects(img, node)


def handle_green_collision(img, hand_points, effect_mode):
    """
    Checks collision with the main green node + draws it.
    """
    global node_x, node_y, node_radius
    global touched_main, main_effect, main_particles

    hit = False
    for (hx, hy) in hand_points:
        if ((hx - node_x)**2 + (hy - node_y)**2)**0.5 < node_radius:
            hit = True
            break

    if hit and not touched_main:
        sound_main.play()
        from effects import trigger_node_effect as _dummy  # ignore
        # trigger main effect
        if effect_mode == "pulse":
            main_effect["pulse_r"] = node_radius
        elif effect_mode == "glow":
            main_effect["glow_alpha"] = 255
        elif effect_mode == "shockwave":
            main_effect["shockwave_r"] = node_radius

        touched_main = True

    elif not hit:
        touched_main = False

    cv2.circle(img, (node_x, node_y), node_radius, (0,255,0), -1)

    # update green effects
    pr = main_effect["pulse_r"]
    if pr > 0:
        cv2.circle(img, (node_x,node_y), pr, (0,255,255), 2)
        main_effect["pulse_r"] += 4
        if main_effect["pulse_r"] > node_radius*3:
            main_effect["pulse_r"] = 0

    sr = main_effect["shockwave_r"]
    if sr > 0:
        cv2.circle(img, (node_x,node_y), sr, (255,255,0), 1)
        main_effect["shockwave_r"] += 6
        if main_effect["shockwave_r"] > node_radius*4:
            main_effect["shockwave_r"] = 0

    ga = main_effect["glow_alpha"]
    if ga > 0:
        cv2.circle(img, (node_x,node_y), node_radius+15, (0,ga,255), 2)
        main_effect["glow_alpha"] = max(0, ga - 15)
