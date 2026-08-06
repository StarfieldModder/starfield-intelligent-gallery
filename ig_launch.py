from PySide6.QtWidgets import QApplication

def main():
    app = QApplication([])

    from crossing.crossing_panel import CrossingPanel
    from temple.temple_startup_animation import TempleStartupAnimation
    from guardian.guardian_awaken_window import GuardianAwakenWindow
    from sentinel.sentinel_boot_sequence import SentinelBootSequence
    from system.first_run_flag import is_first_run, mark_first_run_complete
    from Modules.TempleConsole.main_window import MainWindow   # ← Correct

    from intro.intro_panel import IntroPanel
    from intro.artifact_panel import ArtifactPanel

    # Intro Title Fade
    intro = IntroPanel()
    intro.show()
    app.processEvents()
    intro.close()

    # Temple Artifact Rotation
    artifact = ArtifactPanel()
    artifact.show()
    app.processEvents()
    artifact.close()


    # 1 — The Crossing
    crossing = CrossingPanel()
    crossing.show()
    app.processEvents()
    crossing.close()

    # 2 — Temple Startup Animation (pre)
    pre = TempleStartupAnimation()
    pre.show()
    app.processEvents()
    pre.close()

    # 3 — Guardian Awakening (first run only)
    if is_first_run():
        guardian = GuardianAwakenWindow()
        guardian.show()
        app.processEvents()
        guardian.close()
        mark_first_run_complete()

    # 4 — Temple Startup Animation (post)
    post = TempleStartupAnimation()
    post.show()
    app.processEvents()
    post.close()

    # 5 — Sentinel Boot Sequence
    sentinel = SentinelBootSequence()
    sentinel.show()
    app.processEvents()
    sentinel.close()

    # 6 — Main IG Window (persistent)
    window = MainWindow()
    window.show()

    # Only ONE exec call
    app.exec()

if __name__ == "__main__":
    main()

