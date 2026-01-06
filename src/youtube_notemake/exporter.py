"""Export transcripts to various formats (PDF, JSON)."""

import json
import os
from typing import Dict, List, Any
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, Table, TableStyle
from reportlab.lib import colors


class Exporter:
    """Export transcripts to different formats."""

    @staticmethod
    def export_to_json(
        video_info: Dict,
        transcript: List[Dict],
        statistics: Dict = None,
        ai_summary: Dict = None,
        output_path: str = None
    ) -> str:
        """
        Export to JSON format.

        Args:
            video_info: Video metadata
            transcript: Transcript segments
            statistics: Text statistics
            ai_summary: AI-generated summary and key points
            output_path: Output file path

        Returns:
            Path to saved JSON file
        """
        export_data = {
            'metadata': {
                'export_date': datetime.now().isoformat(),
                'exporter': 'YouTube Notemake v0.2.0'
            },
            'video_info': video_info,
            'transcript': transcript,
        }

        if statistics:
            export_data['statistics'] = statistics

        if ai_summary:
            export_data['ai_summary'] = ai_summary

        # Generate filename if not provided
        if not output_path:
            from .markdown_generator import MarkdownGenerator
            filename = MarkdownGenerator.sanitize_filename(video_info['title'])
            output_path = f"output/{filename}.json"

        # Ensure directory exists
        os.makedirs(os.path.dirname(output_path) if os.path.dirname(output_path) else '.', exist_ok=True)

        # Write JSON
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, indent=2, ensure_ascii=False)

        return output_path

    @staticmethod
    def export_to_pdf(
        video_info: Dict,
        transcript: List[Dict],
        statistics: Dict = None,
        ai_summary: Dict = None,
        output_path: str = None,
        include_timestamps: bool = True
    ) -> str:
        """
        Export to PDF format.

        Args:
            video_info: Video metadata
            transcript: Transcript segments
            statistics: Text statistics
            ai_summary: AI-generated summary and key points
            output_path: Output file path
            include_timestamps: Include timestamps in transcript

        Returns:
            Path to saved PDF file
        """
        # Generate filename if not provided
        if not output_path:
            from .markdown_generator import MarkdownGenerator
            filename = MarkdownGenerator.sanitize_filename(video_info['title'])
            output_path = f"output/{filename}.pdf"

        # Ensure directory exists
        os.makedirs(os.path.dirname(output_path) if os.path.dirname(output_path) else '.', exist_ok=True)

        # Create PDF
        doc = SimpleDocTemplate(output_path, pagesize=letter,
                               rightMargin=72, leftMargin=72,
                               topMargin=72, bottomMargin=18)

        # Container for PDF elements
        story = []
        styles = getSampleStyleSheet()

        # Custom styles
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#1a1a1a'),
            spaceAfter=30,
        )

        heading_style = ParagraphStyle(
            'CustomHeading',
            parent=styles['Heading2'],
            fontSize=16,
            textColor=colors.HexColor('#333333'),
            spaceAfter=12,
        )

        # Title
        story.append(Paragraph(video_info['title'], title_style))
        story.append(Spacer(1, 12))

        # Video Information Table
        video_data = [
            ['Channel:', video_info.get('channel', 'Unknown')],
            ['Upload Date:', video_info.get('upload_date', 'Unknown')],
            ['Duration:', Exporter._format_duration(video_info.get('duration', 0))],
            ['Views:', f"{video_info.get('view_count', 0):,}"],
            ['URL:', video_info.get('url', '')],
        ]

        table = Table(video_data, colWidths=[1.5*inch, 4.5*inch])
        table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor('#555555')),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ]))
        story.append(table)
        story.append(Spacer(1, 20))

        # Statistics
        if statistics:
            story.append(Paragraph('Statistics', heading_style))
            stats_data = [
                ['Word Count:', str(statistics.get('word_count', 0))],
                ['Reading Time:', f"{statistics.get('reading_time_minutes', {}).get('average', 0)} minutes (average)"],
                ['Sentences:', str(statistics.get('sentence_count', 0))],
            ]
            stats_table = Table(stats_data, colWidths=[1.5*inch, 4.5*inch])
            stats_table.setStyle(TableStyle([
                ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
            ]))
            story.append(stats_table)
            story.append(Spacer(1, 20))

        # AI Summary
        if ai_summary and ai_summary.get('summary'):
            story.append(Paragraph('Summary', heading_style))
            summary_text = ai_summary['summary'].replace('\n', '<br/>')
            story.append(Paragraph(summary_text, styles['BodyText']))
            story.append(Spacer(1, 12))

            if ai_summary.get('key_points'):
                story.append(Paragraph('Key Points', heading_style))
                for point in ai_summary['key_points']:
                    story.append(Paragraph(f"• {point}", styles['BodyText']))
                    story.append(Spacer(1, 6))
                story.append(Spacer(1, 12))

        # Transcript
        story.append(PageBreak())
        story.append(Paragraph('Transcript', heading_style))
        story.append(Spacer(1, 12))

        for segment in transcript:
            text = segment['text'].strip()
            if include_timestamps:
                timestamp = Exporter._format_timestamp(segment['start'])
                para_text = f"<b>[{timestamp}]</b> {text}"
            else:
                para_text = text

            story.append(Paragraph(para_text, styles['BodyText']))
            story.append(Spacer(1, 8))

        # Build PDF
        doc.build(story)

        return output_path

    @staticmethod
    def _format_duration(seconds: int) -> str:
        """Format duration as HH:MM:SS."""
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        secs = seconds % 60
        if hours > 0:
            return f"{hours:02d}:{minutes:02d}:{secs:02d}"
        return f"{minutes:02d}:{secs:02d}"

    @staticmethod
    def _format_timestamp(seconds: float) -> str:
        """Format timestamp as HH:MM:SS."""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        if hours > 0:
            return f"{hours:02d}:{minutes:02d}:{secs:02d}"
        return f"{minutes:02d}:{secs:02d}"

    @staticmethod
    def generate_table_of_contents(chapters: List[Dict], transcript: List[Dict]) -> List[Dict]:
        """
        Generate table of contents from chapters.

        Args:
            chapters: Video chapters
            transcript: Transcript segments

        Returns:
            TOC with chapter info and word counts
        """
        toc = []

        for i, chapter in enumerate(chapters):
            # Count words in this chapter
            chapter_segments = [
                seg for seg in transcript
                if seg['start'] >= chapter['start_time'] and seg['start'] < chapter['end_time']
            ]

            chapter_text = ' '.join([seg['text'] for seg in chapter_segments])
            word_count = len(chapter_text.split())

            toc.append({
                'index': i + 1,
                'title': chapter['title'],
                'start_time': chapter['start_time'],
                'end_time': chapter['end_time'],
                'duration': chapter['end_time'] - chapter['start_time'],
                'word_count': word_count,
                'segment_count': len(chapter_segments)
            })

        return toc
