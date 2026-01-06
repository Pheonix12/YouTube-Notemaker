"""Generate formatted markdown files from transcripts."""

import os
import re
from typing import Dict, List, Optional
from datetime import datetime


class MarkdownGenerator:
    """Generate markdown files from video info and transcripts."""

    @staticmethod
    def sanitize_filename(filename: str) -> str:
        """Create a safe filename from video title."""
        # Remove invalid characters
        filename = re.sub(r'[<>:"/\\|?*]', '', filename)
        # Replace spaces with underscores
        filename = filename.replace(' ', '_')
        # Limit length
        filename = filename[:100]
        return filename

    @staticmethod
    def generate_markdown(
        video_info: Dict,
        transcript: List[Dict],
        options: Optional[Dict] = None,
        statistics: Optional[Dict] = None,
        ai_summary: Optional[Dict] = None
    ) -> str:
        """
        Generate formatted markdown content with enhanced features.

        Args:
            video_info: Video metadata dict
            transcript: List of transcript segments
            options: Dict with options
            statistics: Text statistics (word count, reading time, etc.)
            ai_summary: AI-generated summary and key points

        Returns:
            Formatted markdown string
        """
        if options is None:
            options = {}

        # Default options
        include_timestamps = options.get('include_timestamps', True)
        clickable_timestamps = options.get('clickable_timestamps', True)
        group_by_time = options.get('group_by_time', 0)
        include_thumbnail = options.get('include_thumbnail', True)
        include_description = options.get('include_description', True)
        include_tags = options.get('include_tags', False)
        include_statistics = options.get('include_statistics', True)
        include_toc = options.get('include_toc', True)
        clean_text = options.get('clean_text', True)

        md_content = []

        # Title
        md_content.append(f"# {video_info['title']}\n")

        # AI Summary (at top if available)
        if ai_summary and ai_summary.get('summary'):
            md_content.append("## Summary\n")
            md_content.append(ai_summary['summary'] + "\n")

            if ai_summary.get('key_points'):
                md_content.append("### Key Points\n")
                for point in ai_summary['key_points']:
                    md_content.append(f"- {point}")
                md_content.append("")

        # Metadata section
        md_content.append("## Video Information\n")
        md_content.append(f"- **Channel**: {video_info['channel']}")
        md_content.append(f"- **Upload Date**: {video_info.get('upload_date', 'Unknown')}")

        if video_info.get('duration'):
            from .youtube_handler import YouTubeHandler
            duration_str = YouTubeHandler.format_duration(video_info['duration'])
            md_content.append(f"- **Duration**: {duration_str}")

        if video_info.get('view_count'):
            md_content.append(f"- **Views**: {video_info['view_count']:,}")

        if video_info.get('like_count'):
            md_content.append(f"- **Likes**: {video_info['like_count']:,}")

        md_content.append(f"- **URL**: [{video_info['url']}]({video_info['url']})")

        # Tags
        if include_tags and video_info.get('tags'):
            md_content.append(f"\n**Tags**: {', '.join(video_info['tags'][:10])}")

        # Thumbnail
        if include_thumbnail and video_info.get('thumbnail'):
            md_content.append(f"\n![Video Thumbnail]({video_info['thumbnail']})")

        # Statistics
        if include_statistics and statistics:
            md_content.append("\n## Statistics\n")
            md_content.append(f"- **Word Count**: {statistics['word_count']:,}")
            md_content.append(f"- **Character Count**: {statistics['character_count']:,}")
            md_content.append(f"- **Estimated Reading Time**: {statistics['reading_time_minutes']['average']} minutes")
            if 'speaking_rate_wpm' in statistics:
                md_content.append(f"- **Speaking Rate**: {statistics['speaking_rate_wpm']} words/minute")

        # Table of Contents (for chapters)
        if include_toc and video_info.get('chapters'):
            md_content.append("\n## Table of Contents\n")
            for i, chapter in enumerate(video_info['chapters'], 1):
                from .youtube_handler import YouTubeHandler
                timestamp = YouTubeHandler.format_duration(int(chapter['start_time']))
                md_content.append(f"{i}. [{timestamp}](#) - {chapter['title']}")

        # Description
        if include_description and video_info.get('description'):
            md_content.append("\n## Description\n")
            md_content.append(video_info['description'])

        # Transcript section
        md_content.append("\n## Transcript\n")

        if group_by_time > 0:
            md_content.append(
                MarkdownGenerator._format_grouped_transcript(
                    transcript,
                    video_info['video_id'],
                    group_by_time,
                    include_timestamps,
                    clickable_timestamps,
                    clean_text
                )
            )
        else:
            md_content.append(
                MarkdownGenerator._format_sequential_transcript(
                    transcript,
                    video_info['video_id'],
                    include_timestamps,
                    clickable_timestamps,
                    clean_text
                )
            )

        # Footer
        md_content.append(f"\n---\n*Transcript generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} by YouTube Notemake v0.2.0*")

        return '\n'.join(md_content)

    @staticmethod
    def _format_sequential_transcript(
        transcript: List[Dict],
        video_id: str,
        include_timestamps: bool,
        clickable_timestamps: bool,
        clean_text: bool
    ) -> str:
        """Format transcript as sequential text with optional timestamps."""
        from .transcript import TranscriptExtractor

        lines = []

        for segment in transcript:
            text = segment['text']
            if clean_text:
                text = TranscriptExtractor.clean_text(text)

            if include_timestamps:
                timestamp = TranscriptExtractor.format_timestamp(segment['start'])
                if clickable_timestamps:
                    link = TranscriptExtractor.create_youtube_link(video_id, segment['start'])
                    lines.append(f"**[{timestamp}]({link})** {text}")
                else:
                    lines.append(f"**{timestamp}** {text}")
            else:
                lines.append(text)

        return '\n\n'.join(lines)

    @staticmethod
    def _format_grouped_transcript(
        transcript: List[Dict],
        video_id: str,
        group_seconds: int,
        include_timestamps: bool,
        clickable_timestamps: bool,
        clean_text: bool
    ) -> str:
        """Group transcript segments by time intervals."""
        from .transcript import TranscriptExtractor

        groups = []
        current_group = []
        current_group_start = 0

        for segment in transcript:
            group_index = int(segment['start'] // group_seconds)
            group_start = group_index * group_seconds

            if group_start != current_group_start and current_group:
                # Save previous group
                groups.append((current_group_start, current_group))
                current_group = []

            current_group_start = group_start
            current_group.append(segment)

        # Add last group
        if current_group:
            groups.append((current_group_start, current_group))

        # Format groups
        lines = []
        for group_start, segments in groups:
            # Group header
            if include_timestamps:
                timestamp = TranscriptExtractor.format_timestamp(group_start)
                if clickable_timestamps:
                    link = TranscriptExtractor.create_youtube_link(video_id, group_start)
                    lines.append(f"### [{timestamp}]({link})\n")
                else:
                    lines.append(f"### {timestamp}\n")

            # Group text
            group_text = ' '.join([seg['text'] for seg in segments])
            if clean_text:
                group_text = TranscriptExtractor.clean_text(group_text)

            lines.append(group_text + '\n')

        return '\n'.join(lines)

    @staticmethod
    def save_markdown(content: str, output_dir: str, filename: str) -> str:
        """
        Save markdown content to file.

        Returns:
            Full path to saved file
        """
        os.makedirs(output_dir, exist_ok=True)

        # Ensure .md extension
        if not filename.endswith('.md'):
            filename += '.md'

        filepath = os.path.join(output_dir, filename)

        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)

        return filepath
