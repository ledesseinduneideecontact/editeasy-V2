from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import sys
import logging
from pathlib import Path

# Add analyzers to path
sys.path.append(str(Path(__file__).parent))

from analyzers.quality import QualityAnalyzer
from analyzers.scene import SceneAnalyzer
from analyzers.content import ContentAnalyzer
from analyzers.music import MusicAnalyzer
from video_processor import VideoProcessor

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

# Initialize analyzers (for backward compatibility)
quality_analyzer = QualityAnalyzer()
scene_analyzer = SceneAnalyzer(use_pyscenedetect=True)
content_analyzer = ContentAnalyzer()
music_analyzer = MusicAnalyzer()

# Initialize video processor (new)
video_processor = VideoProcessor(use_moviepy=True)

@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'healthy'})

@app.route('/analyze', methods=['POST'])
def analyze():
    try:
        data = request.json
        files = data.get('files', [])
        music = data.get('music')
        settings = data.get('settings', {})

        print(f"Analyzing {len(files)} files...")

        # Analyze each file
        files_analysis = []
        for file_info in files:
            file_path = file_info['path']
            file_type = 'image' if 'image' in file_info['mimetype'] else 'video'

            print(f"Analyzing: {file_path}")

            analysis = {
                'path': file_path,
                'type': file_type,
                'quality': 0.8,  # Default
                'duration': 3 if file_type == 'image' else 5
            }

            try:
                # Quality analysis
                quality_score = quality_analyzer.analyze(file_path, file_type)
                analysis['quality'] = quality_score

                # Scene analysis for videos
                if file_type == 'video':
                    scene_info = scene_analyzer.analyze(file_path)
                    analysis.update(scene_info)

                # Content analysis
                content_info = content_analyzer.analyze(file_path, file_type)
                analysis.update(content_info)

            except Exception as e:
                print(f"Error analyzing {file_path}: {str(e)}")
                # Continue with defaults

            files_analysis.append(analysis)

        # Analyze music if provided
        music_analysis = None
        if music:
            try:
                print(f"Analyzing music: {music['path']}")
                music_analysis = music_analyzer.analyze(music['path'])
            except Exception as e:
                print(f"Error analyzing music: {str(e)}")

        result = {
            'filesAnalysis': files_analysis,
            'musicAnalysis': music_analysis
        }

        print("Analysis complete!")
        return jsonify(result)

    except Exception as e:
        print(f"Analysis error: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/process_video', methods=['POST'])
def process_video():
    """
    Complete video processing with beat sync and MoviePy rendering

    Expects JSON:
    {
        "files": [...],
        "music": {...},
        "settings": {...},
        "outputPath": "..."
    }
    """
    try:
        data = request.json
        files = data.get('files', [])
        music = data.get('music')
        settings = data.get('settings', {})
        output_path = data.get('outputPath', '/tmp/output.mp4')

        logger.info(f"🎬 Processing video with {len(files)} files")

        # Process video with full pipeline
        result = video_processor.process(
            files=files,
            music=music,
            settings=settings,
            output_path=output_path
        )

        logger.info(f"✓ Video processing complete: {result['output_path']}")

        return jsonify({
            'success': True,
            'outputPath': result['output_path'],
            'filesAnalysis': result['files_analysis'],
            'musicAnalysis': result['music_analysis'],
            'editPlan': {
                'clips': len(result['edit_plan']['clips']),
                'transitions': len(result['edit_plan']['transitions']),
                'duration': result['edit_plan']['target_duration']
            }
        })

    except Exception as e:
        logger.error(f"Video processing error: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    logger.info(f"🤖 AI Processor starting on port {port}...")
    logger.info("📍 Available endpoints:")
    logger.info("  - GET  /health          : Health check")
    logger.info("  - POST /analyze         : Analyze files only")
    logger.info("  - POST /process_video   : Full video processing (NEW)")
    app.run(host='0.0.0.0', port=port, debug=True)
