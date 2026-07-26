import os
import ast
from collections import Counter

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
    print("=== SIG MODULE DEPENDENCY HEATMAP ===")
    counter = Counter()

    for file in find_py_files():
        imports = get_imports(file)
        for imp in imports:
            counter[imp] += 1

    for mod, count in counter.most_common():
        print(f"{mod}: {'#' * count} ({count})")

if __name__ == "__main__":
    main()
