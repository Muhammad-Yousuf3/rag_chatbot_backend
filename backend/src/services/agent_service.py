"""Agent service orchestration layer.

T028 [US1] - Orchestrates RAG retrieval, agent response generation,
and conversation management.
T043 [US2] - Adds selected-text mode support.
"""

import logging
import uuid
from dataclasses import dataclass
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

logger = logging.getLogger(__name__)

from ..agents.rag_agent import RAGAgent, get_rag_agent
from ..models.conversation import Conversation, ConversationMode
from ..models.message import Message, MessageRole
from .rag_service import RAGService, SourceReference, get_rag_service


@dataclass
class ChatResponse:
    """Response from chat interaction."""

    message: str
    conversation_id: str
    sources: list[dict[str, Any]]

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for API response."""
        return {
            "message": self.message,
            "conversation_id": self.conversation_id,
            "sources": self.sources,
        }


class AgentService:
    """Service for orchestrating agent interactions."""

    def __init__(
        self,
        rag_service: RAGService | None = None,
        rag_agent: RAGAgent | None = None,
    ):
        """Initialize agent service.

        Args:
            rag_service: RAG retrieval service.
            rag_agent: RAG agent for response generation.
        """
        self.rag_service = rag_service or get_rag_service()
        self.rag_agent = rag_agent or get_rag_agent()

    async def chat(
        self,
        db: AsyncSession,
        message: str,
        conversation_id: str | None = None,
        user_id: str | None = None,
    ) -> ChatResponse:
        """Process a chat message and generate response.

        Args:
            db: Database session.
            message: User's message.
            conversation_id: Optional existing conversation ID.
            user_id: Optional user ID for authenticated users.

        Returns:
            ChatResponse with message, conversation_id, and sources.
        """
        logger.info(f"AgentService.chat called with message: '{message[:50]}...'")

        # Get or create conversation
        conversation = await self._get_or_create_conversation(
            db, conversation_id, user_id
        )
        logger.info(f"Conversation: {conversation.id}")

        # Get conversation history
        history = await self._get_conversation_history(db, conversation.id)
        logger.info(f"History messages: {len(history)}")

        # Retrieve relevant chunks
        logger.info("Retrieving relevant chunks from Qdrant...")
        chunks = await self.rag_service.retrieve_relevant_chunks(message)
        is_covered = len(chunks) > 0
        logger.info(f"Retrieved {len(chunks)} chunks, is_covered={is_covered}")

        # Build context and sources
        context = self.rag_service.build_context(chunks)
        source_refs = self.rag_service.extract_sources(chunks)
        logger.info(f"Context length: {len(context)}, sources: {len(source_refs)}")

        # Generate response
        logger.info("Calling RAG agent to generate response...")
        response_text = await self.rag_agent.generate_response(
            query=message,
            context=context,
            history=history,
            is_covered=is_covered,
        )
        logger.info(f"RAG agent response received: '{response_text[:100] if response_text else 'EMPTY'}...'")

        # Save messages to database
        await self._save_messages(
            db,
            conversation.id,
            user_message=message,
            assistant_message=response_text,
            source_refs=[s.to_dict() for s in source_refs],
        )
        logger.info("Messages saved to database")

        return ChatResponse(
            message=response_text,
            conversation_id=str(conversation.id),
            sources=[s.to_dict() for s in source_refs],
        )

    async def chat_selected(
        self,
        db: AsyncSession,
        message: str,
        selected_text: str,
        conversation_id: str | None = None,
        user_id: str | None = None,
    ) -> ChatResponse:
        """Process a chat message about selected text.

        Args:
            db: Database session.
            message: User's message about the selected text.
            selected_text: The text selected by the user.
            conversation_id: Optional existing conversation ID.
            user_id: Optional user ID for authenticated users.

        Returns:
            ChatResponse with message, conversation_id, and empty sources.
        """
        # Get or create conversation with selected_text mode
        conversation = await self._get_or_create_conversation(
            db, conversation_id, user_id, mode=ConversationMode.SELECTED_TEXT,
            selected_text=selected_text,
        )

        # Get conversation history
        history = await self._get_conversation_history(db, conversation.id)

        # For selected-text mode, context is always covered (it's the selection)
        # The agent will determine if the question relates to the selection
        is_covered = True

        # Generate response using selected text as context
        response_text = await self.rag_agent.generate_response(
            query=message,
            context=selected_text,
            history=history,
            is_covered=is_covered,
            mode="selected_text",
        )

        # Save messages to database (no sources for selected-text mode)
        await self._save_messages(
            db,
            conversation.id,
            user_message=message,
            assistant_message=response_text,
            source_refs=[],
        )

        return ChatResponse(
            message=response_text,
            conversation_id=str(conversation.id),
            sources=[],  # No book sources for selected-text mode
        )

    async def _get_or_create_conversation(
        self,
        db: AsyncSession,
        conversation_id: str | None,
        user_id: str | None,
        mode: ConversationMode = ConversationMode.FULL_BOOK,
        selected_text: str | None = None,
    ) -> Conversation:
        """Get existing conversation or create new one.

        Args:
            db: Database session.
            conversation_id: Optional existing conversation ID.
            user_id: Optional user ID.
            mode: Conversation mode (full_book or selected_text).
            selected_text: Selected text for selected_text mode.

        Returns:
            Conversation instance.
        """
        if conversation_id:
            # Try to get existing conversation
            result = await db.execute(
                select(Conversation).where(Conversation.id == conversation_id)
            )
            conversation = result.scalar_one_or_none()

            if conversation:
                return conversation

        # Create new conversation
        conversation = Conversation(
            id=str(uuid.uuid4()),
            user_id=user_id,
            mode=mode,
            selected_text=selected_text if mode == ConversationMode.SELECTED_TEXT else None,
        )
        db.add(conversation)
        await db.commit()
        await db.refresh(conversation)

        return conversation

    async def _get_conversation_history(
        self,
        db: AsyncSession,
        conversation_id: str,
    ) -> list[dict[str, str]]:
        """Get conversation history as message list.

        Args:
            db: Database session.
            conversation_id: Conversation ID.

        Returns:
            List of message dicts with role and content.
        """
        result = await db.execute(
            select(Message)
            .where(Message.conversation_id == conversation_id)
            .order_by(Message.created_at.asc())
        )
        messages = result.scalars().all()

        return [
            {"role": msg.role.value, "content": msg.content}
            for msg in messages
        ]

    async def _save_messages(
        self,
        db: AsyncSession,
        conversation_id: str,
        user_message: str,
        assistant_message: str,
        source_refs: list[dict[str, Any]],
    ) -> None:
        """Save user and assistant messages to database.

        Args:
            db: Database session.
            conversation_id: Conversation ID.
            user_message: User's message content.
            assistant_message: Assistant's response content.
            source_refs: Source references for assistant message.
        """
        # Save user message
        user_msg = Message(
            id=str(uuid.uuid4()),
            conversation_id=conversation_id,
            role=MessageRole.USER,
            content=user_message,
        )
        db.add(user_msg)

        # Save assistant message with sources
        assistant_msg = Message(
            id=str(uuid.uuid4()),
            conversation_id=conversation_id,
            role=MessageRole.ASSISTANT,
            content=assistant_message,
            source_refs=source_refs if source_refs else None,
        )
        db.add(assistant_msg)

        await db.commit()


def get_agent_service() -> AgentService:
    """FastAPI dependency to get agent service instance.

    Returns:
        Configured AgentService instance.
    """
    return AgentService()


def create_agent_service(
    rag_service: "RAGService | None" = None,
    rag_agent: "RAGAgent | None" = None,
) -> AgentService:
    """Factory function to create agent service instance with custom dependencies.

    Use this for testing or custom configurations. For FastAPI endpoints,
    use get_agent_service() instead.

    Args:
        rag_service: Optional RAG service.
        rag_agent: Optional RAG agent.

    Returns:
        Configured AgentService instance.
    """
    return AgentService(
        rag_service=rag_service,
        rag_agent=rag_agent,
    )
