# ar_instrument_with_floating_panel.py
# Run: ensure note1.wav, note2.wav, note3.wav, note.wav are in same folder

import cv2
import mediapipe as mp
import pygame
import math
import random
import time
import numpy as np

# -----------------------------
# Config
# -----------------------------
PLANE_W, PLANE_H = 600, 400
GRID_SPACING = 50
GRID_ALPHA = 0.18

# -----------------------------
# Audio init
# -----------------------------
pygame.mixer.init()

# Virtual-plane nodes (centered)
nodes = [
    {"x": PLANE_W/4.0, "y": PLANE_H/3.0, "radius": 36,
     "sound": pygame.mixer.Sound("note1.wav"),
     "touched": False, "pulse_r": 0.0, "glow_alpha": 0, "shockwave_r": 0.0, "particles": []},
    {"x": PLANE_W/2.0, "y": PLANE_H/2.0, "radius": 36,
     "sound": pygame.mixer.Sound("note2.wav"),
     "touched": False, "pulse_r": 0.0, "glow_alpha": 0, "shockwave_r": 0.0, "particles": []},
    {"x": 3*PLANE_W/4.0, "y": PLANE_H/6.0, "radius": 36,
     "sound": pygame.mixer.Sound("note3.wav"),
     "touched": False, "pulse_r": 0.0, "glow_alpha": 0, "shockwave_r": 0.0, "particles": []},
]

main_node = {"x": PLANE_W/2.0, "y": 3*PLANE_H/4.0, "radius": 50}
sound_main = pygame.mixer.Sound("note.wav")
touched_main = False
main_effect = {"pulse_r":0.0, "glow_alpha":0, "shockwave_r":0.0}
main_particles = []

# -----------------------------
# Mediapipe
# -----------------------------
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(max_num_hands=1)
mp_draw = mp.solutions.drawing_utils

cap = cv2.VideoCapture(0)
if not cap.isOpened():
    raise RuntimeError("Cannot open camera")

last_landmarks = []
selected_landmark = 8  # index fingertip

# -----------------------------
# Plane / tracking
# -----------------------------
plane_mode = False
plane_points = []       # list of 4 (x,y) image-space corners
H_plane = None
inv_H_plane = None

tracking_features = np.empty((0,1,2), dtype=np.float32)
feature_ids_per_corner = []
prev_gray_for_flow = None
lk_params = dict(winSize=(21,21), maxLevel=3,
                 criteria=(cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, 30, 0.01))
max_features_per_corner = 40

# Calibration modes
finger_calib_mode = False
mouse_calib_mode = False
calib_next_idx = 0
mouse_preview_point = None     # preview point (x,y) before confirming with SPACE
finger_hold_start = None
finger_last_pos = None
finger_hold_thresh = 0.45
finger_stable_radius = 20

# -----------------------------
# Velocity & interaction
# -----------------------------
prev_point = None
prev_time = None
finger_velocity = 0.0

# -----------------------------
# Dropdown UI (effects)
# -----------------------------
effect_options = [("none","None"),("pulse","Pulse Ring"),("glow","Glow Bloom"),
                  ("shockwave","Shockwave"),("particles","Particle Burst")]
current_effect = "none"
dropdown_open = False
dd_x, dd_y = 10, 10
dd_width = 190
dd_header_h = 30
dd_item_h = 24

# -----------------------------
# Floating Start Panel (black theme)
# -----------------------------
panel_x, panel_y = 20, 20
panel_w, panel_h = 260, 160
panel_collapsed = True     # collapsed by default (tiny bar)
panel_dragging = False
panel_drag_offset = (0,0)
panel_bar_h = 26

# Buttons inside panel (relative coords)
def panel_button_rect(rel_x, rel_y, rel_w, rel_h):
    return (int(panel_x + rel_x), int(panel_y + rel_y),
            int(rel_w), int(rel_h))

# Mouse drag index for nodes
drag_index = None  # int for node, "main" or None

# helper clamp
def clamp(v,a,b): return max(a, min(b, v))

