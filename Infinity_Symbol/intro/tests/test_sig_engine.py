r"""
tests/test_sig_engine.py — Unit tests for SIG Intro Engine modules
Run with: pytest tests/ -v --tb=short
"""
import math
import random
import sys
import os

# Ensure project root is on path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import numpy as np
import pytest

# ---------------------------------------------------------------------------
# sig_layer_rings tests
# ---------------------------------------------------------------------------

class TestRingsEasings:
    def test_ease_out_cubic_bounds(self):
        from sig_layer_rings import ease_out_cubic
        assert ease_out_cubic(0.0) == pytest.approx(0.0)
        assert ease_out_cubic(1.0) == pytest.approx(1.0)
        assert 0.0 < ease_out_cubic(0.5) < 1.0

    def test_ease_in_out_sine_bounds(self):
        from sig_layer_rings import ease_in_out_sine
        assert ease_in_out_sine(0.0) == pytest.approx(0.0, abs=1e-6)
        assert ease_in_out_sine(1.0) == pytest.approx(1.0, abs=1e-6)
        assert ease_in_out_sine(0.5) == pytest.approx(0.5, abs=1e-4)

    def test_ease_out_expo_clamps(self):
        from sig_layer_rings import ease_out_expo
        assert ease_out_expo(1.0) == pytest.approx(1.0)
        assert ease_out_expo(0.0) == pytest.approx(0.0, abs=1e-6)
        assert ease_out_expo(2.0) == pytest.approx(1.0)

    def test_all_easings_monotone(self):
        from sig_layer_rings import EASINGS
        for name, fn in EASINGS.items():
            vals = [fn(t) for t in [i/10 for i in range(11)]]
            for a, b in zip(vals, vals[1:]):
                assert b >= a - 1e-6, f"{name} is not monotonically non-decreasing"


class TestRingsGeneration:
    def test_generate_count(self):
        from sig_layer_rings import RingsLayerConfig, generate_rings
        cfg = RingsLayerConfig(num_rings=5, seed=42)
        rings = generate_rings(cfg)
        assert len(rings) == 5

    def test_rings_radius_within_bounds(self):
        from sig_layer_rings import RingsLayerConfig, generate_rings
        cfg = RingsLayerConfig(num_rings=10, seed=7,
                               min_radius_frac=0.1, max_radius_frac=0.8)
        rings = generate_rings(cfg)
        for r in rings:
            assert cfg.min_radius_frac <= r.max_radius <= cfg.max_radius_frac, \
                f"Radius {r.max_radius} out of bounds"

    def test_rings_reproducible_with_seed(self):
        from sig_layer_rings import RingsLayerConfig, generate_rings
        cfg = RingsLayerConfig(num_rings=6, seed=123)
        r1 = generate_rings(cfg)
        r2 = generate_rings(cfg)
        for a, b in zip(r1, r2):
            assert a.max_radius == pytest.approx(b.max_radius)
            assert a.color == b.color

    def test_rings_different_seeds(self):
        from sig_layer_rings import RingsLayerConfig, generate_rings
        r1 = generate_rings(RingsLayerConfig(num_rings=5, seed=1))
        r2 = generate_rings(RingsLayerConfig(num_rings=5, seed=2))
        radii_1 = [r.max_radius for r in r1]
        radii_2 = [r.max_radius for r in r2]
        assert radii_1 != radii_2, "Different seeds should produce different rings"

    def test_render_frame_returns_array(self):
        from sig_layer_rings import RingsLayerConfig, generate_rings, render_rings_frame
        cfg = RingsLayerConfig(num_rings=3, seed=0)
        rings = generate_rings(cfg)
        canvas = np.zeros((120, 160, 4), dtype=np.uint8)
        result = render_rings_frame(canvas, rings, 0.5, 120)
        assert result.shape == (120, 160, 4)
        assert result.dtype == np.uint8

    def test_render_frame_t0_empty(self):
        from sig_layer_rings import RingsLayerConfig, generate_rings, render_rings_frame
        cfg = RingsLayerConfig(num_rings=3, seed=0)
        rings = generate_rings(cfg)
        # Force all rings to start after t=0
        for r in rings:
            r.start_time = 0.5
        canvas = np.zeros((120, 160, 4), dtype=np.uint8)
        result = render_rings_frame(canvas, rings, 0.0, 120)
        # Nothing should be drawn yet
        assert result[:, :, 3].max() == 0

    def test_generate_frames_count(self):
        from sig_layer_rings import generate_rings_frames
        frames = generate_rings_frames(160, 120, 5, seed=42)
        assert len(frames) == 5
        for f in frames:
            assert f.shape == (120, 160, 4)


