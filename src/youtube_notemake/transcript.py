"""Extract and process YouTube video transcripts."""

from typing import List, Dict, Optional, Tuple
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api._errors import TranscriptsDisabled, NoTranscriptFound


class TranscriptExtractor:
    """Extract transcripts from YouTube videos."""

    @staticmethod
    def get_available_transcripts(video_id: str) -> Tuple[List[Dict[str, str]], bool]:
        """
        Get list of available transcript languages.

        Returns:
            Tuple of (list of transcripts, has_transcripts_available)
        """
        try:
            transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
            available = []

            for transcript in transcript_list:
                available.append({
                    'language': transcript.language,
                    'language_code': transcript.language_code,
                    'is_generated': transcript.is_generated,
                })

            return available, True
        except Exception:
            return [], False

    @staticmethod
    def get_transcript(
        video_id: str,
        language: Optional[str] = None,
        preserve_formatting: bool = True
    ) -> List[Dict[str, any]]:
        """
        Fetch transcript for a video.

        Args:
            video_id: YouTube video ID
            language: Language code (e.g., 'en', 'es'). If None, gets default.
            preserve_formatting: Keep original formatting

        Returns:
            List of transcript segments with 'text', 'start', 'duration'
        """
        try:
            if language:
                transcript = YouTubeTranscriptApi.get_transcript(
                    video_id,
                    languages=[language],
                    preserve_formatting=preserve_formatting
                )
            else:
                transcript = YouTubeTranscriptApi.get_transcript(
                    video_id,
                    preserve_formatting=preserve_formatting
                )

            return transcript

        except TranscriptsDisabled:
            raise Exception("Subtitles are disabled for this video")
        except NoTranscriptFound:
            raise Exception(f"No transcript found for language: {language or 'default'}")
        except Exception as e:
            raise Exception(f"Failed to fetch transcript: {str(e)}")

    @staticmethod
    def format_timestamp(seconds: float, include_hours: bool = True) -> str:
        """Convert seconds to timestamp format (HH:MM:SS or MM:SS)."""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)

        if include_hours or hours > 0:
            return f"{hours:02d}:{minutes:02d}:{secs:02d}"
        return f"{minutes:02d}:{secs:02d}"

    @staticmethod
    def create_youtube_link(video_id: str, timestamp: float) -> str:
        """Create a YouTube link with timestamp."""
        seconds = int(timestamp)
        return f"https://www.youtube.com/watch?v={video_id}&t={seconds}s"

    @staticmethod
    def get_full_text(transcript: List[Dict]) -> str:
        """Extract just the text from transcript segments."""
        return ' '.join([segment['text'] for segment in transcript])

    @staticmethod
    def clean_text(text: str) -> str:
        """Clean up auto-generated caption artifacts."""
        # Remove multiple spaces
        text = ' '.join(text.split())

        # Remove common artifacts
        text = text.replace('[Music]', '')
        text = text.replace('[Applause]', '')
        text = text.replace('[Laughter]', '')

        return text.strip()