# -----------------------------
# Helper functions
# -----------------------------
def project_virtual_to_image(vpt, img_w, img_h):
    """If plane is active, use homography; else scale to frame size."""
    global plane_mode, H_plane
    if plane_mode and H_plane is not None:
        src = np.array([[[vpt[0], vpt[1]]]], dtype=np.float32)
        dst = cv2.perspectiveTransform(src, H_plane)
        return (float(dst[0,0,0]), float(dst[0,0,1]))
    else:
        sx = img_w / PLANE_W
        sy = img_h / PLANE_H
        return (int(vpt[0] * sx), int(vpt[1] * sy))

def apply_homography_virtual_to_image(vpt):
    if H_plane is None: return None
    src = np.array([[[vpt[0], vpt[1]]]], dtype=np.float32)
    dst = cv2.perspectiveTransform(src, H_plane)
    return (float(dst[0,0,0]), float(dst[0,0,1]))

def apply_homography_image_to_virtual(pt):
    if inv_H_plane is None: return None
    src = np.array([[[pt[0], pt[1]]]], dtype=np.float32)
    vp = cv2.perspectiveTransform(src, inv_H_plane)
    return (float(vp[0,0,0]), float(vp[0,0,1]))

# Effects
def trigger_effect_node(node, boost=1.0):
    global current_effect
    if current_effect == "pulse":
        node["pulse_r"] = int(node["radius"] * boost)
    elif current_effect == "glow":
        node["glow_alpha"] = int(min(255, 255 * boost))
    elif current_effect == "shockwave":
        node["shockwave_r"] = int(node["radius"] * boost)
    elif current_effect == "particles":
        node["particles"].clear()
        nump = int(max(6, 10 * boost))
        for _ in range(nump):
            angle = random.uniform(0, 2*math.pi)
            speed = random.uniform(3,6)*boost
            node["particles"].append({
                "x": node["x"], "y": node["y"],
                "vx": math.cos(angle)*speed, "vy": math.sin(angle)*speed,
                "life": random.randint(12,30)
            })

def trigger_effect_main(boost=1.0):
    global current_effect, main_effect, main_particles
    if current_effect == "pulse":
        main_effect["pulse_r"] = int(main_node["radius"] * boost)
    elif current_effect == "glow":
        main_effect["glow_alpha"] = int(min(255, 255 * boost))
    elif current_effect == "shockwave":
        main_effect["shockwave_r"] = int(main_node["radius"] * boost)
    elif current_effect == "particles":
        main_particles.clear()
        for _ in range(int(max(8, 14*boost))):
            angle = random.uniform(0, 2*math.pi)
            speed = random.uniform(3,7)*boost
            main_particles.append({
                "x": main_node["x"], "y": main_node["y"],
                "vx": math.cos(angle)*speed, "vy": math.sin(angle)*speed,
                "life": random.randint(14,40)
            })

def update_and_draw_node_effects(img, px, py, node):
    # px,py are image coords for the node's center
    if node["pulse_r"] > 0:
        cv2.circle(img, (int(px), int(py)), int(node["pulse_r"]), (0,255,255), 2)
        node["pulse_r"] += 4
        if node["pulse_r"] > node["radius"] * 3:
            node["pulse_r"] = 0
    if node["shockwave_r"] > 0:
        cv2.circle(img, (int(px), int(py)), int(node["shockwave_r"]), (255,255,0), 1)
        node["shockwave_r"] += 6
        if node["shockwave_r"] > node["radius"] * 4:
            node["shockwave_r"] = 0
    if node["glow_alpha"] > 0:
        glow_color = (0, min(255, node["glow_alpha"]), 255)
        cv2.circle(img, (int(px), int(py)), node["radius"] + 12, glow_color, 2)
        node["glow_alpha"] = max(0, node["glow_alpha"] - 15)
    if node["particles"]:
        alive = []
        for p in node["particles"]:
            p["x"] += p["vx"]; p["y"] += p["vy"]; p["life"] -= 1
            if p["life"] > 0:
                alive.append(p)
                proj = project_virtual_to_image((p["x"], p["y"]), img.shape[1], img.shape[0])
                if proj is not None:
                    cv2.circle(img, (int(proj[0]), int(proj[1])), 3, (255,255,255), -1)
        node["particles"] = alive

