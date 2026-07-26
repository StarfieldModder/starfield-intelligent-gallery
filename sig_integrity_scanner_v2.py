import os
import ast
import sys
from pathlib import Path

# Restrict scanning to ONLY the SIG project root
SIG_ROOT = Path(__file__).resolve().parent

# Folders to ignore (virtual env, Python libs, vendor packages)
IGNORE_FOLDERS = {
    ".venv",
    "venv",
    "Python",
    "site-packages",
    "__pycache__",
    "pip",
    "numpy",
    "pytest",
    "rich",
    "urllib3",
    "pygments",
    "distutils",
    "setuptools",
    "wheel",
    "build",
    "tests",  # optional: remove if you want SIG tests scanned
}


class IntegrityReport:
    def __init__(self):
        self.missing_imports = []
        self.syntax_errors = []
        self.indentation_errors = []
        self.unreadable_files = []
        self.orphan_files = []
        self.circular_imports = []
        self.successful_files = []

    def print_report(self):
        print("\n=== SIG INTEGRITY REPORT v2 (SIG-only scan) ===\n")

        if self.successful_files:
            print("✔ Successfully parsed:")
            for f in self.successful_files:
                print("   •", f)
            print()

        if self.unreadable_files:
            print("⚠ Unreadable files:")
            for f in self.unreadable_files:
                print("   •", f)
            print()

        if self.missing_imports:
            print("✖ Missing SIG imports:")
            for imp in self.missing_imports:
                print("   •", imp)
            print()

        if self.syntax_errors:
            print("✖ Syntax errors:")
            for err in self.syntax_errors:
                print("   •", err)
            print()

        if self.indentation_errors:
            print("✖ Indentation errors:")
            for err in self.indentation_errors:
                print("   •", err)
            print()

        if self.orphan_files:
            print("⚠ Orphaned SIG modules (not imported anywhere):")
            for f in self.orphan_files:
                print("   •", f)
            print()

        if self.circular_imports:
            print("⚠ Circular SIG imports detected:")
            for c in self.circular_imports:
                print("   •", c)
            print()

        print("\n=== END OF SIG REPORT v2 ===\n")


def is_sig_file(path: Path) -> bool:
    """Return True if the file is inside SIG and not in ignored folders."""
    parts = set(path.parts)
    return not parts.intersection(IGNORE_FOLDERS)



def scan_sig():
    report = IntegrityReport()

    # Only scan .py files inside SIG that are not in ignored folders
    py_files = [
        f for f in SIG_ROOT.glob("**/*.py")
        if is_sig_file(f)
    ]

    module_names = {f.stem for f in py_files}
    import_graph = {}

    for file in py_files:
        try:
            with open(file, "r", encoding="utf-8") as f:
                src = f.read()

            tree = ast.parse(src)
            report.successful_files.append(str(file))

            imports = []
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        imports.append(alias.name.split(".")[0])
                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        imports.append(node.module.split(".")[0])

            import_graph[file.stem] = imports

            # Only flag missing imports if they refer to SIG modules
            for imp in imports:
                if imp in module_names:
                    continue
                # If import refers to SIG but file doesn't exist
                sig_path = SIG_ROOT / f"{imp}.py"
                if sig_path.exists():
                    continue
                # Ignore external libraries
                if imp not in sys.builtin_module_names:
                    report.missing_imports.append(f"{imp} (used in {file.name})")

        except PermissionError:
            report.unreadable_files.append(str(file))
        except IndentationError as e:
            report.indentation_errors.append(f"{file.name}: {e}")
        except SyntaxError as e:
            report.syntax_errors.append(f"{file.name}: {e}")
        except Exception as e:
            report.unreadable_files.append(f"{file.name}: {e}")

    # Detect orphan SIG modules
    imported_modules = set()
    for imports in import_graph.values():
        imported_modules.update(imports)

    for file in py_files:
        if file.stem not in imported_modules and file.stem not in ["main", "sig_launcher"]:
            report.orphan_files.append(file.name)

    # Detect circular SIG imports
    for mod, imports in import_graph.items():
        for imp in imports:
            if imp in import_graph and mod in import_graph[imp]:
                report.circular_imports.append(f"{mod} ↔ {imp}")

    report.print_report()


if __name__ == "__main__":
    scan_sig()
