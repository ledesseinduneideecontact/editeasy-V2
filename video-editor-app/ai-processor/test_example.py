"""
Example Test Script for AI Video Processor

This script demonstrates how to use the video processor
with different configurations.
"""

import os
import sys
import time
from pathlib import Path

# Add to path
sys.path.append(str(Path(__file__).parent))

from video_processor import VideoProcessor


def test_basic_processing():
    """Test basic video processing without music"""
    print("=" * 60)
    print("TEST 1: Basic Processing (No Music)")
    print("=" * 60)

    processor = VideoProcessor(use_moviepy=True)

    # Example with placeholder paths - replace with real files
    files = [
        {'path': 'video1.mp4', 'mimetype': 'video/mp4'},
        {'path': 'video2.mp4', 'mimetype': 'video/mp4'},
    ]

    settings = {
        'videoDuration': 30,
        'videoQuality': '1080p',
        'transitionStyle': 'smooth',
        'enableColorGrading': True
    }

    try:
        start_time = time.time()

        result = processor.process(
            files=files,
            music=None,
            settings=settings,
            output_path='output_basic.mp4'
        )

        duration = time.time() - start_time

        print(f"\n✅ SUCCESS in {duration:.2f}s")
        print(f"Output: {result['output_path']}")
        print(f"Clips: {len(result['edit_plan']['clips'])}")
        print(f"Transitions: {len(result['edit_plan']['transitions'])}")

    except FileNotFoundError as e:
        print(f"\n⚠️  File not found: {e}")
        print("Please update the file paths in this test script")
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()


def test_music_sync():
    """Test video processing with music synchronization"""
    print("\n" + "=" * 60)
    print("TEST 2: Music Synchronization")
    print("=" * 60)

    processor = VideoProcessor(use_moviepy=True)

    # Example with placeholder paths - replace with real files
    files = [
        {'path': 'video1.mp4', 'mimetype': 'video/mp4'},
        {'path': 'video2.mp4', 'mimetype': 'video/mp4'},
        {'path': 'video3.mp4', 'mimetype': 'video/mp4'},
    ]

    music = {'path': 'music.mp3'}

    settings = {
        'videoDuration': 'auto',  # Match music length
        'videoQuality': '1080p',
        'transitionStyle': 'adaptive',  # Music-based transitions
        'enableColorGrading': True
    }

    try:
        start_time = time.time()

        result = processor.process(
            files=files,
            music=music,
            settings=settings,
            output_path='output_music_sync.mp4'
        )

        duration = time.time() - start_time

        print(f"\n✅ SUCCESS in {duration:.2f}s")
        print(f"Output: {result['output_path']}")
        print(f"Music BPM: {result['music_analysis']['bpm']:.1f}")
        print(f"Beats detected: {len(result['music_analysis']['beats'])}")
        print(f"Onsets detected: {len(result['music_analysis']['onsets'])}")
        print(f"Clips: {len(result['edit_plan']['clips'])}")
        print(f"Transitions: {len(result['edit_plan']['transitions'])}")

    except FileNotFoundError as e:
        print(f"\n⚠️  File not found: {e}")
        print("Please update the file paths in this test script")
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()


def test_energetic_style():
    """Test energetic video style"""
    print("\n" + "=" * 60)
    print("TEST 3: Energetic Style (Fast Transitions)")
    print("=" * 60)

    processor = VideoProcessor(use_moviepy=True)

    files = [
        {'path': 'video1.mp4', 'mimetype': 'video/mp4'},
        {'path': 'video2.mp4', 'mimetype': 'video/mp4'},
        {'path': 'video3.mp4', 'mimetype': 'video/mp4'},
        {'path': 'video4.mp4', 'mimetype': 'video/mp4'},
    ]

    music = {'path': 'energetic_music.mp3'}

    settings = {
        'videoDuration': 45,
        'videoQuality': '1080p',
        'transitionStyle': 'energetic',  # Fast, punchy transitions
        'enableColorGrading': True
    }

    try:
        start_time = time.time()

        result = processor.process(
            files=files,
            music=music,
            settings=settings,
            output_path='output_energetic.mp4'
        )

        duration = time.time() - start_time

        print(f"\n✅ SUCCESS in {duration:.2f}s")
        print(f"Output: {result['output_path']}")

    except FileNotFoundError as e:
        print(f"\n⚠️  File not found: {e}")
        print("Please update the file paths in this test script")
    except Exception as e:
        print(f"\n❌ ERROR: {e}")


def test_analysis_only():
    """Test file analysis without rendering"""
    print("\n" + "=" * 60)
    print("TEST 4: Analysis Only")
    print("=" * 60)

    from analyzers.scene import SceneAnalyzer
    from analyzers.music import MusicAnalyzer

    scene_analyzer = SceneAnalyzer(use_pyscenedetect=True)
    music_analyzer = MusicAnalyzer()

    # Analyze a video
    try:
        print("\nAnalyzing video...")
        video_analysis = scene_analyzer.analyze('video1.mp4')
        print(f"✓ Scenes detected: {len(video_analysis.get('scenes', []))}")
        print(f"  Method: {video_analysis.get('method')}")
        print(f"  Duration: {video_analysis.get('duration'):.2f}s")
    except FileNotFoundError:
        print("⚠️  Video file not found")
    except Exception as e:
        print(f"❌ Error: {e}")

    # Analyze music
    try:
        print("\nAnalyzing music...")
        music_analysis = music_analyzer.analyze('music.mp3')
        print(f"✓ BPM: {music_analysis.get('bpm'):.1f}")
        print(f"  Beats: {len(music_analysis.get('beats', []))}")
        print(f"  Onsets: {len(music_analysis.get('onsets', []))}")
        print(f"  Mood: {music_analysis.get('mood')}")
        print(f"  Energy: {music_analysis.get('energy'):.2f}")
    except FileNotFoundError:
        print("⚠️  Music file not found")
    except Exception as e:
        print(f"❌ Error: {e}")


def print_instructions():
    """Print usage instructions"""
    print("\n" + "=" * 60)
    print("USAGE INSTRUCTIONS")
    print("=" * 60)
    print("""
This test script demonstrates the AI Video Processor capabilities.

BEFORE RUNNING:
1. Update file paths in each test function
2. Ensure you have sample video and audio files
3. Install all dependencies: pip install -r requirements.txt

TO RUN SPECIFIC TESTS:
- Uncomment the desired test function at the bottom of this file
- Or run: python test_example.py

SAMPLE FILE STRUCTURE:
/path/to/test/
  ├── video1.mp4
  ├── video2.mp4
  ├── video3.mp4
  └── music.mp3

For real usage examples, see INSTALL.md
    """)


if __name__ == '__main__':
    print_instructions()

    # Uncomment to run tests (after updating file paths!)

    # test_analysis_only()
    # test_basic_processing()
    # test_music_sync()
    # test_energetic_style()

    print("\n" + "=" * 60)
    print("To run tests, uncomment the test functions above")
    print("and update the file paths first!")
    print("=" * 60)
