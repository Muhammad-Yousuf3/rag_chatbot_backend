/**
 * TextSelector component for selecting text and asking questions about it.
 *
 * T047 [US2] - Provides UI for text selection and selected-text chat mode.
 */

import React, { useState, useCallback } from 'react';
import { useTextSelection } from '../../hooks/useTextSelection';

export interface TextSelectorProps {
  /**
   * Callback when user wants to ask about selected text.
   */
  onAskAboutSelection: (selectedText: string) => void;

  /**
   * Whether the selector is currently active.
   */
  isActive?: boolean;

  /**
   * Callback to toggle selector active state.
   */
  onToggleActive?: () => void;

  /**
   * Minimum selection length.
   */
  minLength?: number;

  /**
   * Maximum selection length.
   */
  maxLength?: number;
}

/**
 * Floating toolbar that appears when text is selected.
 */
export const TextSelector: React.FC<TextSelectorProps> = ({
  onAskAboutSelection,
  isActive = true,
  onToggleActive,
  minLength = 10,
  maxLength = 50000,
}) => {
  const {
    selectedText,
    isValidSelection,
    clearSelection,
    validationError,
  } = useTextSelection({
    minLength,
    maxLength,
  });

  const [showTooltip, setShowTooltip] = useState(false);

  /**
   * Handle ask button click.
   */
  const handleAsk = useCallback(() => {
    if (isValidSelection && selectedText) {
      onAskAboutSelection(selectedText);
      clearSelection();
    }
  }, [isValidSelection, selectedText, onAskAboutSelection, clearSelection]);

  /**
   * Handle cancel button click.
   */
  const handleCancel = useCallback(() => {
    clearSelection();
  }, [clearSelection]);

  // Don't render if not active or no selection
  if (!isActive || !selectedText) {
    return null;
  }

  return (
    <div
      className="text-selector"
      style={{
        position: 'fixed',
        bottom: '100px',
        right: '20px',
        zIndex: 1001,
        backgroundColor: '#ffffff',
        borderRadius: '8px',
        boxShadow: '0 4px 12px rgba(0, 0, 0, 0.15)',
        padding: '12px',
        maxWidth: '300px',
      }}
    >
      {/* Selection preview */}
      <div
        className="text-selector__preview"
        style={{
          marginBottom: '12px',
          padding: '8px',
          backgroundColor: '#f5f5f5',
          borderRadius: '4px',
          fontSize: '12px',
          maxHeight: '100px',
          overflow: 'hidden',
          position: 'relative',
        }}
      >
        <div
          style={{
            overflow: 'hidden',
            textOverflow: 'ellipsis',
            display: '-webkit-box',
            WebkitLineClamp: 4,
            WebkitBoxOrient: 'vertical',
          }}
        >
          {selectedText}
        </div>
        {selectedText.length > 200 && (
          <div
            style={{
              position: 'absolute',
              bottom: 0,
              left: 0,
              right: 0,
              height: '20px',
              background: 'linear-gradient(transparent, #f5f5f5)',
            }}
          />
        )}
      </div>

      {/* Character count */}
      <div
        className="text-selector__count"
        style={{
          fontSize: '11px',
          color: validationError ? '#cc0000' : '#666666',
          marginBottom: '8px',
        }}
      >
        {validationError || `${selectedText.length} characters selected`}
      </div>

      {/* Actions */}
      <div
        className="text-selector__actions"
        style={{
          display: 'flex',
          gap: '8px',
        }}
      >
        <button
          onClick={handleAsk}
          disabled={!isValidSelection}
          style={{
            flex: 1,
            padding: '8px 16px',
            border: 'none',
            borderRadius: '4px',
            backgroundColor: isValidSelection ? '#0066cc' : '#cccccc',
            color: '#ffffff',
            fontWeight: 'bold',
            cursor: isValidSelection ? 'pointer' : 'not-allowed',
            fontSize: '14px',
          }}
          onMouseEnter={() => !isValidSelection && setShowTooltip(true)}
          onMouseLeave={() => setShowTooltip(false)}
        >
          Ask about this
        </button>
        <button
          onClick={handleCancel}
          style={{
            padding: '8px 12px',
            border: '1px solid #cccccc',
            borderRadius: '4px',
            backgroundColor: 'transparent',
            color: '#666666',
            cursor: 'pointer',
            fontSize: '14px',
          }}
        >
          Cancel
        </button>
      </div>

      {/* Tooltip for disabled state */}
      {showTooltip && validationError && (
        <div
          style={{
            position: 'absolute',
            bottom: '100%',
            left: '50%',
            transform: 'translateX(-50%)',
            backgroundColor: '#333333',
            color: '#ffffff',
            padding: '4px 8px',
            borderRadius: '4px',
            fontSize: '11px',
            marginBottom: '4px',
            whiteSpace: 'nowrap',
          }}
        >
          {validationError}
        </div>
      )}
    </div>
  );
};

export default TextSelector;
