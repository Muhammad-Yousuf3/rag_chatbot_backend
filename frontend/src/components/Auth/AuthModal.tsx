/**
 * AuthModal component for login/register dialog.
 *
 * T082 [US4] - Provides modal wrapper for auth forms.
 */

import React, { useState, useCallback } from 'react';
import { LoginForm } from './LoginForm';
import { RegisterForm } from './RegisterForm';

export interface AuthModalProps {
  /**
   * Whether modal is open.
   */
  isOpen: boolean;

  /**
   * Callback to close modal.
   */
  onClose: () => void;

  /**
   * Callback when login is submitted.
   */
  onLogin: (email: string, password: string) => Promise<void>;

  /**
   * Callback when register is submitted.
   */
  onRegister: (email: string, password: string, displayName?: string) => Promise<void>;

  /**
   * Whether form is in loading state.
   */
  isLoading?: boolean;

  /**
   * Error message to display.
   */
  error?: string | null;

  /**
   * Initial mode (login or register).
   */
  initialMode?: 'login' | 'register';
}

/**
 * AuthModal component.
 */
export const AuthModal: React.FC<AuthModalProps> = ({
  isOpen,
  onClose,
  onLogin,
  onRegister,
  isLoading = false,
  error = null,
  initialMode = 'login',
}) => {
  const [mode, setMode] = useState<'login' | 'register'>(initialMode);

  /**
   * Handle login submission.
   */
  const handleLogin = useCallback(
    async (email: string, password: string) => {
      await onLogin(email, password);
      onClose();
    },
    [onLogin, onClose]
  );

  /**
   * Handle register submission.
   */
  const handleRegister = useCallback(
    async (email: string, password: string, displayName?: string) => {
      await onRegister(email, password, displayName);
      onClose();
    },
    [onRegister, onClose]
  );

  if (!isOpen) return null;

  return (
    <div
      className="auth-modal-overlay"
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
        className="auth-modal"
        onClick={(e) => e.stopPropagation()}
        style={{
          position: 'relative',
          maxWidth: '100%',
        }}
      >
        {/* Close button */}
        <button
          onClick={onClose}
          style={{
            position: 'absolute',
            top: '-40px',
            right: '0',
            background: 'none',
            border: 'none',
            color: '#ffffff',
            fontSize: '24px',
            cursor: 'pointer',
          }}
          aria-label="Close"
        >
          ×
        </button>

        {mode === 'login' ? (
          <LoginForm
            onSubmit={handleLogin}
            onSwitchToRegister={() => setMode('register')}
            isLoading={isLoading}
            error={error}
          />
        ) : (
          <RegisterForm
            onSubmit={handleRegister}
            onSwitchToLogin={() => setMode('login')}
            isLoading={isLoading}
            error={error}
          />
        )}
      </div>
    </div>
  );
};

export default AuthModal;
