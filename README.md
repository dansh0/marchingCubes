# Mesh Viewer

A simple Flask-based web application for real-time 3D viewing of OBJ files.

## Quick Start

1. **Install dependencies** (using uv):
   ```bash
   uv add flask flask-socketio trimesh python-socketio eventlet
   ```

2. **Run the server**:
   ```bash
   python app.py
   ```

3. **Open your browser** to `http://localhost:5000`

## Features

- Real-time 3D viewing with Three.js
- Hot reload when Python files change
- WebSocket-based live updates
- Interactive 3D controls (rotate, pan, zoom)

## Architecture

- **Backend**: Flask + SocketIO + Trimesh
- **Frontend**: Three.js (same concepts as your web dev experience)
- **File watching**: Simple polling (no external dependencies)
