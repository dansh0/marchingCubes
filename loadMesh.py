import trimesh
import numpy as np
import time
import igl
import traceback

def load_mesh(file, mesh_data, levelScalar=0.0):
    """Load the OBJ file and convert to JSON format for Three.js"""
    obj_file = 'models/' + file
    
    try:
        print(f"Loading mesh from: {obj_file}")
        
        # Load mesh with trimeshs
        meshOG = trimesh.load(obj_file)

        # Advanced numpy approach (most efficient)
        print(f"Mesh has {len(meshOG.faces)} faces")

        # Convert to libigl format
        verts = np.array(meshOG.vertices, dtype=np.float64)
        faces = np.array(meshOG.faces, dtype=np.int32)

        meshSize = (meshOG.bounds[1] - meshOG.bounds[0]).max()
        print(f"Mesh size: {meshSize}")

        if (levelScalar != None and float(levelScalar) != 0.0):
            # Build grid of sample points
            nx, ny, nz = 50, 50, 50  # Grid resolution
            scalar = 1.5
            grid_x = np.linspace(verts[:,0].min()*scalar, verts[:,0].max()*scalar, nx)
            grid_y = np.linspace(verts[:,1].min()*scalar, verts[:,1].max()*scalar, ny)
            grid_z = np.linspace(verts[:,2].min()*scalar, verts[:,2].max()*scalar, nz)
            
            # Create grid points for SDF evaluation
            grid_x_mesh, grid_y_mesh, grid_z_mesh = np.meshgrid(grid_x, grid_y, grid_z, indexing='ij')
            grid_points = np.vstack([grid_x_mesh.ravel(), grid_y_mesh.ravel(), grid_z_mesh.ravel()]).T

            # Get signed distance field
            sdf_values, _, _, _ = igl.signed_distance(grid_points, verts, faces)
            
            # Reshape SDF to 3D grid
            sdf_grid = sdf_values.reshape(nx, ny, nz)

            # Create grid vertices (corner points of grid cells)
            grid_verts = np.array([[x, y, z] for x in grid_x for y in grid_y for z in grid_z])

            # Reconstruct the mesh with marching cubes
            vertsLevel, facesLevel, _ = igl.marching_cubes(sdf_grid.ravel(), grid_verts, nx, ny, nz, float(levelScalar)*meshSize)

            # Fix winding order by flipping faces
            facesLevel_flipped = facesLevel[:, ::-1]  # Reverse vertex order in each face
            
            # Convert to trimesh format
            mesh = trimesh.Trimesh(vertsLevel, facesLevel_flipped)

        else:
            mesh = meshOG

        # Export the mesh

        start_time = time.time()

        # One-liner: flatten faces, index vertices, then ravel
        vertices_flat = mesh.vertices[mesh.faces.ravel()].ravel().astype(np.float32)
        normals_flat = mesh.vertex_normals[mesh.faces.ravel()].ravel().astype(np.float32) if hasattr(mesh, 'vertex_normals') else None

        end_time = time.time()
        print(f"Flattened {len(mesh.faces)} faces into {len(vertices_flat)} vertex coords")
        print(f"Numpy advanced indexing took: {end_time - start_time:.4f} seconds")

        # Convert to Three.js format
        # Clear the mesh_data dictionary in-place to remove any previous mesh data,
        # preserving the reference so that any external references to mesh_data remain valid.
        # if (mesh_data != {}):
        #     empty_keys = [k for k,v in mesh_data.iteritems() if not v]
        #     for k in empty_keys:
        #         del mesh_data[k]
        mesh_data.clear()
        mesh_data['vertices'] = vertices_flat.tolist()
        mesh_data['normals'] = normals_flat.tolist() if normals_flat is not None else None
        mesh_data['colors'] = mesh.visual.vertex_colors.tolist() if hasattr(mesh.visual, 'vertex_colors') else None
        mesh_data['isWatertight'] = mesh.is_watertight
        mesh_data['volume'] = mesh.volume
        mesh_data['area'] = mesh.area
        mesh_data['center_mass'] = mesh.center_mass.tolist()
        
        # last_modified = os.path.getmtime(obj_file)
        print(f"Mesh loaded: {len(mesh.vertices)} vertices, {len(mesh.faces)} faces")
        return True
        
    except Exception as e:
        print(f"Error loading mesh: {e}")
        print(traceback.format_exc())
        return False
