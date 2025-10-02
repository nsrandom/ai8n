#!/usr/bin/env python3
"""
Launcher script for the AI8N Workflow Visualizer Streamlit app.

This script ensures the correct working directory and runs the Streamlit app.
"""

import os
import sys
import subprocess

def main():
    """Launch the Streamlit app."""
    # Get the directory where this script is located
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Change to the project root directory (two levels up from ui/streamlit/)
    project_root = os.path.dirname(os.path.dirname(script_dir))
    os.chdir(project_root)
    
    # Path to the Streamlit app
    app_path = os.path.join(script_dir, "app.py")
    
    print(f"Starting AI8N Workflow Visualizer...")
    print(f"Project root: {project_root}")
    print(f"App path: {app_path}")
    print(f"Database path: data/ai8n.db")
    print()
    print("The app will open in your default web browser.")
    print("Press Ctrl+C to stop the app.")
    print()
    
    # Run the Streamlit app
    try:
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", app_path,
            "--server.port", "8501",
            "--server.address", "localhost"
        ], check=True)
    except KeyboardInterrupt:
        print("\nApp stopped by user.")
    except subprocess.CalledProcessError as e:
        print(f"Error running Streamlit app: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
