# Start an interactive Python check
python - <<'PY'
import importlib, sys
sys.path.insert(0, r"C:\SIG")
try:
    mod = importlib.import_module("core.diagnostic_reporter")
    print("Imported core.diagnostic_reporter OK")
    # call the function to ensure it runs without raising
    mod.record_error("test_module", "test_func", 0, "TestError", "This is a test", "info", None)
    print("record_error executed")
except Exception as e:
    print("Import or call failed:", e)
    PY
