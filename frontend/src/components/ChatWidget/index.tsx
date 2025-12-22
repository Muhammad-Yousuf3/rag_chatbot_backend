/**
 * ChatWidget main component.
 *
 * T036-T037 [US1] - Main chat interface component with error handling and loading states.
 * T048-T050 [US2] - Adds selected-text mode integration with mode indicator and exit functionality.
 * T084 [US4] - Adds authentication state integration.
 */

import React, { useEffect, useRef, useCallback, useState } from 'react';
import { useChat, Message, ChatMode } from '../../hooks/useChat';
import { ChatMessage } from './ChatMessage';
import { ChatInput } from './ChatInput';
import { UserResponse } from '../../services/api';

export interface ChatWidgetProps {
  /**
   * Optional initial conversation ID to continue an existing conversation.
   */
  initialConversationId?: string;

  /**
   * Widget title displayed in the header.
   */
  title?: string;

  /**
   * Callback when an error occurs.
   */
  onError?: (error: Error) => void;

  /**
   * Custom class name for styling.
   */
  className?: string;

  /**
   * Whether the widget is minimized/collapsed.
   */
  minimized?: boolean;

  /**
   * Callback when minimize/maximize button is clicked.
   */
  onToggleMinimize?: () => void;

  /**
   * Selected text to discuss (triggers selected-text mode).
   */
  selectedText?: string;

  /**
   * Callback when exiting selected-text mode.
   */
  onExitSelectedTextMode?: () => void;

  /**
   * Current authenticated user (optional).
   */
  user?: UserResponse | null;

  /**
   * Whether user is authenticated.
   */
  isAuthenticated?: boolean;

  /**
   * Callback to open login modal.
   */
  onLoginClick?: () => void;

  /**
   * Callback to logout user.
   */
  onLogout?: () => void;
}

/**
 * Loading indicator component.
 */
const LoadingIndicator: React.FC = () => (
  <div
    className="chat-widget__loading"
    style={{
      display: 'flex',
      alignItems: 'center',
      gap: '8px',
      padding: '12px 16px',
      marginBottom: '16px',
    }}
  >
    <ChatMessage
      role="assistant"
      content=""
      isLoading={true}
    />
  </div>
);

/**
 * Error display component.
 */
const ErrorDisplay: React.FC<{
  error: Error;
  onRetry: () => void;
}> = ({ error, onRetry }) => (
  <div
    className="chat-widget__error"
    style={{
      padding: '12px 16px',
      margin: '0 16px 16px',
      backgroundColor: '#fff0f0',
      border: '1px solid #ffcccc',
      borderRadius: '8px',
      color: '#cc0000',
      display: 'flex',
      flexDirection: 'column',
      gap: '8px',
    }}
  >
    <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
      <span style={{ fontWeight: 'bold' }}>Error:</span>
      <span>{error.message}</span>
    </div>
    <button
      onClick={onRetry}
      style={{
        alignSelf: 'flex-start',
        padding: '8px 16px',
        border: '1px solid #cc0000',
        borderRadius: '4px',
        backgroundColor: 'transparent',
        color: '#cc0000',
        cursor: 'pointer',
      }}
    >
      Retry
    </button>
  </div>
);

/**
 * Empty state component.
 */
const EmptyState: React.FC<{ isSelectedTextMode?: boolean }> = ({
  isSelectedTextMode = false
}) => (
  <div
    className="chat-widget__empty"
    style={{
      display: 'flex',
      flexDirection: 'column',
      alignItems: 'center',
      justifyContent: 'center',
      padding: '48px 24px',
      textAlign: 'center',
      color: '#666666',
    }}
  >
    <div style={{ fontSize: '48px', marginBottom: '16px' }}>
      {isSelectedTextMode ? '📝' : '📚'}
    </div>
    <h3 style={{ margin: '0 0 8px', color: '#333333' }}>
      {isSelectedTextMode
        ? 'Ask about the selected text'
        : 'Ask questions about the book'
      }
    </h3>
    <p style={{ margin: 0, maxWidth: '300px' }}>
      {isSelectedTextMode
        ? 'I\'ll answer questions based only on the text you selected. Ask anything about that specific content!'
        : 'I can help answer questions based on the book\'s content. Ask anything about the topics covered!'
      }
    </p>
  </div>
);

/**
 * Selected-text mode banner component.
 */
