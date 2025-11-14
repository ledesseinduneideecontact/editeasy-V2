"""
Beat Synchronization Module

This module synchronizes video cuts, transitions, and effects with musical beats and onsets.
Perfect for creating rhythm-matched video montages.
"""

import numpy as np
import logging
from typing import List, Dict, Tuple, Optional

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class BeatSynchronizer:
    """
    Synchronize video editing decisions with music beats and onsets

    This class takes music analysis (beats, onsets) and video clips,
    and generates an optimal edit plan that aligns cuts and transitions
    with the musical rhythm.
    """

    def __init__(self, tolerance_ms=100):
        """
        Initialize BeatSynchronizer

        Args:
            tolerance_ms: Tolerance in milliseconds for beat alignment
        """
        self.tolerance = tolerance_ms / 1000.0  # Convert to seconds
        logger.info(f"✓ BeatSynchronizer initialized (tolerance: {tolerance_ms}ms)")

    def sync_clips_to_beats(
        self,
        clips: List[Dict],
        music_analysis: Dict,
        target_duration: Optional[float] = None,
        prefer_onsets: bool = True
    ) -> List[Dict]:
        """
        Synchronize video clips to musical beats

        Args:
            clips: List of clip dicts with 'path', 'duration', 'quality' etc.
            music_analysis: Music analysis from MusicAnalyzer with 'beats', 'onsets', 'bpm'
            target_duration: Target video duration (defaults to music duration)
            prefer_onsets: Prefer aligning cuts to onsets (impactful moments) over regular beats

        Returns:
            List of synced clips with adjusted 'duration' and 'start_time'
        """
        logger.info("🎵 Synchronizing clips to music beats...")

        if not music_analysis or 'beats' not in music_analysis:
            logger.warning("  ⚠ No music analysis available, skipping sync")
            return self._basic_timing(clips, target_duration)

        beats = music_analysis.get('beats', [])
        onsets = music_analysis.get('onsets', [])
        bpm = music_analysis.get('bpm', 120)
        music_duration = music_analysis.get('duration', target_duration or 60)

        if not beats:
            logger.warning("  ⚠ No beats detected, using basic timing")
            return self._basic_timing(clips, target_duration)

        logger.info(f"  Music: {bpm:.1f} BPM, {len(beats)} beats, {len(onsets)} onsets")
        logger.info(f"  Clips: {len(clips)} clips to sync")

        # Determine target duration
        if target_duration is None:
            target_duration = music_duration

        # Select sync points (onsets or beats)
        if prefer_onsets and onsets:
            sync_points = self._get_strong_sync_points(beats, onsets)
            logger.info(f"  Using {len(sync_points)} sync points (onsets + strong beats)")
        else:
            sync_points = self._filter_strong_beats(beats)
            logger.info(f"  Using {len(sync_points)} strong beats")

        # Align clips to sync points
        synced_clips = self._align_clips_to_sync_points(
            clips,
            sync_points,
            target_duration
        )

        logger.info(f"  ✓ Synchronized {len(synced_clips)} clips")

        return synced_clips

    def _get_strong_sync_points(self, beats: List[Dict], onsets: List[Dict]) -> List[Dict]:
        """
        Get strong synchronization points by combining onsets and downbeats
        """
        sync_points = []

        # Add all onsets (impactful moments)
        for onset in onsets:
            sync_points.append({
                'time': onset['time'],
                'strength': onset.get('strength', 1.0) * 1.5,  # Onsets get priority
                'type': 'onset'
            })

        # Add downbeats (strong beats)
        for beat in beats:
            if beat.get('type') == 'downbeat' or beat.get('strength', 0) >= 0.9:
                # Check if not too close to an onset
                is_unique = all(abs(beat['time'] - sp['time']) > 0.2 for sp in sync_points)

                if is_unique:
                    sync_points.append({
                        'time': beat['time'],
                        'strength': beat.get('strength', 1.0),
                        'type': 'downbeat'
                    })

        # Sort by time
        sync_points.sort(key=lambda x: x['time'])

        return sync_points

    def _filter_strong_beats(self, beats: List[Dict]) -> List[Dict]:
        """Filter to keep only strong beats (downbeats)"""
        strong_beats = []

        for beat in beats:
            if beat.get('type') == 'downbeat' or beat.get('strength', 0) >= 0.9:
                strong_beats.append({
                    'time': beat['time'],
                    'strength': beat.get('strength', 1.0),
                    'type': 'downbeat'
                })

        return strong_beats

    def _align_clips_to_sync_points(
        self,
        clips: List[Dict],
        sync_points: List[Dict],
        target_duration: float
    ) -> List[Dict]:
        """
        Align clips to synchronization points

        Strategy:
        1. Sort clips by quality score
        2. Distribute clips across sync points
        3. Adjust durations to fit between sync points
        """
        if not sync_points:
            return self._basic_timing(clips, target_duration)

        # Sort clips by quality (best first)
        sorted_clips = sorted(
            clips,
            key=lambda c: c.get('quality', 0.5),
            reverse=True
        )

        # Calculate how many clips we can fit
        available_sync_points = len(sync_points)
        num_clips_to_use = min(len(sorted_clips), available_sync_points - 1)

        synced_clips = []
        current_time = 0.0

        for i in range(num_clips_to_use):
            clip = sorted_clips[i].copy()

            # Start time is current sync point
            start_sync = sync_points[i]
            end_sync = sync_points[i + 1] if i + 1 < len(sync_points) else None

            clip['start_time'] = start_sync['time']
            clip['sync_type'] = start_sync['type']
            clip['sync_strength'] = start_sync['strength']

            # Duration is time until next sync point
            if end_sync:
                clip['duration'] = end_sync['time'] - start_sync['time']
                clip['end_time'] = end_sync['time']
            else:
                # Last clip extends to target duration
                clip['duration'] = target_duration - start_sync['time']
                clip['end_time'] = target_duration

            # Ensure minimum duration
            if clip['duration'] < 0.5:
                clip['duration'] = 0.5

            # Ensure maximum duration
            if clip['duration'] > 8.0:
                clip['duration'] = 8.0
                clip['end_time'] = clip['start_time'] + clip['duration']

            synced_clips.append(clip)

            logger.info(
                f"    Clip {i+1}: {clip['start_time']:.2f}s - {clip['end_time']:.2f}s "
                f"({clip['duration']:.2f}s) [{clip['sync_type']}]"
            )

        return synced_clips

    def _basic_timing(self, clips: List[Dict], target_duration: Optional[float]) -> List[Dict]:
        """
        Basic timing without beat sync (fallback)
        Distributes clips evenly across target duration
        """
        if not target_duration:
            target_duration = sum(c.get('duration', 3) for c in clips)

        timed_clips = []
        time_per_clip = target_duration / len(clips) if clips else 3.0
        current_time = 0.0

        for i, clip in enumerate(clips):
            clip = clip.copy()
            clip['start_time'] = current_time
            clip['duration'] = min(time_per_clip, clip.get('duration', time_per_clip))
            clip['end_time'] = current_time + clip['duration']
            timed_clips.append(clip)
            current_time = clip['end_time']

        return timed_clips

    def suggest_transitions(
        self,
        synced_clips: List[Dict],
        music_analysis: Dict,
        style: str = 'adaptive'
    ) -> List[Dict]:
        """
        Suggest transitions between clips based on music energy and beats

        Args:
            synced_clips: Clips with start_time and duration
            music_analysis: Music analysis with energy, mood, etc.
            style: Transition style ('adaptive', 'energetic', 'smooth')

        Returns:
            List of transition dicts with type, duration, and timing
        """
        logger.info(f"  🎬 Suggesting transitions (style: {style})...")

        transitions = []
        mood = music_analysis.get('mood', 'neutral')
        energy = music_analysis.get('energy', 0.7)
        bpm = music_analysis.get('bpm', 120)

        # Determine base transition type based on mood and style
        if style == 'adaptive':
            if mood == 'energetic' or energy > 0.8:
                base_transition = 'wipe'
                base_duration = 0.3
            elif mood == 'calm' or energy < 0.4:
                base_transition = 'crossfade'
                base_duration = 1.0
            else:
                base_transition = 'dissolve'
                base_duration = 0.5
        elif style == 'energetic':
            base_transition = 'wipe'
            base_duration = 0.2
        elif style == 'smooth':
            base_transition = 'crossfade'
            base_duration = 0.8
        else:
            base_transition = 'dissolve'
            base_duration = 0.5

        # Create transitions between clips
        for i in range(len(synced_clips) - 1):
            current_clip = synced_clips[i]
            next_clip = synced_clips[i + 1]

            # Transition happens at end of current clip / start of next
            transition_time = current_clip['end_time']

            # Vary transition type for visual interest
            if style == 'adaptive':
                # Mix transitions based on sync type
                if current_clip.get('sync_type') == 'onset':
                    trans_type = 'wipe'  # Punchy transition on onsets
                    trans_duration = 0.2
                elif current_clip.get('sync_type') == 'downbeat':
                    trans_type = 'dissolve'
                    trans_duration = 0.4
                else:
                    trans_type = base_transition
                    trans_duration = base_duration
            else:
                # Alternate for variety
                trans_types = ['crossfade', 'dissolve', 'wipe'] if style == 'energetic' else ['crossfade', 'dissolve']
                trans_type = trans_types[i % len(trans_types)]
                trans_duration = base_duration

            transitions.append({
                'index': i,
                'type': trans_type,
                'duration': trans_duration,
                'time': transition_time,
                'from_clip': i,
                'to_clip': i + 1
            })

        logger.info(f"  ✓ Generated {len(transitions)} transitions")

        return transitions

    def find_nearest_beat(self, target_time: float, beats: List[Dict]) -> Optional[Dict]:
        """
        Find the nearest beat to a target time

        Args:
            target_time: Target time in seconds
            beats: List of beat dicts with 'time'

        Returns:
            Nearest beat dict or None
        """
        if not beats:
            return None

        nearest_beat = min(beats, key=lambda b: abs(b['time'] - target_time))

        # Check if within tolerance
        if abs(nearest_beat['time'] - target_time) <= self.tolerance:
            return nearest_beat

        return None

    def snap_to_beat(self, time: float, beats: List[Dict], prefer_before: bool = False) -> float:
        """
        Snap a time value to the nearest beat

        Args:
            time: Time to snap
            beats: List of beats
            prefer_before: Prefer snapping to beat before rather than after

        Returns:
            Snapped time
        """
        if not beats:
            return time

        beat_times = [b['time'] for b in beats]

        if prefer_before:
            # Find largest beat time <= target time
            before_beats = [t for t in beat_times if t <= time]
            if before_beats:
                return max(before_beats)

        # Find nearest beat
        nearest = min(beat_times, key=lambda t: abs(t - time))
        return nearest
