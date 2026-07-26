import subprocess
import sys

def main():
    print("Running coverage report...")
    subprocess.run(["coverage", "erase"])
    subprocess.run(["coverage", "run", "-m", "pytest"])
    subprocess.run(["coverage", "report"])

    subprocess.run(["coverage", "html"])
    print("Coverage HTML report generated in htmlcov/")

if __name__ == "__main__":
    main()
