# Python Passion Project – Hand Tracking Interaction System

An interactive Python application using OpenCV and MediaPipe for real-time hand tracking. The system includes node-based collision detection, audio feedback through Pygame, and simple UI elements. Designed as part of a college mini-project to explore computer vision, event-driven behavior, and multimedia integration.
This is a branch from the final project as the author is experiment with different way of how technology works the AR implementaion is in written in detail down ways 
---

## Features

- Real-time hand tracking using MediaPipe  
- Circular “nodes” that detect hand proximity  
- Individual sounds triggered on collision  
- Visual feedback for active/inactive nodes  
- Easy to extend with more nodes or custom logic  
- Lightweight, runs on normal laptops  
- can choose which node on hands to use (21-11-2025)
---

## How It Works

1. The camera feed is captured using OpenCV  
2. MediaPipe detects and tracks the hand landmarks  
3. The program extracts the center position of the hand  
4. Every node checks the distance between itself and the hand  
5. If the hand enters a node’s radius:  
   - The node plays its assigned sound  
   - The node changes visual state  
6. A green “main” node plays a separate sound on touch  

---

## Tech Stack

- **Python**
- **OpenCV**
- **MediaPipe**
- **Pygame** (Audio System)

---

## Limitations
- Requires good lighting for stable hand tracking
- Not ideal on low-end webcams (tracking may lag)
- No gesture recognition yet, only positional detection
- Works best with a single hand at a time

## Future Improvements
- UI to customize node positions and sound files
- Add gesture recognition (fist, open hand, swipe, etc.)
- Add multi-hand support
- Add visualizer animations linked to sound
- Integrate background music or rhythm games
- Build a mini game or interactive learning tool
  
##  Author
- Wahab
Passionate about computer vision, hardware, building interactive systems, and learning through projects.
## Installation
### 1. Clone the repository
```bash
git clone https://github.com/000wahab000/Python-Passion-project.git
cd Python-Passion-project
```

### 2. Install dependencies
```bash
pip install opencv-python mediapipe pygame
```

### 3. Run the project
```bash
python main.py
```
## AR experiment

### Controls
- q Quit program
- m Mouse-V calibration (AR branch)
- f Finger-V calibration (AR branch)
- r Reset plane tracking (AR branch)


---

## File Structure
- main.py
- nodes.py
- effects.py
- hand_tracking.py
- ui.py
- note.wav
- note1.wav
- note2.wav
- note3.wav
- README.md


---

## Experimental AR Systems (chaos-lab-AR branch)

These features are prototypes and not part of the stable main branch.

### Plane Calibration

- Mouse-V: click 4 corners of a physical plane
- Finger-V: hold your fingertip steady to lock corners

### Plane Tracking

- Optical flow tracks corner movement
- Homography updates every frame
- Plane disables itself if tracking confidence is too low

### AR Projection

- Grid overlay projected onto the calibrated plane
- Nodes can be mapped into plane coordinates

---

## Project Status

- Main branch: stable
- chaos-lab-AR branch: experimental and unstable
- Further features may be added depending on available sanity and free time

---

## Lessons Learned

- Hand tracking is fun when the camera behaves
- OpenCV is not a UI framework but we used it anyway
- AR math does not care about your feelings
- Pygame somehow always survives



