"""Extract audio from YouTube videos and transcribe using Whisper."""

import os
import tempfile
from typing import List, Dict, Optional
import yt_dlp
import whisper
from pathlib import Path
from .ytdlp_config import get_base_ydl_opts


class AudioTranscriber:
    """Handle audio extraction and speech-to-text transcription."""

    def __init__(self, model_size: str = "base"):
        """
        Initialize the audio transcriber.

        Args:
            model_size: Whisper model size (tiny, base, small, medium, large)
                - tiny: Fastest, least accurate (~1GB RAM)
                - base: Fast, good accuracy (~1GB RAM)
                - small: Balanced (~2GB RAM)
                - medium: Slower, better accuracy (~5GB RAM)
                - large: Slowest, best accuracy (~10GB RAM)
        """
        self.model_size = model_size
        self.model = None

    def load_model(self):
        """Load Whisper model (lazy loading)."""
        if self.model is None:
            self.model = whisper.load_model(self.model_size)
        return self.model

    @staticmethod
    def download_audio(url: str, output_path: Optional[str] = None) -> str:
        """
        Download audio from YouTube video.

        Args:
            url: YouTube video URL
            output_path: Path to save audio file. If None, uses temp directory.

        Returns:
            Path to downloaded audio file
        """
        if output_path is None:
            temp_dir = tempfile.gettempdir()
            output_path = os.path.join(temp_dir, "youtube_audio.%(ext)s")

        ydl_opts = get_base_ydl_opts(
            format='bestaudio/bestaudio*/best',
            outtmpl=output_path,
            postprocessors=[{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
            quiet=True,
            no_warnings=True,
        )

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                # Get the actual output filename
                filename = ydl.prepare_filename(info)
                # Change extension to mp3
                audio_file = os.path.splitext(filename)[0] + '.mp3'
                return audio_file
        except Exception as e:
            raise Exception(f"Failed to download audio: {str(e)}")

    def transcribe_audio(
        self,
        audio_file: str,
        language: Optional[str] = None,
        task: str = "transcribe"
    ) -> Dict:
        """
        Transcribe audio file using Whisper.

        Args:
            audio_file: Path to audio file
            language: Language code (e.g., 'en', 'es'). None for auto-detect.
            task: 'transcribe' or 'translate' (translate to English)

        Returns:
            Dict with 'text', 'segments', 'language'
        """
        model = self.load_model()

        try:
            result = model.transcribe(
                audio_file,
                language=language,
                task=task,
                verbose=False
            )
            return result
        except Exception as e:
            raise Exception(f"Failed to transcribe audio: {str(e)}")

    def transcribe_youtube_video(
        self,
        url: str,
        language: Optional[str] = None,
        task: str = "transcribe",
        keep_audio: bool = False
    ) -> Dict:
        """
        Download and transcribe a YouTube video.

        Args:
            url: YouTube video URL
            language: Language code for transcription
            task: 'transcribe' or 'translate'
            keep_audio: Keep downloaded audio file

        Returns:
            Dict with transcription results and metadata
        """
        audio_file = None

        try:
            # Download audio
            audio_file = self.download_audio(url)

            # Transcribe
            result = self.transcribe_audio(audio_file, language, task)

            return {
                'text': result['text'],
                'segments': result['segments'],
                'language': result['language'],
                'audio_file': audio_file if keep_audio else None
            }

        except Exception as e:
            raise e

        finally:
            # Cleanup audio file if not keeping
            if not keep_audio and audio_file and os.path.exists(audio_file):
                try:
                    os.remove(audio_file)
                except Exception:
                    pass

    @staticmethod
    def convert_whisper_to_transcript_format(segments: List[Dict]) -> List[Dict]:
        """
        Convert Whisper segments to transcript format compatible with markdown generator.

        Args:
            segments: Whisper segments from transcription

        Returns:
            List of dicts with 'text', 'start', 'duration'
        """
        transcript = []

        for segment in segments:
            transcript.append({
                'text': segment['text'].strip(),
                'start': segment['start'],
                'duration': segment['end'] - segment['start']
            })

        return transcript

    @staticmethod
    def get_available_models() -> List[Dict[str, str]]:
        """Get list of available Whisper models with descriptions."""
        return [
            {
                'name': 'tiny',
                'description': 'Fastest, least accurate (~1GB RAM, ~32x faster)',
                'size': '~39M parameters'
            },
            {
                'name': 'base',
                'description': 'Fast, good accuracy (~1GB RAM, ~16x faster)',
                'size': '~74M parameters'
            },
            {
                'name': 'small',
                'description': 'Balanced speed/accuracy (~2GB RAM, ~6x faster)',
                'size': '~244M parameters'
            },
            {
                'name': 'medium',
                'description': 'Slower, better accuracy (~5GB RAM, ~2x faster)',
                'size': '~769M parameters'
            },
            {
                'name': 'large',
                'description': 'Best accuracy, slowest (~10GB RAM)',
                'size': '~1550M parameters'
            }
        ]
