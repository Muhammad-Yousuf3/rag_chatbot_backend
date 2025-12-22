/**
 * ChatMessage component for displaying individual chat messages.
 *
 * T034 [US1] - Renders user and assistant messages with source citations.
 */

import React from 'react';
import { SourceReference } from '../../services/api';

export interface ChatMessageProps {
  role: 'user' | 'assistant';
  content: string;
  sources?: SourceReference[];
  timestamp?: Date;
  isLoading?: boolean;
}

/**
 * Format a timestamp for display.
 */
function formatTimestamp(date: Date): string {
  return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
}

/**
 * Component for rendering a single chat message.
 */
export const ChatMessage: React.FC<ChatMessageProps> = ({
  role,
  content,
  sources,
  timestamp,
  isLoading = false,
}) => {
  const isUser = role === 'user';

  return (
    <div
      className={`chat-message chat-message--${role}`}
      style={{
        display: 'flex',
        flexDirection: 'column',
        alignItems: isUser ? 'flex-end' : 'flex-start',
        marginBottom: '16px',
        maxWidth: '100%',
      }}
    >
      {/* Message bubble */}
      <div
        className="chat-message__bubble"
        style={{
          maxWidth: '80%',
          padding: '12px 16px',
          borderRadius: isUser ? '18px 18px 4px 18px' : '18px 18px 18px 4px',
          backgroundColor: isUser ? '#0066cc' : '#f0f0f0',
          color: isUser ? '#ffffff' : '#333333',
        }}
      >
        {isLoading ? (
          <div className="chat-message__loading">
            <span className="loading-dot">.</span>
            <span className="loading-dot">.</span>
            <span className="loading-dot">.</span>
          </div>
        ) : (
          <div
            className="chat-message__content"
            style={{ whiteSpace: 'pre-wrap', wordBreak: 'break-word' }}
          >
            {content}
          </div>
        )}
      </div>

      {/* Source citations for assistant messages */}
      {!isUser && sources && sources.length > 0 && (
        <div
          className="chat-message__sources"
          style={{
            marginTop: '8px',
            fontSize: '12px',
            color: '#666666',
            maxWidth: '80%',
          }}
        >
          <span style={{ fontWeight: 'bold' }}>Sources:</span>
          <ul style={{ margin: '4px 0 0 0', paddingLeft: '20px' }}>
            {sources.map((source, index) => (
              <li key={index} className="chat-message__source">
                {source.chapter}
                {source.section && `, ${source.section}`}
                {source.page && ` (p. ${source.page})`}
                <span
                  style={{
                    marginLeft: '8px',
                    color: '#999999',
                    fontSize: '11px',
                  }}
                >
                  {Math.round(source.relevance * 100)}% relevant
                </span>
              </li>
            ))}
          </ul>
        </div>
      )}

      {/* Timestamp */}
      {timestamp && (
        <div
          className="chat-message__timestamp"
          style={{
            fontSize: '10px',
            color: '#999999',
            marginTop: '4px',
          }}
        >
          {formatTimestamp(timestamp)}
        </div>
      )}
    </div>
  );
};

export default ChatMessage;
