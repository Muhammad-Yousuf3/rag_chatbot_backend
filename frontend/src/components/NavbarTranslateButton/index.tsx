/**
 * NavbarTranslateButton - Global translation toggle button for navbar.
 *
 * Features:
 * - Toggles full-page translation on/off
 * - Shows loading state during translation
 * - Displays error messages gracefully
 * - Persists state across navigation
 * - Accessible and production-ready
 */

import React from 'react';
import { usePageTranslationContext } from '../../contexts/PageTranslationContext';
import './styles.css';

export interface NavbarTranslateButtonProps {
  /**
   * Button label when translation is off.
   */
  label?: string;

  /**
   * Button label when translation is on.
   */
  activeLabel?: string;

  /**
   * Whether to show text label (false = icon only).
   */
  showLabel?: boolean;

  /**
   * Custom CSS class.
   */
  className?: string;

  /**
   * Button variant style.
   */
  variant?: 'default' | 'minimal' | 'outline';
}

/**
 * Loading spinner component.
 */
const LoadingSpinner: React.FC<{ size?: number }> = ({ size = 16 }) => (
  <svg
    width={size}
    height={size}
    viewBox="0 0 24 24"
    fill="none"
    className="translate-button__spinner"
  >
    <circle
      cx="12"
      cy="12"
      r="10"
      stroke="currentColor"
      strokeWidth="3"
      strokeLinecap="round"
      strokeDasharray="32 32"
    />
  </svg>
);

/**
 * Translation icon component.
 */
const TranslateIcon: React.FC<{ size?: number; active?: boolean }> = ({
  size = 20,
  active = false,
}) => (
  <svg
    width={size}
    height={size}
    viewBox="0 0 24 24"
    fill="none"
    stroke="currentColor"
    strokeWidth="2"
    strokeLinecap="round"
    strokeLinejoin="round"
    className={`translate-button__icon ${active ? 'translate-button__icon--active' : ''}`}
  >
    <path d="M5 8h14M5 8v3m0-3V5m14 3v3m0-3V5" />
    <path d="M2 12h20" />
    <path d="M9 16h6" />
    <path d="M12 16v3" />
  </svg>
);

/**
 * Navbar translate button component.
 */
export const NavbarTranslateButton: React.FC<NavbarTranslateButtonProps> = ({
  label = 'Translate',
  activeLabel = 'Original',
  showLabel = true,
  className = '',
  variant = 'default',
}) => {
  const {
    isEnabled,
    isTranslating,
    error,
    toggleTranslation,
  } = usePageTranslationContext();

  const buttonLabel = isEnabled ? activeLabel : label;
  const variantClass = `translate-button--${variant}`;
  const activeClass = isEnabled ? 'translate-button--active' : '';
  const loadingClass = isTranslating ? 'translate-button--loading' : '';

  return (
    <div className={`translate-button-wrapper ${className}`}>
      <button
        onClick={toggleTranslation}
        disabled={isTranslating}
        className={`translate-button ${variantClass} ${activeClass} ${loadingClass}`}
        aria-label={isEnabled ? 'Show original text' : 'Translate page'}
        title={isEnabled ? 'Click to show original text' : 'Click to translate page to Urdu'}
        type="button"
      >
        <span className="translate-button__content">
          {isTranslating ? (
            <LoadingSpinner size={18} />
          ) : (
            <TranslateIcon size={20} active={isEnabled} />
          )}

          {showLabel && (
            <span className="translate-button__label">
              {isTranslating ? 'Translating...' : buttonLabel}
            </span>
          )}
        </span>
      </button>

      {/* Error tooltip */}
      {error && (
        <div className="translate-button__error" role="alert">
          <span className="translate-button__error-icon">⚠️</span>
          <span className="translate-button__error-message">{error}</span>
        </div>
      )}
    </div>
  );
};

export default NavbarTranslateButton;
