"""Advanced text processing for transcripts."""

import re
from typing import List, Dict
from collections import Counter


class TextProcessor:
    """Process and enhance transcript text."""

    # Common filler words to optionally remove
    FILLER_WORDS = [
        'um', 'uh', 'ah', 'er', 'like', 'you know', 'I mean',
        'sort of', 'kind of', 'basically', 'actually', 'literally'
    ]

    @staticmethod
    def detect_paragraphs(transcript: List[Dict], min_pause: float = 2.0) -> List[Dict]:
        """
        Detect paragraph breaks based on pauses between segments.

        Args:
            transcript: List of transcript segments
            min_pause: Minimum pause duration (seconds) to indicate paragraph break

        Returns:
            Transcript with paragraph markers
        """
        if not transcript:
            return transcript

        processed = []
        for i, segment in enumerate(transcript):
            segment_copy = segment.copy()

            # Check if there's a significant pause before next segment
            if i < len(transcript) - 1:
                next_segment = transcript[i + 1]
                current_end = segment['start'] + segment.get('duration', 0)
                pause_duration = next_segment['start'] - current_end

                if pause_duration >= min_pause:
                    segment_copy['paragraph_break'] = True
                else:
                    segment_copy['paragraph_break'] = False
            else:
                segment_copy['paragraph_break'] = True  # End of transcript

            processed.append(segment_copy)

        return processed

    @staticmethod
    def format_paragraphs(transcript: List[Dict]) -> str:
        """
        Format transcript into paragraphs.

        Args:
            transcript: Transcript with paragraph_break markers

        Returns:
            Formatted text with paragraph breaks
        """
        paragraphs = []
        current_paragraph = []

        for segment in transcript:
            current_paragraph.append(segment['text'].strip())

            if segment.get('paragraph_break', False):
                # Join current paragraph and add to list
                paragraph_text = ' '.join(current_paragraph)
                paragraphs.append(paragraph_text)
                current_paragraph = []

        # Add any remaining text
        if current_paragraph:
            paragraphs.append(' '.join(current_paragraph))

        return '\n\n'.join(paragraphs)

    @staticmethod
    def remove_filler_words(text: str, custom_fillers: List[str] = None) -> str:
        """
        Remove filler words from text.

        Args:
            text: Input text
            custom_fillers: Additional filler words to remove

        Returns:
            Text with filler words removed
        """
        fillers = TextProcessor.FILLER_WORDS.copy()
        if custom_fillers:
            fillers.extend(custom_fillers)

        # Create pattern for word boundaries
        for filler in fillers:
            # Case insensitive removal with word boundaries
            pattern = r'\b' + re.escape(filler) + r'\b'
            text = re.sub(pattern, '', text, flags=re.IGNORECASE)

        # Clean up multiple spaces
        text = re.sub(r'\s+', ' ', text)
        return text.strip()

    @staticmethod
    def fix_capitalization(text: str) -> str:
        """
        Fix sentence capitalization.

        Args:
            text: Input text

        Returns:
            Text with proper capitalization
        """
        # Split into sentences
        sentences = re.split(r'([.!?]+\s+)', text)

        fixed_sentences = []
        for i, part in enumerate(sentences):
            if i % 2 == 0 and part:  # Actual sentence content
                # Capitalize first letter
                part = part[0].upper() + part[1:] if len(part) > 1 else part.upper()
            fixed_sentences.append(part)

        return ''.join(fixed_sentences)

    @staticmethod
    def add_punctuation_intelligence(text: str) -> str:
        """
        Improve punctuation in auto-generated transcripts.

        Args:
            text: Input text

        Returns:
            Text with improved punctuation
        """
        # Add period at the end if missing
        if text and not text[-1] in '.!?':
            text += '.'

        # Add space after punctuation if missing
        text = re.sub(r'([.!?,;:])([A-Za-z])', r'\1 \2', text)

        # Remove space before punctuation
        text = re.sub(r'\s+([.!?,;:])', r'\1', text)

        # Fix multiple punctuation
        text = re.sub(r'([.!?]){2,}', r'\1', text)

        return text

    @staticmethod
    def calculate_statistics(text: str, duration: int = None) -> Dict:
        """
        Calculate text statistics.

        Args:
            text: Input text
            duration: Video duration in seconds

        Returns:
            Dictionary with statistics
        """
        words = text.split()
        word_count = len(words)
        char_count = len(text)
        char_count_no_spaces = len(text.replace(' ', ''))

        # Average reading speed: 200-250 words per minute
        reading_time_min = word_count / 250  # Fast reader
        reading_time_max = word_count / 200  # Slow reader
        reading_time_avg = word_count / 225  # Average

        # Sentence count (approximate)
        sentences = re.split(r'[.!?]+', text)
        sentence_count = len([s for s in sentences if s.strip()])

        stats = {
            'word_count': word_count,
            'character_count': char_count,
            'character_count_no_spaces': char_count_no_spaces,
            'sentence_count': sentence_count,
            'reading_time_minutes': {
                'fast': round(reading_time_min, 1),
                'average': round(reading_time_avg, 1),
                'slow': round(reading_time_max, 1)
            }
        }

        if duration:
            # Words per minute spoken in video
            stats['speaking_rate_wpm'] = round((word_count / duration) * 60, 1)

        return stats

    @staticmethod
    def extract_keywords(text: str, top_n: int = 10) -> List[tuple]:
        """
        Extract keywords from text.

        Args:
            text: Input text
            top_n: Number of top keywords to return

        Returns:
            List of (keyword, frequency) tuples
        """
        # Convert to lowercase and remove punctuation
        text = text.lower()
        text = re.sub(r'[^\w\s]', '', text)

        # Common stop words
        stop_words = {
            'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
            'of', 'with', 'by', 'from', 'as', 'is', 'was', 'are', 'were', 'been',
            'be', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would',
            'could', 'should', 'may', 'might', 'can', 'this', 'that', 'these',
            'those', 'i', 'you', 'he', 'she', 'it', 'we', 'they', 'what', 'which',
            'who', 'when', 'where', 'why', 'how', 'so', 'than', 'too', 'very'
        }

        words = text.split()
        # Filter out stop words and short words
        keywords = [w for w in words if w not in stop_words and len(w) > 3]

        # Count frequency
        word_freq = Counter(keywords)

        return word_freq.most_common(top_n)

    @staticmethod
    def generate_summary_points(text: str, num_sentences: int = 5) -> List[str]:
        """
        Generate key summary points (basic extraction).

        Args:
            text: Input text
            num_sentences: Number of sentences to extract

        Returns:
            List of key sentences
        """
        # Split into sentences
        sentences = re.split(r'[.!?]+', text)
        sentences = [s.strip() for s in sentences if len(s.strip()) > 20]

        if len(sentences) <= num_sentences:
            return sentences

        # Simple extraction: take sentences from different parts
        indices = []
        step = len(sentences) / num_sentences

        for i in range(num_sentences):
            idx = int(i * step)
            if idx < len(sentences):
                indices.append(idx)

        return [sentences[i] for i in indices]

    @staticmethod
    def format_with_chapters(transcript: List[Dict], chapters: List[Dict]) -> List[Dict]:
        """
        Add chapter markers to transcript segments.

        Args:
            transcript: Transcript segments
            chapters: Video chapters with start_time, end_time, title

        Returns:
            Transcript with chapter markers
        """
        if not chapters:
            return transcript

        processed = []
        chapter_idx = 0

        for segment in transcript:
            segment_copy = segment.copy()

            # Check if we've entered a new chapter
            if chapter_idx < len(chapters):
                chapter = chapters[chapter_idx]
                if segment['start'] >= chapter['start_time']:
                    # Check if still in this chapter
                    if segment['start'] < chapter['end_time']:
                        segment_copy['chapter'] = chapter['title']
                        segment_copy['chapter_index'] = chapter_idx
                    else:
                        # Move to next chapter
                        chapter_idx += 1
                        if chapter_idx < len(chapters):
                            next_chapter = chapters[chapter_idx]
                            segment_copy['chapter'] = next_chapter['title']
                            segment_copy['chapter_index'] = chapter_idx

            processed.append(segment_copy)

        return processed