def update_and_draw_main_effects(img):
    proj = project_virtual_to_image((main_node["x"], main_node["y"]), img.shape[1], img.shape[0])
    if proj is None: return
    px, py = int(proj[0]), int(proj[1])
    if main_effect["pulse_r"] > 0:
        cv2.circle(img, (px,py), int(main_effect["pulse_r"]), (0,255,255), 2)
        main_effect["pulse_r"] += 4
        if main_effect["pulse_r"] > main_node["radius"] * 3:
            main_effect["pulse_r"] = 0
    if main_effect["shockwave_r"] > 0:
        cv2.circle(img, (px,py), int(main_effect["shockwave_r"]), (255,255,0), 1)
        main_effect["shockwave_r"] += 6
        if main_effect["shockwave_r"] > main_node["radius"] * 4:
            main_effect["shockwave_r"] = 0
    if main_effect["glow_alpha"] > 0:
        glow_color = (0, min(255, main_effect["glow_alpha"]), 255)
        cv2.circle(img, (px,py), main_node["radius"] + 15, glow_color, 2)
        main_effect["glow_alpha"] = max(0, main_effect["glow_alpha"] - 15)
    if main_particles:
        alive = []
        for p in main_particles:
            p["x"] += p["vx"]; p["y"] += p["vy"]; p["life"] -= 1
            if p["life"] > 0:
                alive.append(p)
                projp = project_virtual_to_image((p["x"], p["y"]), img.shape[1], img.shape[0])
                if projp is not None:
                    cv2.circle(img, (int(projp[0]), int(projp[1])), 3, (255,255,255), -1)
        main_particles[:] = alive

# -----------------------------
# Plane calibration & optical flow
# -----------------------------
def reset_plane():
    global plane_mode, plane_points, H_plane, inv_H_plane, tracking_features, feature_ids_per_corner, prev_gray_for_flow
    plane_mode = False
    plane_points = []
    H_plane = None
    inv_H_plane = None
    tracking_features = np.empty((0,1,2), dtype=np.float32)
    feature_ids_per_corner[:] = []
    prev_gray_for_flow = None
    print("[plane] reset")

def finalize_calibration_and_prepare_tracking(frame_gray):
    global H_plane, inv_H_plane, plane_mode, tracking_features, feature_ids_per_corner, prev_gray_for_flow
    if len(plane_points) != 4:
        print("[plane] need 4 corners")
        return
    src = np.float32([[0,0],[PLANE_W,0],[PLANE_W,PLANE_H],[0,PLANE_H]])
    dst = np.float32(plane_points)
    H_plane = cv2.getPerspectiveTransform(src, dst)
    inv_H_plane = cv2.getPerspectiveTransform(dst, src)
    plane_mode = True
    # build initial features
    pts = []; ids = []
    for i, (cx,cy) in enumerate(plane_points):
        x0, y0 = max(0,int(cx-30)), max(0,int(cy-30))
        x1, y1 = min(frame_gray.shape[1],int(cx+30)), min(frame_gray.shape[0],int(cy+30))
        if x1<=x0 or y1<=y0:
            found = None
        else:
            roi = frame_gray[y0:y1, x0:x1]
            found = cv2.goodFeaturesToTrack(roi, maxCorners=max_features_per_corner, qualityLevel=0.01, minDistance=6)
        if found is not None:
            for pt in found:
                gx = int(pt[0][0] + x0); gy = int(pt[0][1] + y0)
                pts.append((gx,gy)); ids.append(i)
        if len([x for x in ids if x==i]) < 4:
            pts.append((int(cx),int(cy))); ids.append(i)
    if pts:
        tracking_features = np.float32(pts).reshape(-1,1,2)
        feature_ids_per_corner[:] = ids
    else:
        tracking_features = np.empty((0,1,2), dtype=np.float32)
        feature_ids_per_corner[:] = []
    prev_gray_for_flow = frame_gray.copy()
    print("[plane] calibration done; plane active")

