"""RAG Agent using Gemini API.

T027 [US1] - Implements the RAG agent for book-grounded Q&A using
Google Gemini for response generation.
T043 [US2] - Adds selected-text mode support.
T077-T078 [US4] - Adds personalization context support.
"""

import logging
from pathlib import Path
from typing import Any, Literal, Optional

from src.config import get_settings
from src.services.gemini_client import GeminiService, get_gemini_service

logger = logging.getLogger(__name__)

# Type alias for conversation modes
ConversationModeType = Literal["full_book", "selected_text"]


class RAGAgent:
    """Agent for book-grounded question answering."""

    NOT_COVERED_RESPONSE = (
        "This topic is not covered in this book. The book focuses on the "
        "specific technical content that has been indexed. You might want "
        "to consult other resources for information about this topic."
    )

    NOT_IN_SELECTION_RESPONSE = (
        "This is not mentioned in the selected text. The selection focuses on "
        "specific content that doesn't cover this topic. Please select "
        "additional text if you need information about this."
    )

    def __init__(
        self,
        gemini_client: GeminiService | None = None,
        system_prompt: str | None = None,
    ):
        """Initialize RAG agent.

        Args:
            gemini_client: Gemini client for API calls.
            system_prompt: Optional custom system prompt.
        """
        settings = get_settings()
        self._model = settings.chat_model
        self._max_tokens = settings.max_tokens
        self._gemini_client = gemini_client or get_gemini_service()

        # Load system prompts for both modes
        if system_prompt:
            self.system_prompt = system_prompt
        else:
            self.system_prompt = self._load_system_prompt("rag_system.txt")

        self.selected_text_prompt = self._load_system_prompt("selected_text.txt")

    def _load_system_prompt(self, filename: str = "rag_system.txt") -> str:
        """Load system prompt from template file.

        Args:
            filename: Name of the prompt file to load.

        Returns:
            System prompt string.
        """
        prompt_path = Path(__file__).parent / "prompts" / filename

        if prompt_path.exists():
            return prompt_path.read_text(encoding="utf-8")

        # Fallback default prompts
        if filename == "selected_text.txt":
            return """You are an expert AI assistant helping users understand
selected text. Base your answers ONLY on the selected text provided.
If the question cannot be answered from the selection, say "This is not
mentioned in the selected text." """

        return """You are an expert AI assistant specialized in answering questions
about technical book content. Base your answers ONLY on the provided context.
If the question cannot be answered from the context, say "This topic is not
covered in this book." Always cite your sources with chapter and page numbers."""

    async def generate_response(
        self,
        query: str,
        context: str | None,
        history: list[dict[str, str]] | None = None,
        is_covered: bool = True,
        mode: ConversationModeType = "full_book",
        personalization_context: Optional[str] = None,
    ) -> str:
        """Generate a response to the user's query.

        Args:
            query: User's question.
            context: Retrieved book context or selected text.
            history: Conversation history.
            is_covered: Whether the query is covered by content.
            mode: Conversation mode (full_book or selected_text).
            personalization_context: Optional personalization context for response adaptation.

        Returns:
            Generated response string.
        """
        logger.info(f"RAGAgent.generate_response called: query='{query[:50]}...', is_covered={is_covered}, mode={mode}, context_len={len(context) if context else 0}")

        # Handle not-covered case based on mode
        if not is_covered or not context:
            logger.info(f"Returning static response: is_covered={is_covered}, has_context={bool(context)}")
            if mode == "selected_text":
                return self.NOT_IN_SELECTION_RESPONSE
            return self.NOT_COVERED_RESPONSE

        # Select appropriate system prompt based on mode and personalization
        if personalization_context:
            base_prompt = self.selected_text_prompt if mode == "selected_text" else self.system_prompt
            system_prompt = f"{base_prompt}\n\n{personalization_context}"
        else:
            system_prompt = self.selected_text_prompt if mode == "selected_text" else self.system_prompt

        # Build messages for Gemini
        messages = self._build_messages(query, context, history, mode, personalization_context)

        # Add system prompt as first message
        full_messages = [{"role": "system", "content": system_prompt}] + messages

        logger.info(f"Calling Gemini API with {len(full_messages)} messages, model={self._model}")

        # Call Gemini API
        try:
            response = await self._gemini_client.chat_completion(
                messages=full_messages,
                temperature=0.3,
                max_tokens=self._max_tokens,
            )
            logger.info(f"Gemini API response received: '{response[:100] if response else 'EMPTY'}...'")
            return response
        except Exception as e:
            logger.error(f"Gemini API call failed: {type(e).__name__}: {e}", exc_info=True)
            raise

    def _build_messages(
        self,
        query: str,
        context: str,
        history: list[dict[str, str]] | None = None,
        mode: ConversationModeType = "full_book",
        personalization_context: Optional[str] = None,
    ) -> list[dict[str, str]]:
        """Build message list for the agent.

        Args:
            query: User's current question.
            context: Retrieved book context or selected text.
            history: Previous conversation messages.
            mode: Conversation mode.
            personalization_context: Optional personalization instructions.

        Returns:
            List of messages for the agent.
        """
        messages = []

        # Add conversation history (limited)
        if history:
            # Limit history to last 10 exchanges to manage token usage
            recent_history = history[-20:]  # Last 10 exchanges (user + assistant)
            messages.extend(recent_history)

        # Format context based on mode
        if mode == "selected_text":
            context_message = self.format_selected_text_prompt(context)
        else:
            context_message = self.format_context_prompt(context)

        # Add personalization note if provided
        user_note = ""
        if personalization_context:
            user_note = f"\n\n[User Context: {personalization_context}]"

        messages.append({
            "role": "user",
            "content": f"{context_message}{user_note}\n\nQuestion: {query}",
        })

        return messages

    def format_context_prompt(self, context: str) -> str:
        """Format the context into a prompt section for full book mode.

        Args:
            context: Raw context from retrieval.

        Returns:
            Formatted context prompt.
        """
        return f"""Here is the relevant content from the book that you should use to answer the question:

<book_context>
{context}
</book_context>

Please answer the following question based ONLY on the context provided above.
If the answer is not in the context, say "This topic is not covered in this book."
Always cite the specific chapter, section, and page numbers from the sources."""

    def format_selected_text_prompt(self, selected_text: str) -> str:
        """Format the selected text into a prompt section.

        Args:
            selected_text: User-selected text from the book.

        Returns:
            Formatted prompt for selected-text mode.
        """
        return f"""Here is the text that the user has selected and wants to discuss:

<selected_text>
{selected_text}
</selected_text>

Please answer the following question based ONLY on the selected text provided above.
Do not use any external knowledge or content from outside the selection.
If the question asks about something not mentioned in the selected text,
say "This is not mentioned in the selected text." """

    def format_source_citations(
        self, sources: list[dict[str, Any]]
    ) -> str:
        """Format source references into citation text.

        Args:
            sources: List of source references.

        Returns:
            Formatted citation string.
        """
        if not sources:
            return ""

        citations = []
        for source in sources:
            citation = f"[{source['chapter']}"
            if source.get("section"):
                citation += f", {source['section']}"
            if source.get("page"):
                citation += f", Page {source['page']}"
            citation += "]"
            citations.append(citation)

        return "Sources: " + ", ".join(citations)


def get_rag_agent() -> RAGAgent:
    """FastAPI dependency to get RAG agent instance.

    Returns:
        Configured RAGAgent instance.
    """
    return RAGAgent()
