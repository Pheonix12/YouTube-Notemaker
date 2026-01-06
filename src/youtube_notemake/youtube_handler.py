"""Handle YouTube URL parsing and video information extraction."""

import re
from typing import Optional, Dict, Any
from datetime import datetime
import yt_dlp


class YouTubeHandler:
    """Handle YouTube video URL parsing and metadata extraction."""

    @staticmethod
    def extract_video_id(url: str) -> Optional[str]:
        """
        Extract video ID from various YouTube URL formats.

        Supports:
        - https://www.youtube.com/watch?v=VIDEO_ID
        - https://youtu.be/VIDEO_ID
        - https://www.youtube.com/embed/VIDEO_ID
        - https://www.youtube.com/v/VIDEO_ID
        """
        patterns = [
            r'(?:youtube\.com\/watch\?v=|youtu\.be\/|youtube\.com\/embed\/|youtube\.com\/v\/)([a-zA-Z0-9_-]{11})',
            r'youtube\.com\/watch\?.*v=([a-zA-Z0-9_-]{11})',
        ]

        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)

        return None

    @staticmethod
    def validate_url(url: str) -> bool:
        """Validate if the URL is a valid YouTube URL."""
        return YouTubeHandler.extract_video_id(url) is not None

    @staticmethod
    def get_video_info(url: str) -> Dict[str, Any]:
        """
        Fetch video metadata using yt-dlp.

        Returns dict with:
        - title: Video title
        - channel: Channel name
        - upload_date: Upload date
        - duration: Duration in seconds
        - view_count: Number of views
        - description: Video description
        - thumbnail: Thumbnail URL
        - tags: Video tags
        - chapters: Video chapters
        - like_count: Number of likes
        - comment_count: Number of comments
        """
        ydl_opts = {
            'quiet': True,
            'no_warnings': True,
            'extract_flat': False,
        }

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)

                upload_date = None
                if info.get('upload_date'):
                    upload_date = datetime.strptime(info['upload_date'], '%Y%m%d').strftime('%Y-%m-%d')

                # Extract chapters if available
                chapters = []
                if info.get('chapters'):
                    for chapter in info['chapters']:
                        chapters.append({
                            'title': chapter.get('title', ''),
                            'start_time': chapter.get('start_time', 0),
                            'end_time': chapter.get('end_time', 0)
                        })

                return {
                    'video_id': info.get('id', ''),
                    'title': info.get('title', 'Unknown'),
                    'channel': info.get('uploader', 'Unknown'),
                    'channel_id': info.get('channel_id', ''),
                    'upload_date': upload_date,
                    'duration': info.get('duration', 0),
                    'view_count': info.get('view_count', 0),
                    'like_count': info.get('like_count', 0),
                    'comment_count': info.get('comment_count', 0),
                    'description': info.get('description', ''),
                    'thumbnail': info.get('thumbnail', ''),
                    'tags': info.get('tags', []),
                    'categories': info.get('categories', []),
                    'chapters': chapters,
                    'url': url,
                }
        except Exception as e:
            raise Exception(f"Failed to fetch video info: {str(e)}")

    @staticmethod
    def format_duration(seconds: int) -> str:
        """Convert seconds to HH:MM:SS or MM:SS format."""
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        secs = seconds % 60

        if hours > 0:
            return f"{hours:02d}:{minutes:02d}:{secs:02d}"
        return f"{minutes:02d}:{secs:02d}"
