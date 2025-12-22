/**
 * ChatInput component for message input and submission.
 *
 * T035 [US1] - Provides text input with submit functionality for chat.
 */

import React, { useState, useCallback, useRef, useEffect } from 'react';

export interface ChatInputProps {
  onSend: (message: string) => void;
  disabled?: boolean;
  placeholder?: string;
  maxLength?: number;
}

/**
 * Component for chat message input.
 */
export const ChatInput: React.FC<ChatInputProps> = ({
  onSend,
  disabled = false,
  placeholder = 'Ask a question about the book...',
  maxLength = 10000,
}) => {
  const [message, setMessage] = useState('');
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  /**
   * Handle input change.
   */
  const handleChange = useCallback(
    (e: React.ChangeEvent<HTMLTextAreaElement>) => {
      const value = e.target.value;
      if (value.length <= maxLength) {
        setMessage(value);
      }
    },
    [maxLength]
  );

  /**
   * Handle form submission.
   */
  const handleSubmit = useCallback(
    (e?: React.FormEvent) => {
      if (e) {
        e.preventDefault();
      }

      const trimmedMessage = message.trim();
      if (trimmedMessage && !disabled) {
        onSend(trimmedMessage);
        setMessage('');

        // Reset textarea height
        if (textareaRef.current) {
          textareaRef.current.style.height = 'auto';
        }
      }
    },
    [message, disabled, onSend]
  );

  /**
   * Handle keyboard shortcuts.
   */
  const handleKeyDown = useCallback(
    (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
      // Submit on Enter (without Shift)
      if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        handleSubmit();
      }
    },
    [handleSubmit]
  );

  /**
   * Auto-resize textarea based on content.
   */
  useEffect(() => {
    const textarea = textareaRef.current;
    if (textarea) {
      textarea.style.height = 'auto';
      textarea.style.height = `${Math.min(textarea.scrollHeight, 200)}px`;
    }
  }, [message]);

  const charactersRemaining = maxLength - message.length;
  const showCharacterCount = message.length > maxLength * 0.8;

  return (
    <form
      className="chat-input"
      onSubmit={handleSubmit}
      style={{
        display: 'flex',
        flexDirection: 'column',
        gap: '8px',
        padding: '16px',
        borderTop: '1px solid #e0e0e0',
        backgroundColor: '#ffffff',
      }}
    >
      <div
        className="chat-input__container"
        style={{
          display: 'flex',
          gap: '8px',
          alignItems: 'flex-end',
        }}
      >
        <textarea
          ref={textareaRef}
          className="chat-input__textarea"
          value={message}
          onChange={handleChange}
          onKeyDown={handleKeyDown}
          placeholder={placeholder}
          disabled={disabled}
          rows={1}
          style={{
            flex: 1,
            padding: '12px',
            border: '1px solid #cccccc',
            borderRadius: '8px',
            resize: 'none',
            fontFamily: 'inherit',
            fontSize: '14px',
            lineHeight: '1.4',
            minHeight: '44px',
            maxHeight: '200px',
            outline: 'none',
            opacity: disabled ? 0.6 : 1,
          }}
          aria-label="Chat message input"
        />
        <button
          type="submit"
          className="chat-input__submit"
          disabled={disabled || !message.trim()}
          style={{
            padding: '12px 24px',
            border: 'none',
            borderRadius: '8px',
            backgroundColor:
              disabled || !message.trim() ? '#cccccc' : '#0066cc',
            color: '#ffffff',
            fontWeight: 'bold',
            cursor: disabled || !message.trim() ? 'not-allowed' : 'pointer',
            transition: 'background-color 0.2s',
          }}
          aria-label="Send message"
        >
          Send
        </button>
      </div>

      {/* Character count and hints */}
      <div
        className="chat-input__footer"
        style={{
          display: 'flex',
          justifyContent: 'space-between',
          fontSize: '12px',
          color: '#666666',
        }}
      >
        <span className="chat-input__hint">
          Press Enter to send, Shift+Enter for new line
        </span>
        {showCharacterCount && (
          <span
            className="chat-input__character-count"
            style={{
              color: charactersRemaining < 100 ? '#cc0000' : '#666666',
            }}
          >
            {charactersRemaining} characters remaining
          </span>
        )}
      </div>
    </form>
  );
};

export default ChatInput;
