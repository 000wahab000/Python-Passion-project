# Python Passion Project – Hand Tracking Interaction System

An interactive Python application using OpenCV and MediaPipe for real-time hand tracking. The system includes node-based collision detection, audio feedback through Pygame, and simple UI elements. Designed as part of a college mini-project to explore computer vision, event-driven behavior, and multimedia integration.

---

## Features

- Real-time hand tracking using MediaPipe  
- Circular “nodes” that detect hand proximity  
- Individual sounds triggered on collision  
- Visual feedback for active/inactive nodes  
- Easy to extend with more nodes or custom logic  
- Lightweight, runs on normal laptops  

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

```
