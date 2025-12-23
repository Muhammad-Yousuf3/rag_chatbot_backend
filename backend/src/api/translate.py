"""Translation API endpoints.

T059-T060 [US3] - Implements GET and POST /api/translate/{chapterSlug} endpoints.
T061 [US3] - Includes progress tracking.
"""

from typing import Union

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from ..db.database import get_db
from ..schemas.translate import (
    TranslationErrorResponse,
    TranslationPendingResponse,
    TranslationRequest,
    TranslationResponse,
)
from ..services.translation_service import TranslationService, get_translation_service

router = APIRouter(prefix="/translate", tags=["translate"])


@router.get(
    "/{chapter_slug}",
    response_model=Union[TranslationResponse, TranslationPendingResponse],
    summary="Get chapter translation",
    description="Get the Urdu translation for a chapter if available.",
    responses={
        200: {
            "description": "Translation found",
            "model": TranslationResponse,
        },
        202: {
            "description": "Translation in progress",
            "model": TranslationPendingResponse,
        },
        404: {
            "description": "Translation not found",
        },
    },
)
async def get_translation(
    chapter_slug: str,
    language: str = Query(default="ur", description="Target language code"),
    db: AsyncSession = Depends(get_db),
    translation_service: TranslationService = Depends(get_translation_service),
):
    """Get translation for a chapter.

    Args:
        chapter_slug: Chapter identifier.
        language: Target language code.
        db: Database session.
        translation_service: Translation service.

    Returns:
        TranslationResponse if completed, TranslationPendingResponse if in progress.

    Raises:
        HTTPException: If translation not found.
    """
    try:
        result = await translation_service.get_translation(
            db=db,
            chapter_slug=chapter_slug,
            language=language,
        )

        if result.status == "completed":
            return TranslationResponse(
                chapter_slug=result.chapter_slug,
                language=result.language,
                content=result.content or "",
                created_at=result.created_at or "",
            )
        elif result.status in ["pending", "in_progress"]:
            return TranslationPendingResponse(
                chapter_slug=result.chapter_slug,
                language=result.language,
                status=result.status,
                estimated_seconds=result.estimated_seconds,
            )
        elif result.status == "not_found":
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Translation not found for chapter: {chapter_slug}",
            )
        else:
            # Failed
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=result.error_message or "Translation failed",
            )

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.post(
    "/{chapter_slug}",
    response_model=Union[TranslationResponse, TranslationPendingResponse],
    status_code=status.HTTP_202_ACCEPTED,
    summary="Request chapter translation",
    description="Request Urdu translation for a chapter. Returns immediately with status.",
    responses={
        200: {
            "description": "Translation already completed",
            "model": TranslationResponse,
        },
        202: {
            "description": "Translation started or in progress",
            "model": TranslationPendingResponse,
        },
        400: {
            "description": "Invalid request",
        },
    },
)
async def request_translation(
    chapter_slug: str,
    request: TranslationRequest,
    db: AsyncSession = Depends(get_db),
    translation_service: TranslationService = Depends(get_translation_service),
):
    """Request translation for a chapter.

    Args:
        chapter_slug: Chapter identifier.
        request: Translation request with language and optional content.
        db: Database session.
        translation_service: Translation service.

    Returns:
        TranslationResponse if completed, TranslationPendingResponse if started.
    """
    try:
        # Check if content is provided, otherwise we need a content source
        if not request.content:
            # In a real implementation, you would fetch content from a content service
            # For now, return an error if content is not provided
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Content is required for translation. Please provide the chapter content.",
            )

        result = await translation_service.request_translation(
            db=db,
            chapter_slug=chapter_slug,
            content=request.content,
            language=request.language,
        )

        if result.status == "completed":
            return TranslationResponse(
                chapter_slug=result.chapter_slug,
                language=result.language,
                content=result.content or "",
                created_at=result.created_at or "",
            )
        elif result.status in ["pending", "in_progress"]:
            return TranslationPendingResponse(
                chapter_slug=result.chapter_slug,
                language=result.language,
                status=result.status,
                estimated_seconds=result.estimated_seconds,
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=result.error_message or "Translation request failed",
            )

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while processing the translation request.",
        )


@router.get(
    "/{chapter_slug}/progress",
    summary="Get translation progress",
    description="Get the progress status of a translation request.",
    responses={
        200: {"description": "Progress information"},
    },
)
async def get_translation_progress(
    chapter_slug: str,
    language: str = Query(default="ur", description="Target language code"),
    db: AsyncSession = Depends(get_db),
    translation_service: TranslationService = Depends(get_translation_service),
):
    """Get translation progress for a chapter.

    Args:
        chapter_slug: Chapter identifier.
        language: Target language code.
        db: Database session.
        translation_service: Translation service.

    Returns:
        Progress information dictionary.
    """
    try:
        progress = await translation_service.get_translation_progress(
            db=db,
            chapter_slug=chapter_slug,
            language=language,
        )
        return progress

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
