import ast
import subprocess
import sys
import pkg_resources
import importlib

def get_imports_from_code(code):
    tree = ast.parse(code)
    imports = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                imports.add(alias.name.split('.')[0])
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                imports.add(node.module.split('.')[0])
    return imports

def get_version(module):
    try:
        return pkg_resources.get_distribution(module).version
    except Exception:
        try:
            mod = importlib.import_module(module)
            return getattr(mod, "__version__", "unknown")
        except Exception:
            return None

def install_package(module, version=None):
    try:
        if version:
            subprocess.check_call([sys.executable, "-m", "pip", "install", f"{module}=={version}"])
        else:
            subprocess.check_call([sys.executable, "-m", "pip", "install", module])
    except subprocess.CalledProcessError:
        print(f"❌ Failed to install {module}")

if __name__ == "__main__":
    # Example: read your python script
    filename = "your_script.py"   # change this to your code file
    with open(filename, "r", encoding="utf-8") as f:
        code = f.read()

    imports = get_imports_from_code(code)

    for module in imports:
        version = get_version(module)
        if version is None:
            print(f"📦 Installing missing package: {module}")
            install_package(module)
        else:
            print(f"✅ {module} already installed (version {version})")