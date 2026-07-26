import os

SOURCE_DIRS = ["sig"]
OUTPUT = "docs/auto-generated-modules.md"

def find_modules():
    modules = []
    for root, _, files in os.walk("sig"):
        for f in files:
            if f.endswith(".py"):
                modules.append(os.path.join(root, f))
    return modules

def main():
    modules = find_modules()
    lines = ["# SIG Auto-Generated Module Index", ""]
    for m in modules:
        rel = os.path.relpath(m, ".")
        lines.append(f"- `{rel}`")
    os.makedirs("docs", exist_ok=True)
    with open(OUTPUT, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    print(f"Documentation built at {OUTPUT}")

if __name__ == "__main__":
    main()
