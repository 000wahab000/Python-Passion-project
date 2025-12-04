import cv2

# EFFECT OPTIONS
effect_options = [
    ("none", "None"),
    ("pulse", "Pulse Ring"),
    ("glow", "Glow Bloom"),
    ("shockwave", "Shockwave"),
    ("particles", "Particle Burst")
]

current_effect = "none"
dropdown_open = False

# Dropdown position
dd_x, dd_y = 10, 10
dd_width = 190
dd_header_h = 30
dd_item_h = 24


def draw_dropdown(img):
    """Draws dropdown menu on screen."""
    global current_effect, dropdown_open

    # find label for selected effect
    label = "Effect: " + [txt for key, txt in effect_options if key == current_effect][0]

    cv2.rectangle(img, (dd_x, dd_y), (dd_x+dd_width, dd_y+dd_header_h),
                  (40,40,40), -1)
    cv2.rectangle(img, (dd_x, dd_y), (dd_x+dd_width, dd_y+dd_header_h),
                  (200,200,200), 1)

    cv2.putText(img, label, (dd_x+8, dd_y+20),
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (230,230,230), 1)

    arrow = "▼" if not dropdown_open else "▲"
    cv2.putText(img, arrow, (dd_x+dd_width-20, dd_y+20),
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (230,230,230), 1)

    if dropdown_open:
        for i, (_, text) in enumerate(effect_options):
            top = dd_y+dd_header_h + i*dd_item_h
            bottom = top + dd_item_h
            cv2.rectangle(img, (dd_x, top), (dd_x+dd_width, bottom),
                          (30,30,30), -1)
            cv2.rectangle(img, (dd_x, top), (dd_x+dd_width, bottom),
                          (160,160,160), 1)
            cv2.putText(img, text, (dd_x+8, top+17),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (230,230,230), 1)


def ui_click(x, y):
    """Processes mouse click for dropdown."""
    global dropdown_open, current_effect

    # header click
    if dd_x <= x <= dd_x+dd_width and dd_y <= y <= dd_y+dd_header_h:
        dropdown_open = not dropdown_open
        return True

    # options
    if dropdown_open:
        for i, (key, txt) in enumerate(effect_options):
            top = dd_y+dd_header_h + i*dd_item_h
            bottom = top + dd_item_h
            if dd_x <= x <= dd_x+dd_width and top <= y <= bottom:
                current_effect = key
                dropdown_open = False
                print("Effect:", txt)
                return True

        dropdown_open = False

    return False
