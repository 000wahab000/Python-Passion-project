import cv2
import random
import math

def trigger_node_effect(node, effect):
    """Initializes the visual effect state for a blue node."""
    if effect == "pulse":
        node["pulse_r"] = node["radius"]

    elif effect == "glow":
        node["glow_alpha"] = 255

    elif effect == "shockwave":
        node["shockwave_r"] = node["radius"]

    elif effect == "particles":
        node["particles"].clear()
        for i in range(10):
            ang = random.uniform(0, 2*math.pi)
            sp = random.uniform(3, 6)
            node["particles"].append({
                "x": node["x"],
                "y": node["y"],
                "vx": math.cos(ang)*sp,
                "vy": math.sin(ang)*sp,
                "life": random.randint(15, 30)
            })


def update_node_effects(img, node):
    """Updates and draws the visual effect for a blue node."""
    # PULSE
    if node["pulse_r"] > 0:
        cv2.circle(img, (node["x"], node["y"]), int(node["pulse_r"]), (0,255,255), 2)
        node["pulse_r"] += 4
        if node["pulse_r"] > node["radius"]*3:
            node["pulse_r"] = 0

    # SHOCKWAVE
    if node["shockwave_r"] > 0:
        cv2.circle(img, (node["x"], node["y"]), int(node["shockwave_r"]), (255,255,0), 1)
        node["shockwave_r"] += 6
        if node["shockwave_r"] > node["radius"]*4:
            node["shockwave_r"] = 0

    # GLOW BLOOM
    if node["glow_alpha"] > 0:
        col = (0, node["glow_alpha"], 255)
        cv2.circle(img, (node["x"], node["y"]), node["radius"]+12, col, 2)
        node["glow_alpha"] = max(0, node["glow_alpha"] - 15)

    # PARTICLES
    alive = []
    for p in node["particles"]:
        p["x"] += p["vx"]
        p["y"] += p["vy"]
        p["life"] -= 1
        if p["life"] > 0:
            alive.append(p)
            cv2.circle(img, (int(p["x"]), int(p["y"])), 3, (255,255,255), -1)
    node["particles"] = alive
