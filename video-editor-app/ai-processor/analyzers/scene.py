import cv2
import numpy as np

class SceneAnalyzer:
    """Detect scene changes and interesting moments in videos"""

    def __init__(self, threshold=30.0):
        self.threshold = threshold

    def analyze(self, video_path):
        """
        Analyze video for scene changes and optimal cut points
        Returns dict with duration, scenes, and suggested cuts
        """
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            return {'duration': 5, 'scenes': [], 'suggestedCuts': []}

        fps = cap.get(cv2.CAP_PROP_FPS)
        frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        duration = frame_count / fps if fps > 0 else 5

        # Detect scene changes
        scenes = self._detect_scenes(cap, fps)

        # Suggest cut points based on scenes
        suggested_cuts = self._suggest_cuts(scenes, duration)

        cap.release()

        return {
            'duration': float(duration),
            'scenes': scenes,
            'suggestedCuts': suggested_cuts
        }

    def _detect_scenes(self, cap, fps):
        """Detect scene changes using histogram comparison"""
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
        """Suggest optimal cut points based on scene analysis"""
        if not scenes:
            # No scenes detected, suggest cuts based on duration
            if duration > 10:
                return [
                    {'time': 1.0, 'reason': 'start_trim'},
                    {'time': duration - 1.0, 'reason': 'end_trim'}
                ]
            return []

        cuts = []

        # Suggest keeping best scenes (longer = better usually)
        scene_scores = []
        for scene in scenes:
            score = scene['duration']  # Simple scoring
            scene_scores.append((score, scene))

        scene_scores.sort(reverse=True)

        # If video is too long, suggest trimming worst scenes
        if duration > 15 and len(scenes) > 3:
            worst_scenes = scene_scores[-2:]  # Keep worst 2 scenes
            for _, scene in worst_scenes:
                cuts.append({
                    'time': float(scene['start']),
                    'duration': float(scene['duration']),
                    'reason': 'low_quality_scene'
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
