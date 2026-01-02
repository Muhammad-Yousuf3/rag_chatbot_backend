"""Translate Agent for Urdu translation.

T057 [US3] - Implements the translation agent using Gemini for
translating chapter content to Urdu.
"""

import asyncio
import logging
from pathlib import Path
from typing import Any

from ..config import get_settings
from ..services.gemini_client import GeminiService, get_gemini_service

logger = logging.getLogger(__name__)


class TranslateAgent:
    """Agent for translating content to Urdu."""

    SUPPORTED_LANGUAGES = {"ur": "Urdu", "اردو": "Urdu"}

    def __init__(
        self,
        gemini_client: GeminiService | None = None,
        system_prompt: str | None = None,
    ):
        """Initialize translate agent.

        Args:
            gemini_client: Gemini client for API calls.
            system_prompt: Optional custom system prompt.
        """
        settings = get_settings()
        self._model = settings.chat_model
        self._max_tokens = settings.max_tokens
        self._gemini_client = gemini_client or get_gemini_service()

        # Load system prompt
        if system_prompt:
            self.system_prompt = system_prompt
        else:
            self.system_prompt = self._load_system_prompt()

    def _load_system_prompt(self) -> str:
        """Load system prompt from template file.

        Returns:
            System prompt string.
        """
        prompt_path = Path(__file__).parent / "prompts" / "translate.txt"

        if prompt_path.exists():
            return prompt_path.read_text(encoding="utf-8")

        # Fallback default prompt
        return """You are an expert translator specializing in translating
technical content from English to Urdu. Produce natural, fluent Urdu
translations while preserving code blocks, technical terms, and markdown
formatting."""

    async def translate(
        self,
        content: str,
        target_language: str = "ur",
    ) -> str:
        """Translate content to target language.

        Args:
            content: Content to translate.
            target_language: Target language code (default: "ur" for Urdu).

        Returns:
            Translated content.

        Raises:
            ValueError: If target language is not supported.
        """
        if target_language not in self.SUPPORTED_LANGUAGES:
            raise ValueError(
                f"Unsupported language: {target_language}. "
                f"Supported languages: {list(self.SUPPORTED_LANGUAGES.keys())}"
            )

        if not content or not content.strip():
            return ""

        logger.info(f"Translating content (length={len(content)}) to {target_language}")

        # Build messages for translation
        messages = [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": content},
        ]

        # Call Gemini API
        try:
            response = await self._gemini_client.chat_completion(
                messages=messages,
                temperature=0.3,
                max_tokens=self._max_tokens,
            )
            logger.info(f"Translation successful (response length={len(response)})")
            return response
        except Exception as e:
            logger.error(f"Translation API call failed: {type(e).__name__}: {e}", exc_info=True)
            raise

    async def translate_chunked(
        self,
        content: str,
        target_language: str = "ur",
        chunk_size: int = 4000,
    ) -> str:
        """Translate long content by chunking.

        Handles two formats:
        1. Separator-based: Text segments joined with |||SEP|||
        2. Paragraph-based: Traditional paragraph chunks

        Args:
            content: Content to translate.
            target_language: Target language code.
            chunk_size: Approximate characters per chunk.

        Returns:
            Translated content with same format as input.
        """
        # Check if content uses separator format (from full-page translation)
        SEPARATOR = "|||SEP|||"
        if SEPARATOR in content:
            return await self._translate_with_separator(content, target_language, chunk_size)

        # Original paragraph-based chunking for regular content
        if len(content) <= chunk_size:
            return await self.translate(content, target_language)

        # Split by paragraphs to maintain context
        paragraphs = content.split("\n\n")
        chunks = []
        current_chunk = []
        current_size = 0

        for para in paragraphs:
            if current_size + len(para) > chunk_size and current_chunk:
                chunks.append("\n\n".join(current_chunk))
                current_chunk = [para]
                current_size = len(para)
            else:
                current_chunk.append(para)
                current_size += len(para)

        if current_chunk:
            chunks.append("\n\n".join(current_chunk))

        # Translate each chunk with delay between calls to avoid rate limits
        translated_chunks = []
        for i, chunk in enumerate(chunks):
            translated = await self.translate(chunk, target_language)
            translated_chunks.append(translated)
            # Add delay between chunks to avoid rate limiting (skip after last chunk)
            if i < len(chunks) - 1:
                await asyncio.sleep(2)

        return "\n\n".join(translated_chunks)

    async def _translate_with_separator(
        self,
        content: str,
        target_language: str,
        chunk_size: int = 4000,
    ) -> str:
        """Translate content that uses |||SEP||| separator format.

        This preserves the exact number of segments for DOM-based translation.

        Args:
            content: Content with |||SEP||| separators.
            target_language: Target language code.
            chunk_size: Max characters per API call.

        Returns:
            Translated content with same number of |||SEP||| segments.
        """
        SEPARATOR = "|||SEP|||"
        segments = content.split(SEPARATOR)

        # Process in batches to stay within API limits
        translated_segments = []
        current_batch = []
        current_size = 0

        for segment in segments:
            segment_size = len(segment) + len(SEPARATOR)

            # If adding this segment exceeds chunk size, translate current batch
            if current_size + segment_size > chunk_size and current_batch:
                batch_text = SEPARATOR.join(current_batch)
                translated_batch = await self._translate_preserving_separator(
                    batch_text, target_language
                )
                translated_segments.extend(translated_batch.split(SEPARATOR))
                # Add delay between batches to avoid rate limiting
                await asyncio.sleep(2)
                current_batch = [segment]
                current_size = segment_size
            else:
                current_batch.append(segment)
                current_size += segment_size

        # Translate remaining batch
        if current_batch:
            batch_text = SEPARATOR.join(current_batch)
            translated_batch = await self._translate_preserving_separator(
                batch_text, target_language
            )
            translated_segments.extend(translated_batch.split(SEPARATOR))

        return SEPARATOR.join(translated_segments)

    async def _translate_preserving_separator(
        self,
        content: str,
        target_language: str,
    ) -> str:
        """Translate content while preserving |||SEP||| separators.

        Args:
            content: Text with |||SEP||| separators.
            target_language: Target language.

        Returns:
            Translated text with separators preserved.
        """
        SEPARATOR = "|||SEP|||"

        # Build a prompt that explicitly tells the LLM to preserve separators
        translation_prompt = f"""Translate the following text to {self.SUPPORTED_LANGUAGES.get(target_language, 'Urdu')}.

CRITICAL RULES:
1. Keep all |||SEP||| markers EXACTLY as they are - do not translate or modify them
2. Translate ONLY the text between the markers
3. Maintain the EXACT same number of |||SEP||| markers in your output
4. Do not add or remove any |||SEP||| markers
5. Output ONLY the translated text with markers, no explanations

Text to translate:
{content}"""

        messages = [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": translation_prompt},
        ]

        response = await self._gemini_client.chat_completion(
            messages=messages,
            temperature=0.3,
            max_tokens=self._max_tokens,
        )

        # Verify separator count matches
        original_count = content.count(SEPARATOR)
        response_count = response.count(SEPARATOR)

        if response_count != original_count:
            # Fallback: translate each segment individually with delay
            segments = content.split(SEPARATOR)
            translated = []
            for i, seg in enumerate(segments):
                if seg.strip():
                    trans = await self.translate(seg.strip(), target_language)
                    translated.append(trans)
                    # Add delay between segments to avoid rate limiting
                    if i < len(segments) - 1:
                        await asyncio.sleep(2)
                else:
                    translated.append(seg)
            return SEPARATOR.join(translated)

        return response


def get_translate_agent() -> TranslateAgent:
    """FastAPI dependency to get translate agent instance.

    Returns:
        Configured TranslateAgent instance.
    """
    return TranslateAgent()
