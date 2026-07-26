import subprocess
import sys

def main():
    print("Running SIG unit tests...")
    result = subprocess.run(["pytest", "-q"], capture_output=True, text=True)

    print(result.stdout)
    print(result.stderr)

    if result.returncode != 0:
        print("Unit tests failed.")
        sys.exit(1)

    print("All unit tests passed successfully.")

if __name__ == "__main__":
    main()
