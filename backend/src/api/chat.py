"""Chat API endpoints.

T029 [US1] - Implements POST /api/chat endpoint for book-grounded Q&A.
T044 [US2] - Implements POST /api/chat/selected endpoint for selected-text mode.
T080-T081 [US4] - Implements conversation history endpoints.
"""

import logging
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status

logger = logging.getLogger(__name__)
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from .auth import get_current_user_optional, get_current_user_required
from ..db.database import get_db
from ..models.conversation import Conversation
from ..schemas.auth import (
    ConversationDetailResponse,
    ConversationListResponse,
    ConversationSummary,
    MessageResponse,
)
from ..schemas.chat import ChatRequest, ChatResponse, SelectedTextRequest, SourceReference
from ..services.agent_service import AgentService, get_agent_service

router = APIRouter(prefix="/chat", tags=["chat"])


@router.post(
    "",
    response_model=ChatResponse,
    status_code=status.HTTP_200_OK,
    summary="Send a chat message",
    description="Send a message and receive a book-grounded response with source citations.",
    responses={
        200: {
            "description": "Successful response with answer and sources",
            "model": ChatResponse,
        },
        422: {
            "description": "Validation error",
        },
        500: {
            "description": "Internal server error",
        },
    },
)
async def chat(
    request: ChatRequest,
    db: AsyncSession = Depends(get_db),
    agent_service: AgentService = Depends(get_agent_service),
) -> ChatResponse:
    """Process a chat message and return book-grounded response.

    Args:
        request: Chat request with message and optional conversation_id.
        db: Database session.
        agent_service: Agent service for processing.

    Returns:
        ChatResponse with message, conversation_id, and sources.
    """
    try:
        logger.info(f"Processing chat request: message='{request.message[:50]}...', conversation_id={request.conversation_id}")

        result = await agent_service.chat(
            db=db,
            message=request.message,
            conversation_id=request.conversation_id,
        )

        logger.info(f"Chat response generated successfully: conversation_id={result.conversation_id}, sources_count={len(result.sources)}")

        return ChatResponse(
            message=result.message,
            conversation_id=result.conversation_id,
            sources=[
                SourceReference(**source)
                for source in result.sources
            ],
        )

    except ValueError as e:
        logger.warning(f"ValueError in chat endpoint: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except Exception as e:
        logger.error(f"Error in chat endpoint: {type(e).__name__}: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while processing your request: {str(e)}",
        )


@router.post(
    "/selected",
    response_model=ChatResponse,
    status_code=status.HTTP_200_OK,
    summary="Send a message about selected text",
    description="Send a message about user-selected text and receive a response based only on that selection.",
    responses={
        200: {
            "description": "Successful response based on selected text",
            "model": ChatResponse,
        },
        422: {
            "description": "Validation error (invalid message or selected text)",
        },
        500: {
            "description": "Internal server error",
        },
    },
)
async def chat_selected(
    request: SelectedTextRequest,
    db: AsyncSession = Depends(get_db),
    agent_service: AgentService = Depends(get_agent_service),
) -> ChatResponse:
    """Process a chat message about selected text.

    The response will be based ONLY on the provided selected text,
    not on the full book content. This is useful for discussing
    specific paragraphs or sections.

    Args:
        request: Request with message, selected_text, and optional conversation_id.
        db: Database session.
        agent_service: Agent service for processing.

    Returns:
        ChatResponse with message, conversation_id, and empty sources.
    """
    try:
        logger.info(f"Processing chat_selected request: message='{request.message[:50]}...', selected_text_len={len(request.selected_text)}")

        result = await agent_service.chat_selected(
            db=db,
            message=request.message,
            selected_text=request.selected_text,
            conversation_id=request.conversation_id,
        )

        logger.info(f"Chat selected response generated successfully: conversation_id={result.conversation_id}")

        return ChatResponse(
            message=result.message,
            conversation_id=result.conversation_id,
            sources=[],  # No book sources for selected-text mode
        )

    except ValueError as e:
        logger.warning(f"ValueError in chat_selected endpoint: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except Exception as e:
        logger.error(f"Error in chat_selected endpoint: {type(e).__name__}: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An error occurred while processing your request: {str(e)}",
        )


@router.get(
    "/conversations",
    response_model=ConversationListResponse,
    summary="List conversations",
    description="Get list of conversations for the current user.",
    responses={
        200: {"description": "List of conversations"},
        401: {"description": "Not authenticated"},
    },
)
async def list_conversations(
    limit: int = Query(default=20, ge=1, le=100, description="Number of conversations to return"),
    offset: int = Query(default=0, ge=0, description="Number of conversations to skip"),
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user_required),
):
    """List conversations for the current user.

    Args:
        limit: Maximum number of conversations to return.
        offset: Number of conversations to skip.
        db: Database session.
        current_user: Authenticated user.

    Returns:
        List of conversation summaries.
    """
    user_id = current_user["id"]

    # Get total count
    count_stmt = select(func.count(Conversation.id)).where(
        Conversation.user_id == user_id
    )
    count_result = await db.execute(count_stmt)
    total = count_result.scalar() or 0

    # Get conversations with message count
    stmt = (
        select(Conversation)
        .options(selectinload(Conversation.messages))
        .where(Conversation.user_id == user_id)
        .order_by(Conversation.updated_at.desc())
        .limit(limit)
        .offset(offset)
    )
    result = await db.execute(stmt)
    conversations = result.scalars().all()

    # Build response
    conversation_summaries = []
    for conv in conversations:
        messages = conv.messages or []
        last_message = messages[-1] if messages else None

        conversation_summaries.append(
            ConversationSummary(
                id=str(conv.id),
                mode=conv.mode.value,
                message_count=len(messages),
                last_message_preview=(
                    last_message.content[:100] + "..."
                    if last_message and len(last_message.content) > 100
                    else (last_message.content if last_message else None)
                ),
                created_at=str(conv.created_at),
                updated_at=str(conv.updated_at),
            )
        )

    return ConversationListResponse(
        conversations=conversation_summaries,
        total=total,
    )


@router.get(
    "/conversations/{conversation_id}",
    response_model=ConversationDetailResponse,
    summary="Get conversation",
    description="Get a specific conversation with its messages.",
    responses={
        200: {"description": "Conversation details"},
        401: {"description": "Not authenticated"},
        404: {"description": "Conversation not found"},
    },
)
async def get_conversation(
    conversation_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user_required),
):
    """Get a specific conversation with all messages.

    Args:
        conversation_id: Conversation ID.
        db: Database session.
        current_user: Authenticated user.

    Returns:
        Conversation details with messages.

    Raises:
        HTTPException: If conversation not found or belongs to another user.
    """
    user_id = current_user["id"]

    # Get conversation with messages
    stmt = (
        select(Conversation)
        .options(selectinload(Conversation.messages))
        .where(Conversation.id == conversation_id)
    )
    result = await db.execute(stmt)
    conversation = result.scalar_one_or_none()

    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found",
        )

    # Check ownership - return 404 to not reveal existence
    if conversation.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found",
        )

    # Build response
    messages = [
        MessageResponse(
            id=str(msg.id),
            role=msg.role.value,
            content=msg.content,
            created_at=str(msg.created_at),
        )
        for msg in (conversation.messages or [])
    ]

    return ConversationDetailResponse(
        id=str(conversation.id),
        user_id=str(conversation.user_id) if conversation.user_id else None,
        mode=conversation.mode.value,
        selected_text=conversation.selected_text,
        messages=messages,
        created_at=str(conversation.created_at),
        updated_at=str(conversation.updated_at),
    )
