r"""
compile_crossing.py  —  SIG "The Crossing" Frame Compiler
Compiles PNG/JPG frames into a single MP4. Run from your .venv terminal.
"""
import sys, argparse
from pathlib import Path

def compile_frames(frames_dir, output_path, fps, quality, pattern):
    try:
        import imageio
    except ImportError:
        print("ERROR: Run:  pip install imageio imageio-ffmpeg")
        sys.exit(1)

    frames_dir  = Path(frames_dir)
    output_path = Path(output_path)

    if not frames_dir.exists():
        print(f"\n  ERROR: Frames folder not found:\n    {frames_dir}\n")
        sys.exit(1)

    frame_files = sorted(frames_dir.glob(pattern))
    if not frame_files:
        print(f"\n  ERROR: No '{pattern}' files found in {frames_dir}\n")
        sys.exit(1)

    total = len(frame_files)
    print(f"""
============================================================
  SIG  —  The Crossing  —  Frame Compiler
  Frames   : {total}  ({pattern})
  FPS      : {fps}   Duration: {total/fps:.1f}s ({total/fps/60:.1f} min)
  Quality  : {quality}/10
  Output   : {output_path}
============================================================
""")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    writer = imageio.get_writer(str(output_path), fps=fps,
                                quality=quality, macro_block_size=None)
    bar_w = 40
    for i, f in enumerate(frame_files):
        writer.append_data(imageio.imread(str(f)))
        done = int((i+1)/total*bar_w)
        print(f"\r  [{'█'*done}{'░'*(bar_w-done)}]  {(i+1)/total*100:5.1f}%  ({i+1}/{total})",
              end="", flush=True)
    writer.close()
    size_mb = output_path.stat().st_size / (1024*1024)
    print(f"\n\n  ✅ DONE!  {output_path.name}  —  {size_mb:.2f} MB\n")

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--frames",   default=r"C:\SIG\Crossing\frames")
    p.add_argument("--output",   default=r"C:\SIG\renders\The_Crossing.mp4")
    p.add_argument("--fps",      type=float, default=24.0)
    p.add_argument("--quality",  type=int,   default=9)
    p.add_argument("--pattern",  default="*.png")
    args = p.parse_args()
    compile_frames(args.frames, args.output, args.fps, args.quality, args.pattern)

if __name__ == "__main__":
    main()

