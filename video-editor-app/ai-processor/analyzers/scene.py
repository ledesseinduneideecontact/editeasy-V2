import cv2
import numpy as np
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SceneAnalyzer:
    """Detect scene changes and interesting moments in videos using PySceneDetect"""

    def __init__(self, threshold=30.0, use_pyscenedetect=True):
        """
        Initialize SceneAnalyzer

        Args:
            threshold: Threshold for histogram-based detection (fallback method)
            use_pyscenedetect: Use PySceneDetect for superior scene detection
        """
        self.threshold = threshold
        self.use_pyscenedetect = use_pyscenedetect

        # Try to import scenedetect
        try:
            from scenedetect import detect, ContentDetector, AdaptiveDetector, ThresholdDetector
            self.scenedetect_available = True
            logger.info("✓ PySceneDetect available - using advanced scene detection")
        except ImportError:
            self.scenedetect_available = False
            logger.warning("⚠ PySceneDetect not available - using fallback histogram method")
            logger.warning("  Install with: pip install scenedetect[opencv]")

    def analyze(self, video_path):
        """
        Analyze video for scene changes and optimal cut points
        Returns dict with duration, scenes, and suggested cuts

        Args:
            video_path: Path to video file

        Returns:
            dict: {
                'duration': float,
                'scenes': list of scene dicts,
                'suggestedCuts': list of cut suggestions,
                'method': detection method used
            }
        """
        logger.info(f"🎬 Analyzing video: {Path(video_path).name}")

        # Get video duration first
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            logger.error(f"❌ Cannot open video: {video_path}")
            return {'duration': 5, 'scenes': [], 'suggestedCuts': [], 'method': 'none'}

        fps = cap.get(cv2.CAP_PROP_FPS)
        frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        duration = frame_count / fps if fps > 0 else 5
        cap.release()

        logger.info(f"  Duration: {duration:.2f}s, FPS: {fps:.2f}, Frames: {frame_count}")

        # Detect scene changes using best available method
        if self.use_pyscenedetect and self.scenedetect_available:
            scenes = self._detect_scenes_pyscenedetect(video_path, duration)
            method = 'pyscenedetect'
        else:
            cap = cv2.VideoCapture(video_path)
            scenes = self._detect_scenes_histogram(cap, fps)
            cap.release()
            method = 'histogram'

        logger.info(f"  Detected {len(scenes)} scenes using {method} method")

        # Suggest cut points based on scenes
        suggested_cuts = self._suggest_cuts(scenes, duration)

        logger.info(f"  Suggested {len(suggested_cuts)} cut points")

        return {
            'duration': float(duration),
            'scenes': scenes,
            'suggestedCuts': suggested_cuts,
            'method': method
        }

    def _detect_scenes_pyscenedetect(self, video_path, duration):
        """
        Detect scenes using PySceneDetect - superior algorithm
        Uses ContentDetector for fast cuts and AdaptiveDetector for gradual transitions
        """
        from scenedetect import detect, ContentDetector, AdaptiveDetector

        try:
            logger.info("  🔍 Running PySceneDetect ContentDetector...")

            # Use ContentDetector for fast cuts (threshold=27 is good default)
            scene_list = detect(video_path, ContentDetector(threshold=27.0))

            scenes = []
            for i, (start_time, end_time) in enumerate(scene_list):
                start = start_time.get_seconds()
                end = end_time.get_seconds()
                scene_duration = end - start

                # Filter out very short scenes (< 0.5s)
                if scene_duration >= 0.5:
                    scenes.append({
                        'start': float(start),
                        'end': float(end),
                        'duration': float(scene_duration),
                        'index': i,
                        'quality_score': self._estimate_scene_quality(scene_duration)
                    })

            logger.info(f"  ✓ Detected {len(scenes)} high-quality scenes")

            # If very few scenes detected, try AdaptiveDetector for gradual transitions
            if len(scenes) < 3 and duration > 10:
                logger.info("  🔍 Running AdaptiveDetector for gradual transitions...")
                scene_list_adaptive = detect(video_path, AdaptiveDetector())

                for start_time, end_time in scene_list_adaptive:
                    start = start_time.get_seconds()
                    end = end_time.get_seconds()
                    scene_duration = end - start

                    # Check if not already detected
                    is_new = all(abs(s['start'] - start) > 1.0 for s in scenes)

                    if scene_duration >= 0.5 and is_new:
                        scenes.append({
                            'start': float(start),
                            'end': float(end),
                            'duration': float(scene_duration),
                            'index': len(scenes),
                            'quality_score': self._estimate_scene_quality(scene_duration),
                            'type': 'gradual'
                        })

                # Re-sort by start time
                scenes.sort(key=lambda x: x['start'])

                logger.info(f"  ✓ Total scenes after adaptive detection: {len(scenes)}")

            return scenes

        except Exception as e:
            logger.error(f"  ❌ PySceneDetect error: {str(e)}")
            logger.info("  Falling back to histogram method")
            cap = cv2.VideoCapture(video_path)
            fps = cap.get(cv2.CAP_PROP_FPS)
            scenes = self._detect_scenes_histogram(cap, fps)
            cap.release()
            return scenes

    def _estimate_scene_quality(self, duration):
        """
        Estimate scene quality based on duration
        Longer scenes (up to a point) are generally better
        """
        # Optimal scene duration is 2-5 seconds
        if 2.0 <= duration <= 5.0:
            return 1.0
        elif 1.0 <= duration < 2.0:
            return 0.8
        elif 5.0 < duration <= 8.0:
            return 0.9
        elif duration < 1.0:
            return 0.5
        else:
            return 0.7

    def _detect_scenes_histogram(self, cap, fps):
        """Detect scene changes using histogram comparison (fallback method)"""
        scenes = []
        prev_hist = None
        frame_idx = 0
        scene_start = 0

        # Sample every 5 frames for efficiency
        sample_rate = 5

        while True:
            ret, frame = cap.read()
            if not ret:
                break

            if frame_idx % sample_rate != 0:
                frame_idx += 1
                continue

            # Calculate histogram
            hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
            hist = cv2.calcHist([hsv], [0, 1], None, [50, 60], [0, 180, 0, 256])
            hist = cv2.normalize(hist, hist).flatten()

            if prev_hist is not None:
                # Compare histograms
                diff = cv2.compareHist(prev_hist, hist, cv2.HISTCMP_BHATTACHARYYA)
                diff_percent = diff * 100

                # Scene change detected
                if diff_percent > self.threshold:
                    timestamp = frame_idx / fps
                    scene_duration = timestamp - scene_start

                    if scene_duration > 1.0:  # Minimum scene duration
                        scenes.append({
                            'start': float(scene_start),
                            'end': float(timestamp),
                            'duration': float(scene_duration)
                        })
                        scene_start = timestamp

            prev_hist = hist
            frame_idx += 1

        # Add final scene
        if cap.get(cv2.CAP_PROP_POS_FRAMES) > 0:
            final_timestamp = frame_idx / fps
            if final_timestamp - scene_start > 1.0:
                scenes.append({
                    'start': float(scene_start),
                    'end': float(final_timestamp),
                    'duration': float(final_timestamp - scene_start)
                })

        return scenes

    def _suggest_cuts(self, scenes, duration):
        """
        Suggest optimal cut points based on scene analysis
        Uses quality scores to identify best scenes to keep
        """
        if not scenes:
            logger.info("  No scenes detected")
            if duration > 10:
                return [
                    {'time': 1.0, 'reason': 'start_trim', 'confidence': 0.8},
                    {'time': duration - 1.0, 'reason': 'end_trim', 'confidence': 0.8}
                ]
            return []

        cuts = []

        # Score scenes based on quality_score (if available) or duration
        scene_scores = []
        for scene in scenes:
            # Use quality_score if available, otherwise estimate from duration
            if 'quality_score' in scene:
                score = scene['quality_score']
            else:
                score = self._estimate_scene_quality(scene['duration'])
                scene['quality_score'] = score

            scene_scores.append((score, scene))

        scene_scores.sort(reverse=True)

        # Log scene quality distribution
        avg_quality = sum(s[0] for s in scene_scores) / len(scene_scores)
        logger.info(f"  Average scene quality: {avg_quality:.2f}")

        # Identify poor quality scenes to potentially cut
        poor_scenes = [s for s in scene_scores if s[0] < 0.6]

        if poor_scenes and duration > 15:
            logger.info(f"  Found {len(poor_scenes)} low-quality scenes")
            for score, scene in poor_scenes[:3]:  # Limit to worst 3
                cuts.append({
                    'time': float(scene['start']),
                    'duration': float(scene['duration']),
                    'reason': 'low_quality_scene',
                    'quality_score': float(score),
                    'confidence': 0.7
                })

        # Suggest trimming very short scenes at start/end
        if scenes[0]['duration'] < 1.0:
            cuts.append({
                'time': 0.0,
                'duration': float(scenes[0]['duration']),
                'reason': 'short_intro',
                'confidence': 0.6
            })

        if scenes[-1]['duration'] < 1.0:
            cuts.append({
                'time': float(scenes[-1]['start']),
                'duration': float(scenes[-1]['duration']),
                'reason': 'short_outro',
                'confidence': 0.6
            })

        return cuts

    def detect_motion_intensity(self, video_path):
        """Detect motion intensity throughout video"""
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            return []

        fps = cap.get(cv2.CAP_PROP_FPS)
        ret, prev_frame = cap.read()
        if not ret:
            cap.release()
            return []

        prev_gray = cv2.cvtColor(prev_frame, cv2.COLOR_BGR2GRAY)
        motion_data = []
        frame_idx = 1

        while True:
            ret, frame = cap.read()
            if not ret:
                break

            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

            # Calculate optical flow
            flow = cv2.calcOpticalFlowFarneback(
                prev_gray, gray, None, 0.5, 3, 15, 3, 5, 1.2, 0
            )

            # Calculate motion magnitude
            magnitude = np.sqrt(flow[..., 0]**2 + flow[..., 1]**2)
            motion_intensity = np.mean(magnitude)

            timestamp = frame_idx / fps
            motion_data.append({
                'time': float(timestamp),
                'intensity': float(motion_intensity)
            })

            prev_gray = gray
            frame_idx += 1

            # Limit analysis to first 100 frames for efficiency
            if frame_idx > 100:
                break

        cap.release()
        return motion_data
