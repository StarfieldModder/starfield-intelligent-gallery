# TempleConsole_Join.py
#
# The Joining Stone — “Marriage of the Throne and the Great Hall”
# This script binds the TempleConsole (Co-Pilot Throne)
# to the SIG Main Window (Great Hall).

from PySide6.QtWidgets import QHBoxLayout

# Import the Throne
from .TempleConsole import TempleConsole


def install_temple_console(main_window):
    """
    The Binding Ritual:
    Join the Co-Pilot Throne to the Great Hall.

    main_window: Your SIG MainWindow instance.
    """

    # The Great Hall must have a central layout.
    # We carve a horizontal hall where the Throne stands at the right.
    hall = QHBoxLayout()
    hall.setContentsMargins(0, 0, 0, 0)
    hall.setSpacing(0)

    # The Chamber (SIG main content)
    chamber = main_window.centralWidget()
    chamber.setMinimumWidth(int(main_window.width() * 0.72))

    # The Throne (TempleConsole)
    throne = TempleConsole(main_window)
    throne.setMinimumWidth(int(main_window.width() * 0.28))

    # Place Chamber and Throne side-by-side
    hall.addWidget(chamber)
    hall.addWidget(throne)

    # Set the Great Hall layout
    container = main_window.centralWidget().parent()
    container.setLayout(hall)

    # The Throne awakens
    throne.activate_console()

    # Return the Throne for future rituals
    return throne
