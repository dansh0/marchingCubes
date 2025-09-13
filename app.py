import os
import json
import time
import threading
import numpy as np
from flask import Flask, render_template, jsonify
from flask_socketio import SocketIO, emit
import loadMesh
load_mesh = loadMesh.load_mesh
import importlib

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key'
socketio = SocketIO(app, cors_allowed_origins="*")

# Global mesh data
mesh_data = {}
last_modified = 0
obj_files = []
current_mesh_file = None
currentLevelScalar = 0.0

def watch_files():
    """Simple file watcher using polling instead of watchdog"""
    last_modified = {}
    global loadMesh, load_mesh
    
    while True:
        try:
            # Check Python files
            for file in ['app.py', 'main.py', 'loadMesh.py']:
                if os.path.exists(file):
                    current_mtime = os.path.getmtime(file)
                    if file not in last_modified or current_mtime > last_modified[file]:
                        print(f"Python file changed: {file}")
                        if file == 'loadMesh.py':
                            try:
                                importlib.invalidate_caches()
                                loadMesh = importlib.reload(loadMesh)
                                load_mesh = loadMesh.load_mesh
                                print("Reloaded loadMesh.load_mesh")
                                if current_mesh_file:
                                    if load_mesh(current_mesh_file, mesh_data, currentLevelScalar):
                                        socketio.emit('mesh_updated', mesh_data)
                            except Exception as re:
                                print(f"Failed to reload loadMesh: {re}")
                        socketio.emit('code_updated', {'file': file})
                        last_modified[file] = current_mtime
            
            # Check for html file
            if os.path.exists('templates/viewer.html'):
                current_mtime = os.path.getmtime('templates/viewer.html')
                if 'templates/viewer.html' not in last_modified or current_mtime > last_modified['templates/viewer.html']:
                    print("HTML file changed: templates/viewer.html")
                    socketio.emit('code_updated', {'file': 'templates/viewer.html'})
                    last_modified['templates/viewer.html'] = current_mtime

            # check for obj files in models folder and add them to the obj_files list if they are not already in the list
            for file in os.listdir('models'):
                if file.endswith('.obj') and file not in obj_files:
                    obj_files.append(file)
                    print(f"OBJ file added: {file}")
                    socketio.emit('model_list_updated', {'file': f'models/{file}'})
                    last_modified[f'models/{file}'] = os.path.getmtime(f'models/{file}')

            time.sleep(1)  # Check every second
            
        except Exception as e:
            print(f"Error in file watcher: {e}")
            time.sleep(5)

@app.route('/')
def index():
    """Serve the main viewer page"""
    return render_template('viewer.html')

@app.route('/api/mesh')
def get_mesh():
    """API endpoint to get current mesh data"""
    if mesh_data == {}:
        success = load_mesh(current_mesh_file, mesh_data, currentLevelScalar)
        if not success:
            return jsonify({'error': 'Failed to load mesh', 'vertices': [], 'faces': []}), 500
        else:
            socketio.emit('mesh_updated', mesh_data)
    return jsonify(mesh_data)

@app.route('/api/model_list')
def get_model_list():
    """API endpoint to get the list of models"""
    return jsonify(obj_files)

@socketio.on('connect')
def handle_connect():
    """Handle client connection"""
    print('Client connected')
    if mesh_data:
        emit('mesh_updated', mesh_data)

@socketio.on('disconnect')
def handle_disconnect():
    """Handle client disconnection"""
    print('Client disconnected')

@socketio.on('change_mesh')
def change_mesh(file, levelScalar):
    """Change the current mesh to the new mesh"""
    global mesh_data, last_modified, current_mesh_file
    current_mesh_file = file
    mesh_data = {}
    last_modified = 0
    currentLevelScalar = float(levelScalar)
    success = load_mesh(file, mesh_data, float(levelScalar))
    if success:
        socketio.emit('mesh_updated', mesh_data)

if __name__ == '__main__':
    # create initial model list
    for file in os.listdir('models'):
        if file.endswith('.obj') and file not in obj_files:
            obj_files.append(file)
    print(f"Initial model list: {obj_files}")
    current_mesh_file = obj_files[0]

    # Load initial mesh
    success = load_mesh(current_mesh_file, mesh_data, currentLevelScalar)
    if success:
        socketio.emit('mesh_updated', mesh_data)
    
    # Start file watcher in background thread
    watcher_thread = threading.Thread(target=watch_files, daemon=True)
    watcher_thread.start()
    print("File watcher started")
    
    # Run Flask app with SocketIO (disable Flask's reloader to avoid watchdog issues)
    socketio.run(app, debug=True, host='0.0.0.0', port=5000, use_reloader=False)
