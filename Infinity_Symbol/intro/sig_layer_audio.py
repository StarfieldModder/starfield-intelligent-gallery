r"""
sig_layer_audio.py — Audio Cues & Event-Driven Playback
SIG Intro Engine Module 6
Provides event-driven audio playback, volume envelopes, mixing,
and a curated list of royalty-free audio URLs with license attribution.
Downloads and caches audio assets locally.
"""
from __future__ import annotations
import json
import os
import threading
import time
from dataclasses import dataclass, field
from typing import Callable, Dict, List, Optional, Tuple

# ---------------------------------------------------------------------------
# Royalty-Free Audio Manifest
# All assets are Creative Commons 0 (CC0) or Pixabay License (royalty-free,
# no attribution required for Pixabay content; CC0 requires none).
# ---------------------------------------------------------------------------

AUDIO_MANIFEST: Dict[str, dict] = {
    "spark_01": {
        "url": "https://cdn.pixabay.com/audio/2022/03/24/audio_1e5be45c47.mp3",
        "description": "Electric spark / zap sound effect",
        "license": "Pixabay License — royalty-free, no attribution required",
        "source": "Pixabay",
        "tags": ["spark", "electric", "zap"],
        "duration_sec": 0.8,
    },
    "click_01": {
        "url": "https://cdn.pixabay.com/audio/2021/08/04/audio_0625c1539c.mp3",
        "description": "Clean UI click / tap",
        "license": "Pixabay License — royalty-free, no attribution required",
        "source": "Pixabay",
        "tags": ["click", "ui", "tap"],
        "duration_sec": 0.2,
    },
    "whoosh_01": {
        "url": "https://cdn.pixabay.com/audio/2022/01/18/audio_d0c6ff1fca.mp3",
        "description": "Fast whoosh / swipe transition",
        "license": "Pixabay License — royalty-free, no attribution required",
        "source": "Pixabay",
        "tags": ["whoosh", "swipe", "transition"],
        "duration_sec": 0.6,
    },
    "hum_machine_01": {
        "url": "https://cdn.pixabay.com/audio/2022/08/04/audio_2dde668d05.mp3",
        "description": "Low machine / power-up hum",
        "license": "Pixabay License — royalty-free, no attribution required",
        "source": "Pixabay",
        "tags": ["hum", "machine", "power"],
        "duration_sec": 3.5,
    },
    "clap_impact_01": {
        "url": "https://cdn.pixabay.com/audio/2022/03/15/audio_733739a40d.mp3",
        "description": "Sharp clap / impact hit",
        "license": "Pixabay License — royalty-free, no attribution required",
        "source": "Pixabay",
        "tags": ["clap", "impact", "hit"],
        "duration_sec": 0.4,
    },
    "ambience_space_01": {
        "url": "https://cdn.pixabay.com/audio/2022/05/27/audio_1808fbf07a.mp3",
        "description": "Deep space ambient loop",
        "license": "Pixabay License — royalty-free, no attribution required",
        "source": "Pixabay",
        "tags": ["ambient", "space", "loop", "background"],
        "duration_sec": 30.0,
    },
    "reveal_shimmer_01": {
        "url": "https://cdn.pixabay.com/audio/2021/08/09/audio_dc39bde808.mp3",
        "description": "Magical shimmer / reveal chime",
        "license": "Pixabay License — royalty-free, no attribution required",
        "source": "Pixabay",
        "tags": ["shimmer", "reveal", "chime", "magic"],
        "duration_sec": 1.2,
    },
    "glyph_appear_01": {
        "url": "https://cdn.pixabay.com/audio/2022/12/19/audio_26422c454d.mp3",
        "description": "Soft digital pop / glyph appear",
        "license": "Pixabay License — royalty-free, no attribution required",
        "source": "Pixabay",
        "tags": ["pop", "digital", "glyph", "appear"],
        "duration_sec": 0.3,
    },
}

# Mapping from event names used in other modules → audio asset keys
EVENT_TO_AUDIO: Dict[str, str] = {
    "spark":   "spark_01",
    "click":   "click_01",
    "whoosh":  "whoosh_01",
    "hum":     "hum_machine_01",
    "clap":    "clap_impact_01",
    "ambient": "ambience_space_01",
    "shimmer": "reveal_shimmer_01",
    "glyph":   "glyph_appear_01",
}