def regenerate_features_around_corners(frame_gray):
    global tracking_features, feature_ids_per_corner
    pts = []; ids = []
    for i,(cx,cy) in enumerate(plane_points):
        x0, y0 = max(0,int(cx-35)), max(0,int(cy-35))
        x1, y1 = min(frame_gray.shape[1],int(cx+35)), min(frame_gray.shape[0],int(cy+35))
        if x1<=x0 or y1<=y0:
            found = None
        else:
            roi = frame_gray[y0:y1, x0:x1]
            found = cv2.goodFeaturesToTrack(roi, maxCorners=max_features_per_corner, qualityLevel=0.01, minDistance=6)
        if found is not None:
            for pt in found:
                gx = int(pt[0][0] + x0); gy = int(pt[0][1] + y0)
                pts.append((gx,gy)); ids.append(i)
        if len([x for x in ids if x==i]) < 4:
            pts.append((int(cx),int(cy))); ids.append(i)
    if pts:
        tracking_features = np.float32(pts).reshape(-1,1,2)
        feature_ids_per_corner[:] = ids
    else:
        tracking_features = np.empty((0,1,2), dtype=np.float32)
        feature_ids_per_corner[:] = []

def update_optical_flow_and_update_corners(frame_gray):
    global tracking_features, feature_ids_per_corner, plane_points, plane_mode, prev_gray_for_flow
    if not plane_mode or tracking_features is None or tracking_features.size == 0:
        return
    if prev_gray_for_flow is None:
        prev_gray_for_flow = frame_gray.copy()
        return
    new_pts, status, err = cv2.calcOpticalFlowPyrLK(prev_gray_for_flow, frame_gray, tracking_features, None, **lk_params)
    if new_pts is None:
        regenerate_features_around_corners(frame_gray)
        prev_gray_for_flow = frame_gray.copy()
        return
    status = status.reshape(-1)
    new_pts = new_pts.reshape(-1,2)
    corner_updates = {i: [] for i in range(4)}
    for idx, st in enumerate(status):
        if st == 1:
            cid = feature_ids_per_corner[idx]
            corner_updates[cid].append(tuple(new_pts[idx]))
    lost = 0
    for i in range(4):
        pts = corner_updates.get(i, [])
        if len(pts) >= max(1, int(0.25*max_features_per_corner)):
            avg_x = int(sum(p[0] for p in pts)/len(pts))
            avg_y = int(sum(p[1] for p in pts)/len(pts))
            plane_points[i] = (avg_x, avg_y)
        else:
            lost += 1
    if lost >= 2:
        print("[plane] lost too many corners -> disable")
        reset_plane()
    else:
        regenerate_features_around_corners(frame_gray)
        prev_gray_for_flow = frame_gray.copy()

def draw_plane_grid(img):
    if not plane_mode or H_plane is None:
        return
    pts = []
    for gx in range(0, PLANE_W+1, GRID_SPACING):
        for gy in range(0, PLANE_H+1, GRID_SPACING):
            pts.append((gx, gy))
    if not pts: return
    src = np.float32(pts).reshape(-1,1,2)
    dst = cv2.perspectiveTransform(src, H_plane).reshape(-1,2)
    for (x,y) in dst:
        xi, yi = int(x), int(y)
        if 0<=xi<img.shape[1] and 0<=yi<img.shape[0]:
            cv2.circle(img, (xi, yi), 1, (200,200,200), -1)
    poly = np.array(plane_points, dtype=np.int32)
    cv2.polylines(img, [poly], isClosed=True, color=(180,180,180), thickness=1)

