import sys
import subprocess
import os

def main():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(base_dir)
    
    print("====================================================")
    print("Starting NekoDesk Executable Compilation")
    print("====================================================")
    
    # 1. Pre-generate assets if missing
    assets_dir = os.path.join(base_dir, "assets")
    if not os.path.exists(assets_dir) or not os.listdir(assets_dir):
        print("Assets folder empty. Running procedural asset builder...")
        try:
            import generate_assets
            generate_assets.main()
        except ImportError:
            # Fallback path inclusion
            sys.path.insert(0, base_dir)
            import generate_assets
            generate_assets.main()

    # 2. Check for PyInstaller dependency
    try:
        import PyInstaller
        print("PyInstaller library found.")
    except ImportError:
        print("PyInstaller not found. Installing via pip...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])
        except Exception as e:
            print(f"Failed to auto-install PyInstaller: {e}")
            print("Please run 'pip install pyinstaller' manually before building.")
            sys.exit(1)

    # 3. Execute PyInstaller compilation
    print("Executing PyInstaller compiler...")
    cmd = ["pyinstaller", "NekoDesk.spec", "--clean", "-y"]
    try:
        subprocess.check_call(cmd)
        print("\n====================================================")
        print("Compilation Successful!")
        print("====================================================")
        
        dist_dir = os.path.join(base_dir, "dist")
        if sys.platform == "darwin":
            print(f"App bundle: {os.path.join(dist_dir, 'NekoDesk.app')}")
        elif sys.platform == "win32":
            print(f"Executable: {os.path.join(dist_dir, 'NekoDesk', 'NekoDesk.exe')}")
        else:
            print(f"Executable: {os.path.join(dist_dir, 'NekoDesk', 'NekoDesk')}")
            
    except Exception as e:
        print(f"\nCompilation failed during PyInstaller run: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
