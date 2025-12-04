import cv2
import mediapipe as mp

mp_hands = mp.solutions.hands
hands = mp_hands.Hands(max_num_hands=2)
mp_draw = mp.solutions.drawing_utils

# stores latest list of all 21 landmarks
last_landmarks = []
selected_landmark = 8   # default = index fingertip


def process_hands(img):
    """
    Processes the frame with MediaPipe, updates last_landmarks,
    and returns a list of (x,y) points that correspond to whichever
    landmark is currently selected.
    """
    global last_landmarks, selected_landmark, hands

    rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    results = hands.process(rgb)

    last_landmarks = []  
    selected_points = []

    if results.multi_hand_landmarks:
        h, w, c = img.shape

        for handLms in results.multi_hand_landmarks:
            temp = []

            for lm in handLms.landmark:
                lx, ly = int(lm.x * w), int(lm.y * h)
                temp.append((lx, ly))
                cv2.circle(img, (lx, ly), 4, (0, 0, 255), -1)

            last_landmarks = temp.copy()

            if 0 <= selected_landmark < len(last_landmarks):
                sx, sy = last_landmarks[selected_landmark]
                selected_points.append((sx, sy))
                cv2.circle(img, (sx, sy), 10, (0, 255, 255), 2)

            mp_draw.draw_landmarks(img, handLms, mp_hands.HAND_CONNECTIONS)

    return selected_points


def select_landmark(x, y):
    """Called when user clicks near any red landmark."""
    global last_landmarks, selected_landmark

    for idx, (lx, ly) in enumerate(last_landmarks):
        dist = ((x - lx)**2 + (y - ly)**2)**0.5
        if dist < 15:
            selected_landmark = idx
            print("Selected landmark:", idx)
            return True

    return False