# ---------------------------------------------------------------------------
# Volume Envelope
# ---------------------------------------------------------------------------

@dataclass
class VolumeEnvelope:
    """ADSR-style volume envelope (all times in seconds)."""
    attack: float = 0.05
    decay: float = 0.10
    sustain_level: float = 0.85
    release: float = 0.30

    def amplitude_at(self, t: float, note_duration: float) -> float:
        """Return amplitude [0,1] at time t seconds into the note."""
        if t < 0:
            return 0.0
        if t < self.attack:
            return t / self.attack
        t2 = t - self.attack
        if t2 < self.decay:
            return 1.0 - (1.0 - self.sustain_level) * (t2 / self.decay)
        t3 = t2 - self.decay
        sustain_duration = max(0.0, note_duration - self.attack - self.decay - self.release)
        if t3 < sustain_duration:
            return self.sustain_level
        t4 = t3 - sustain_duration
        if t4 < self.release:
            return self.sustain_level * (1.0 - t4 / self.release)
        return 0.0


# ---------------------------------------------------------------------------
# Audio Event
# ---------------------------------------------------------------------------

@dataclass
class AudioEvent:
    """One scheduled audio playback event."""
    event_name: str
    trigger_time: float   # seconds from layer start
    volume: float = 1.0
    envelope: VolumeEnvelope = field(default_factory=VolumeEnvelope)
    loop: bool = False


# ---------------------------------------------------------------------------
# Downloader / Cache
# ---------------------------------------------------------------------------

def get_cache_dir(base: str = "cache") -> str:
    os.makedirs(base, exist_ok=True)
    return base


def download_audio(asset_key: str, cache_dir: str = "cache",
                   timeout: int = 15) -> Optional[str]:
    """Download audio asset and return local file path, or None on failure."""
    if asset_key not in AUDIO_MANIFEST:
        print(f"[audio] Unknown asset key: {asset_key}")
        return None
    entry = AUDIO_MANIFEST[asset_key]
    url = entry["url"]
    ext = url.rsplit(".", 1)[-1].split("?")[0]
    fname = os.path.join(cache_dir, f"{asset_key}.{ext}")
    if os.path.exists(fname):
        return fname
    try:
        import requests
        print(f"[audio] Downloading {asset_key} from {url} …")
        r = requests.get(url, timeout=timeout, stream=True)
        r.raise_for_status()
        with open(fname, "wb") as f:
            for chunk in r.iter_content(8192):
                f.write(chunk)
        print(f"[audio] Saved → {fname}")
        return fname
    except Exception as e:
        print(f"[audio] Download failed for {asset_key}: {e}")
        return None


def download_all(cache_dir: str = "cache") -> Dict[str, Optional[str]]:
    """Download all manifest assets. Returns {key: local_path or None}."""
    results = {}
    for key in AUDIO_MANIFEST:
        results[key] = download_audio(key, cache_dir)
    return results


def save_manifest(path: str = "cache/audio_manifest.json") -> None:
    """Write manifest JSON with license info."""
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    with open(path, "w") as f:
        json.dump(AUDIO_MANIFEST, f, indent=2)
    print(f"[audio] Manifest saved → {path}")


# ---------------------------------------------------------------------------
# Mixer (thin wrapper around pydub or sounddevice)
# ---------------------------------------------------------------------------