const SelectedTextBanner: React.FC<{
  selectedText: string;
  onExit: () => void;
}> = ({ selectedText, onExit }) => (
  <div
    className="chat-widget__selected-text-banner"
    style={{
      padding: '12px 16px',
      backgroundColor: '#e8f4fd',
      borderBottom: '1px solid #b3d7f5',
      display: 'flex',
      flexDirection: 'column',
      gap: '8px',
    }}
  >
    <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
        <span style={{ fontSize: '16px' }}>📝</span>
        <span style={{ fontWeight: 'bold', color: '#0066cc', fontSize: '13px' }}>
          Selected Text Mode
        </span>
      </div>
      <button
        onClick={onExit}
        style={{
          padding: '4px 12px',
          border: '1px solid #0066cc',
          borderRadius: '4px',
          backgroundColor: 'transparent',
          color: '#0066cc',
          cursor: 'pointer',
          fontSize: '12px',
          fontWeight: 'bold',
        }}
        aria-label="Exit selected text mode"
      >
        Exit Mode
      </button>
    </div>
    <div
      style={{
        fontSize: '12px',
        color: '#555555',
        backgroundColor: '#ffffff',
        padding: '8px',
        borderRadius: '4px',
        maxHeight: '60px',
        overflow: 'hidden',
        position: 'relative',
      }}
    >
      <div
        style={{
          overflow: 'hidden',
          textOverflow: 'ellipsis',
          display: '-webkit-box',
          WebkitLineClamp: 2,
          WebkitBoxOrient: 'vertical',
        }}
      >
        "{selectedText}"
      </div>
    </div>
  </div>
);

/**
 * User badge component for header.
 */
const UserBadge: React.FC<{
  user?: UserResponse | null;
  isAuthenticated?: boolean;
  onLoginClick?: () => void;
  onLogout?: () => void;
}> = ({ user, isAuthenticated, onLoginClick, onLogout }) => {
  const [showMenu, setShowMenu] = useState(false);

  if (!isAuthenticated || !user) {
    return onLoginClick ? (
      <button
        onClick={onLoginClick}
        style={{
          padding: '6px 12px',
          border: '1px solid #0066cc',
          borderRadius: '4px',
          backgroundColor: 'transparent',
          color: '#0066cc',
          cursor: 'pointer',
          fontSize: '12px',
          fontWeight: '500',
        }}
      >
        Sign In
      </button>
    ) : null;
  }

  const displayName = user.display_name || user.email.split('@')[0];
  const initials = displayName.slice(0, 2).toUpperCase();

  return (
    <div style={{ position: 'relative' }}>
      <button
        onClick={() => setShowMenu(!showMenu)}
        style={{
          display: 'flex',
          alignItems: 'center',
          gap: '6px',
          padding: '4px 8px',
          border: '1px solid #e0e0e0',
          borderRadius: '16px',
          backgroundColor: 'transparent',
          cursor: 'pointer',
          fontSize: '12px',
        }}
      >
        <div
          style={{
            width: '22px',
            height: '22px',
            borderRadius: '50%',
            backgroundColor: '#1976d2',
            color: '#ffffff',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            fontSize: '10px',
            fontWeight: '600',
          }}
        >
          {initials}
        </div>
        <span style={{ maxWidth: '80px', overflow: 'hidden', textOverflow: 'ellipsis' }}>
          {displayName}
        </span>
      </button>

      {showMenu && (
        <>
          <div
            style={{
              position: 'fixed',
              top: 0,
              left: 0,
              right: 0,
              bottom: 0,
              zIndex: 999,
            }}
            onClick={() => setShowMenu(false)}
          />
          <div
            style={{
              position: 'absolute',
              top: '100%',
              right: 0,
              marginTop: '4px',
              backgroundColor: '#ffffff',
              borderRadius: '8px',
              boxShadow: '0 2px 8px rgba(0, 0, 0, 0.15)',
              minWidth: '150px',
              zIndex: 1000,
              padding: '8px 0',
            }}
          >
            <div style={{ padding: '8px 12px', borderBottom: '1px solid #e0e0e0' }}>
              <div style={{ fontSize: '12px', fontWeight: '500' }}>{displayName}</div>
              <div style={{ fontSize: '11px', color: '#666666' }}>
                {user.experience_level || 'Beginner'} level
              </div>
            </div>
            {onLogout && (
              <button
                onClick={() => {
                  setShowMenu(false);
                  onLogout();
                }}
                style={{
                  display: 'block',
                  width: '100%',
                  padding: '8px 12px',
                  border: 'none',
                  backgroundColor: 'transparent',
                  textAlign: 'left',
                  cursor: 'pointer',
                  fontSize: '12px',
                  color: '#c62828',
                }}
              >
                Sign Out
              </button>
            )}
          </div>
        </>
      )}
    </div>
  );
};

/**
 * Main ChatWidget component.
 */
