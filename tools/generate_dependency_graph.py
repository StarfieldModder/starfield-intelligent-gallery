import os
import ast

OUTPUT = "sig_dependency_graph.txt"

def find_py_files(root="sig"):
    for dirpath, _, filenames in os.walk(root):
        for f in filenames:
            if f.endswith(".py"):
                yield os.path.join(dirpath, f)

def get_imports(path):
    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        tree = ast.parse(f.read(), filename=path)
    imports = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for n in node.names:
                imports.append(n.name)
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                imports.append(node.module)
    return imports

def main():
    lines = []
    for file in find_py_files():
        imports = get_imports(file)
        if imports:
            lines.append(f"{file}:")
            for imp in imports:
                lines.append(f"  -> {imp}")
            lines.append("")

    with open(OUTPUT, "w", encoding="utf-8") as out:
        out.write("\n".join(lines))

    print(f"Dependency graph written to {OUTPUT}")

if __name__ == "__main__":
    main()