# -----------------------------
# Panel drawing / interaction
# -----------------------------
def draw_panel(img):
    global panel_x, panel_y, panel_w, panel_h, panel_collapsed
    # panel background (black theme)
    if panel_collapsed:
        # small bar
        bar_w = 110; bar_h = panel_bar_h
        x = int(panel_x); y = int(panel_y)
        cv2.rectangle(img, (x,y), (x+bar_w, y+bar_h), (30,30,30), -1)
        cv2.rectangle(img, (x,y), (x+bar_w, y+bar_h), (90,90,90), 1)
        cv2.putText(img, "Start ▶", (x+8, y+17), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (220,220,220), 1)
        return
    # expanded
    x = int(panel_x); y = int(panel_y)
    w = panel_w; h = panel_h
    cv2.rectangle(img, (x,y), (x+w, y+h), (20,20,20), -1)
    cv2.rectangle(img, (x,y), (x+w, y+h), (100,100,100), 1)
    # top bar
    cv2.rectangle(img, (x,y), (x+w, y+panel_bar_h), (40,40,40), -1)
    cv2.putText(img, "Start Panel", (x+8, y+18), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (230,230,230), 1)
    # panel contents
    sx = x+8; sy = y+36
    cv2.putText(img, f"Plane: {'ON' if plane_mode else 'OFF'}", (sx, sy), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (200,200,200), 1)
    sy += 22
    cv2.putText(img, f"Corners: {len(plane_points)}/4", (sx, sy), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (200,200,200), 1)
    sy += 22
    cv2.putText(img, "Controls:", (sx, sy), cv2.FONT_HERSHEY_SIMPLEX, 0.44, (190,190,190), 1)
    sy += 18
    # buttons (draw simple rectangles)
    bx = x+8; by = sy
    bw = 110; bh = 26
    # Mouse-Calib button
    cv2.rectangle(img, (bx,by), (bx+bw, by+bh), (50,50,50), -1)
    cv2.rectangle(img, (bx,by), (bx+bw, by+bh), (130,130,130), 1)
    cv2.putText(img, "Mouse Calib (M)", (bx+6, by+18), cv2.FONT_HERSHEY_SIMPLEX, 0.43, (220,220,220), 1)
    # Finger-Calib
    bx2 = bx + bw + 8
    cv2.rectangle(img, (bx2,by), (bx2+bw, by+bh), (50,50,50), -1)
    cv2.rectangle(img, (bx2,by), (bx2+bw, by+bh), (130,130,130), 1)
    cv2.putText(img, "Finger Calib (F)", (bx2+6, by+18), cv2.FONT_HERSHEY_SIMPLEX, 0.43, (220,220,220), 1)
    # Reset button
    by += bh + 10
    bx = x+8
    cv2.rectangle(img, (bx,by), (bx+bw, by+bh), (50,50,50), -1)
    cv2.rectangle(img, (bx,by), (bx+bw, by+bh), (180,80,80), 1)
    cv2.putText(img, "Reset Plane (R)", (bx+6, by+18), cv2.FONT_HERSHEY_SIMPLEX, 0.43, (230,230,230), 1)
    # Close/minimize area
    cv2.putText(img, "▢", (x+w-24, y+18), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (200,200,200), 1)
    # show a tiny node list preview
    cv2.putText(img, "Nodes: center", (sx, y+h-28), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (180,180,180), 1)

def point_in_rect(px, py, rx, ry, rw, rh):
    return (px >= rx and px <= rx+rw and py >= ry and py <= ry+rh)

# -----------------------------
# Mouse callback (global)
# -----------------------------
mouse_state = {"x":0,"y":0,"down":False}

