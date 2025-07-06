#!/usr/bin/env python3
"""
Web Interface Demo Script
Mendemonstrasikan cara menjalankan AI Agent melalui web browser
"""

import subprocess
import sys
import time
import webbrowser
from pathlib import Path

def check_dependencies():
    """Check if required dependencies are installed"""
    required_packages = ['streamlit', 'fastapi', 'uvicorn']
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            missing_packages.append(package)
    
    return missing_packages

def install_dependencies(packages):
    """Install missing dependencies"""
    if packages:
        print(f"📦 Installing missing packages: {', '.join(packages)}")
        try:
            subprocess.check_call([sys.executable, '-m', 'pip', 'install'] + packages)
            print("✅ Dependencies installed successfully!")
            return True
        except subprocess.CalledProcessError:
            print("❌ Failed to install dependencies")
            return False
    return True

def run_streamlit_demo():
    """Run Streamlit demo"""
    print("\n🎨 Starting Streamlit Web Interface...")
    print("=" * 50)
    print("📱 Interface: Simple & User-Friendly")
    print("🌐 URL: http://localhost:8501")
    print("⚙️ Features: Chat, Settings, Export")
    print("=" * 50)
    
    try:
        # Start Streamlit
        process = subprocess.Popen([
            sys.executable, '-m', 'streamlit', 'run', 'streamlit_app.py',
            '--server.port', '8501',
            '--server.headless', 'true',
            '--browser.gatherUsageStats', 'false'
        ])
        
        # Wait a bit for server to start
        time.sleep(3)
        
        # Open browser
        webbrowser.open('http://localhost:8501')
        
        print("\n✅ Streamlit server started!")
        print("🌐 Opening browser automatically...")
        print("🛑 Press Ctrl+C to stop the server")
        
        # Wait for user to stop
        try:
            process.wait()
        except KeyboardInterrupt:
            print("\n🛑 Stopping Streamlit server...")
            process.terminate()
            process.wait()
            
    except FileNotFoundError:
        print("❌ Streamlit not found. Please install it first.")
    except Exception as e:
        print(f"❌ Error starting Streamlit: {e}")

def run_fastapi_demo():
    """Run FastAPI demo"""
    print("\n🚀 Starting FastAPI Web Interface...")
    print("=" * 50)
    print("📱 Interface: Modern & Feature-Rich")
    print("🌐 URL: http://localhost:8000")
    print("⚙️ Features: Real-time Chat, WebSocket, API")
    print("📖 API Docs: http://localhost:8000/docs")
    print("=" * 50)
    
    try:
        # Start FastAPI with Uvicorn
        process = subprocess.Popen([
            sys.executable, '-m', 'uvicorn', 'web_app:app',
            '--host', '0.0.0.0',
            '--port', '8000',
            '--reload'
        ])
        
        # Wait a bit for server to start
        time.sleep(3)
        
        # Open browser
        webbrowser.open('http://localhost:8000')
        
        print("\n✅ FastAPI server started!")
        print("🌐 Opening browser automatically...")
        print("📖 API documentation: http://localhost:8000/docs")
        print("🛑 Press Ctrl+C to stop the server")
        
        # Wait for user to stop
        try:
            process.wait()
        except KeyboardInterrupt:
            print("\n🛑 Stopping FastAPI server...")
            process.terminate()
            process.wait()
            
    except FileNotFoundError:
        print("❌ FastAPI/Uvicorn not found. Please install them first.")
    except Exception as e:
        print(f"❌ Error starting FastAPI: {e}")

def show_cli_demo():
    """Show CLI demo"""
    print("\n💻 CLI Demo - Basic Calculator Test")
    print("=" * 50)
    
    try:
        result = subprocess.run([
            sys.executable, 'main.py', 
            '--message', 'Calculate 15 * 23 + 100'
        ], capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            print("✅ CLI working correctly!")
            print("📤 Test command: Calculate 15 * 23 + 100")
            print("📥 Response preview:")
            # Show last few lines of output
            lines = result.stdout.strip().split('\n')
            for line in lines[-3:]:
                if line.strip():
                    print(f"   {line}")
        else:
            print("⚠️ CLI test completed with warnings")
            print("💡 This may be due to missing API keys (normal in demo mode)")
            
    except subprocess.TimeoutExpired:
        print("⏰ CLI test timed out (may be waiting for API response)")
    except Exception as e:
        print(f"❌ CLI test error: {e}")

def main():
    """Main demo function"""
    print("🤖 AI Personal Assistant - Web Demo")
    print("=" * 60)
    print("Mendemonstrasikan cara mengakses AI Agent via Web Browser")
    print("=" * 60)
    
    # Check current directory
    if not Path('main.py').exists():
        print("❌ Error: Please run this script from the ai-agent directory")
        print("💡 Current files should include: main.py, streamlit_app.py, web_app.py")
        return
    
    # Check dependencies
    missing = check_dependencies()
    if missing:
        print(f"📦 Missing dependencies: {', '.join(missing)}")
        install_choice = input("🤔 Install missing packages? (y/n): ").lower().strip()
        if install_choice == 'y':
            if not install_dependencies(missing):
                print("❌ Cannot proceed without dependencies")
                return
        else:
            print("⚠️ Some features may not work without required packages")
    
    # Show menu
    while True:
        print("\n🌐 Choose Web Interface Demo:")
        print("1. 🎨 Streamlit Interface (Simple & Easy)")
        print("2. 🚀 FastAPI Interface (Advanced & Modern)")
        print("3. 💻 CLI Demo (Quick Test)")
        print("4. 📖 View Documentation")
        print("5. ❌ Exit")
        
        choice = input("\n👉 Enter your choice (1-5): ").strip()
        
        if choice == '1':
            run_streamlit_demo()
        elif choice == '2':
            run_fastapi_demo()
        elif choice == '3':
            show_cli_demo()
        elif choice == '4':
            print("\n📖 Documentation Files:")
            print("   - README.md - Main project documentation")
            print("   - WEB_SETUP.md - Web interface setup guide")
            print("   - PROJECT_SUMMARY.md - Complete project overview")
            print("   - demo.py - Tools demo script")
        elif choice == '5':
            print("\n👋 Thank you for trying the AI Personal Assistant!")
            print("🌟 Your AI agent is ready for production use.")
            break
        else:
            print("❌ Invalid choice. Please enter 1-5.")

if __name__ == "__main__":
    main()
