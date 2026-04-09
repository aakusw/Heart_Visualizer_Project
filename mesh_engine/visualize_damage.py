import pyvista as pv
import pandas as pd
from pathlib import Path

# 1. Setup Paths
base_path = Path(__file__).resolve().parent.parent
stl_path = base_path / "mesh_engine" /"heart_reference.stl" / "heart_pt1.stl"

# 2. Load your 3D Mesh
if not stl_path.exists():
    print(f"Error: Could not find {stl_path}. Check your file name!")
else:
    mesh = pv.read(str(stl_path))

    # 3. Define the Patient Data (From your successful terminal run)
    healthy_ef = 78.49
    damaged_ef = 24.88

    # 4. Calculate Dilation (How much the heart 'swells')
    # If 70% is normal, a 24% EF heart is roughly 40% larger in volume
    dilation_factor = 1.4 

    # 5. Create the 'Damaged' Mesh by scaling the points
    # We scale X and Y (width) but keep Z (height) similar to real pathology
    damaged_mesh = mesh.copy()
    damaged_mesh.points *= [dilation_factor, dilation_factor, 1.0]

    # 6. Setup the Side-by-Side View
    plotter = pv.Plotter(shape=(1, 2))

    # Left: Healthy Heart
    plotter.subplot(0, 0)
    plotter.add_text("HEALTHY (EF: 78%)", font_size=12)
    plotter.add_mesh(mesh, color="salmon", show_edges=True)

    # Right: Damaged Heart
    plotter.subplot(0, 1)
    plotter.add_text("DAMAGED (EF: 24%)", font_size=12)
    plotter.add_mesh(damaged_mesh, color="crimson", show_edges=True)

    print("Opening 3D Visualizer...")
    plotter.show()