def mouse_event(event, x, y, flags, param):
    global mouse_state, panel_dragging, panel_drag_offset, panel_x, panel_y, panel_collapsed
    global mouse_calib_mode, calib_next_idx, mouse_preview_point, plane_points
    global drag_index, nodes, main_node, inv_H_plane, last_landmarks, selected_landmark
    mouse_state["x"], mouse_state["y"] = x, y

    if event == cv2.EVENT_LBUTTONDOWN:
        mouse_state["down"] = True
        # check panel collapsed bar (top-left small area) if collapsed
        if panel_collapsed:
            bx, by = int(panel_x), int(panel_y); bw = 110; bh = panel_bar_h
            if point_in_rect(x,y,bx,by,bw,bh):
                panel_collapsed = False
                return
        else:
            # check panel top bar for dragging
            if point_in_rect(x,y,int(panel_x),int(panel_y),panel_w,panel_bar_h):
                panel_dragging = True
                panel_drag_offset = (x - panel_x, y - panel_y)
                return
            # panel buttons (relative positions)
            # Mouse Calib button
            bx, by = int(panel_x+8), int(panel_y+36+18)
            bw, bh = 110, 26
            if point_in_rect(x,y,bx,by,bw,bh):
                # start mouse-calib: clear current, enter mode, require preview+space.
                reset_plane()
                mouse_calib_mode = True
                calib_next_idx = 0
                mouse_preview_point = None
                print("[panel] mouse calibration started: click to preview corner, press SPACE to confirm each.")
                return
            # Finger Calib button
            bx2 = int(panel_x+8+110+8)
            by2 = by
            if point_in_rect(x,y,bx2,by2,bw,bh):
                reset_plane()
                mouse_calib_mode = False
                # finger mode relies on landmark detection
                global finger_calib_mode
                finger_calib_mode = True
                calib_next_idx = 0
                print("[panel] finger calibration started: hold fingertip at corners (~0.45s).")
                return
            # Reset button
            rbx, rby = int(panel_x+8), int(by+bh+10)
            if point_in_rect(x,y, rbx, rby, bw, bh):
                reset_plane()
                print("[panel] reset pressed")
                return
        # if not panel interactions, and not in calibration, then check for node drag
        if not mouse_calib_mode and not finger_calib_mode:
            # convert click to virtual coords
            vclick = None
            if plane_mode and inv_H_plane is not None:
                vp = apply_homography_image_to_virtual((x,y))
                if vp is not None:
                    vclick = vp
            else:
                # scale image->virtual
                fw = last_frame_w; fh = last_frame_h
                if fw and fh:
                    vclick = (x * PLANE_W / fw, y * PLANE_H / fh)
            if vclick is not None:
                # check nodes
                for i,node in enumerate(nodes):
                    if math.hypot(vclick[0]-node["x"], vclick[1]-node["y"]) < node["radius"]:
                        drag_index = i; return
                # check main
                if math.hypot(vclick[0]-main_node["x"], vclick[1]-main_node["y"]) < main_node["radius"]:
                    drag_index = "main"; return
            # check if clicked in dropdown header area to toggle
            if point_in_rect(x,y, dd_x, dd_y, dd_width, dd_header_h):
                global dropdown_open
                dropdown_open = not dropdown_open
                return

    elif event == cv2.EVENT_LBUTTONUP:
        mouse_state["down"] = False
        panel_dragging = False
        drag_index = None

    elif event == cv2.EVENT_MOUSEMOVE:
        # panel drag follow
        if panel_dragging:
            panel_x = x - panel_drag_offset[0]
            panel_y = y - panel_drag_offset[1]
            # clamp to screen roughly (we'll clip further when drawing)
            panel_x = clamp(panel_x, 0, 800)
            panel_y = clamp(panel_y, 0, 600)
            return
        # node dragging
        if drag_index is not None:
            # convert mouse to virtual coords
            if plane_mode and inv_H_plane is not None:
                vp = apply_homography_image_to_virtual((x,y))
                if vp is not None:
                    vx, vy = vp
                else:
                    return
            else:
                fw = last_frame_w; fh = last_frame_h
                if fw and fh:
                    vx, vy = (x * PLANE_W / fw, y * PLANE_H / fh)
                else:
                    return
            if drag_index == "main":
                main_node["x"], main_node["y"] = vx, vy
            else:
                nodes[drag_index]["x"], nodes[drag_index]["y"] = vx, vy

# set mouse callback
cv2.namedWindow("Hand Tracking")
cv2.setMouseCallback("Hand Tracking", mouse_event)

# -----------------------------
# Loop state
# -----------------------------
print("Controls: m (panel mouse-calib), f (panel finger-calib), r reset, SPACE confirm previewed mouse corner, q quit")
last_frame_w = None; last_frame_h = None
last_frame_gray = None
def draw_dropdown(img):
    global dropdown_open, current_effect

    # label
    label = "Effect: "
    for key, text in effect_options:
        if current_effect == key:
            label += text
            break

    # header box
    cv2.rectangle(img, (dd_x, dd_y), (dd_x + dd_width, dd_y + dd_header_h), (40, 40, 40), -1)
    cv2.rectangle(img, (dd_x, dd_y), (dd_x + dd_width, dd_y + dd_header_h), (180, 180, 180), 1)
    cv2.putText(img, label, (dd_x + 8, dd_y + 20),
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (230,230,230), 1)

    arrow = "▼" if not dropdown_open else "▲"
    cv2.putText(img, arrow, (dd_x + dd_width - 20, dd_y + 20),
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (230,230,230), 1)

    if dropdown_open:
        for i, (key, text) in enumerate(effect_options):
            top = dd_y + dd_header_h + i * dd_item_h
            bottom = top + dd_item_h
            cv2.rectangle(img, (dd_x, top), (dd_x + dd_width, bottom), (30,30,30), -1)
            cv2.rectangle(img, (dd_x, top), (dd_x + dd_width, bottom), (160,160,160), 1)
            cv2.putText(img, text, (dd_x + 8, top + 17),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (230,230,230), 1)