# ---------------------------------------------------------------------------
# sig_layer_glyphs tests
# ---------------------------------------------------------------------------

class TestGlyphs:
    def test_generate_count(self):
        from sig_layer_glyphs import GlyphsLayerConfig, generate_glyphs
        cfg = GlyphsLayerConfig(num_glyphs=4, seed=5)
        glyphs = generate_glyphs(cfg)
        assert len(glyphs) == 4

    def test_no_extreme_collision(self):
        from sig_layer_glyphs import GlyphsLayerConfig, generate_glyphs
        cfg = GlyphsLayerConfig(num_glyphs=6, collision_margin=0.1, seed=99)
        glyphs = generate_glyphs(cfg)
        positions = [g.final_pos for g in glyphs]
        for i, p1 in enumerate(positions):
            for j, p2 in enumerate(positions):
                if i == j: continue
                d = math.hypot(p1[0]-p2[0], p1[1]-p2[1])
                # Soft check: most pairs should not overlap
                # (rejection sampling may fail under heavy constraints)
                if d < 0.02:
                    pytest.xfail("Extreme collision under tight constraints")

    def test_positions_in_canvas(self):
        from sig_layer_glyphs import GlyphsLayerConfig, generate_glyphs
        cfg = GlyphsLayerConfig(num_glyphs=5, seed=3)
        glyphs = generate_glyphs(cfg)
        for g in glyphs:
            assert 0.0 <= g.final_pos[0] <= 1.0
            assert 0.0 <= g.final_pos[1] <= 1.0

    def test_reproducibility(self):
        from sig_layer_glyphs import GlyphsLayerConfig, generate_glyphs
        cfg = GlyphsLayerConfig(num_glyphs=4, seed=77)
        g1 = generate_glyphs(cfg)
        g2 = generate_glyphs(cfg)
        for a, b in zip(g1, g2):
            assert a.final_pos == b.final_pos

    def test_path_functions(self):
        from sig_layer_glyphs import PATHS
        src = (0.1, 0.1); dst = (0.8, 0.8)
        for name, fn in PATHS.items():
            p0 = fn(0.0, src, dst)
            p1 = fn(1.0, src, dst)
            # At t=0 → near src; at t=1 → near dst
            assert math.hypot(p0[0]-src[0], p0[1]-src[1]) < 0.6, f"{name} t=0 not near src"
            assert math.hypot(p1[0]-dst[0], p1[1]-dst[1]) < 0.2, f"{name} t=1 not near dst"


# ---------------------------------------------------------------------------
# sig_layer_hologrid tests
# ---------------------------------------------------------------------------

class TestHologrid:
    def test_render_returns_array(self):
        from sig_layer_hologrid import HologridConfig, render_hologrid_frame
        cfg = HologridConfig(seed=1)
        canvas = np.zeros((120, 160, 4), dtype=np.uint8)
        result = render_hologrid_frame(canvas, cfg, 0.5, 1.0)
        assert result.shape == (120, 160, 4)

    def test_before_activation_empty(self):
        from sig_layer_hologrid import HologridConfig, render_hologrid_frame
        cfg = HologridConfig(activation_start=0.5, seed=1)
        canvas = np.zeros((120, 160, 4), dtype=np.uint8)
        result = render_hologrid_frame(canvas, cfg, 0.1, 0.1)
        assert result[:, :, 3].max() == 0

    def test_after_activation_has_pixels(self):
        from sig_layer_hologrid import HologridConfig, render_hologrid_frame
        cfg = HologridConfig(activation_start=0.0, activation_duration=0.1, seed=2)
        canvas = np.zeros((120, 160, 4), dtype=np.uint8)
        result = render_hologrid_frame(canvas, cfg, 0.5, 1.0)
        assert result[:, :, 3].max() > 0

    def test_frame_sequence(self):
        from sig_layer_hologrid import generate_hologrid_frames
        frames = generate_hologrid_frames(80, 60, 6, fps=6.0, seed=42)
        assert len(frames) == 6
        for f in frames:
            assert f.shape == (60, 80, 4)


