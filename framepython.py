import argparse
import os
import json
import sys
import subprocess
import traceback
import runpy

REGISTRY_FILE = ".framepython.json"

# -----------------------------
# Helpers
# -----------------------------
def normalize_folder(folder):
    return "." if folder == "current" else folder

def load_registry():
    if not os.path.exists(REGISTRY_FILE):
        print("[framepython] No project registered yet. Run --register first.")
        sys.exit(1)
    with open(REGISTRY_FILE) as f:
        return json.load(f)

def save_registry(data):
    with open(REGISTRY_FILE, "w") as f:
        json.dump(data, f, indent=2)

# -----------------------------
# Dependencies
# -----------------------------
def ensure_installed(deps):
    for dep in deps:
        try:
            __import__(dep)
        except ImportError:
            print(f"[framepython] Installing {dep}...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", dep])

# -----------------------------
# Register
# -----------------------------
def register(folder):
    folder = normalize_folder(folder)
    py_files = [f for f in os.listdir(folder) if f.endswith(".py")]
    registry = {"files": {}, "dependencies": []}

    # Assign .FILE, .FILE2...
    for i, f in enumerate(py_files):
        key = ".FILE" if i == 0 else f".FILE{i+1}"
        registry["files"][key] = f

    # Ask for dependencies
    libs = input("Enter libraries (comma+space separated): ")
    deps = [lib.strip() for lib in libs.split(",") if lib.strip()]
    registry["dependencies"] = deps

    # Auto install
    ensure_installed(deps)

    save_registry(registry)
    print("[framepython] Project registered!")

# -----------------------------
# List
# -----------------------------
def list_files():
    reg = load_registry()
    print("[framepython] Registered files:")
    for key, val in reg["files"].items():
        print(f"  {key} -> {val}")

# -----------------------------
# Debug
# -----------------------------
def debug(dotfile=None):
    reg = load_registry()
    targets = []

    if dotfile:
        if dotfile not in reg["files"]:
            print(f"[framepython] {dotfile} not registered.")
            return
        targets = [(dotfile, reg["files"][dotfile])]
    else:
        targets = reg["files"].items()

    for dot, filepath in targets:
        print(f"\n[framepython] Debugging {dot} ({filepath})")
        try:
            runpy.run_path(filepath, run_name="__main__")
        except Exception:
            print("----- ERROR TRACEBACK -----")
            print(traceback.format_exc())
            print("---------------------------")

# -----------------------------
# Compile
# -----------------------------
def compile_file(dotfile):
    reg = load_registry()
    if dotfile not in reg["files"]:
        print(f"[framepython] {dotfile} not registered.")
        return
    filepath = reg["files"][dotfile]
    print(f"[framepython] Compiling {dotfile} ({filepath})...")
    subprocess.run([sys.executable, "-m", "PyInstaller", "--onefile", filepath])

# -----------------------------
# Main CLI
# -----------------------------
def main():
    parser = argparse.ArgumentParser(prog="framepython")
    parser.add_argument("--register", action="store_true")
    parser.add_argument("--folder", type=str, default=None)
    parser.add_argument("--list", action="store_true")
    parser.add_argument("--debug", nargs="?", const=True)
    parser.add_argument("--compile", type=str)

    args = parser.parse_args()

    if args.register:
        if not args.folder:
            print("Usage: framepython --register --folder current")
        else:
            register(args.folder)

    elif args.list:
        list_files()

    elif args.debug:
        if args.debug is True:
            debug()
        else:
            debug(args.debug)

    elif args.compile:
        compile_file(args.compile)

    else:
        parser.print_help()

if __name__ == "__main__":
    main()
