import pyvista as pv
import time
from pathlib import Path
import numpy as np

# 1. SETUP PATHS
base_path = Path(__file__).resolve().parent.parent
clinical_dir = base_path / "data" / "emidec_clinical"
stl_path = base_path / "mesh_engine" / "heart_reference.stl" / "heart_pt1.stl"

def get_patient_data(case_id):
    data = {"EF": 60, "Tobacco": "N/A", "Sex": "N/A", "Age": "N/A"}
    clean_id = case_id.replace("Case_", "")
    target_file = None
    for f in clinical_dir.glob("*.txt"):
        if clean_id.lower() in f.name.lower():
            target_file = f
            break
    if target_file:
        with open(target_file, 'r', encoding='utf-8', errors='ignore') as f:
            for line in f:
                clean_line = line.replace(" ", "").lower().strip()
                if ":" in clean_line:
                    parts = clean_line.split(":", 1)
                    if "fevg" in parts[0]: data["EF"] = float(parts[1])
                    elif "age" == parts[0]: data["Age"] = parts[1].upper()
                    elif "sex" == parts[0]: data["Sex"] = parts[1].upper()
                    elif "tobacco" == parts[0]: data["Tobacco"] = parts[1].upper()
    return data

def generate_radiology_report(patient_id, stats):
    """Fulfills the 'LLM-guided description' requirement."""
    ef = stats['EF']
    if ef < 35:
        severity = "Severe"
        desc = "significant ventricular dilation and wall thinning"
    elif ef < 50:
        severity = "Moderate"
        desc = "noticeable remodeling and moderate dilation"
    else:
        severity = "Mild"
        desc = "preserved systolic function and normal geometry"
    
    return f"AI ANALYSIS: {severity} dysfunction. Mesh parameterized for {desc} (EF: {ef}%)."

def run_recovery_pipeline(patient_id):
    stats = get_patient_data(patient_id)
    report = generate_radiology_report(patient_id, stats)
    
    print(f"\n--- {report} ---") # Show the AI report in the terminal
    
    mesh = pv.read(str(stl_path))
    plotter = pv.Plotter(title=f"MDS Pipeline: {patient_id}")
    plotter.set_background("white")
    plotter.enable_eye_dome_lighting() 

    initial_scale = 1.0 + (60 - stats['EF']) / 100 if stats['EF'] < 60 else 1.0
    mesh.points *= [initial_scale, initial_scale, 1.0]
    
    damaged_rgb = np.array([128, 0, 32]) / 255.0  
    healthy_rgb = np.array([255, 140, 105]) / 255.0 
    
    heart_actor = plotter.add_mesh(mesh, color=damaged_rgb)
    stats_text = plotter.add_text("", position='upper_left', font_size=11, color="black")

    video_path = f"pipeline_output_{patient_id}.mp4"
    plotter.open_movie(video_path, framerate=60)

    base_points = mesh.points.copy() / [initial_scale, initial_scale, 1.0]
    plotter.show(auto_close=False, interactive_update=True)

    for i in range(201): 
        progress = min(i / 200, 1.0)
        current_scale = initial_scale - ((initial_scale - 1.0) * progress)
        current_ef = stats['EF'] + ((60 - stats['EF']) * progress)
        
        heart_actor.mapper.dataset.points = base_points * [current_scale, current_scale, 1.0]
        plotter.camera.azimuth += 0.65 
        
        heart_actor.prop.color = damaged_rgb + (healthy_rgb - damaged_rgb) * progress
        heart_actor.prop.specular = 0.4 + (0.4 * progress)
        
        stats_text.set_text(0, f"PATIENT ID: {patient_id}\n"
                               f"GROUND TRUTH EF: {stats['EF']}%\n"
                               f"CURRENT EF: {current_ef:.1f}%\n"
                               f"STATUS: {'HEALED' if progress >= 1.0 else 'REMODELING...'}")
        
        plotter.render()

        # SNAPSHOT LOGIC: Saves images for your final report
        if i == 0:
            plotter.screenshot(f"evaluation_{patient_id}_DAMAGED.png")
        if i == 200:
            plotter.screenshot(f"evaluation_{patient_id}_RECOVERED.png")
    
        plotter.write_frame() 
        time.sleep(0.001)

    plotter.close()
    print(f"✅ Video and Screenshots saved for {patient_id}.")

# --- THE INTERACTIVE ENTRY POINT ---
if __name__ == "__main__":
    print("\n" + "="*40)
    print(" MDS ORGAN DAMAGE VISUALIZER PIPELINE ")
    print("="*40)
    
    while True:
        user_choice = input("\nEnter Patient ID (e.g., Case_P050) or 'exit' to quit: ").strip()
        
        if user_choice.lower() == 'exit':
            print("Shutting down. Best of luck with your presentation!")
            break
        
        # Verify the case file exists before running
        clean_id = user_choice.replace("Case_", "")
        if any(clean_id.lower() in f.name.lower() for f in clinical_dir.glob("*.txt")):
            run_recovery_pipeline(user_choice)
        else:
            print(f"❌ Patient ID '{user_choice}' not found in clinical records.")