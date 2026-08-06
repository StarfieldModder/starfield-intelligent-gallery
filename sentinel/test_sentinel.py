# ============================================================
#  SENTINEL TEST HARNESS
#  By: Mark J. Latsha, Author ...  Microsoft Copilot, AI Asst
#  Location: C:\IG\sentinel\test_sentinel.py
# ============================================================

from sentinel.sentinel_api import invoke_sentinel

def run_tests():
    print("\n--- SENTINEL TEST HARNESS ---\n")

    tests = [
        ("ArchiveModule", "instability detected"),
        ("MemoryChamber", "timeline fracture"),
        ("GuardianAI", "override disturbance"),
        ("UIEngine", "optional file missing"),
        ("CoreSystem", "fatal corruption"),
    ]

    for module, reason in tests:
        print(f"\n>>> TEST: {module} — {reason}")
        invoke_sentinel(module, reason)

if __name__ == "__main__":
    run_tests()
