"""Caching system for transcripts and video info."""

import json
import os
import hashlib
from typing import Optional, Dict, Any
from datetime import datetime, timedelta
from pathlib import Path


class CacheManager:
    """Manage cache for transcripts and video metadata."""

    def __init__(self, cache_dir: str = ".cache"):
        """
        Initialize cache manager.

        Args:
            cache_dir: Directory to store cache files
        """
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(exist_ok=True)

        # Separate subdirectories for different types
        self.video_info_dir = self.cache_dir / "video_info"
        self.transcript_dir = self.cache_dir / "transcripts"
        self.audio_dir = self.cache_dir / "audio"

        self.video_info_dir.mkdir(exist_ok=True)
        self.transcript_dir.mkdir(exist_ok=True)
        self.audio_dir.mkdir(exist_ok=True)

    def _get_cache_key(self, video_id: str, suffix: str = "") -> str:
        """Generate cache key from video ID."""
        return hashlib.md5(f"{video_id}{suffix}".encode()).hexdigest()

    def _is_cache_valid(self, cache_file: Path, max_age_days: int = 30) -> bool:
        """Check if cache file exists and is not expired."""
        if not cache_file.exists():
            return False

        # Check age
        file_time = datetime.fromtimestamp(cache_file.stat().st_mtime)
        age = datetime.now() - file_time

        return age < timedelta(days=max_age_days)

    def cache_video_info(self, video_id: str, video_info: Dict[str, Any]) -> None:
        """
        Cache video information.

        Args:
            video_id: YouTube video ID
            video_info: Video metadata dictionary
        """
        cache_key = self._get_cache_key(video_id)
        cache_file = self.video_info_dir / f"{cache_key}.json"

        cache_data = {
            'cached_at': datetime.now().isoformat(),
            'video_id': video_id,
            'data': video_info
        }

        with open(cache_file, 'w', encoding='utf-8') as f:
            json.dump(cache_data, f, indent=2, ensure_ascii=False)

    def get_cached_video_info(self, video_id: str, max_age_days: int = 30) -> Optional[Dict[str, Any]]:
        """
        Get cached video information.

        Args:
            video_id: YouTube video ID
            max_age_days: Maximum cache age in days

        Returns:
            Video info dict or None if not cached/expired
        """
        cache_key = self._get_cache_key(video_id)
        cache_file = self.video_info_dir / f"{cache_key}.json"

        if not self._is_cache_valid(cache_file, max_age_days):
            return None

        try:
            with open(cache_file, 'r', encoding='utf-8') as f:
                cache_data = json.load(f)
            return cache_data['data']
        except Exception:
            return None

    def cache_transcript(self, video_id: str, language: str, transcript: list) -> None:
        """
        Cache transcript.

        Args:
            video_id: YouTube video ID
            language: Language code
            transcript: Transcript segments
        """
        cache_key = self._get_cache_key(video_id, language)
        cache_file = self.transcript_dir / f"{cache_key}.json"

        cache_data = {
            'cached_at': datetime.now().isoformat(),
            'video_id': video_id,
            'language': language,
            'data': transcript
        }

        with open(cache_file, 'w', encoding='utf-8') as f:
            json.dump(cache_data, f, indent=2, ensure_ascii=False)

    def get_cached_transcript(self, video_id: str, language: str, max_age_days: int = 30) -> Optional[list]:
        """
        Get cached transcript.

        Args:
            video_id: YouTube video ID
            language: Language code
            max_age_days: Maximum cache age in days

        Returns:
            Transcript list or None if not cached/expired
        """
        cache_key = self._get_cache_key(video_id, language)
        cache_file = self.transcript_dir / f"{cache_key}.json"

        if not self._is_cache_valid(cache_file, max_age_days):
            return None

        try:
            with open(cache_file, 'r', encoding='utf-8') as f:
                cache_data = json.load(f)
            return cache_data['data']
        except Exception:
            return None

    def clear_cache(self, cache_type: str = "all") -> int:
        """
        Clear cache files.

        Args:
            cache_type: "all", "video_info", "transcripts", or "audio"

        Returns:
            Number of files deleted
        """
        deleted_count = 0

        if cache_type in ["all", "video_info"]:
            for file in self.video_info_dir.glob("*.json"):
                file.unlink()
                deleted_count += 1

        if cache_type in ["all", "transcripts"]:
            for file in self.transcript_dir.glob("*.json"):
                file.unlink()
                deleted_count += 1

        if cache_type in ["all", "audio"]:
            for file in self.audio_dir.glob("*"):
                file.unlink()
                deleted_count += 1

        return deleted_count

    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        video_info_count = len(list(self.video_info_dir.glob("*.json")))
        transcript_count = len(list(self.transcript_dir.glob("*.json")))
        audio_count = len(list(self.audio_dir.glob("*")))

        # Calculate sizes
        def get_dir_size(directory):
            return sum(f.stat().st_size for f in directory.rglob('*') if f.is_file())

        return {
            'video_info_count': video_info_count,
            'transcript_count': transcript_count,
            'audio_count': audio_count,
            'total_size_mb': round(get_dir_size(self.cache_dir) / (1024 * 1024), 2),
            'cache_dir': str(self.cache_dir)
        }
