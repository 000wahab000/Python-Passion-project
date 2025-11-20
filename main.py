import cv2
import mediapipe as mp
import pygame
import math
import random

# -----------------------------
# AUDIO SYSTEM
# -----------------------------
pygame.mixer.init()

# Blue nodes
nodes = [
    {
        "x": 200,
        "y": 200,
        "radius": 40,
        "sound": pygame.mixer.Sound("note1.wav"),
        "touched": False,
        # visual effect state
        "pulse_r": 0.0,
        "glow_alpha": 0,
        "shockwave_r": 0.0,
        "particles": []
    },
    {
        "x": 400,
        "y": 300,
        "radius": 40,
        "sound": pygame.mixer.Sound("note2.wav"),
        "touched": False,
        "pulse_r": 0.0,
        "glow_alpha": 0,
        "shockwave_r": 0.0,
        "particles": []
    },
    {
        "x": 600,
        "y": 150,
        "radius": 40,
        "sound": pygame.mixer.Sound("note3.wav"),
        "touched": False,
        "pulse_r": 0.0,
        "glow_alpha": 0,
        "shockwave_r": 0.0,
        "particles": []
    }
]

# Green main node
node_x = 300
node_y = 450
node_radius = 60
touched_main = False
sound_main = pygame.mixer.Sound("note.wav")

# main node effect state
main_effect = {
    "pulse_r": 0.0,
    "glow_alpha": 0,
    "shockwave_r": 0.0,
}
main_particles = []

# -----------------------------
# HAND TRACKING SETUP
# -----------------------------
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(max_num_hands=2)
mp_draw = mp.solutions.drawing_utils

cap = cv2.VideoCapture(0)

# Store latest 21 landmark coords (last hand processed)
last_landmarks = []
selected_landmark = 8    # default = index fingertip

# -----------------------------
# EFFECT SELECTION DROPDOWN
# -----------------------------
effect_options = [
    ("none", "None"),
    ("pulse", "Pulse Ring"),
    ("glow", "Glow Bloom"),
    ("shockwave", "Shockwave"),
    ("particles", "Particle Burst")
]
current_effect = "none"
dropdown_open = False

# Dropdown UI geometry (top-left)
dd_x, dd_y = 10, 10
dd_width = 190
dd_header_h = 30
dd_item_h = 24

# -----------------------------
# NODE DRAGGING
# -----------------------------
drag_index = None  # index of dragged node OR "main"


def trigger_effect_node(node):
    """Set visual effect state for a blue node when triggered."""
    global current_effect

    if current_effect == "pulse":
        node["pulse_r"] = node["radius"]
    elif current_effect == "glow":
        node["glow_alpha"] = 255
    elif current_effect == "shockwave":
        node["shockwave_r"] = node["radius"]
    elif current_effect == "particles":
        node["particles"].clear()
        for i in range(10):
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(3, 6)
            vx = math.cos(angle) * speed
            vy = math.sin(angle) * speed
            node["particles"].append({
                "x": node["x"],
                "y": node["y"],
                "vx": vx,
                "vy": vy,
                "life": random.randint(15, 30)
            })


def trigger_effect_main():
    """Set visual effect state for the green main node when triggered."""
    global current_effect, main_effect, main_particles, node_x, node_y, node_radius

    if current_effect == "pulse":
        main_effect["pulse_r"] = node_radius
    elif current_effect == "glow":
        main_effect["glow_alpha"] = 255
    elif current_effect == "shockwave":
        main_effect["shockwave_r"] = node_radius
    elif current_effect == "particles":
        main_particles.clear()
        for i in range(14):
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(3, 7)
            vx = math.cos(angle) * speed
            vy = math.sin(angle) * speed
            main_particles.append({
                "x": node_x,
                "y": node_y,
                "vx": vx,
                "vy": vy,
                "life": random.randint(18, 35)
            })


