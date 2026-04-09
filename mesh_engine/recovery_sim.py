import pyvista as pv
import time
from pathlib import Path

# Setup
base_path = Path(__file__).resolve().parent.parent
stl_path = base_path / "mesh_engine" /"heart_reference.stl" / "heart_pt1.stl"
mesh = pv.read(str(stl_path))

# Setup the Plotter
plotter = pv.Plotter()
plotter.add_text("RECOVERY SIMULATION: Shrinking Dilation", font_size=12)

# Start with the 'Damaged' state (1.35x larger)
current_scale = 1.35
heart_actor = plotter.add_mesh(mesh.copy().scale([current_scale, current_scale, 1.0]), color="crimson")

def animate():
    global current_scale
    # We will shrink the heart in 50 small steps back to 1.0 (Healthy)
    for i in range(50):
        new_scale = 1.35 - (i * 0.007) # Gradually reduce scale
        
        # Create the 'Recovering' mesh
        recovered_mesh = mesh.copy()
        recovered_mesh.points *= [new_scale, new_scale, 1.0]
        
        # Update the display
        plotter.update_coordinates(recovered_mesh.points, mesh=heart_actor)
        
        # Change color from Crimson (SICK) to Salmon (HEALTHY) as it shrinks
        if new_scale < 1.1:
            heart_actor.mapper.dataset.active_scalars_name = None # Clear existing
            heart_actor.prop.color = "salmon"
            
        plotter.render()
        time.sleep(0.05) # Control the speed of recovery

plotter.show(auto_close=False)
print("Starting recovery simulation...")
animate()
plotter.close()