export const ChatWidget: React.FC<ChatWidgetProps> = ({
  initialConversationId,
  title = 'Book Assistant',
  onError,
  className = '',
  minimized = false,
  onToggleMinimize,
  selectedText: externalSelectedText,
  onExitSelectedTextMode,
  user,
  isAuthenticated,
  onLoginClick,
  onLogout,
}) => {
  const {
    messages,
    isLoading,
    error,
    mode,
    selectedText: internalSelectedText,
    sendMessage,
    sendSelectedTextMessage,
    enterSelectedTextMode,
    exitSelectedTextMode,
    clearConversation,
    retryLastMessage,
  } = useChat({
    initialConversationId,
    onError,
  });

  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Handle external selected text changes
  useEffect(() => {
    if (externalSelectedText && externalSelectedText.trim()) {
      enterSelectedTextMode(externalSelectedText);
    }
  }, [externalSelectedText, enterSelectedTextMode]);

  // Determine the active selected text
  const activeSelectedText = internalSelectedText || externalSelectedText || null;
  const isSelectedTextMode = mode === 'selected_text' && activeSelectedText;

  /**
   * Handle send message - route to appropriate method based on mode.
   */
  const handleSendMessage = useCallback(
    (content: string) => {
      if (isSelectedTextMode && activeSelectedText) {
        sendSelectedTextMessage(content, activeSelectedText);
      } else {
        sendMessage(content);
      }
    },
    [isSelectedTextMode, activeSelectedText, sendMessage, sendSelectedTextMessage]
  );

  /**
   * Handle exit selected-text mode.
   */
  const handleExitSelectedTextMode = useCallback(() => {
    exitSelectedTextMode();
    onExitSelectedTextMode?.();
  }, [exitSelectedTextMode, onExitSelectedTextMode]);

  // Auto-scroll to bottom when new messages arrive
  useEffect(() => {
    if (messagesEndRef.current) {
      messagesEndRef.current.scrollIntoView({ behavior: 'smooth' });
    }
  }, [messages, isLoading]);

  if (minimized) {
    return (
      <div
        className={`chat-widget chat-widget--minimized ${className}`}
        style={{
          position: 'fixed',
          bottom: '20px',
          right: '20px',
          width: '60px',
          height: '60px',
          borderRadius: '50%',
          backgroundColor: '#0066cc',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          cursor: 'pointer',
          boxShadow: '0 4px 12px rgba(0, 0, 0, 0.15)',
        }}
        onClick={onToggleMinimize}
        aria-label="Open chat"
      >
        <span style={{ fontSize: '24px' }}>💬</span>
      </div>
    );
  }

  return (
    <div
      className={`chat-widget ${className}`}
      style={{
        display: 'flex',
        flexDirection: 'column',
        width: '100%',
        maxWidth: '600px',
        height: '100%',
        maxHeight: '700px',
        border: '1px solid #e0e0e0',
        borderRadius: '12px',
        backgroundColor: '#ffffff',
        boxShadow: '0 4px 12px rgba(0, 0, 0, 0.1)',
        overflow: 'hidden',
      }}
    >
      {/* Header */}
      <div
        className="chat-widget__header"
        style={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          padding: '16px',
          borderBottom: isSelectedTextMode ? 'none' : '1px solid #e0e0e0',
          backgroundColor: '#f8f9fa',
        }}
      >
        <h2
          style={{
            margin: 0,
            fontSize: '18px',
            fontWeight: 'bold',
            color: '#333333',
          }}
        >
          {title}
        </h2>
        <div style={{ display: 'flex', gap: '8px', alignItems: 'center' }}>
          <UserBadge
            user={user}
            isAuthenticated={isAuthenticated}
            onLoginClick={onLoginClick}
            onLogout={onLogout}
          />
          {messages.length > 0 && (
            <button
              onClick={clearConversation}
              style={{
                padding: '8px 12px',
                border: '1px solid #cccccc',
                borderRadius: '4px',
                backgroundColor: 'transparent',
                color: '#666666',
                cursor: 'pointer',
                fontSize: '12px',
              }}
              aria-label="Clear conversation"
            >
              Clear
            </button>
          )}
          {onToggleMinimize && (
            <button
              onClick={onToggleMinimize}
              style={{
                padding: '8px',
                border: 'none',
                borderRadius: '4px',
                backgroundColor: 'transparent',
                color: '#666666',
                cursor: 'pointer',
                fontSize: '16px',
              }}
              aria-label="Minimize chat"
            >
              −
            </button>
          )}
        </div>
      </div>

      {/* Selected-text mode banner */}
      {isSelectedTextMode && activeSelectedText && (
        <SelectedTextBanner
          selectedText={activeSelectedText}
          onExit={handleExitSelectedTextMode}
        />
      )}

      {/* Messages area */}
      <div
        className="chat-widget__messages"
        style={{
          flex: 1,
          overflowY: 'auto',
          padding: '16px',
        }}
      >
        {messages.length === 0 && !isLoading ? (
          <EmptyState isSelectedTextMode={isSelectedTextMode} />
        ) : (
          <>
            {messages.map((message) => (
              <ChatMessage
                key={message.id}
                role={message.role}
                content={message.content}
                sources={message.sources}
                timestamp={message.timestamp}
              />
            ))}
            {isLoading && <LoadingIndicator />}
          </>
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* Error display */}
      {error && <ErrorDisplay error={error} onRetry={retryLastMessage} />}

      {/* Input area */}
      <ChatInput
        onSend={handleSendMessage}
        disabled={isLoading}
        placeholder={
          isSelectedTextMode
            ? 'Ask about the selected text...'
            : 'Ask a question about the book...'
        }
      />
    </div>
  );
};

export default ChatWidget;
