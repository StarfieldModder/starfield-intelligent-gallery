import importlib, sys
try:
    m = importlib.import_module("guardian.guardian_ai")
    print("Loaded guardian.guardian_ai")
    print("Symbols:", sorted([n for n in dir(m) if not n.startswith("_")]))
except Exception as e:
    print("Import failed:", e)
    raise