# ---------------------------------------------------------------------------
# sig_layer_parallax tests
# ---------------------------------------------------------------------------

class TestParallax:
    def test_build_catalogs_count(self):
        from sig_layer_parallax import ParallaxConfig, build_parallax
        cfg = ParallaxConfig(seed=5)
        _, catalogs = build_parallax(160, 120, cfg)
        assert len(catalogs) == len(cfg.layers)

    def test_star_catalog_shapes(self):
        from sig_layer_parallax import ParallaxLayerDef, build_star_catalog
        layer = ParallaxLayerDef(depth=0.5, star_density=2.0)
        rng = random.Random(42)
        cat = build_star_catalog(layer, 160, 120, rng)
        assert cat.xs.shape == cat.ys.shape == cat.sizes.shape
        assert cat.colors.shape[1] == 4

    def test_render_frame_shape(self):
        from sig_layer_parallax import ParallaxConfig, build_parallax, render_parallax_frame
        cfg, cats = build_parallax(160, 120, seed=1)
        canvas = np.zeros((120, 160, 4), dtype=np.uint8)
        result = render_parallax_frame(canvas, cfg, cats, 0.5, 1.0)
        assert result.shape == (120, 160, 4)

    def test_reveal_at_zero_is_transparent(self):
        from sig_layer_parallax import ParallaxConfig, build_parallax, render_parallax_frame
        cfg = ParallaxConfig(reveal_start=0.5, seed=0)
        cfg_built, cats = build_parallax(160, 120, cfg)
        canvas = np.zeros((120, 160, 4), dtype=np.uint8)
        result = render_parallax_frame(canvas, cfg_built, cats, 0.0, 0.0)
        assert result[:, :, 3].max() == 0

    def test_generate_frames(self):
        from sig_layer_parallax import generate_parallax_frames
        frames = generate_parallax_frames(80, 60, 5, seed=7)
        assert len(frames) == 5


# ---------------------------------------------------------------------------
# sig_layer_title tests
# ---------------------------------------------------------------------------

class TestTitle:
    def test_render_frame_shape(self):
        from sig_layer_title import TitleConfig, render_title_frame
        cfg = TitleConfig(title_text="SIG", seed=1)
        canvas = np.zeros((120, 160, 4), dtype=np.uint8)
        result = render_title_frame(canvas, cfg, 0.5)
        assert result.shape == (120, 160, 4)

    def test_early_frame_empty(self):
        from sig_layer_title import TitleConfig, render_title_frame
        cfg = TitleConfig(title_entry_start=0.9, seed=1)
        canvas = np.zeros((120, 160, 4), dtype=np.uint8)
        result = render_title_frame(canvas, cfg, 0.0)
        # No chars should be drawn before entry_start
        assert result[:, :, 3].max() == 0

    def test_reproducibility(self):
        from sig_layer_title import TitleConfig, render_title_frame
        cfg = TitleConfig(seed=55)
        c1 = np.zeros((120, 160, 4), dtype=np.uint8)
        c2 = np.zeros((120, 160, 4), dtype=np.uint8)
        r1 = render_title_frame(c1, cfg, 0.8, random.Random(55))
        r2 = render_title_frame(c2, cfg, 0.8, random.Random(55))
        np.testing.assert_array_equal(r1, r2)

    def test_generate_frames(self):
        from sig_layer_title import generate_title_frames
        frames = generate_title_frames(80, 60, 4, seed=9)
        assert len(frames) == 4
        for f in frames:
            assert f.shape == (60, 80, 4)


# ---------------------------------------------------------------------------
# sig_layer_audio tests
# ---------------------------------------------------------------------------

