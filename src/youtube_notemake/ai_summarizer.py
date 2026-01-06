"""AI-powered summarization using OpenAI or Claude API."""

import os
from typing import Dict, List, Optional
from anthropic import Anthropic
from openai import OpenAI


class AISummarizer:
    """Generate summaries and key points using AI."""

    def __init__(self, provider: str = "claude", api_key: Optional[str] = None):
        """
        Initialize AI summarizer.

        Args:
            provider: "claude" or "openai"
            api_key: API key (if None, reads from environment)
        """
        self.provider = provider.lower()

        if self.provider == "claude":
            self.client = Anthropic(api_key=api_key or os.getenv("ANTHROPIC_API_KEY"))
            self.model = "claude-3-5-sonnet-20241022"
        elif self.provider == "openai":
            self.client = OpenAI(api_key=api_key or os.getenv("OPENAI_API_KEY"))
            self.model = "gpt-4-turbo-preview"
        else:
            raise ValueError("Provider must be 'claude' or 'openai'")

    def generate_summary(self, text: str, max_length: int = 300) -> str:
        """
        Generate a concise summary of the transcript.

        Args:
            text: Full transcript text
            max_length: Maximum summary length in words

        Returns:
            Summary text
        """
        prompt = f"""Please provide a concise summary of the following video transcript in approximately {max_length} words.
Focus on the main points and key takeaways.

Transcript:
{text[:15000]}  # Limit to avoid token limits

Summary:"""

        try:
            if self.provider == "claude":
                response = self.client.messages.create(
                    model=self.model,
                    max_tokens=1024,
                    messages=[{"role": "user", "content": prompt}]
                )
                return response.content[0].text.strip()

            else:  # openai
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=1024
                )
                return response.choices[0].message.content.strip()

        except Exception as e:
            return f"Error generating summary: {str(e)}"

    def extract_key_points(self, text: str, num_points: int = 5) -> List[str]:
        """
        Extract key points from the transcript.

        Args:
            text: Full transcript text
            num_points: Number of key points to extract

        Returns:
            List of key points
        """
        prompt = f"""Analyze the following video transcript and extract exactly {num_points} key points or main ideas.
Format each point as a clear, concise bullet point.

Transcript:
{text[:15000]}

Key Points (return only the numbered list):"""

        try:
            if self.provider == "claude":
                response = self.client.messages.create(
                    model=self.model,
                    max_tokens=1024,
                    messages=[{"role": "user", "content": prompt}]
                )
                content = response.content[0].text.strip()

            else:  # openai
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=1024
                )
                content = response.choices[0].message.content.strip()

            # Parse the response into list
            points = []
            for line in content.split('\n'):
                line = line.strip()
                if line and (line[0].isdigit() or line.startswith('-') or line.startswith('•')):
                    # Remove numbering and bullets
                    point = line.lstrip('0123456789.-•) ').strip()
                    if point:
                        points.append(point)

            return points[:num_points]

        except Exception as e:
            return [f"Error extracting key points: {str(e)}"]

    def generate_chapter_summary(self, chapter_title: str, chapter_text: str) -> str:
        """
        Generate a summary for a specific chapter.

        Args:
            chapter_title: Title of the chapter
            chapter_text: Text content of the chapter

        Returns:
            Chapter summary
        """
        prompt = f"""Summarize the following section titled "{chapter_title}" in 2-3 sentences.

Content:
{chapter_text[:10000]}

Summary:"""

        try:
            if self.provider == "claude":
                response = self.client.messages.create(
                    model=self.model,
                    max_tokens=256,
                    messages=[{"role": "user", "content": prompt}]
                )
                return response.content[0].text.strip()

            else:  # openai
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=256
                )
                return response.choices[0].message.content.strip()

        except Exception as e:
            return f"Error generating chapter summary: {str(e)}"

    def generate_questions(self, text: str, num_questions: int = 5) -> List[str]:
        """
        Generate discussion questions based on the content.

        Args:
            text: Full transcript text
            num_questions: Number of questions to generate

        Returns:
            List of questions
        """
        prompt = f"""Based on the following transcript, generate {num_questions} thought-provoking discussion questions
that could be used for study or reflection.

Transcript:
{text[:15000]}

Questions:"""

        try:
            if self.provider == "claude":
                response = self.client.messages.create(
                    model=self.model,
                    max_tokens=512,
                    messages=[{"role": "user", "content": prompt}]
                )
                content = response.content[0].text.strip()

            else:  # openai
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=512
                )
                content = response.choices[0].message.content.strip()

            # Parse questions
            questions = []
            for line in content.split('\n'):
                line = line.strip()
                if line and (line[0].isdigit() or '?' in line):
                    question = line.lstrip('0123456789.-) ').strip()
                    if question and '?' in question:
                        questions.append(question)

            return questions[:num_questions]

        except Exception as e:
            return [f"Error generating questions: {str(e)}"]

    def analyze_sentiment_and_tone(self, text: str) -> Dict[str, str]:
        """
        Analyze the overall sentiment and tone of the content.

        Args:
            text: Full transcript text

        Returns:
            Dictionary with sentiment and tone analysis
        """
        prompt = f"""Analyze the sentiment and tone of the following transcript.
Provide:
1. Overall sentiment (positive/negative/neutral)
2. Tone (e.g., educational, entertaining, serious, casual)
3. Target audience (e.g., beginners, experts, general public)
4. Content type (e.g., tutorial, discussion, lecture, entertainment)

Transcript:
{text[:10000]}

Analysis:"""

        try:
            if self.provider == "claude":
                response = self.client.messages.create(
                    model=self.model,
                    max_tokens=512,
                    messages=[{"role": "user", "content": prompt}]
                )
                content = response.content[0].text.strip()

            else:  # openai
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=512
                )
                content = response.choices[0].message.content.strip()

            # Simple parsing (could be improved)
            return {
                'analysis': content
            }

        except Exception as e:
            return {'analysis': f"Error analyzing content: {str(e)}"}

    @staticmethod
    def check_api_key(provider: str) -> bool:
        """Check if API key is available for the provider."""
        if provider.lower() == "claude":
            return bool(os.getenv("ANTHROPIC_API_KEY"))
        elif provider.lower() == "openai":
            return bool(os.getenv("OPENAI_API_KEY"))
        return False
