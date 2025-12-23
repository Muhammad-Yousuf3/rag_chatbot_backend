"""LLM client wrapper - redirects to Gemini implementation.

This file maintains backward compatibility by re-exporting from gemini_client.
"""

from .gemini_client import (
    GeminiService,
    get_gemini_service,
)

# Re-export with OpenAI-compatible names for backward compatibility
OpenAIService = GeminiService
OpenAIClient = GeminiService
get_openai_service = get_gemini_service
get_openai_client = get_gemini_service
