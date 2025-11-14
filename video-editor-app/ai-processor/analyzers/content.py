import cv2
import numpy as np

class ContentAnalyzer:
    """Analyze content of images and videos (faces, objects, composition)"""

    def __init__(self):
        # Load pre-trained face detector
        try:
            self.face_cascade = cv2.CascadeClassifier(
                cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
            )
        except:
            self.face_cascade = None
            print("Warning: Face detection not available")

    def analyze(self, file_path, file_type):
        """
        Analyze content of image or video
        Returns dict with faces, composition, colors, etc.
        """
        try:
            if file_type == 'image':
                return self._analyze_image(file_path)
            else:
                return self._analyze_video(file_path)
        except Exception as e:
            print(f"Content analysis error for {file_path}: {str(e)}")
            return {}

    def _analyze_image(self, image_path):
        """Analyze image content"""
        img = cv2.imread(image_path)
        if img is None:
            return {}

        result = {}

        # Face detection
        if self.face_cascade is not None:
            result['faces'] = self._detect_faces(img)
            result['hasFaces'] = len(result['faces']) > 0

        # Composition analysis
        result['composition'] = self._analyze_composition(img)

        # Color analysis
        result['dominantColors'] = self._analyze_colors(img)

        # Interest points
        result['interestScore'] = self._calculate_interest_score(img)

        return result

    def _analyze_video(self, video_path):
        """Analyze video content by sampling frames"""
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            return {}

        # Sample middle frame
        frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        cap.set(cv2.CAP_PROP_POS_FRAMES, frame_count // 2)

        ret, frame = cap.read()
        cap.release()

        if not ret:
            return {}

        # Analyze the sampled frame
        result = {}

        if self.face_cascade is not None:
            result['faces'] = self._detect_faces(frame)
            result['hasFaces'] = len(result['faces']) > 0

        result['composition'] = self._analyze_composition(frame)
        result['dominantColors'] = self._analyze_colors(frame)
        result['interestScore'] = self._calculate_interest_score(frame)

        return result

    def _detect_faces(self, img):
        """Detect faces in image"""
        if self.face_cascade is None:
            return []

        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        faces = self.face_cascade.detectMultiScale(
            gray,
            scaleFactor=1.1,
            minNeighbors=5,
            minSize=(30, 30)
        )

        face_list = []
        height, width = img.shape[:2]

        for (x, y, w, h) in faces:
            face_list.append({
                'x': float(x / width),
                'y': float(y / height),
                'width': float(w / width),
                'height': float(h / height),
                'confidence': 0.8  # Haar cascades don't provide confidence
            })

        return face_list

    def _analyze_composition(self, img):
        """Analyze image composition (rule of thirds, etc.)"""
        height, width = img.shape[:2]

        # Convert to grayscale for analysis
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        # Detect edges
        edges = cv2.Canny(gray, 100, 200)

        # Divide into rule of thirds grid
        h_third = height // 3
        w_third = width // 3

        # Calculate edge density in each section
        sections = []
        for i in range(3):
            for j in range(3):
                section = edges[i*h_third:(i+1)*h_third, j*w_third:(j+1)*w_third]
                density = np.sum(section > 0) / section.size
                sections.append(density)

        # Interest points often lie on thirds intersections
        # Higher density in corners/thirds = better composition
        thirds_score = sum([sections[0], sections[2], sections[6], sections[8]]) / 4
        center_score = sections[4]

        # Balance score (center vs edges)
        balance_score = 1.0 - abs(center_score - thirds_score)

        return {
            'thirdsDensity': float(thirds_score),
            'centerDensity': float(center_score),
            'balanceScore': float(balance_score),
            'compositionScore': float((thirds_score * 0.6 + balance_score * 0.4))
        }

    def _analyze_colors(self, img):
        """Extract dominant colors from image"""
        # Resize for faster processing
        small_img = cv2.resize(img, (150, 150))

        # Reshape to list of pixels
        pixels = small_img.reshape(-1, 3)

        # Convert to float
        pixels = np.float32(pixels)

        # K-means clustering to find dominant colors
        criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 200, 0.2)
        k = 5
        _, labels, centers = cv2.kmeans(pixels, k, None, criteria, 10, cv2.KMEANS_RANDOM_CENTERS)

        # Count pixels in each cluster
        counts = np.bincount(labels.flatten())

        # Sort by frequency
        dominant_colors = []
        for i in np.argsort(counts)[::-1]:
            color = centers[i].astype(int)
            percentage = float(counts[i] / len(labels))
            dominant_colors.append({
                'color': [int(color[2]), int(color[1]), int(color[0])],  # BGR to RGB
                'percentage': percentage
            })

        return dominant_colors

    def _calculate_interest_score(self, img):
        """Calculate overall interest score of image"""
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        # Edge density (more edges = more interesting)
        edges = cv2.Canny(gray, 100, 200)
        edge_density = np.sum(edges > 0) / edges.size

        # Color variety (more variety = more interesting)
        hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
        hist = cv2.calcHist([hsv], [0], None, [180], [0, 180])
        color_variety = np.count_nonzero(hist) / 180

        # Contrast
        contrast = np.std(gray) / 128

        # Combine scores
        interest_score = (
            edge_density * 0.4 +
            color_variety * 0.3 +
            contrast * 0.3
        )

        return float(min(interest_score, 1.0))

    def detect_text(self, img):
        """Detect presence of text in image (simplified)"""
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        # Use edge detection and morphology to detect text-like regions
        edges = cv2.Canny(gray, 50, 150)

        # Dilate to connect text components
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 5))
        dilated = cv2.dilate(edges, kernel, iterations=1)

        # Find contours
        contours, _ = cv2.findContours(dilated, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        # Count rectangular contours (likely text)
        text_regions = 0
        for contour in contours:
            x, y, w, h = cv2.boundingRect(contour)
            aspect_ratio = w / h if h > 0 else 0
            if 0.2 < aspect_ratio < 10 and w > 10 and h > 10:
                text_regions += 1

        return {
            'hasText': text_regions > 5,
            'textRegions': text_regions
        }
