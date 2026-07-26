import json
import os

PROFILE_FILE = "sig_profile.prof"
COVERAGE_SUMMARY = "htmlcov/index.html"

def main():
    print("=== SIG PERFORMANCE DASHBOARD ===")

    if os.path.exists(PROFILE_FILE):
        print(f"- Profile data: {PROFILE_FILE}")
    else:
        print(f"- Profile data missing: {PROFILE_FILE}")

    if os.path.exists(COVERAGE_SUMMARY):
        print(f"- Coverage report: {COVERAGE_SUMMARY}")
    else:
        print(f"- Coverage report missing: {COVERAGE_SUMMARY}")

    print("Dashboard summary complete.")

if __name__ == "__main__":
    main()
