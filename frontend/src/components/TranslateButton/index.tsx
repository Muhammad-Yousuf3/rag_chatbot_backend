/**
 * TranslateButton component for requesting chapter translations.
 *
 * T063-T065 [US3] - Provides UI for translation requests with loading state.
 */

import React, { useState, useCallback } from 'react';
import { useTranslation, TranslationStatus } from '../../hooks/useTranslation';

export interface TranslateButtonProps {
  /**
   * Chapter identifier.
   */
  chapterSlug: string;

  /**
   * Chapter content to translate.
   */
  content: string;

  /**
   * Callback when translation completes.
   */
  onTranslationComplete?: (translatedContent: string) => void;

  /**
   * Button label.
   */
  label?: string;

  /**
   * Whether to show the translated content in a modal.
   */
  showModal?: boolean;

  /**
   * Custom class name.
   */
  className?: string;
}

/**
 * Loading spinner component.
 */
const LoadingSpinner: React.FC = () => (
  <span
    style={{
      display: 'inline-block',
      width: '16px',
      height: '16px',
      border: '2px solid #ffffff',
      borderTopColor: 'transparent',
      borderRadius: '50%',
      animation: 'spin 1s linear infinite',
    }}
  />
);

/**
 * Translation modal component.
 */
const TranslationModal: React.FC<{
  content: string;
  onClose: () => void;
  chapterSlug: string;
}> = ({ content, onClose, chapterSlug }) => (
  <div
    className="translation-modal-overlay"
    style={{
      position: 'fixed',
      top: 0,
      left: 0,
      right: 0,
      bottom: 0,
      backgroundColor: 'rgba(0, 0, 0, 0.5)',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      zIndex: 2000,
    }}
    onClick={onClose}
  >
    <div
      className="translation-modal"
      style={{
        backgroundColor: '#ffffff',
        borderRadius: '12px',
        maxWidth: '800px',
        maxHeight: '80vh',
        width: '90%',
        overflow: 'hidden',
        display: 'flex',
        flexDirection: 'column',
      }}
      onClick={(e) => e.stopPropagation()}
    >
      {/* Header */}
      <div
        style={{
          padding: '16px 24px',
          borderBottom: '1px solid #e0e0e0',
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
        }}
      >
        <h2 style={{ margin: 0, fontSize: '18px' }}>
          اردو ترجمہ - {chapterSlug}
        </h2>
        <button
          onClick={onClose}
          style={{
            border: 'none',
            background: 'none',
            fontSize: '24px',
            cursor: 'pointer',
            color: '#666666',
          }}
          aria-label="Close"
        >
          ×
        </button>
      </div>

      {/* Content */}
      <div
        style={{
          padding: '24px',
          overflowY: 'auto',
          direction: 'rtl',
          textAlign: 'right',
          fontFamily: 'Noto Nastaliq Urdu, serif',
          fontSize: '18px',
          lineHeight: '2',
        }}
      >
        <div dangerouslySetInnerHTML={{ __html: content.replace(/\n/g, '<br/>') }} />
      </div>
    </div>
  </div>
);

/**
 * Progress indicator component.
 */
const ProgressIndicator: React.FC<{
  status: TranslationStatus;
  estimatedSeconds: number | null;
}> = ({ status, estimatedSeconds }) => {
  const getMessage = () => {
    switch (status) {
      case 'loading':
        return 'Starting translation...';
      case 'polling':
        return estimatedSeconds
          ? `Translating... (~${estimatedSeconds}s remaining)`
          : 'Translating...';
      default:
        return '';
    }
  };

  return (
    <div
      style={{
        display: 'flex',
        alignItems: 'center',
        gap: '8px',
        fontSize: '14px',
        color: '#666666',
      }}
    >
      <LoadingSpinner />
      <span>{getMessage()}</span>
    </div>
  );
};

/**
 * TranslateButton component.
 */
export const TranslateButton: React.FC<TranslateButtonProps> = ({
  chapterSlug,
  content,
  onTranslationComplete,
  label = 'اردو میں ترجمہ کریں',
  showModal = true,
  className = '',
}) => {
  const [showTranslation, setShowTranslation] = useState(false);

  const {
    content: translatedContent,
    status,
    error,
    estimatedSeconds,
    requestTranslation,
    getTranslation,
    reset,
  } = useTranslation({
    onComplete: (content) => {
      onTranslationComplete?.(content);
      if (showModal) {
        setShowTranslation(true);
      }
    },
  });

  /**
   * Handle button click.
   */
  const handleClick = useCallback(async () => {
    if (status === 'completed' && translatedContent) {
      // Already have translation, show it
      setShowTranslation(true);
      return;
    }

    if (status === 'loading' || status === 'polling') {
      // Already in progress
      return;
    }

    // First try to get existing translation
    try {
      await getTranslation(chapterSlug);
    } catch {
      // If not found, request new translation
      await requestTranslation(chapterSlug, content);
    }
  }, [status, translatedContent, chapterSlug, content, getTranslation, requestTranslation]);

  /**
   * Handle modal close.
   */
  const handleCloseModal = useCallback(() => {
    setShowTranslation(false);
  }, []);

  const isLoading = status === 'loading' || status === 'polling';
  const isCompleted = status === 'completed' && translatedContent;

  return (
    <>
      <div className={`translate-button-container ${className}`}>
        <button
          onClick={handleClick}
          disabled={isLoading}
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: '8px',
            padding: '10px 20px',
            border: 'none',
            borderRadius: '8px',
            backgroundColor: isLoading ? '#999999' : '#2e7d32',
            color: '#ffffff',
            fontWeight: 'bold',
            cursor: isLoading ? 'not-allowed' : 'pointer',
            fontSize: '14px',
            transition: 'background-color 0.2s',
          }}
        >
          {isLoading ? (
            <LoadingSpinner />
          ) : (
            <span style={{ fontSize: '18px' }}>🌐</span>
          )}
          <span>{isCompleted ? 'ترجمہ دیکھیں' : label}</span>
        </button>

        {/* Progress indicator */}
        {isLoading && (
          <div style={{ marginTop: '8px' }}>
            <ProgressIndicator status={status} estimatedSeconds={estimatedSeconds} />
          </div>
        )}

        {/* Error message */}
        {error && (
          <div
            style={{
              marginTop: '8px',
              padding: '8px 12px',
              backgroundColor: '#ffebee',
              borderRadius: '4px',
              color: '#c62828',
              fontSize: '14px',
            }}
          >
            Error: {error}
          </div>
        )}
      </div>

      {/* Translation modal */}
      {showModal && showTranslation && translatedContent && (
        <TranslationModal
          content={translatedContent}
          onClose={handleCloseModal}
          chapterSlug={chapterSlug}
        />
      )}

      {/* CSS for spinner animation */}
      <style>{`
        @keyframes spin {
          to {
            transform: rotate(360deg);
          }
        }
      `}</style>
    </>
  );
};

export default TranslateButton;
