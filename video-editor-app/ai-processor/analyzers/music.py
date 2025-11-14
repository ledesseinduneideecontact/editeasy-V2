import numpy as np
import subprocess
import json
import tempfile
import os
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MusicAnalyzer:
    """
    Analyze music files for tempo, beats, energy, and onsets
    Optimized for video synchronization
    """

    def __init__(self):
        """Initialize MusicAnalyzer"""
        # Try to import librosa
        try:
            import librosa
            self.librosa_available = True
            logger.info("✓ Librosa available - using advanced music analysis")
        except ImportError:
            self.librosa_available = False
            logger.warning("⚠ Librosa not available - using basic analysis")
            logger.warning("  Install with: pip install librosa soundfile")

    def analyze(self, music_path):
        """
        Analyze music file for tempo, beats, energy, onsets, and duration

        Args:
            music_path: Path to audio file

        Returns:
            dict: {
                'duration': float,
                'bpm': float,
                'beats': list of beat dicts with time and strength,
                'onsets': list of onset times (impactful moments),
                'energy': float (0-1),
                'mood': str,
                'sections': list of musical sections
            }
        """
        try:
            logger.info(f"🎵 Analyzing music: {os.path.basename(music_path)}")

            # Get audio duration and basic info
            duration = self._get_duration(music_path)
            logger.info(f"  Duration: {duration:.2f}s")

            # Try to analyze with librosa if available
            if self.librosa_available:
                result = self._analyze_with_librosa(music_path, duration)
                logger.info(f"  ✓ Advanced analysis complete: BPM={result['bpm']:.1f}, Mood={result.get('mood', 'unknown')}")
                return result
            else:
                logger.info("  Using basic analysis (librosa not available)")
                return self._basic_analysis(music_path, duration)

        except Exception as e:
            logger.error(f"  ❌ Music analysis error: {str(e)}")
            return {
                'duration': 180,
                'bpm': 120,
                'beats': [],
                'onsets': [],
                'energy': 0.7,
                'mood': 'unknown'
            }

    def _get_duration(self, music_path):
        """Get audio duration using ffprobe"""
        try:
            cmd = [
                'ffprobe',
                '-v', 'error',
                '-show_entries', 'format=duration',
                '-of', 'json',
                music_path
            ]
            result = subprocess.run(cmd, capture_output=True, text=True)
            data = json.loads(result.stdout)
            return float(data['format']['duration'])
        except:
            return 180.0  # Default 3 minutes

    def _analyze_with_librosa(self, music_path, duration):
        """
        Analyze music using librosa library with advanced features
        Detects beats, onsets, energy, and musical structure
        """
        import librosa

        logger.info("  🔍 Running advanced Librosa analysis...")

        # Load audio file (analyze first 90 seconds for better accuracy)
        analysis_duration = min(duration, 90.0)
        y, sr = librosa.load(music_path, duration=analysis_duration)

        logger.info(f"  Sample rate: {sr} Hz, Samples: {len(y)}")

        # === BEAT DETECTION ===
        logger.info("  🥁 Detecting beats...")
        tempo, beat_frames = librosa.beat.beat_track(y=y, sr=sr, start_bpm=120, units='frames')
        beat_times = librosa.frames_to_time(beat_frames, sr=sr)

        logger.info(f"  Detected {len(beat_times)} beats at {tempo:.1f} BPM")

        # === ONSET DETECTION (Impactful moments) ===
        logger.info("  💥 Detecting onsets (impactful moments)...")
        onset_frames = librosa.onset.onset_detect(
            y=y,
            sr=sr,
            backtrack=True,
            units='frames'
        )
        onset_times = librosa.frames_to_time(onset_frames, sr=sr)

        # Get onset strength for each onset
        onset_env = librosa.onset.onset_strength(y=y, sr=sr)
        onset_strengths = []
        for frame in onset_frames:
            if frame < len(onset_env):
                onset_strengths.append(float(onset_env[frame]))
            else:
                onset_strengths.append(1.0)

        # Normalize onset strengths
        if onset_strengths:
            max_strength = max(onset_strengths)
            onset_strengths = [s / max_strength for s in onset_strengths]

        logger.info(f"  Detected {len(onset_times)} onsets")

        # === ENERGY ANALYSIS ===
        rms = librosa.feature.rms(y=y)[0]
        energy = float(np.mean(rms))
        energy_normalized = min(energy * 10, 1.0)  # Normalize to 0-1

        # === SPECTRAL FEATURES ===
        spectral_centroid = librosa.feature.spectral_centroid(y=y, sr=sr)[0]
        brightness = float(np.mean(spectral_centroid))

        # Zero crossing rate (percussion/noisiness)
        zcr = librosa.feature.zero_crossing_rate(y)[0]
        percussiveness = float(np.mean(zcr))

        # === GENERATE BEAT TIMELINE ===
        # Create precise beat list with strength indicators
        beats = []
        beat_interval = 60.0 / tempo  # seconds per beat

        # Use detected beat times for precision
        for i, beat_time in enumerate(beat_times):
            # Determine if this is a strong beat (downbeat)
            is_downbeat = i % 4 == 0  # Every 4th beat is typically a downbeat

            beats.append({
                'time': float(beat_time),
                'strength': 1.0 if is_downbeat else 0.7,
                'type': 'downbeat' if is_downbeat else 'beat',
                'index': i
            })

        # Extend beats to full duration if needed
        if duration > analysis_duration:
            last_beat_time = beats[-1]['time'] if beats else 0
            beat_idx = len(beats)

            while last_beat_time < duration:
                last_beat_time += beat_interval
                is_downbeat = beat_idx % 4 == 0

                beats.append({
                    'time': float(last_beat_time),
                    'strength': 0.9 if is_downbeat else 0.6,  # Lower confidence for extrapolated beats
                    'type': 'downbeat' if is_downbeat else 'beat',
                    'index': beat_idx,
                    'extrapolated': True
                })
                beat_idx += 1

        # === ONSET TIMELINE ===
        onsets = []
        for i, (onset_time, strength) in enumerate(zip(onset_times, onset_strengths)):
            onsets.append({
                'time': float(onset_time),
                'strength': float(strength),
                'index': i
            })

        # Sort by time
        onsets.sort(key=lambda x: x['time'])

        logger.info(f"  ✓ Analysis complete: {len(beats)} beats, {len(onsets)} onsets")

        return {
            'duration': float(duration),
            'bpm': float(tempo),
            'beats': beats,
            'onsets': onsets,
            'energy': float(energy_normalized),
            'brightness': float(brightness / sr * 2),  # Normalize
            'percussiveness': float(percussiveness),
            'mood': self._estimate_mood(energy_normalized, tempo, percussiveness)
        }

    def _basic_analysis(self, music_path, duration):
        """Basic analysis without librosa (fallback)"""
        logger.info("  Using basic beat estimation (120 BPM)")

        # Estimate BPM based on typical music (default 120 BPM)
        bpm = 120

        # Generate regular beats
        beat_interval = 60.0 / bpm
        beats = []
        onsets = []
        t = beat_interval
        beat_idx = 0

        while t < duration:
            is_downbeat = beat_idx % 4 == 0

            beats.append({
                'time': float(t),
                'strength': 1.0 if is_downbeat else 0.6,
                'type': 'downbeat' if is_downbeat else 'beat',
                'index': beat_idx
            })

            # Every downbeat is an onset
            if is_downbeat:
                onsets.append({
                    'time': float(t),
                    'strength': 0.8,
                    'index': len(onsets)
                })

            t += beat_interval
            beat_idx += 1

        logger.info(f"  Generated {len(beats)} beats, {len(onsets)} onsets")

        return {
            'duration': float(duration),
            'bpm': float(bpm),
            'beats': beats,
            'onsets': onsets,
            'energy': 0.7,
            'mood': 'neutral'
        }

    def _estimate_mood(self, energy, tempo, percussiveness):
        """Estimate music mood based on features"""
        if tempo > 140 and energy > 0.7:
            return 'energetic'
        elif tempo < 90 and energy < 0.5:
            return 'calm'
        elif energy > 0.6 and percussiveness > 0.5:
            return 'dynamic'
        elif tempo < 100:
            return 'relaxed'
        else:
            return 'neutral'

    def get_beat_times(self, music_path, max_beats=50):
        """Get precise beat times for synchronization"""
        try:
            import librosa

            y, sr = librosa.load(music_path, duration=60)
            tempo, beat_frames = librosa.beat.beat_track(y=y, sr=sr)
            beat_times = librosa.frames_to_time(beat_frames, sr=sr)

            return [float(t) for t in beat_times[:max_beats]]

        except:
            # Fallback: generate regular beats at 120 BPM
            beat_interval = 0.5  # 120 BPM = 0.5 seconds per beat
            return [i * beat_interval for i in range(max_beats)]

    def analyze_sections(self, music_path):
        """Analyze music sections (intro, verse, chorus, etc.)"""
        try:
            import librosa

            y, sr = librosa.load(music_path, duration=60)

            # Segment music
            mfcc = librosa.feature.mfcc(y=y, sr=sr)
            mfcc_delta = librosa.feature.delta(mfcc)

            # Use self-similarity matrix
            rec = librosa.segment.recurrence_matrix(mfcc)

            # Detect boundaries
            boundaries = librosa.segment.agglomerative(mfcc, 5)
            boundary_times = librosa.frames_to_time(boundaries, sr=sr)

            sections = []
            for i in range(len(boundary_times) - 1):
                sections.append({
                    'start': float(boundary_times[i]),
                    'end': float(boundary_times[i + 1]),
                    'type': 'section'
                })

            return sections

        except:
            # Fallback: simple sections
            return [
                {'start': 0, 'end': 30, 'type': 'intro'},
                {'start': 30, 'end': 120, 'type': 'main'},
                {'start': 120, 'end': 180, 'type': 'outro'}
            ]
