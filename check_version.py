import ast
import pkg_resources
import importlib

def get_imports_from_file(filename):
    with open(filename, "r", encoding="utf-8") as f:
        tree = ast.parse(f.read(), filename=filename)
    
    imports = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                imports.add(alias.name.split('.')[0])
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                imports.add(node.module.split('.')[0])
    return imports

def get_versions(modules):
    versions = {}
    for module in modules:
        try:
            # Try pkg_resources first
            versions[module] = pkg_resources.get_distribution(module).version
        except Exception:
            try:
                # Try __version__ attribute
                mod = importlib.import_module(module)
                versions[module] = getattr(mod, "__version__", "unknown")
            except Exception:
                versions[module] = "not installed"
    return versions

if __name__ == "__main__":
    filename = "V2/DashInteface.py"  # replace with your python file
    imports = get_imports_from_file(filename)
    versions = get_versions(imports)

    for lib, ver in versions.items():
        print(f"{lib}=={ver}")