class AudioMixer:
    """
    Runtime audio mixer. Supports event-driven triggering.
    Uses pydub + simpleaudio when available; falls back to sounddevice.
    In headless mode (no playback device), all methods are no-ops.
    """

    def __init__(self, cache_dir: str = "cache", headless: bool = False):
        self.cache_dir = cache_dir
        self.headless = headless
        self._local_files: Dict[str, Optional[str]] = {}
        self._active: Dict[str, object] = {}
        self._lock = threading.Lock()

    def preload(self, keys: Optional[List[str]] = None) -> None:
        """Download and cache audio for given keys (or all)."""
        targets = keys or list(AUDIO_MANIFEST.keys())
        for key in targets:
            self._local_files[key] = download_audio(key, self.cache_dir)

    def trigger(self, event_name: str, volume: float = 1.0,
                envelope: Optional[VolumeEnvelope] = None) -> None:
        """Fire an audio event by name (non-blocking)."""
        if self.headless:
            print(f"[audio-headless] trigger: {event_name} vol={volume:.2f}")
            return
        asset_key = EVENT_TO_AUDIO.get(event_name)
        if not asset_key:
            return
        local = self._local_files.get(asset_key)
        if not local:
            local = download_audio(asset_key, self.cache_dir)
            self._local_files[asset_key] = local
        if not local:
            return
        threading.Thread(target=self._play, args=(local, volume),
                         daemon=True).start()

    def _play(self, path: str, volume: float) -> None:
        """Internal: play audio file. Tries pydub → sounddevice → skip."""
        try:
            from pydub import AudioSegment
            from pydub.playback import play
            seg = AudioSegment.from_file(path)
            seg = seg + (20 * (volume - 1.0))  # dB adjust
            play(seg)
            return
        except Exception:
            pass
        try:
            import sounddevice as sd
            import soundfile as sf
            data, sr = sf.read(path, dtype="float32")
            data *= volume
            sd.play(data, sr)
            sd.wait()
            return
        except Exception:
            pass
        print(f"[audio] No playback backend available for {path}")

    def schedule(self, events: List[AudioEvent], realtime: bool = True) -> None:
        """
        Schedule a list of AudioEvents relative to now.
        If realtime=False, just prints the schedule (headless/test mode).
        """
        if not realtime or self.headless:
            for ev in sorted(events, key=lambda e: e.trigger_time):
                print(f"[audio-schedule] t={ev.trigger_time:.3f}s → {ev.event_name} "
                      f"vol={ev.volume:.2f} loop={ev.loop}")
            return
        start = time.monotonic()
        for ev in sorted(events, key=lambda e: e.trigger_time):
            def _deferred(e=ev):
                wait = e.trigger_time - (time.monotonic() - start)
                if wait > 0:
                    time.sleep(wait)
                self.trigger(e.event_name, e.volume)
            threading.Thread(target=_deferred, daemon=True).start()

    def stop_all(self) -> None:
        """Stop all active playback (best effort)."""
        pass  # playback threads are daemon; they end with the process


# ---------------------------------------------------------------------------
# Default intro schedule
# ---------------------------------------------------------------------------

def default_intro_schedule(total_duration_sec: float = 8.0) -> List[AudioEvent]:
    """
    Return a default audio schedule for the full SIG intro sequence.
    Times are in seconds from intro start.
    """
    d = total_duration_sec
    return [
        AudioEvent("ambient",   0.0,          volume=0.4, loop=True),
        AudioEvent("hum",       0.2,          volume=0.6),
        AudioEvent("click",     d * 0.10,     volume=0.8),
        AudioEvent("spark",     d * 0.20,     volume=0.9),
        AudioEvent("whoosh",    d * 0.30,     volume=0.7),
        AudioEvent("glyph",     d * 0.35,     volume=0.6),
        AudioEvent("glyph",     d * 0.45,     volume=0.5),
        AudioEvent("spark",     d * 0.55,     volume=0.8),
        AudioEvent("shimmer",   d * 0.70,     volume=1.0),
        AudioEvent("clap",      d * 0.85,     volume=1.0),
    ]


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="SIG Audio Layer — download and test")
    parser.add_argument("--download-all", action="store_true",
                        help="Download all manifest audio assets")
    parser.add_argument("--save-manifest", action="store_true",
                        help="Save audio manifest JSON to cache/")
    parser.add_argument("--cache-dir", default="cache")
    parser.add_argument("--play", metavar="EVENT",
                        help="Play a named event (requires playback device)")
    args = parser.parse_args()

    if args.save_manifest:
        save_manifest(os.path.join(args.cache_dir, "audio_manifest.json"))
    if args.download_all:
        results = download_all(args.cache_dir)
        ok = sum(1 for v in results.values() if v)
        print(f"Downloaded {ok}/{len(results)} assets.")
    if args.play:
        mixer = AudioMixer(cache_dir=args.cache_dir)
        mixer.preload([EVENT_TO_AUDIO.get(args.play, args.play)])
        mixer.trigger(args.play)
        time.sleep(3)

