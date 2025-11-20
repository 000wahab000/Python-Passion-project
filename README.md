Python Passion Project – Hand Tracking Interaction System

An interactive Python application using OpenCV and MediaPipe for real-time hand tracking. The system includes node-based collision detection, audio feedback through Pygame, and simple UI elements. Designed as part of a college mini-project to explore computer vision, event-driven behavior, and multimedia integration.

Features

Real-time hand tracking using MediaPipe

Circular “nodes” that detect hand proximity

Individual sounds triggered on collision

Visual feedback for active/inactive nodes

Easy to extend with more nodes or custom logic

Lightweight, runs on normal laptops

How It Works

The camera feed is captured using OpenCV

MediaPipe detects and tracks the hand landmarks

The program extracts the center position of the hand

Every node checks the distance between itself and the hand

If the hand enters a node’s radius:

The node plays its assigned sound

The node changes visual state

A green “main” node plays a separate sound on touch

Tech Stack

Python

OpenCV

MediaPipe

Pygame (Audio System)

Installation
1. Clone the repository
git clone https://github.com/000wahab000/Python-Passion-project.git
cd Python-Passion-project

2. Install dependencies
pip install opencv-python mediapipe pygame

3. Run the project
python main.py

Project Structure
Python-Passion-project/
│── main.py
│── note.wav
│── note1.wav
│── note2.wav
│── note3.wav
│── README.md
│── .gitignore

Future Improvements

Add UI to customize node positions and sounds

Add gesture recognition

Add sound visualizer for fun

Add multiple hand support

Make a game or learning tool based on this system

Author

Wahab
Passionate about computer vision, hardware, and interactive systems.
