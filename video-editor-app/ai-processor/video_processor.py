"""
Video Processor - Main Orchestration Module

Coordinates scene detection, music analysis, beat synchronization, and video rendering.
This is the main entry point for automated video editing.
"""

import os
import sys
import json
import logging
from pathlib import Path
from typing import Dict, List, Optional

# Add analyzers to path
sys.path.append(str(Path(__file__).parent))

from analyzers.quality import QualityAnalyzer
from analyzers.scene import SceneAnalyzer
from analyzers.content import ContentAnalyzer
from analyzers.music import MusicAnalyzer
from analyzers.beat_sync import BeatSynchronizer
from moviepy_renderer import MoviePyRenderer

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class VideoProcessor:
    """
    Main video processing orchestrator

    Coordinates all analysis and rendering steps:
    1. Analyze video files (scenes, quality, content)
    2. Analyze music (beats, onsets, energy)
    3. Synchronize clips to beats
    4. Render with professional transitions
    """

    def __init__(self, use_moviepy: bool = True):
        """
        Initialize Video Processor

        Args:
            use_moviepy: Use MoviePy for rendering (True) or FFmpeg fallback (False)
        """
        logger.info("🚀 Initializing Video Processor...")

        # Initialize analyzers
        self.quality_analyzer = QualityAnalyzer()
        self.scene_analyzer = SceneAnalyzer(use_pyscenedetect=True)
        self.content_analyzer = ContentAnalyzer()
        self.music_analyzer = MusicAnalyzer()
        self.beat_synchronizer = BeatSynchronizer(tolerance_ms=100)

        # Initialize renderer
        self.use_moviepy = use_moviepy
        if use_moviepy:
            self.renderer = MoviePyRenderer()
        else:
            self.renderer = None

        logger.info("✓ Video Processor initialized")

    def process(
        self,
        files: List[Dict],
        music: Optional[Dict] = None,
        settings: Optional[Dict] = None,
        output_path: str = 'output.mp4'
    ) -> Dict:
        """
        Process videos and create automatic montage

        Args:
            files: List of file dicts with 'path', 'mimetype', etc.
            music: Optional music file dict with 'path'
            settings: Settings dict with video preferences
            output_path: Path for output video

        Returns:
            dict: Processing result with output path and metadata
        """
        logger.info("=" * 60)
        logger.info("🎬 STARTING AUTOMATED VIDEO EDITING")
        logger.info("=" * 60)

        settings = settings or {}

        try:
            # Step 1: Analyze all files
            logger.info("\n📊 STEP 1: ANALYZING FILES")
            logger.info("-" * 60)
            files_analysis = self._analyze_files(files)

            # Step 2: Analyze music (if provided)
            music_analysis = None
            if music and music.get('path'):
                logger.info("\n🎵 STEP 2: ANALYZING MUSIC")
                logger.info("-" * 60)
                music_analysis = self.music_analyzer.analyze(music['path'])
            else:
                logger.info("\n⚠ STEP 2: NO MUSIC PROVIDED - SKIPPING")

            # Step 3: Generate edit plan
            logger.info("\n📝 STEP 3: GENERATING EDIT PLAN")
            logger.info("-" * 60)
            edit_plan = self._generate_edit_plan(
                files_analysis,
                music_analysis,
                settings
            )

            # Step 4: Render video
            logger.info("\n🎨 STEP 4: RENDERING VIDEO")
            logger.info("-" * 60)
            output_path = self._render_video(
                edit_plan,
                music.get('path') if music else None,
                output_path,
                settings
            )

            logger.info("\n" + "=" * 60)
            logger.info("✅ VIDEO PROCESSING COMPLETE")
            logger.info("=" * 60)
            logger.info(f"📹 Output: {output_path}")

            return {
                'success': True,
                'output_path': output_path,
                'files_analysis': files_analysis,
                'music_analysis': music_analysis,
                'edit_plan': edit_plan
            }

        except Exception as e:
            logger.error(f"\n❌ PROCESSING FAILED: {str(e)}")
            import traceback
            traceback.print_exc()
            raise

    def _analyze_files(self, files: List[Dict]) -> List[Dict]:
        """Analyze all input files"""
        files_analysis = []

        for i, file_info in enumerate(files, 1):
            file_path = file_info['path']
            file_type = 'image' if 'image' in file_info.get('mimetype', '') else 'video'

            logger.info(f"\n📹 File {i}/{len(files)}: {Path(file_path).name}")

            analysis = {
                'path': file_path,
                'type': file_type,
                'quality': 0.8,  # Default
                'duration': 3 if file_type == 'image' else 5
            }

            try:
                # Quality analysis
                quality_score = self.quality_analyzer.analyze(file_path, file_type)
                analysis['quality'] = quality_score
                logger.info(f"  Quality: {quality_score:.2f}")

                # Scene analysis for videos
                if file_type == 'video':
                    scene_info = self.scene_analyzer.analyze(file_path)
                    analysis.update(scene_info)
                    logger.info(f"  Scenes: {len(scene_info.get('scenes', []))}")

                # Content analysis
                content_info = self.content_analyzer.analyze(file_path, file_type)
                analysis.update(content_info)

            except Exception as e:
                logger.error(f"  ⚠ Analysis error: {str(e)}")
                # Continue with defaults

            files_analysis.append(analysis)

        return files_analysis

    def _generate_edit_plan(
        self,
        files_analysis: List[Dict],
        music_analysis: Optional[Dict],
        settings: Dict
    ) -> Dict:
        """
        Generate comprehensive edit plan with beat synchronization
        """
        logger.info("Generating edit plan...")

        # Determine target duration
        target_duration = settings.get('videoDuration', 'auto')

        if target_duration == 'auto' and music_analysis:
            target_duration = music_analysis['duration']
        elif target_duration == 'auto':
            target_duration = 60.0  # Default 1 minute
        else:
            try:
                target_duration = float(target_duration)
            except:
                target_duration = 60.0

        logger.info(f"  Target duration: {target_duration:.1f}s")

        # Prepare clips for synchronization
        clips = []
        for file_analysis in files_analysis:
            clips.append({
                'path': file_analysis['path'],
                'type': file_analysis['type'],
                'duration': file_analysis.get('duration', 3),
                'quality': file_analysis.get('quality', 0.5),
                'start_trim': 0,
                'end_trim': 0
            })

        # Synchronize clips to beats if music is available
        if music_analysis:
            logger.info("\n🎵 Synchronizing clips to music beats...")
            synced_clips = self.beat_synchronizer.sync_clips_to_beats(
                clips,
                music_analysis,
                target_duration=target_duration,
                prefer_onsets=True
            )

            # Generate transitions based on music
            transition_style = settings.get('transitionStyle', 'adaptive')
            transitions = self.beat_synchronizer.suggest_transitions(
                synced_clips,
                music_analysis,
                style=transition_style
            )

        else:
            logger.info("  No music - using even distribution")
            # Basic timing without beat sync
            synced_clips = self._distribute_clips_evenly(clips, target_duration)
            transitions = self._basic_transitions(synced_clips, settings)

        # Resolution settings
        quality_setting = settings.get('videoQuality', '1080p')
        if quality_setting == '4k':
            resolution = (3840, 2160)
        elif quality_setting == '1080p':
            resolution = (1920, 1080)
        else:
            resolution = (1280, 720)

        edit_plan = {
            'clips': synced_clips,
            'transitions': transitions,
            'target_duration': target_duration,
            'resolution': resolution,
            'fps': 30,
            'enable_stabilization': settings.get('enableStabilization', False),
            'enable_color_grading': settings.get('enableColorGrading', True)
        }

        logger.info(f"\n✓ Edit plan generated:")
        logger.info(f"  Clips: {len(synced_clips)}")
        logger.info(f"  Transitions: {len(transitions)}")
        logger.info(f"  Resolution: {resolution[0]}x{resolution[1]}")

        return edit_plan

    def _distribute_clips_evenly(self, clips: List[Dict], target_duration: float) -> List[Dict]:
        """Distribute clips evenly without beat sync"""
        time_per_clip = target_duration / len(clips) if clips else 3.0
        current_time = 0.0

        synced_clips = []
        for clip in clips:
            clip = clip.copy()
            clip['start_time'] = current_time
            clip['duration'] = min(time_per_clip, clip.get('duration', time_per_clip))
            clip['end_time'] = current_time + clip['duration']
            synced_clips.append(clip)
            current_time = clip['end_time']

        return synced_clips

    def _basic_transitions(self, clips: List[Dict], settings: Dict) -> List[Dict]:
        """Generate basic transitions without music sync"""
        transitions = []
        trans_type = 'crossfade'

        for i in range(len(clips) - 1):
            transitions.append({
                'index': i,
                'type': trans_type,
                'duration': 0.5,
                'time': clips[i]['end_time'],
                'from_clip': i,
                'to_clip': i + 1
            })

        return transitions

    def _render_video(
        self,
        edit_plan: Dict,
        music_path: Optional[str],
        output_path: str,
        settings: Dict
    ) -> str:
        """Render final video"""

        if self.use_moviepy and self.renderer and self.renderer.moviepy_available:
            logger.info("Using MoviePy renderer (professional mode)")

            output_path = self.renderer.render(
                clips_info=edit_plan['clips'],
                transitions=edit_plan['transitions'],
                output_path=output_path,
                music_path=music_path,
                resolution=tuple(edit_plan['resolution']),
                fps=edit_plan['fps'],
                enable_stabilization=edit_plan.get('enable_stabilization', False),
                enable_color_grading=edit_plan.get('enable_color_grading', True)
            )

        else:
            logger.warning("MoviePy not available - using FFmpeg fallback")
            # Use FFmpeg fallback from original implementation
            output_path = self._render_with_ffmpeg(edit_plan, music_path, output_path)

        return output_path

    def _render_with_ffmpeg(self, edit_plan: Dict, music_path: Optional[str], output_path: str) -> str:
        """FFmpeg fallback rendering (basic)"""
        import subprocess

        clips = edit_plan['clips']
        resolution = f"{edit_plan['resolution'][0]}x{edit_plan['resolution'][1]}"

        args = []

        # Input files
        for clip in clips:
            args.extend(['-i', clip['path']])

        if music_path:
            args.extend(['-i', music_path])

        # Filter complex for scaling and concatenation
        filter_complex = ''
        for i in range(len(clips)):
            filter_complex += f'[{i}:v]scale={resolution}:force_original_aspect_ratio=decrease,pad={resolution}:(ow-iw)/2:(oh-ih)/2:black[v{i}];'

        filter_complex += ''.join(f'[v{i}]' for i in range(len(clips)))
        filter_complex += f'concat=n={len(clips)}:v=1:a=0[outv]'

        args.extend(['-filter_complex', filter_complex])
        args.extend(['-map', '[outv]'])

        if music_path:
            args.extend(['-map', f'{len(clips)}:a', '-shortest'])

        args.extend([
            '-c:v', 'libx264',
            '-preset', 'medium',
            '-crf', '23',
            '-pix_fmt', 'yuv420p',
            '-y', output_path
        ])

        logger.info("Running FFmpeg...")
        subprocess.run(['ffmpeg'] + args, check=True, capture_output=True)

        return output_path


def main():
    """Main entry point for command-line usage"""
    import argparse

    parser = argparse.ArgumentParser(description='Automated Video Editor')
    parser.add_argument('--files', required=True, help='JSON string with files list')
    parser.add_argument('--music', help='Path to music file')
    parser.add_argument('--settings', help='JSON string with settings')
    parser.add_argument('--output', required=True, help='Output video path')
    parser.add_argument('--no-moviepy', action='store_true', help='Disable MoviePy rendering')

    args = parser.parse_args()

    # Parse inputs
    files = json.loads(args.files)
    music = {'path': args.music} if args.music else None
    settings = json.loads(args.settings) if args.settings else {}

    # Process
    processor = VideoProcessor(use_moviepy=not args.no_moviepy)
    result = processor.process(files, music, settings, args.output)

    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
