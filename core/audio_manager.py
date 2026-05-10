# core/audio_manager.py

import math
from array import array
import pygame


class AudioManager:
    def __init__(self):
        self.available = False
        self.sounds = {}
        self.music_sound = None
        self.music_channel = None

        try:
            if pygame.mixer.get_init() is None:
                pygame.mixer.init(frequency=22050, size=-16, channels=1, buffer=512)

            self.available = True
            self.music_channel = pygame.mixer.Channel(0)
            self._build_sounds()
        except Exception as e:
            print(f"[WARN] Audio disabled: {e}")
            self.available = False

    def _build_sounds(self):
        self.sounds["shoot"] = self._make_tone(
            freq=720, duration=0.06, volume=0.18, wave_type="square"
        )
        self.sounds["death"] = self._make_sweep(
            start_freq=260, end_freq=110, duration=0.18, volume=0.20
        )
        self.sounds["warning"] = self._make_sequence(
            [
                (880, 0.10),
                (0, 0.04),
                (880, 0.10),
                (0, 0.04),
                (660, 0.16),
            ],
            volume=0.22,
            wave_type="square"
        )
        self.sounds["victory"] = self._make_sequence(
            [
                (523, 0.10),
                (659, 0.10),
                (784, 0.12),
                (1046, 0.25),
            ],
            volume=0.25,
            wave_type="sine"
        )


    def stop_music(self):
        if self.available:
            pygame.mixer.music.stop()

    def _make_tone(self, freq, duration, volume=0.2, wave_type="sine", sample_rate=22050):
        n_samples = max(1, int(sample_rate * duration))
        buf = array("h")

        attack = int(n_samples * 0.08)
        release = int(n_samples * 0.18)

        for i in range(n_samples):
            t = i / sample_rate

            if wave_type == "square":
                sample = 1.0 if math.sin(2 * math.pi * freq * t) >= 0 else -1.0
            else:
                sample = math.sin(2 * math.pi * freq * t)

            env = 1.0
            if attack > 0 and i < attack:
                env = i / attack
            if release > 0 and i > n_samples - release:
                env = min(env, (n_samples - i) / release)

            value = int(32767 * volume * env * sample)
            buf.append(value)

        return pygame.mixer.Sound(buffer=buf.tobytes())

    def _make_sweep(self, start_freq, end_freq, duration, volume=0.2, sample_rate=22050):
        n_samples = max(1, int(sample_rate * duration))
        buf = array("h")

        release = int(n_samples * 0.25)

        phase = 0.0
        for i in range(n_samples):
            progress = i / max(1, n_samples - 1)
            freq = start_freq + (end_freq - start_freq) * progress

            phase += 2 * math.pi * freq / sample_rate
            sample = math.sin(phase)

            env = 1.0
            if release > 0 and i > n_samples - release:
                env = (n_samples - i) / release

            value = int(32767 * volume * env * sample)
            buf.append(value)

        return pygame.mixer.Sound(buffer=buf.tobytes())

    def _make_sequence(self, notes, volume=0.2, wave_type="sine", sample_rate=22050):
        buf = array("h")

        for freq, duration in notes:
            n_samples = max(1, int(sample_rate * duration))
            attack = int(n_samples * 0.08)
            release = int(n_samples * 0.18)

            for i in range(n_samples):
                if freq == 0:
                    buf.append(0)
                    continue

                t = i / sample_rate

                if wave_type == "square":
                    sample = 1.0 if math.sin(2 * math.pi * freq * t) >= 0 else -1.0
                else:
                    sample = math.sin(2 * math.pi * freq * t)

                env = 1.0
                if attack > 0 and i < attack:
                    env = i / attack
                if release > 0 and i > n_samples - release:
                    env = min(env, (n_samples - i) / release)

                value = int(32767 * volume * env * sample)
                buf.append(value)

        return pygame.mixer.Sound(buffer=buf.tobytes())

    def _make_pad_music(self, duration=4.0, volume=0.08, sample_rate=22050):
        n_samples = max(1, int(sample_rate * duration))
        buf = array("h")

        freqs = [130.81, 164.81, 196.00]  # C3, E3, G3

        for i in range(n_samples):
            t = i / sample_rate

            # soft chord pad
            sample = 0.0
            for idx, freq in enumerate(freqs):
                phase_shift = idx * 0.7
                sample += math.sin(2 * math.pi * freq * t + phase_shift)

            sample /= len(freqs)

            # gentle pulse
            lfo = 0.75 + 0.25 * math.sin(2 * math.pi * 0.35 * t)
            sample *= lfo

            # fade edges
            edge = 0.5
            env = 1.0
            if t < edge:
                env = min(env, t / edge)
            if t > duration - edge:
                env = min(env, (duration - t) / edge)

            value = int(32767 * volume * env * sample)
            buf.append(value)

        return pygame.mixer.Sound(buffer=buf.tobytes())

    def play_music(self):
        if not self.available:
            return

        try:
            pygame.mixer.music.load("assets/sounds/music/bg_music.mp3")
            pygame.mixer.music.set_volume(0.15)  # ปรับความดังตรงนี้
            pygame.mixer.music.play(-1, fade_ms=1000)
        except Exception as e:
            print(f"[WARN] Failed to load music: {e}")

    def stop_music(self):
        if self.available and self.music_channel is not None:
            self.music_channel.stop()

    def play(self, name):
        if not self.available:
            return

        sound = self.sounds.get(name)
        if sound is not None:
            sound.play()