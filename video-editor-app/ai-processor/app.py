from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import sys
from pathlib import Path

# Add analyzers to path
sys.path.append(str(Path(__file__).parent))

from analyzers.quality import QualityAnalyzer
from analyzers.scene import SceneAnalyzer
from analyzers.content import ContentAnalyzer
from analyzers.music import MusicAnalyzer

app = Flask(__name__)
CORS(app)

# Initialize analyzers
quality_analyzer = QualityAnalyzer()
scene_analyzer = SceneAnalyzer()
content_analyzer = ContentAnalyzer()
music_analyzer = MusicAnalyzer()

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

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    print(f"🤖 AI Processor starting on port {port}...")
    app.run(host='0.0.0.0', port=port, debug=True)
