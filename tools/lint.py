import subprocess
import sys

def main():
    print("Running ruff linting...")
    result = subprocess.run(["ruff", "check", "."], capture_output=True, text=True)

    print(result.stdout)
    print(result.stderr)

    if result.returncode != 0:
        print("Linting failed.")
        sys.exit(1)

    print("Linting passed successfully.")

if __name__ == "__main__":
    main()