# -----------------------------
# Main loop
# -----------------------------
try:
    while True:
        success, frame = cap.read()
        if not success:
            print("camera error")
            break
        frame = cv2.flip(frame, 1)
        img = frame.copy()
        h, w = img.shape[:2]
        last_frame_w, last_frame_h = w, h

        # mediapipe
        rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        results = hands.process(rgb)

        # grayscale for tracking
        current_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        last_frame_gray = current_gray.copy()

        # landmark extraction
        last_landmarks = []
        hand_points = []
        if results.multi_hand_landmarks:
            for handLms in results.multi_hand_landmarks:
                for id, lm in enumerate(handLms.landmark):
                    lx, ly = int(lm.x * w), int(lm.y * h)
                    last_landmarks.append((lx, ly))
                    cv2.circle(img, (lx, ly), 3, (0,0,255), -1)
                if 0 <= selected_landmark < len(last_landmarks):
                    sx, sy = last_landmarks[selected_landmark]
                    hand_points.append((sx, sy))
                    cv2.circle(img, (sx, sy), 8, (0,255,255), 2)
                mp_draw.draw_landmarks(img, handLms, mp_hands.HAND_CONNECTIONS)

        # finger calibration (if active)
        if finger_calib_mode and last_landmarks:
            fx, fy = last_landmarks[selected_landmark]
            cv2.putText(img, f"Finger-V: hold to lock corner {calib_next_idx+1}/4", (10,90),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (240,240,240), 1)
            if finger_last_pos is None:
                finger_last_pos = (fx, fy)
                finger_hold_start = time.time()
            else:
                dist_hold = math.hypot(fx - finger_last_pos[0], fy - finger_last_pos[1])
                if dist_hold <= finger_stable_radius:
                    if finger_hold_start is None:
                        finger_hold_start = time.time()
                    elif (time.time() - finger_hold_start) >= finger_hold_thresh:
                        plane_points.append((fx, fy))
                        calib_next_idx += 1
                        print(f"[finger] locked corner {calib_next_idx} at {(fx,fy)}")
                        finger_last_pos = None; finger_hold_start = None
                        if calib_next_idx == 4:
                            finger_calib_mode = False
                            finalize_calibration_and_prepare_tracking(current_gray)
                else:
                    finger_last_pos = (fx, fy)
                    finger_hold_start = time.time()

        # mouse calibration preview (click to preview, press SPACE to confirm)
        if mouse_calib_mode:
            cv2.putText(img, f"Mouse-V: click to preview corner {calib_next_idx+1}/4, SPACE to confirm", (10,90),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.45, (240,240,240), 1)
            # preview point is set by click handler; draw it
            if mouse_preview_point is not None:
                cv2.circle(img, (int(mouse_preview_point[0]), int(mouse_preview_point[1])), 6, (0,200,100), -1)
                cv2.putText(img, "Preview", (int(mouse_preview_point[0])+8, int(mouse_preview_point[1])), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (200,200,200), 1)

        # update tracking for plane
        if plane_mode:
            update_optical_flow_and_update_corners(current_gray)

        # draw grid & corner markers if needed
        if mouse_calib_mode or finger_calib_mode or plane_mode:
            for i,p in enumerate(plane_points):
                cv2.circle(img, (int(p[0]), int(p[1])), 6, (100,220,100), -1)
                cv2.putText(img, f"{i+1}", (int(p[0])+6, int(p[1])+6), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (220,220,220), 1)
            if plane_mode:
                draw_plane_grid(img)

        # velocity calculation (safe)
        current_time = time.time()
        if hand_points:
            hx, hy = hand_points[0]
            if prev_point is not None and prev_time is not None:
                dt = current_time - prev_time
                dt = max(0.016, min(dt, 0.1))
                dist = math.hypot(hx - prev_point[0], hy - prev_point[1])
                raw_vel = dist / dt
                finger_velocity = min(raw_vel, 800.0)
            else:
                finger_velocity = 0.0
            prev_point = (hx, hy); prev_time = current_time
            cv2.putText(img, f"vel:{int(finger_velocity)}", (10,60), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (200,200,50), 1)
        else:
            prev_point = None; prev_time = None; finger_velocity = 0.0

        # draw nodes + collisions (map hand to virtual coords for hit detection)
        # build check_points (virtual)
        if plane_mode and inv_H_plane is not None and hand_points:
            check_points = []
            for (hx,hy) in hand_points:
                vp = apply_homography_image_to_virtual((hx,hy))
                if vp is not None: check_points.append(vp)
        else:
            check_points = []
            for (hx,hy) in hand_points:
                if w and h:
                    check_points.append((hx * PLANE_W / w, hy * PLANE_H / h))

        for node in nodes:
            node_hit = False
            for (vx,vy) in check_points:
                if math.hypot(vx - node["x"], vy - node["y"]) < node["radius"]:
                    node_hit = True
                    if not node["touched"]:
                        vol = clamp(finger_velocity / 40.0, 0.05, 1.0)
                        node["sound"].set_volume(vol); node["sound"].play()
                        boost = 1.0 + min(1.5, finger_velocity / 150.0)
                        trigger_effect_node(node, boost)
                        node["touched"] = True
            if not node_hit:
                node["touched"] = False
            base_color = (0,255,0) if node["touched"] else (255,0,0)
            proj = project_virtual_to_image((node["x"], node["y"]), w, h)
            if proj is not None:
                px, py = int(proj[0]), int(proj[1])
                cv2.circle(img, (px,py), node["radius"], base_color, -1)
                update_and_draw_node_effects(img, px, py, node)

        # main node
        main_hit = False
        for (vx,vy) in check_points:
            if math.hypot(vx - main_node["x"], vy - main_node["y"]) < main_node["radius"]:
                main_hit = True; break
        if main_hit and not touched_main:
            vol = clamp(finger_velocity / 40.0, 0.05, 1.0)
            sound_main.set_volume(vol); sound_main.play()
            boost = 1.0 + min(1.5, finger_velocity / 150.0)
            trigger_effect_main(boost)
            touched_main = True
        elif not main_hit:
            touched_main = False
        projm = project_virtual_to_image((main_node["x"], main_node["y"]), w, h)
        if projm is not None:
            cv2.circle(img, (int(projm[0]), int(projm[1])), main_node["radius"], (0,255,0), -1)
            update_and_draw_main_effects(img)

        # dropdown and panel
        draw_dropdown(img)
        draw_panel(img)

        # hints
        cv2.putText(img, "SPACE to confirm previewed corner (mouse-calib). Click preview then SPACE.", (8, h-28),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.42, (200,200,200), 1)
        cv2.putText(img, "q: quit", (8, h-12), cv2.FONT_HERSHEY_SIMPLEX, 0.42, (200,200,200), 1)

        # show final
        cv2.imshow("Hand Tracking", img)

        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            break
        elif key == ord('r'):
            reset_plane()
        elif key == ord('m'):
            # start mouse-calib (same as panel button)
            reset_plane(); mouse_calib_mode = True; calib_next_idx = 0; mouse_preview_point = None
            print("[key] mouse calib started")
        elif key == ord('f'):
            reset_plane(); finger_calib_mode = True; calib_next_idx = 0; finger_last_pos = None; finger_hold_start = None
            print("[key] finger calib started")
        elif key == ord(' '):
            # confirm previewed mouse point
            if mouse_calib_mode and mouse_preview_point is not None:
                plane_points.append((int(mouse_preview_point[0]), int(mouse_preview_point[1])))
                print(f"[mouse] locked corner {calib_next_idx+1} at {mouse_preview_point}")
                calib_next_idx += 1
                mouse_preview_point = None
                if calib_next_idx == 4:
                    mouse_calib_mode = False
                    finalize_calibration_and_prepare_tracking(current_gray)
        elif key == ord('d'):
            dropdown_open = not dropdown_open

        # handle click-to-preview for mouse-calibration (we set preview point on mouse down)
        if mouse_state["down"] and mouse_calib_mode:
            # the mouse_event will set mouse_preview_point on click; here we allow continuous updating if user holds
            # ensure preview is the last mouse position
            if mouse_preview_point is None:
                # use global mouse_state coordinates
                mouse_preview_point = (mouse_state["x"], mouse_state["y"])
        # if not mouse_calib_mode, clear preview
        if not mouse_calib_mode:
            mouse_preview_point = None

except KeyboardInterrupt:
    pass
finally:
    cap.release()
    cv2.destroyAllWindows()

