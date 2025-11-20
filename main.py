import cv2
import mediapipe as mp
import pygame

# -----------------------------
# AUDIO SYSTEM
# -----------------------------
pygame.mixer.init()

# Load blue-node sounds
nodes = [
    {"x": 200, "y": 200, "radius": 40, "sound": pygame.mixer.Sound("note1.wav"), "touched": False},
    {"x": 400, "y": 300, "radius": 40, "sound": pygame.mixer.Sound("note2.wav"), "touched": False},
    {"x": 600, "y": 150, "radius": 40, "sound": pygame.mixer.Sound("note3.wav"), "touched": False}
]

# Green node sound
sound_main = pygame.mixer.Sound("note.wav")

# -----------------------------
# HAND TRACKING
# -----------------------------
mp_hands = mp.solutions.hands
hands = mp_hands.Hands()
mp_draw = mp.solutions.drawing_utils

cap = cv2.VideoCapture(0)

# -----------------------------
# NODE DRAGGING
# -----------------------------
node_x = 300
node_y = 300
node_radius = 40
touched_main = False

drag_index = None   # None, "main", or index of node


def mouse_event(event, x, y, flags, param):
    global drag_index, node_x, node_y

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
    result = hands.process(rgb)

    cx, cy = None, None

    # HAND + FINGERTIP TRACKING
    if result.multi_hand_landmarks:
        for handLms in result.multi_hand_landmarks:
            mp_draw.draw_landmarks(img, handLms, mp_hands.HAND_CONNECTIONS)

            tip = handLms.landmark[8]  # index finger
            h, w, c = img.shape
            cx = int(tip.x * w)
            cy = int(tip.y * h)

            cv2.circle(img, (cx, cy), 10, (0, 0, 255), -1)

    # -----------------------------
    # CHECK BLUE NODE COLLISION
    # -----------------------------
    if cx is not None:
        for node in nodes:
            dist = ((cx - node["x"])**2 + (cy - node["y"])**2)**0.5

            if dist < node["radius"]:
                if not node["touched"]:
                    node["sound"].play()
                    node["touched"] = True

                cv2.circle(img, (node["x"], node["y"]), node["radius"], (0,255,0), -1)
            else:
                node["touched"] = False
                cv2.circle(img, (node["x"], node["y"]), node["radius"], (255,0,0), -1)
    else:
        for node in nodes:
            cv2.circle(img, (node["x"], node["y"]), node["radius"], (255,0,0), -1)

    # -----------------------------
    # GREEN NODE DRAW
    # -----------------------------
    cv2.circle(img, (node_x, node_y), node_radius, (0,255,0), -1)

    # GREEN NODE SOUND COLLISION
    if cx is not None:
        dist_main = ((cx - node_x)**2 + (cy - node_y)**2)**0.5

        if dist_main < node_radius:
            if not touched_main:
                sound_main.play()
                touched_main = True
        else:
            touched_main = False

    cv2.imshow("Hand Tracking", img)

    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

cap.release()
cv2.destroyAllWindows()
