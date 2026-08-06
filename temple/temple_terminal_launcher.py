# ============================================================
#  TEMPLE TERMINAL LAUNCHER
#  Location: C:\IG\temple\temple_terminal_launcher.py
# ============================================================

import curses
import subprocess
import sys

MENU_ITEMS = [
    "Open Temple Resonance Dashboard",
    "Feed Event: MemoryChamber — echo instability",
    "Feed Event: TimelineEngine — fracture detected",
    "Feed Event: GuardianAI — override disturbance",
    "Exit Terminal"
]

def run_dashboard():
    subprocess.Popen([sys.executable, r"C:\IG\temple\launch_resonance_dashboard.py"])

def feed_event(module, description):
    subprocess.Popen([
        sys.executable,
        r"C:\IG\temple\feed_resonance_event.py",
        module,
        description
    ])

def draw_menu(stdscr, selected):
    stdscr.clear()
    stdscr.addstr(0, 0, "Temple Console — Arrow Keys to Navigate, ENTER to Select", curses.A_BOLD)

    for idx, item in enumerate(MENU_ITEMS):
        if idx == selected:
            stdscr.addstr(idx + 2, 2, item, curses.A_REVERSE)
        else:
            stdscr.addstr(idx + 2, 2, item)

    stdscr.refresh()

def main(stdscr):
    curses.curs_set(0)
    selected = 0

    while True:
        draw_menu(stdscr, selected)
        key = stdscr.getch()

        if key == curses.KEY_UP:
            selected = (selected - 1) % len(MENU_ITEMS)
        elif key == curses.KEY_DOWN:
            selected = (selected + 1) % len(MENU_ITEMS)
        elif key in (curses.KEY_ENTER, 10, 13):
            choice = MENU_ITEMS[selected]

            if choice == "Open Temple Resonance Dashboard":
                run_dashboard()

            elif choice == "Feed Event: MemoryChamber — echo instability":
                feed_event("MemoryChamber", "echo instability")

            elif choice == "Feed Event: TimelineEngine — fracture detected":
                feed_event("TimelineEngine", "fracture detected")

            elif choice == "Feed Event: GuardianAI — override disturbance":
                feed_event("GuardianAI", "override disturbance")

            elif choice == "Exit Terminal":
                break

curses.wrapper(main)
