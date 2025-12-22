/**
 * useChat React hook for managing chat state and API interactions.
 *
 * T033 [US1] - Provides state management and API integration for chat functionality.
 * T048 [US2] - Adds selected-text mode support.
 */

import { useState, useCallback, useRef } from 'react';
import { chatApi, SourceReference } from '../services/api';

export type ChatMode = 'full_book' | 'selected_text';

export interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  sources?: SourceReference[];
  timestamp: Date;
}

export interface UseChatOptions {
  initialConversationId?: string;
  onError?: (error: Error) => void;
}

export interface UseChatReturn {
  messages: Message[];
  conversationId: string | null;
  isLoading: boolean;
  error: Error | null;
  mode: ChatMode;
  selectedText: string | null;
  sendMessage: (content: string) => Promise<void>;
  sendSelectedTextMessage: (content: string, selectedText: string) => Promise<void>;
  enterSelectedTextMode: (text: string) => void;
  exitSelectedTextMode: () => void;
  clearConversation: () => void;
  retryLastMessage: () => Promise<void>;
}

/**
 * Custom hook for managing chat interactions.
 *
 * @param options - Configuration options
 * @returns Chat state and actions
 */
export function useChat(options: UseChatOptions = {}): UseChatReturn {
  const { initialConversationId, onError } = options;

  const [messages, setMessages] = useState<Message[]>([]);
  const [conversationId, setConversationId] = useState<string | null>(
    initialConversationId || null
  );
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<Error | null>(null);
  const [mode, setMode] = useState<ChatMode>('full_book');
  const [selectedText, setSelectedText] = useState<string | null>(null);

  // Store the last user message for retry functionality
  const lastUserMessageRef = useRef<string | null>(null);
  const lastSelectedTextRef = useRef<string | null>(null);

  /**
   * Generate a unique message ID.
   */
  const generateMessageId = useCallback((): string => {
    return `msg_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
  }, []);

  /**
   * Send a message and get a response.
   */
  const sendMessage = useCallback(
    async (content: string): Promise<void> => {
      if (!content.trim() || isLoading) {
        return;
      }

      const trimmedContent = content.trim();
      lastUserMessageRef.current = trimmedContent;

      // Add user message immediately
      const userMessage: Message = {
        id: generateMessageId(),
        role: 'user',
        content: trimmedContent,
        timestamp: new Date(),
      };

      setMessages((prev) => [...prev, userMessage]);
      setIsLoading(true);
      setError(null);

      try {
        const response = await chatApi.sendMessage({
          message: trimmedContent,
          conversation_id: conversationId || undefined,
        });

        // Update conversation ID if this is a new conversation
        if (!conversationId) {
          setConversationId(response.conversation_id);
        }

        // Add assistant message
        const assistantMessage: Message = {
          id: generateMessageId(),
          role: 'assistant',
          content: response.message,
          sources: response.sources,
          timestamp: new Date(),
        };

        setMessages((prev) => [...prev, assistantMessage]);
      } catch (err) {
        const error = err instanceof Error ? err : new Error('Failed to send message');
        setError(error);

        // Remove the user message on error
        setMessages((prev) => prev.filter((m) => m.id !== userMessage.id));

        if (onError) {
          onError(error);
        }
      } finally {
        setIsLoading(false);
      }
    },
    [conversationId, isLoading, generateMessageId, onError]
  );

  /**
   * Send a message about selected text.
   */
  const sendSelectedTextMessage = useCallback(
    async (content: string, text: string): Promise<void> => {
      if (!content.trim() || !text.trim() || isLoading) {
        return;
      }

      const trimmedContent = content.trim();
      const trimmedText = text.trim();
      lastUserMessageRef.current = trimmedContent;
      lastSelectedTextRef.current = trimmedText;

      // Add user message immediately
      const userMessage: Message = {
        id: generateMessageId(),
        role: 'user',
        content: trimmedContent,
        timestamp: new Date(),
      };

      setMessages((prev) => [...prev, userMessage]);
      setIsLoading(true);
      setError(null);

      try {
        const response = await chatApi.sendSelectedTextMessage({
          message: trimmedContent,
          selected_text: trimmedText,
          conversation_id: conversationId || undefined,
        });

        // Update conversation ID if this is a new conversation
        if (!conversationId) {
          setConversationId(response.conversation_id);
        }

        // Add assistant message (no sources for selected-text mode)
        const assistantMessage: Message = {
          id: generateMessageId(),
          role: 'assistant',
          content: response.message,
          sources: [], // No book sources for selected-text mode
          timestamp: new Date(),
        };

        setMessages((prev) => [...prev, assistantMessage]);
      } catch (err) {
        const error = err instanceof Error ? err : new Error('Failed to send message');
        setError(error);

        // Remove the user message on error
        setMessages((prev) => prev.filter((m) => m.id !== userMessage.id));

        if (onError) {
          onError(error);
        }
      } finally {
        setIsLoading(false);
      }
    },
    [conversationId, isLoading, generateMessageId, onError]
  );

  /**
   * Enter selected-text mode with the given text.
   */
  const enterSelectedTextMode = useCallback((text: string): void => {
    setMode('selected_text');
    setSelectedText(text);
    // Clear conversation when entering selected-text mode
    setMessages([]);
    setConversationId(null);
    setError(null);
  }, []);

  /**
   * Exit selected-text mode and return to full book mode.
   */
  const exitSelectedTextMode = useCallback((): void => {
    setMode('full_book');
    setSelectedText(null);
    // Clear conversation when exiting selected-text mode
    setMessages([]);
    setConversationId(null);
    setError(null);
    lastSelectedTextRef.current = null;
  }, []);

  /**
   * Clear the conversation and start fresh.
   */
  const clearConversation = useCallback((): void => {
    setMessages([]);
    setConversationId(null);
    setError(null);
    lastUserMessageRef.current = null;
    lastSelectedTextRef.current = null;
    // Also reset mode
    setMode('full_book');
    setSelectedText(null);
  }, []);

  /**
   * Retry the last message if it failed.
   */
  const retryLastMessage = useCallback(async (): Promise<void> => {
    if (lastUserMessageRef.current && !isLoading) {
      const lastMessage = lastUserMessageRef.current;
      // Remove the last failed attempt
      setMessages((prev) => {
        const lastUserMsgIndex = [...prev].reverse().findIndex((m) => m.role === 'user');
        if (lastUserMsgIndex >= 0) {
          const actualIndex = prev.length - 1 - lastUserMsgIndex;
          return prev.slice(0, actualIndex);
        }
        return prev;
      });

      // Retry in the appropriate mode
      if (mode === 'selected_text' && lastSelectedTextRef.current) {
        await sendSelectedTextMessage(lastMessage, lastSelectedTextRef.current);
      } else {
        await sendMessage(lastMessage);
      }
    }
  }, [isLoading, mode, sendMessage, sendSelectedTextMessage]);

  return {
    messages,
    conversationId,
    isLoading,
    error,
    mode,
    selectedText,
    sendMessage,
    sendSelectedTextMessage,
    enterSelectedTextMode,
    exitSelectedTextMode,
    clearConversation,
    retryLastMessage,
  };
}

export default useChat;
