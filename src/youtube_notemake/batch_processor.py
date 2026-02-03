"""Batch processing for multiple videos and playlists."""

import re
from typing import List, Dict, Optional, Callable
import yt_dlp
from .youtube_handler import YouTubeHandler
from .ytdlp_config import get_base_ydl_opts


class BatchProcessor:
    """Process multiple videos or entire playlists."""

    @staticmethod
    def extract_playlist_id(url: str) -> Optional[str]:
        """
        Extract playlist ID from YouTube URL.

        Supports:
        - https://www.youtube.com/playlist?list=PLAYLIST_ID
        - https://www.youtube.com/watch?v=VIDEO_ID&list=PLAYLIST_ID
        """
        patterns = [
            r'[?&]list=([a-zA-Z0-9_-]+)',
            r'youtube\.com/playlist\?list=([a-zA-Z0-9_-]+)'
        ]

        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)

        return None

    @staticmethod
    def get_playlist_videos(playlist_url: str, max_videos: Optional[int] = None) -> List[Dict[str, str]]:
        """
        Get list of videos from a playlist.

        Args:
            playlist_url: YouTube playlist URL
            max_videos: Maximum number of videos to retrieve

        Returns:
            List of dicts with 'video_id', 'title', 'url'
        """
        ydl_opts = get_base_ydl_opts(
            quiet=True,
            no_warnings=True,
            extract_flat=True,
            force_generic_extractor=False,
        )

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                playlist_info = ydl.extract_info(playlist_url, download=False)

                if 'entries' not in playlist_info:
                    raise Exception("No videos found in playlist")

                videos = []
                entries = playlist_info['entries']

                if max_videos:
                    entries = entries[:max_videos]

                for entry in entries:
                    if entry:  # Some entries might be None
                        videos.append({
                            'video_id': entry.get('id', ''),
                            'title': entry.get('title', 'Unknown'),
                            'url': f"https://www.youtube.com/watch?v={entry.get('id', '')}"
                        })

                return videos

        except Exception as e:
            raise Exception(f"Failed to fetch playlist: {str(e)}")

    @staticmethod
    def get_channel_videos(channel_url: str, max_videos: int = 50) -> List[Dict[str, str]]:
        """
        Get videos from a YouTube channel.

        Args:
            channel_url: YouTube channel URL
            max_videos: Maximum number of videos to retrieve

        Returns:
            List of dicts with 'video_id', 'title', 'url'
        """
        ydl_opts = get_base_ydl_opts(
            quiet=True,
            no_warnings=True,
            extract_flat=True,
            playlistend=max_videos,
        )

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                channel_info = ydl.extract_info(channel_url, download=False)

                videos = []
                if 'entries' in channel_info:
                    for entry in channel_info['entries']:
                        if entry:
                            videos.append({
                                'video_id': entry.get('id', ''),
                                'title': entry.get('title', 'Unknown'),
                                'url': f"https://www.youtube.com/watch?v={entry.get('id', '')}"
                            })

                return videos[:max_videos]

        except Exception as e:
            raise Exception(f"Failed to fetch channel videos: {str(e)}")

    @staticmethod
    def process_url_list(
        urls: List[str],
        progress_callback: Optional[Callable[[int, int, str], None]] = None
    ) -> List[Dict[str, any]]:
        """
        Process a list of YouTube URLs.

        Args:
            urls: List of YouTube video URLs
            progress_callback: Optional callback(current, total, status)

        Returns:
            List of results with success/error info
        """
        results = []
        total = len(urls)

        for i, url in enumerate(urls):
            if progress_callback:
                progress_callback(i + 1, total, f"Processing {url}")

            try:
                # Validate URL
                if not YouTubeHandler.validate_url(url):
                    results.append({
                        'url': url,
                        'success': False,
                        'error': 'Invalid YouTube URL'
                    })
                    continue

                video_id = YouTubeHandler.extract_video_id(url)

                results.append({
                    'url': url,
                    'video_id': video_id,
                    'success': True,
                    'error': None
                })

            except Exception as e:
                results.append({
                    'url': url,
                    'success': False,
                    'error': str(e)
                })

        return results

    @staticmethod
    def read_urls_from_file(file_path: str) -> List[str]:
        """
        Read YouTube URLs from a text file (one per line).

        Args:
            file_path: Path to text file

        Returns:
            List of URLs
        """
        urls = []

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    # Skip empty lines and comments
                    if line and not line.startswith('#'):
                        urls.append(line)

            return urls

        except Exception as e:
            raise Exception(f"Failed to read file: {str(e)}")

    @staticmethod
    def validate_batch_urls(urls: List[str]) -> Dict[str, List[str]]:
        """
        Validate a batch of URLs.

        Args:
            urls: List of URLs to validate

        Returns:
            Dict with 'valid' and 'invalid' lists
        """
        valid = []
        invalid = []

        for url in urls:
            if YouTubeHandler.validate_url(url):
                valid.append(url)
            else:
                invalid.append(url)

        return {
            'valid': valid,
            'invalid': invalid,
            'total': len(urls),
            'valid_count': len(valid),
            'invalid_count': len(invalid)
        }

    @staticmethod
    def organize_by_channel(video_infos: List[Dict]) -> Dict[str, List[Dict]]:
        """
        Organize videos by channel.

        Args:
            video_infos: List of video info dicts

        Returns:
            Dict mapping channel names to video lists
        """
        by_channel = {}

        for video_info in video_infos:
            channel = video_info.get('channel', 'Unknown')

            if channel not in by_channel:
                by_channel[channel] = []

            by_channel[channel].append(video_info)

        return by_channel

    @staticmethod
    def organize_by_date(video_infos: List[Dict]) -> Dict[str, List[Dict]]:
        """
        Organize videos by upload date.

        Args:
            video_infos: List of video info dicts

        Returns:
            Dict mapping dates to video lists
        """
        by_date = {}

        for video_info in video_infos:
            date = video_info.get('upload_date', 'Unknown')

            if date not in by_date:
                by_date[date] = []

            by_date[date].append(video_info)

        return by_date
