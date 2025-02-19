import os
import numpy as np
import open3d as o3d
import trimesh

def load_and_visualize_stls(directory):
    # List all STL files in the directory
    stl_files = [f for f in os.listdir(directory) if f.endswith('.stl')]
    
    # Create an empty list to hold all meshes
    combined_mesh = o3d.geometry.TriangleMesh()

    # Load each STL file and combine them into one mesh
    for stl_file in stl_files:
        stl_path = os.path.join(directory, stl_file)
        mesh = o3d.io.read_triangle_mesh(stl_path)
        combined_mesh += mesh

    # Visualize the combined mesh
    combined_mesh.compute_vertex_normals()  # Compute normals for better shading
    combined_mesh.paint_uniform_color([0.5, 0.5, 0.5])  # Set a uniform color to make it more opaque
    o3d.visualization.draw_geometries([combined_mesh])

def load_and_combine_stls(directory):
    # stl_files = [f for f in os.listdir(directory) if f.endswith('.stl') and 'tibia' not in f.lower() and 'fibula' not in f.lower()]
    stl_files = [f for f in os.listdir(directory) if f.endswith('.stl') and 'tibia' not in f.lower() and 'fibula' not in f.lower()]

    combined_mesh = o3d.geometry.TriangleMesh()
    for stl_file in stl_files:
        stl_path = os.path.join(directory, stl_file)
        mesh = o3d.io.read_triangle_mesh(stl_path)
        combined_mesh += mesh
    combined_mesh.compute_vertex_normals()
    combined_mesh.paint_uniform_color([0.5, 0.5, 0.5])
    return combined_mesh

# Convert Open3D mesh to Trimesh
def o3d_to_trimesh(o3d_mesh):
    vertices = np.asarray(o3d_mesh.vertices)
    faces = np.asarray(o3d_mesh.triangles)
    return trimesh.Trimesh(vertices=vertices, faces=faces)

def mirror_mesh_if_needed(mesh, directory):
    if '_L' in directory or '_Left' in directory:
        mesh.transform([[-1, 0, 0, 0],
                        [0, 1, 0, 0],
                        [0, 0, 1, 0],
                        [0, 0, 0, 1]])
    return mesh

# Usage
current_directory = 'PCFD_F02_R'
reference_directory = 'ST_C_002_L'

reference_mesh = load_and_combine_stls(reference_directory)
current_mesh = load_and_combine_stls(current_directory)

reference_trimesh = o3d_to_trimesh(reference_mesh)
current_trimesh = o3d_to_trimesh(current_mesh)

reference_mesh = mirror_mesh_if_needed(reference_mesh, reference_directory)
current_mesh = mirror_mesh_if_needed(current_mesh, current_directory)

# # Visualize the reference and current meshes before ICP
# reference_mesh.paint_uniform_color([0.5, 0.5, 0.5])  # Grey for reference mesh
# current_mesh.paint_uniform_color([1, 0, 0])  # Red for current mesh

# o3d.visualization.draw_geometries([reference_mesh, current_mesh])

# Sample points from the meshes
reference_points = np.asarray(reference_mesh.sample_points_uniformly(number_of_points=10000).points)
current_points = np.asarray(current_mesh.sample_points_uniformly(number_of_points=10000).points)

# Perform ICP
matrix, distances, iterations = trimesh.registration.icp(current_points, reference_points, scale=False, max_iterations=1000)
matrix = np.array(matrix)  # Ensure the transformation matrix is a valid numpy array

# Apply the transformation to the current mesh
current_mesh.transform(matrix)


# Visualize the original current mesh, the reference mesh, and the transformed current mesh with different colors

# Paint the meshes with different colors
reference_mesh.paint_uniform_color([0.5, 0.5, 0.5])  # Grey for reference mesh
current_mesh.paint_uniform_color([0, 1, 0])  # Green for transformed current mesh

# Load the original current mesh again to visualize it
original_current_mesh = load_and_combine_stls(current_directory)
original_current_mesh.paint_uniform_color([0, 0, 1])  # Blue for original current mesh

# Visualize all three meshes
o3d.visualization.draw_geometries([reference_mesh, original_current_mesh, current_mesh])

