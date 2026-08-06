# ============================================================
#  FIRST RUN FLAG
#  Location: C:\IG\system\first_run_flag.py
# ============================================================

import os

FLAG_PATH = r"C:\IG\system\first_run.txt"

def is_first_run():
    return not os.path.exists(FLAG_PATH)

def mark_first_run_complete():
    with open(FLAG_PATH, "w") as f:
        f.write("Guardian awakened.")