def update_and_draw_node_effects(img, node):
    """Update visual effect state for a blue node and draw overlays."""
    # Pulse ring
    if node["pulse_r"] > 0:
        cv2.circle(img, (node["x"], node["y"]), int(node["pulse_r"]), (0, 255, 255), 2)
        node["pulse_r"] += 4
        if node["pulse_r"] > node["radius"] * 3:
            node["pulse_r"] = 0

    # Shockwave (larger, thinner ring)
    if node["shockwave_r"] > 0:
        cv2.circle(img, (node["x"], node["y"]), int(node["shockwave_r"]), (255, 255, 0), 1)
        node["shockwave_r"] += 6
        if node["shockwave_r"] > node["radius"] * 4:
            node["shockwave_r"] = 0

    # Glow bloom
    if node["glow_alpha"] > 0:
        # fake glow using brighter circle around node
        glow_color = (0, min(255, node["glow_alpha"]), 255)
        cv2.circle(img, (node["x"], node["y"]), node["radius"] + 12, glow_color, 2)
        node["glow_alpha"] = max(0, node["glow_alpha"] - 15)

    # Particle burst
    if node["particles"]:
        alive_particles = []
        for p in node["particles"]:
            p["x"] += p["vx"]
            p["y"] += p["vy"]
            p["life"] -= 1
            if p["life"] > 0:
                alive_particles.append(p)
                cv2.circle(img, (int(p["x"]), int(p["y"])), 3, (255, 255, 255), -1)
        node["particles"] = alive_particles


def update_and_draw_main_effects(img):
    """Update visual effects for the main green node."""
    global main_effect, main_particles, node_x, node_y, node_radius

    # Pulse ring
    if main_effect["pulse_r"] > 0:
        cv2.circle(img, (node_x, node_y), int(main_effect["pulse_r"]), (0, 255, 255), 2)
        main_effect["pulse_r"] += 4
        if main_effect["pulse_r"] > node_radius * 3:
            main_effect["pulse_r"] = 0

    # Shockwave
    if main_effect["shockwave_r"] > 0:
        cv2.circle(img, (node_x, node_y), int(main_effect["shockwave_r"]), (255, 255, 0), 1)
        main_effect["shockwave_r"] += 6
        if main_effect["shockwave_r"] > node_radius * 4:
            main_effect["shockwave_r"] = 0

    # Glow bloom
    if main_effect["glow_alpha"] > 0:
        glow_color = (0, min(255, main_effect["glow_alpha"]), 255)
        cv2.circle(img, (node_x, node_y), node_radius + 15, glow_color, 2)
        main_effect["glow_alpha"] = max(0, main_effect["glow_alpha"] - 15)

    # Particles
    if main_particles:
        alive_main = []
        for p in main_particles:
            p["x"] += p["vx"]
            p["y"] += p["vy"]
            p["life"] -= 1
            if p["life"] > 0:
                alive_main.append(p)
                cv2.circle(img, (int(p["x"]), int(p["y"])), 3, (255, 255, 255), -1)
        main_particles[:] = alive_main


