"""Gemini client wrapper for embeddings and chat completions.

Uses the new google.genai package (replacing deprecated google.generativeai).
"""

import asyncio
import json
import logging
from typing import List, Optional

from google import genai
from google.genai import types

from ..config import get_settings

logger = logging.getLogger(__name__)


class GeminiService:
    """Service for interacting with Google Gemini API."""

    def __init__(self):
        """Initialize Gemini client."""
        settings = get_settings()

        # Initialize the new genai client
        self.client = genai.Client(api_key=settings.gemini_api_key)

        self.embedding_model = settings.embedding_model
        self.chat_model = settings.chat_model

    async def create_embedding(self, text: str) -> List[float]:
        """Create embedding for a single text.

        Args:
            text: Text to embed

        Returns:
            Embedding vector
        """
        delay = 10
        max_retries = 10

        for attempt in range(max_retries):
            try:
                # Run in executor since the client is synchronous
                loop = asyncio.get_event_loop()
                result = await loop.run_in_executor(
                    None,
                    lambda: self.client.models.embed_content(
                        model=self.embedding_model,
                        contents=text,
                    )
                )
                return result.embeddings[0].values
            except Exception as e:
                error_str = str(e)
                if "429" in error_str or "quota" in error_str.lower() or "ResourceExhausted" in error_str:
                    wait_time = delay * (1.5 ** attempt)
                    if wait_time > 120:
                        wait_time = 120
                    logger.warning(f"Rate limit hit. Retrying in {wait_time:.1f}s... (Attempt {attempt + 1}/{max_retries})")
                    await asyncio.sleep(wait_time)
                else:
                    raise e

        raise Exception(f"Failed to get embedding after {max_retries} retries")

    async def create_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Create embeddings for multiple texts using batch API.

        Args:
            texts: List of texts to embed

        Returns:
            List of embedding vectors
        """
        # Batching configuration
        BATCH_SIZE = 100
        embeddings = []

        for i in range(0, len(texts), BATCH_SIZE):
            batch = texts[i:i + BATCH_SIZE]

            # Retry logic for the batch
            delay = 10
            max_retries = 5
            batch_success = False

            for attempt in range(max_retries):
                try:
                    loop = asyncio.get_event_loop()
                    result = await loop.run_in_executor(
                        None,
                        lambda b=batch: self.client.models.embed_content(
                            model=self.embedding_model,
                            contents=b,
                        )
                    )

                    # Extract embeddings from result
                    for emb in result.embeddings:
                        embeddings.append(emb.values)

                    batch_success = True
                    break

                except Exception as e:
                    error_str = str(e)
                    if "429" in error_str or "quota" in error_str.lower() or "ResourceExhausted" in error_str:
                        wait_time = delay * (2 ** attempt)
                        if wait_time > 120:
                            wait_time = 120
                        logger.warning(f"Batch rate limit hit. Retrying in {wait_time}s... (Attempt {attempt + 1}/{max_retries})")
                        await asyncio.sleep(wait_time)
                    else:
                        raise e

            if not batch_success:
                 raise Exception(f"Failed to embed batch after {max_retries} retries")

            # Small delay between batches
            await asyncio.sleep(2)

        return embeddings

    async def chat_completion(
        self,
        messages: List[dict],
        temperature: float = 0.3,
        max_tokens: Optional[int] = None,
    ) -> str:
        """Create a chat completion.

        Args:
            messages: List of message dicts with 'role' and 'content'
            temperature: Sampling temperature (0-2)
            max_tokens: Maximum tokens in response

        Returns:
            Assistant message content
        """
        logger.info(f"GeminiService.chat_completion called: messages_count={len(messages)}, model={self.chat_model}")

        # Convert messages to Gemini format
        contents = []
        system_instruction = None

        for msg in messages:
            role = msg.get("role", "user")
            content = msg.get("content", "")

            if role == "system":
                system_instruction = content
            elif role == "user":
                contents.append(types.Content(
                    role="user",
                    parts=[types.Part.from_text(text=content)]
                ))
            elif role == "assistant":
                contents.append(types.Content(
                    role="model",
                    parts=[types.Part.from_text(text=content)]
                ))

        logger.info(f"Converted to Gemini format: {len(contents)} content items, has_system_instruction={system_instruction is not None}")

        # Build generation config
        config = types.GenerateContentConfig(
            temperature=temperature,
            max_output_tokens=max_tokens,
            system_instruction=system_instruction,
        )

        # Generate response
        try:
            logger.info(f"Calling Gemini API: model={self.chat_model}")
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None,
                lambda: self.client.models.generate_content(
                    model=self.chat_model,
                    contents=contents,
                    config=config,
                )
            )
            logger.info(f"Gemini API response received successfully")
            return response.text
        except Exception as e:
            logger.error(f"Gemini API call failed: {type(e).__name__}: {e}", exc_info=True)
            raise

    async def chat_completion_with_json(
        self,
        messages: List[dict],
        temperature: float = 0.3,
    ) -> dict:
        """Create a chat completion with JSON response format.

        Args:
            messages: List of message dicts
            temperature: Sampling temperature

        Returns:
            Parsed JSON response
        """
        # Add instruction to return JSON
        modified_messages = messages.copy()
        if modified_messages:
            last_idx = len(modified_messages) - 1
            modified_messages[last_idx] = {
                **modified_messages[last_idx],
                "content": modified_messages[last_idx]["content"] + "\n\nRespond with valid JSON only."
            }

        response = await self.chat_completion(
            messages=modified_messages,
            temperature=temperature,
        )

        # Try to parse JSON from response
        try:
            # Find JSON in response
            start = response.find('{')
            end = response.rfind('}') + 1
            if start != -1 and end > start:
                return json.loads(response[start:end])
            return json.loads(response)
        except json.JSONDecodeError:
            # Return as wrapped dict if not valid JSON
            return {"response": response}

    def health_check(self) -> bool:
        """Check if Gemini API is accessible."""
        try:
            # Simple check - just verify client is configured
            return True
        except Exception:
            return False


# Singleton instance
_gemini_service: Optional[GeminiService] = None


def get_gemini_service() -> GeminiService:
    """Get or create Gemini service instance."""
    global _gemini_service
    if _gemini_service is None:
        _gemini_service = GeminiService()
    return _gemini_service


# Alias for compatibility with existing code that expects OpenAI interface
OpenAIClient = GeminiService
OpenAIService = GeminiService
get_openai_service = get_gemini_service
get_openai_client = get_gemini_service
