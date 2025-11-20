import cv2
from hand_tracking import process_hands, select_landmark
from nodes import nodes, node_x, node_y, node_radius
from nodes import handle_blue_collisions, handle_green_collision
from ui import draw_dropdown, ui_click, current_effect

# mouse dragging
drag_index = None

def mouse_event(event, x, y, flags, param):
    global drag_index, node_x, node_y

    # dropdown UI
    if event == cv2.EVENT_LBUTTONDOWN:
        if ui_click(x, y):
            return

    # node dragging
    if event == cv2.EVENT_LBUTTONDOWN:

        # check blue nodes
        for i, node in enumerate(nodes):
            if ((x-node["x"])**2 + (y-node["y"])**2)**0.5 < node["radius"]:
                drag_index = i
                return

        # check green
        if ((x-node_x)**2 + (y-node_y)**2)**0.5 < node_radius:
            drag_index = "main"
            return

        select_landmark(x, y)

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

cap = cv2.VideoCapture(0)

while True:
    success, img = cap.read()
    if not success:
        break

    img = cv2.flip(img, 1)

    # get selected fingertip for each hand
    hand_points = process_hands(img)

    # collisions + effects
    handle_blue_collisions(img, hand_points, current_effect)
    handle_green_collision(img, hand_points, current_effect)

    # UI
    draw_dropdown(img)

    cv2.imshow("Hand Tracking", img)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