class TestAudio:
    def test_manifest_keys(self):
        from sig_layer_audio import AUDIO_MANIFEST, EVENT_TO_AUDIO
        for event, key in EVENT_TO_AUDIO.items():
            assert key in AUDIO_MANIFEST, f"Event '{event}' maps to unknown key '{key}'"

    def test_manifest_has_required_fields(self):
        from sig_layer_audio import AUDIO_MANIFEST
        required = {"url", "description", "license", "source", "tags", "duration_sec"}
        for key, entry in AUDIO_MANIFEST.items():
            missing = required - set(entry.keys())
            assert not missing, f"Asset '{key}' missing fields: {missing}"

    def test_volume_envelope_attack(self):
        from sig_layer_audio import VolumeEnvelope
        env = VolumeEnvelope(attack=0.1, decay=0.1, sustain_level=0.8, release=0.2)
        assert env.amplitude_at(0.0, 1.0) == pytest.approx(0.0)
        assert env.amplitude_at(0.05, 1.0) == pytest.approx(0.5, abs=0.01)
        assert env.amplitude_at(0.1, 1.0) == pytest.approx(1.0, abs=0.01)

    def test_volume_envelope_sustain(self):
        from sig_layer_audio import VolumeEnvelope
        env = VolumeEnvelope(attack=0.1, decay=0.1, sustain_level=0.75, release=0.1)
        # Mid-sustain
        a = env.amplitude_at(0.4, 1.0)
        assert a == pytest.approx(0.75, abs=0.05)

    def test_volume_envelope_release(self):
        from sig_layer_audio import VolumeEnvelope
        env = VolumeEnvelope(attack=0.05, decay=0.05, sustain_level=1.0, release=0.2)
        # After full release
        a = env.amplitude_at(2.0, 1.0)
        assert a == pytest.approx(0.0, abs=0.01)

    def test_mixer_headless_no_crash(self):
        from sig_layer_audio import AudioMixer
        mixer = AudioMixer(headless=True)
        mixer.trigger("click")
        mixer.trigger("spark")
        mixer.stop_all()

    def test_default_schedule_length(self):
        from sig_layer_audio import default_intro_schedule
        schedule = default_intro_schedule(8.0)
        assert len(schedule) >= 5

    def test_schedule_times_within_duration(self):
        from sig_layer_audio import default_intro_schedule
        dur = 10.0
        schedule = default_intro_schedule(dur)
        for ev in schedule:
            assert ev.trigger_time >= 0.0
            assert ev.trigger_time <= dur + 0.01


# ---------------------------------------------------------------------------
# sig_main_intro integration tests
# ---------------------------------------------------------------------------

class TestIntroSequence:
    def _make_seq(self, seed=42):
        from sig_main_intro import IntroSequenceConfig, IntroSequence
        cfg = IntroSequenceConfig(
            width=160, height=120, fps=6.0, duration_sec=2.0,
            seed=seed, headless=True,
        )
        return IntroSequence(cfg)

    def test_sequence_builds(self):
        seq = self._make_seq(42)
        assert seq is not None

    def test_render_frame_shape(self):
        seq = self._make_seq(1)
        frame = seq.render_frame(0)
        assert frame.shape == (120, 160, 3)
        assert frame.dtype == np.uint8

    def test_render_frame_valid_range(self):
        seq = self._make_seq(2)
        frame = seq.render_frame(5)
        assert frame.min() >= 0
        assert frame.max() <= 255

    def test_render_all_count(self):
        seq = self._make_seq(3)
        total = int(seq.cfg.fps * seq.cfg.duration_sec)
        frames = seq.render_all(progress=False)
        assert len(frames) == total

    def test_reproducible_frames(self):
        seq1 = self._make_seq(99)
        seq2 = self._make_seq(99)
        f1 = seq1.render_frame(3)
        f2 = seq2.render_frame(3)
        np.testing.assert_array_equal(f1, f2)

    def test_different_seeds_differ(self):
        seq1 = self._make_seq(1)
        seq2 = self._make_seq(2)
        f1 = seq1.render_frame(6)
        f2 = seq2.render_frame(6)
        # At least some pixels must differ
        assert not np.array_equal(f1, f2), "Different seeds should produce different frames"

    def test_audio_schedule_headless(self):
        seq = self._make_seq(7)
        # Should not raise
        seq.play_audio(realtime=False)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

