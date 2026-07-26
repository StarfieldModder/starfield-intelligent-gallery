import cProfile
import pstats
import sys
import sig

def main():
    print("Profiling SIG modules...")

    profiler = cProfile.Profile()
    profiler.enable()

    # Import all SIG modules
    for name in dir(sig):
        try:
            __import__(f"sig.{name}")
        except Exception:
            pass

    profiler.disable()

    stats = pstats.Stats(profiler).sort_stats("cumtime")
    stats.dump_stats("sig_profile.prof")

    print("Performance profile written to sig_profile.prof")

if __name__ == "__main__":
    main()
