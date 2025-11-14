#!/usr/bin/env python3
"""
Test script for AI analyzers
Usage: python test_analyzers.py <path_to_image_or_video>
"""

import sys
import os
from pathlib import Path
import json

# Add parent directory to path
sys.path.append(str(Path(__file__).parent))

from analyzers.quality import QualityAnalyzer
from analyzers.scene import SceneAnalyzer
from analyzers.content import ContentAnalyzer
from analyzers.music import MusicAnalyzer

def test_image(file_path):
    """Test analyzers on an image"""
    print(f"\n{'='*60}")
    print(f"Testing IMAGE: {file_path}")
    print('='*60)

    # Quality analysis
    print("\n📊 Quality Analysis:")
    quality_analyzer = QualityAnalyzer()
    quality = quality_analyzer.analyze(file_path, 'image')
    print(f"  Quality Score: {quality:.2f}")

    # Content analysis
    print("\n🎨 Content Analysis:")
    content_analyzer = ContentAnalyzer()
    content = content_analyzer.analyze(file_path, 'image')
    print(f"  Has Faces: {content.get('hasFaces', False)}")
    print(f"  Number of Faces: {len(content.get('faces', []))}")
    print(f"  Interest Score: {content.get('interestScore', 0):.2f}")

    if 'composition' in content:
        print(f"  Composition Score: {content['composition'].get('compositionScore', 0):.2f}")

    if 'dominantColors' in content:
        print(f"  Dominant Colors: {len(content['dominantColors'])} colors detected")

    print("\n✅ Image analysis complete!")
    return {'quality': quality, 'content': content}

def test_video(file_path):
    """Test analyzers on a video"""
    print(f"\n{'='*60}")
    print(f"Testing VIDEO: {file_path}")
    print('='*60)

    # Quality analysis
    print("\n📊 Quality Analysis:")
    quality_analyzer = QualityAnalyzer()
    quality = quality_analyzer.analyze(file_path, 'video')
    print(f"  Quality Score: {quality:.2f}")

    motion = quality_analyzer.detect_motion(file_path)
    print(f"  Motion Score: {motion:.2f}")

    # Scene analysis
    print("\n🎬 Scene Analysis:")
    scene_analyzer = SceneAnalyzer()
    scene_data = scene_analyzer.analyze(file_path)
    print(f"  Duration: {scene_data['duration']:.2f}s")
    print(f"  Scenes Detected: {len(scene_data['scenes'])}")

    for i, scene in enumerate(scene_data['scenes'][:5]):
        print(f"    Scene {i+1}: {scene['start']:.2f}s - {scene['end']:.2f}s ({scene['duration']:.2f}s)")

    if scene_data['suggestedCuts']:
        print(f"  Suggested Cuts: {len(scene_data['suggestedCuts'])}")

    # Content analysis
    print("\n🎨 Content Analysis:")
    content_analyzer = ContentAnalyzer()
    content = content_analyzer.analyze(file_path, 'video')
    print(f"  Has Faces: {content.get('hasFaces', False)}")
    print(f"  Number of Faces: {len(content.get('faces', []))}")
    print(f"  Interest Score: {content.get('interestScore', 0):.2f}")

    print("\n✅ Video analysis complete!")
    return {'quality': quality, 'motion': motion, 'scenes': scene_data, 'content': content}

def test_audio(file_path):
    """Test music analyzer on an audio file"""
    print(f"\n{'='*60}")
    print(f"Testing AUDIO: {file_path}")
    print('='*60)

    print("\n🎵 Music Analysis:")
    music_analyzer = MusicAnalyzer()
    music_data = music_analyzer.analyze(file_path)

    print(f"  Duration: {music_data['duration']:.2f}s")
    print(f"  BPM: {music_data['bpm']:.1f}")
    print(f"  Energy: {music_data.get('energy', 0):.2f}")
    print(f"  Mood: {music_data.get('mood', 'unknown')}")
    print(f"  Beats Detected: {len(music_data.get('beats', []))}")

    if music_data.get('beats'):
        first_beats = music_data['beats'][:10]
        print(f"  First beats at: {[f\"{b['time']:.2f}s\" for b in first_beats]}")

    print("\n✅ Audio analysis complete!")
    return music_data

def main():
    if len(sys.argv) < 2:
        print("Usage: python test_analyzers.py <path_to_file>")
        print("\nExamples:")
        print("  python test_analyzers.py /path/to/image.jpg")
        print("  python test_analyzers.py /path/to/video.mp4")
        print("  python test_analyzers.py /path/to/music.mp3")
        sys.exit(1)

    file_path = sys.argv[1]

    if not os.path.exists(file_path):
        print(f"❌ File not found: {file_path}")
        sys.exit(1)

    # Detect file type
    ext = Path(file_path).suffix.lower()

    try:
        if ext in ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp']:
            result = test_image(file_path)
        elif ext in ['.mp4', '.mov', '.avi', '.mkv', '.webm', '.flv']:
            result = test_video(file_path)
        elif ext in ['.mp3', '.wav', '.ogg', '.m4a', '.flac']:
            result = test_audio(file_path)
        else:
            print(f"❌ Unsupported file type: {ext}")
            sys.exit(1)

        # Save results to JSON
        output_file = f"test_results_{Path(file_path).stem}.json"
        with open(output_file, 'w') as f:
            json.dump(result, f, indent=2, default=str)

        print(f"\n💾 Results saved to: {output_file}")

    except Exception as e:
        print(f"\n❌ Error during analysis: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == '__main__':
    main()
