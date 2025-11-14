import cv2
import numpy as np
from pathlib import Path

class QualityAnalyzer:
    """Analyze image and video quality using computer vision techniques"""

    def __init__(self):
        pass

    def analyze(self, file_path, file_type):
        """
        Analyze quality of an image or video
        Returns a quality score between 0 and 1
        """
        try:
            if file_type == 'image':
                return self._analyze_image(file_path)
            else:
                return self._analyze_video(file_path)
        except Exception as e:
            print(f"Quality analysis error for {file_path}: {str(e)}")
            return 0.7  # Default quality

    def _analyze_image(self, image_path):
        """Analyze image quality"""
        img = cv2.imread(image_path)
        if img is None:
            return 0.5

        scores = []

        # 1. Blur detection (Laplacian variance)
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        laplacian_var = cv2.Laplacian(gray, cv2.CV_64F).var()
        blur_score = min(laplacian_var / 500, 1.0)  # Normalize
        scores.append(blur_score)

        # 2. Brightness analysis
        brightness = np.mean(gray)
        # Optimal brightness is around 120-140
        brightness_score = 1.0 - abs(brightness - 130) / 130
        brightness_score = max(0, brightness_score)
        scores.append(brightness_score)

        # 3. Contrast analysis
        contrast = np.std(gray)
        contrast_score = min(contrast / 64, 1.0)
        scores.append(contrast_score)

        # 4. Resolution score
        pixels = img.shape[0] * img.shape[1]
        resolution_score = min(pixels / (1920 * 1080), 1.0)
        scores.append(resolution_score)

        # 5. Color distribution (avoid over/underexposed)
        hist = cv2.calcHist([gray], [0], None, [256], [0, 256])
        hist = hist.flatten() / hist.sum()

        # Check if too concentrated at extremes
        extreme_pixels = hist[0:10].sum() + hist[246:256].sum()
        exposure_score = 1.0 - min(extreme_pixels * 2, 1.0)
        scores.append(exposure_score)

        # Weighted average
        weights = [0.3, 0.2, 0.2, 0.15, 0.15]  # Blur is most important
        quality = sum(s * w for s, w in zip(scores, weights))

        return float(quality)

    def _analyze_video(self, video_path):
        """Analyze video quality by sampling frames"""
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            return 0.5

        frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        fps = cap.get(cv2.CAP_PROP_FPS)

        # Sample 5 frames evenly distributed
        sample_frames = min(5, frame_count)
        frame_indices = np.linspace(0, frame_count - 1, sample_frames, dtype=int)

        quality_scores = []

        for frame_idx in frame_indices:
            cap.set(cv2.CAP_PROP_POS_FRAMES, frame_idx)
            ret, frame = cap.read()
            if not ret:
                continue

            # Analyze frame quality
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

            # Blur detection
            laplacian_var = cv2.Laplacian(gray, cv2.CV_64F).var()
            blur_score = min(laplacian_var / 500, 1.0)

            # Brightness
            brightness = np.mean(gray)
            brightness_score = 1.0 - abs(brightness - 130) / 130
            brightness_score = max(0, brightness_score)

            # Contrast
            contrast = np.std(gray)
            contrast_score = min(contrast / 64, 1.0)

            frame_quality = (blur_score * 0.5 + brightness_score * 0.25 + contrast_score * 0.25)
            quality_scores.append(frame_quality)

        cap.release()

        if not quality_scores:
            return 0.5

        # Return average quality
        return float(np.mean(quality_scores))

    def detect_motion(self, video_path):
        """Detect amount of motion in video"""
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            return 0.5

        ret, prev_frame = cap.read()
        if not ret:
            cap.release()
            return 0.5

        prev_gray = cv2.cvtColor(prev_frame, cv2.COLOR_BGR2GRAY)
        motion_scores = []

        frame_count = 0
        max_frames = 30  # Sample first 30 frames

        while frame_count < max_frames:
            ret, frame = cap.read()
            if not ret:
                break

            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

            # Calculate frame difference
            diff = cv2.absdiff(prev_gray, gray)
            motion = np.mean(diff)
            motion_scores.append(motion)

            prev_gray = gray
            frame_count += 1

        cap.release()

        if not motion_scores:
            return 0.5

        # Normalize motion score
        avg_motion = np.mean(motion_scores)
        motion_score = min(avg_motion / 50, 1.0)

        return float(motion_score)
