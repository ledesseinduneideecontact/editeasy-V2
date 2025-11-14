import numpy as np
import subprocess
import json
import tempfile
import os

class MusicAnalyzer:
    """Analyze music files for tempo, beats, energy"""

    def __init__(self):
        pass

    def analyze(self, music_path):
        """
        Analyze music file for tempo, beats, energy, and duration
        Returns dict with analysis results
        """
        try:
            # Get audio duration and basic info
            duration = self._get_duration(music_path)

            # Try to analyze with librosa if available
            try:
                import librosa
                return self._analyze_with_librosa(music_path, duration)
            except ImportError:
                print("librosa not available, using basic analysis")
                return self._basic_analysis(music_path, duration)

        except Exception as e:
            print(f"Music analysis error: {str(e)}")
            return {
                'duration': 180,
                'bpm': 120,
                'beats': [],
                'energy': 0.7
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
        """Analyze music using librosa library"""
        import librosa

        # Load audio file
        y, sr = librosa.load(music_path, duration=60)  # Analyze first 60 seconds

        # Tempo and beat tracking
        tempo, beat_frames = librosa.beat.beat_track(y=y, sr=sr)
        beat_times = librosa.frames_to_time(beat_frames, sr=sr)

        # Energy/RMS
        rms = librosa.feature.rms(y=y)[0]
        energy = float(np.mean(rms))
        energy_normalized = min(energy * 10, 1.0)  # Normalize

        # Spectral features for mood
        spectral_centroid = librosa.feature.spectral_centroid(y=y, sr=sr)[0]
        brightness = float(np.mean(spectral_centroid))

        # Zero crossing rate (indicates noisiness/percussion)
        zcr = librosa.feature.zero_crossing_rate(y)[0]
        percussiveness = float(np.mean(zcr))

        # Generate beat timestamps for entire duration
        beat_interval = 60.0 / tempo  # seconds per beat
        beats = []
        t = beat_interval
        while t < duration:
            beats.append({
                'time': float(t),
                'strength': 1.0 if t in beat_times else 0.5
            })
            t += beat_interval

        return {
            'duration': float(duration),
            'bpm': float(tempo),
            'beats': beats[:100],  # Limit to first 100 beats
            'energy': float(energy_normalized),
            'brightness': float(brightness / sr * 2),  # Normalize
            'percussiveness': float(percussiveness),
            'mood': self._estimate_mood(energy_normalized, tempo, percussiveness)
        }

    def _basic_analysis(self, music_path, duration):
        """Basic analysis without librosa"""
        # Estimate BPM based on typical music (default 120 BPM)
        bpm = 120

        # Generate regular beats
        beat_interval = 60.0 / bpm
        beats = []
        t = beat_interval
        while t < duration and len(beats) < 100:
            beats.append({
                'time': float(t),
                'strength': 1.0 if int(t / beat_interval) % 4 == 0 else 0.5
            })
            t += beat_interval

        return {
            'duration': float(duration),
            'bpm': float(bpm),
            'beats': beats,
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