def draw_dropdown(img):
    """Draw the effects dropdown UI."""
    global current_effect, dropdown_open

    # Find label for current effect
    label = "Effects"
    for key, text in effect_options:
        if key == current_effect:
            label = f"Effect: {text}"
            break

    # Header box
    cv2.rectangle(img, (dd_x, dd_y), (dd_x + dd_width, dd_y + dd_header_h), (40, 40, 40), -1)
    cv2.rectangle(img, (dd_x, dd_y), (dd_x + dd_width, dd_y + dd_header_h), (200, 200, 200), 1)
    cv2.putText(img, label, (dd_x + 8, dd_y + 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (230, 230, 230), 1)

    # Arrow
    arrow = "▼" if not dropdown_open else "▲"
    cv2.putText(img, arrow, (dd_x + dd_width - 20, dd_y + 20),
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (230, 230, 230), 1)

    # Options list
    if dropdown_open:
        for i, (_, text) in enumerate(effect_options):
            top = dd_y + dd_header_h + i * dd_item_h
            bottom = top + dd_item_h
            cv2.rectangle(img, (dd_x, top), (dd_x + dd_width, bottom), (30, 30, 30), -1)
            cv2.rectangle(img, (dd_x, top), (dd_x + dd_width, bottom), (160, 160, 160), 1)
            cv2.putText(img, text, (dd_x + 8, top + 17), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (230, 230, 230), 1)


def mouse_event(event, x, y, flags, param):
    global drag_index, node_x, node_y, selected_landmark, last_landmarks
    global dropdown_open, current_effect

    # ----------------- DROPDOWN INTERACTION -----------------
    if event == cv2.EVENT_LBUTTONDOWN:
        # Click on header to toggle open/close
        if dd_x <= x <= dd_x + dd_width and dd_y <= y <= dd_y + dd_header_h:
            dropdown_open = not dropdown_open
            return

        # If open, check each option
        if dropdown_open:
            for i, (key, text) in enumerate(effect_options):
                top = dd_y + dd_header_h + i * dd_item_h
                bottom = top + dd_item_h
                if dd_x <= x <= dd_x + dd_width and top <= y <= bottom:
                    current_effect = key
                    dropdown_open = False
                    print("Selected effect:", text)
                    return
            # Click outside options while open: close menu
            dropdown_open = False

    # ----------------- NODE DRAGGING / LANDMARK SELECT -----------------
    if event == cv2.EVENT_LBUTTONDOWN:
        # Check blue nodes first
        for i, node in enumerate(nodes):
            dist = ((x - node["x"])**2 + (y - node["y"])**2)**0.5
            if dist < node["radius"]:
                drag_index = i
                return

        # Check green node
        dist_main = ((x - node_x)**2 + (y - node_y)**2)**0.5
        if dist_main < node_radius:
            drag_index = "main"
            return

        # Landmark selection (click near any red dot)
        if last_landmarks:
            for idx, (lx, ly) in enumerate(last_landmarks):
                dist = ((x - lx)**2 + (y - ly)**2)**0.5
                if dist < 15:
                    selected_landmark = idx
                    print("Selected landmark:", idx)
                    return

    elif event == cv2.EVENT_MOUSEMOVE:
        if drag_index == "main":
            node_x = x
            node_y = y
        elif isinstance(drag_index, int):
            nodes[drag_index]["x"] = x
            nodes[drag_index]["y"] = y

    elif event == cv2.EVENT_LBUTTONUP:
        drag_index = None


cv2.namedWindow("Hand Tracking")
cv2.setMouseCallback("Hand Tracking", mouse_event)

# -----------------------------
# MAIN LOOP
# -----------------------------
while True:
    success, img = cap.read()
    if not success:
        break

    img = cv2.flip(img, 1)
    rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    results = hands.process(rgb)

    last_landmarks = []
    hand_points = []  # (sx, sy) of selected landmark per hand

    # ---------------------------------------------------------
    # MULTI-HAND LANDMARK EXTRACTION & ACTIVE POINTS
    # ---------------------------------------------------------
    if results.multi_hand_landmarks:
        for handLms in results.multi_hand_landmarks:
            h, w, c = img.shape

            temp_landmarks = []
            for id, lm in enumerate(handLms.landmark):
                lx, ly = int(lm.x * w), int(lm.y * h)
                temp_landmarks.append((lx, ly))
                cv2.circle(img, (lx, ly), 4, (0, 0, 255), -1)

            last_landmarks = temp_landmarks.copy()

            # Safe guard in case selected_landmark goes out of range
            if 0 <= selected_landmark < len(last_landmarks):
                sx, sy = last_landmarks[selected_landmark]
                hand_points.append((sx, sy))
                cv2.circle(img, (sx, sy), 10, (0, 255, 255), 2)

            mp_draw.draw_landmarks(img, handLms, mp_hands.HAND_CONNECTIONS)

    # ---------------------------------------------------------
    # BLUE NODE COLLISIONS + DRAW
    # ---------------------------------------------------------
    for node in nodes:
        node_hit = False

        for (hx, hy) in hand_points:
            dist = ((hx - node["x"])**2 + (hy - node["y"])**2)**0.5
            if dist < node["radius"]:
                node_hit = True
                if not node["touched"]:
                    node["sound"].play()
                    trigger_effect_node(node)
                    node["touched"] = True

        if not node_hit:
            node["touched"] = False

        base_color = (0, 255, 0) if node["touched"] else (255, 0, 0)
        cv2.circle(img, (node["x"], node["y"]), node["radius"], base_color, -1)
        update_and_draw_node_effects(img, node)

    # ---------------------------------------------------------
    # GREEN MAIN NODE COLLISION + DRAW
    # ---------------------------------------------------------
    main_hit = False

    for (hx, hy) in hand_points:
        dist_main = ((hx - node_x)**2 + (hy - node_y)**2)**0.5
        if dist_main < node_radius:
            main_hit = True
            break

    if main_hit and not touched_main:
        sound_main.play()
        trigger_effect_main()
        touched_main = True
    elif not main_hit:
        touched_main = False

    cv2.circle(img, (node_x, node_y), node_radius, (0, 255, 0), -1)
    update_and_draw_main_effects(img)

    # ---------------------------------------------------------
    # UI: DROPDOWN
    # ---------------------------------------------------------
    draw_dropdown(img)

    # ---------------------------------------------------------
    # DISPLAY
    # ---------------------------------------------------------
    cv2.imshow("Hand Tracking", img)
    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

cap.release()
cv2.destroyAllWindows()
