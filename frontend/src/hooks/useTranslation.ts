/**
 * useTranslation React hook for managing translation state.
 *
 * T062 [US3] - Provides translation request and status management.
 */

import { useState, useCallback, useEffect, useRef } from 'react';
import { api, TranslationResponse, TranslationPendingResponse } from '../services/api';

export type TranslationStatus = 'idle' | 'loading' | 'polling' | 'completed' | 'error';

export interface UseTranslationOptions {
  /**
   * Polling interval in milliseconds for in-progress translations.
   */
  pollingInterval?: number;

  /**
   * Callback when translation completes.
   */
  onComplete?: (content: string) => void;

  /**
   * Callback when an error occurs.
   */
  onError?: (error: Error) => void;
}

export interface UseTranslationReturn {
  /**
   * Translated content (if completed).
   */
  content: string | null;

  /**
   * Current translation status.
   */
  status: TranslationStatus;

  /**
   * Error message if translation failed.
   */
  error: string | null;

  /**
   * Estimated seconds remaining (if in progress).
   */
  estimatedSeconds: number | null;

  /**
   * Request translation for a chapter.
   */
  requestTranslation: (chapterSlug: string, content: string) => Promise<void>;

  /**
   * Get existing translation for a chapter.
   */
  getTranslation: (chapterSlug: string) => Promise<void>;

  /**
   * Reset translation state.
   */
  reset: () => void;
}

/**
 * Custom hook for managing chapter translations.
 *
 * @param options - Configuration options
 * @returns Translation state and actions
 */
export function useTranslation(
  options: UseTranslationOptions = {}
): UseTranslationReturn {
  const { pollingInterval = 3000, onComplete, onError } = options;

  const [content, setContent] = useState<string | null>(null);
  const [status, setStatus] = useState<TranslationStatus>('idle');
  const [error, setError] = useState<string | null>(null);
  const [estimatedSeconds, setEstimatedSeconds] = useState<number | null>(null);

  // Refs for polling
  const pollingRef = useRef<NodeJS.Timeout | null>(null);
  const currentChapterRef = useRef<string | null>(null);

  /**
   * Stop polling.
   */
  const stopPolling = useCallback(() => {
    if (pollingRef.current) {
      clearInterval(pollingRef.current);
      pollingRef.current = null;
    }
  }, []);

  /**
   * Handle translation response.
   */
  const handleResponse = useCallback(
    (response: TranslationResponse | TranslationPendingResponse) => {
      if ('content' in response) {
        // Completed translation
        setContent(response.content);
        setStatus('completed');
        setEstimatedSeconds(null);
        stopPolling();
        onComplete?.(response.content);
      } else {
        // Pending translation
        setStatus('polling');
        setEstimatedSeconds(response.estimated_seconds ?? null);
      }
    },
    [stopPolling, onComplete]
  );

  /**
   * Poll for translation status.
   */
  const pollTranslation = useCallback(
    async (chapterSlug: string) => {
      try {
        const response = await api.getTranslation(chapterSlug);
        handleResponse(response);
      } catch (err) {
        // Continue polling on error (might be temporary)
        console.warn('Polling error:', err);
      }
    },
    [handleResponse]
  );

  /**
   * Start polling for a chapter.
   */
  const startPolling = useCallback(
    (chapterSlug: string) => {
      stopPolling();
      currentChapterRef.current = chapterSlug;

      pollingRef.current = setInterval(() => {
        if (currentChapterRef.current === chapterSlug) {
          pollTranslation(chapterSlug);
        }
      }, pollingInterval);
    },
    [pollingInterval, pollTranslation, stopPolling]
  );

  /**
   * Request translation for a chapter.
   */
  const requestTranslation = useCallback(
    async (chapterSlug: string, chapterContent: string): Promise<void> => {
      setStatus('loading');
      setError(null);
      setContent(null);
      currentChapterRef.current = chapterSlug;

      try {
        const response = await api.requestTranslation(chapterSlug);

        if ('content' in response) {
          // Already completed
          handleResponse(response);
        } else {
          // In progress, start polling
          handleResponse(response);
          startPolling(chapterSlug);
        }
      } catch (err) {
        const errorMessage = err instanceof Error ? err.message : 'Translation request failed';
        setError(errorMessage);
        setStatus('error');
        onError?.(err instanceof Error ? err : new Error(errorMessage));
      }
    },
    [handleResponse, startPolling, onError]
  );

  /**
   * Get existing translation for a chapter.
   */
  const getTranslation = useCallback(
    async (chapterSlug: string): Promise<void> => {
      setStatus('loading');
      setError(null);
      currentChapterRef.current = chapterSlug;

      try {
        const response = await api.getTranslation(chapterSlug);
        handleResponse(response);

        if (!('content' in response)) {
          // In progress, start polling
          startPolling(chapterSlug);
        }
      } catch (err) {
        const errorMessage = err instanceof Error ? err.message : 'Failed to get translation';
        setError(errorMessage);
        setStatus('error');
        onError?.(err instanceof Error ? err : new Error(errorMessage));
      }
    },
    [handleResponse, startPolling, onError]
  );

  /**
   * Reset translation state.
   */
  const reset = useCallback(() => {
    stopPolling();
    setContent(null);
    setStatus('idle');
    setError(null);
    setEstimatedSeconds(null);
    currentChapterRef.current = null;
  }, [stopPolling]);

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      stopPolling();
    };
  }, [stopPolling]);

  return {
    content,
    status,
    error,
    estimatedSeconds,
    requestTranslation,
    getTranslation,
    reset,
  };
}

export default useTranslation;
