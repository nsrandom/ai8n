#!/usr/bin/env python3
"""
Launcher script for the AI8N Node.js Workflow UI

This script provides an easy way to start the Node.js UI with proper setup.
"""

import subprocess
import sys
import os
import time
import webbrowser
from pathlib import Path

def check_requirements():
    """Check if all requirements are met."""
    print("🔍 Checking requirements...")
    
    # Check Node.js
    try:
        result = subprocess.run(['node', '--version'], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ Node.js {result.stdout.strip()}")
        else:
            print("❌ Node.js not found. Please install Node.js 14.0.0 or higher.")
            return False
    except FileNotFoundError:
        print("❌ Node.js not found. Please install Node.js 14.0.0 or higher.")
        return False
    
    # Check npm
    try:
        result = subprocess.run(['npm', '--version'], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ npm {result.stdout.strip()}")
        else:
            print("❌ npm not found. Please install npm.")
            return False
    except FileNotFoundError:
        print("❌ npm not found. Please install npm.")
        return False
    
    # Check if package.json exists
    if not Path('package.json').exists():
        print("❌ package.json not found. Please run this script from the ui/nodejs directory.")
        return False
    
    # Check if node_modules exists
    if not Path('node_modules').exists():
        print("📦 Installing dependencies...")
        result = subprocess.run(['npm', 'install'], capture_output=True, text=True)
        if result.returncode != 0:
            print(f"❌ Failed to install dependencies: {result.stderr}")
            return False
        print("✅ Dependencies installed")
    
    # Check if database exists
    db_path = Path('../../data/ai8n.db')
    if not db_path.exists():
        print("⚠️  Database not found. Creating sample workflows...")
        try:
            # Try to create sample workflows
            result = subprocess.run([
                sys.executable, 
                '../../data/create_incrementor_workflow.py', 
                '3'
            ], capture_output=True, text=True, cwd='../..')
            
            if result.returncode == 0:
                print("✅ Sample workflows created")
            else:
                print(f"⚠️  Could not create sample workflows: {result.stderr}")
                print("   You may need to create workflows manually.")
        except Exception as e:
            print(f"⚠️  Could not create sample workflows: {e}")
            print("   You may need to create workflows manually.")
    
    return True

def start_server():
    """Start the Node.js server."""
    print("🚀 Starting AI8N Workflow UI...")
    
    try:
        # Start the server
        process = subprocess.Popen(['npm', 'start'], 
                                 stdout=subprocess.PIPE, 
                                 stderr=subprocess.PIPE, 
                                 text=True)
        
        # Wait a moment for server to start
        time.sleep(3)
        
        # Check if server is running
        if process.poll() is None:
            print("✅ Server started successfully!")
            print("🌐 Opening browser...")
            
            # Open browser
            webbrowser.open('http://localhost:3000')
            
            print("\n" + "="*50)
            print("🎉 AI8N Workflow UI is running!")
            print("📍 URL: http://localhost:3000")
            print("🛑 Press Ctrl+C to stop the server")
            print("="*50)
            
            try:
                # Wait for user to stop the server
                process.wait()
            except KeyboardInterrupt:
                print("\n🛑 Stopping server...")
                process.terminate()
                process.wait()
                print("✅ Server stopped")
        else:
            stdout, stderr = process.communicate()
            print(f"❌ Server failed to start:")
            print(f"STDOUT: {stdout}")
            print(f"STDERR: {stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Error starting server: {e}")
        return False
    
    return True

def main():
    """Main function."""
    print("🔄 AI8N Workflow UI Launcher")
    print("=" * 40)
    
    # Check if we're in the right directory
    if not Path('package.json').exists():
        print("❌ Please run this script from the ui/nodejs directory.")
        print("   Current directory:", os.getcwd())
        sys.exit(1)
    
    # Check requirements
    if not check_requirements():
        print("\n❌ Requirements check failed. Please fix the issues above.")
        sys.exit(1)
    
    print("\n✅ All requirements met!")
    
    # Start server
    if not start_server():
        print("\n❌ Failed to start server.")
        sys.exit(1)

if __name__ == "__main__":
    main()
