# Mesh Viewer

A simple Flask-based web application for real-time 3D viewing of OBJ files.

## Quick Start

1. **Install dependencies** (using uv, not required):
   ```bash
   uv add -r requirements.txt
   ```

2. **Run the server**:
   ```bash
   uv run app.py
   ```

3. **Open your browser** to `http://localhost:5000`

## Features

- Load multiple OBJ files
- Basic bloat/shrink to show marching cubes demo
- Real-time 3D viewing with Three.js
- Hot (ish) reload when Python files change
- WebSocket-based live updates
- Interactive 3D controls (rotate, pan, zoom)

## Architecture

- **Backend**: Flask + SocketIO + Trimesh + libigl
- **Frontend**: Three.js (same concepts as your web dev experience)
- **File watching**: Simple polling (no external dependencies)

