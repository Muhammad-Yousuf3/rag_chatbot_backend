/**
 * LoginForm component for user authentication.
 *
 * T082 [US4] - Provides login form UI.
 */

import React, { useState, useCallback } from 'react';

export interface LoginFormProps {
  /**
   * Callback when login is submitted.
   */
  onSubmit: (email: string, password: string) => Promise<void>;

  /**
   * Callback to switch to register mode.
   */
  onSwitchToRegister?: () => void;

  /**
   * Whether form is in loading state.
   */
  isLoading?: boolean;

  /**
   * Error message to display.
   */
  error?: string | null;

  /**
   * Custom class name.
   */
  className?: string;
}

/**
 * LoginForm component.
 */
export const LoginForm: React.FC<LoginFormProps> = ({
  onSubmit,
  onSwitchToRegister,
  isLoading = false,
  error = null,
  className = '',
}) => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [localError, setLocalError] = useState<string | null>(null);

  /**
   * Handle form submission.
   */
  const handleSubmit = useCallback(
    async (e: React.FormEvent) => {
      e.preventDefault();
      setLocalError(null);

      if (!email || !password) {
        setLocalError('Please enter email and password');
        return;
      }

      try {
        await onSubmit(email, password);
      } catch (err) {
        // Error is handled by parent via error prop
      }
    },
    [email, password, onSubmit]
  );

  const displayError = error || localError;

  return (
    <form
      className={`auth-form login-form ${className}`}
      onSubmit={handleSubmit}
      style={{
        display: 'flex',
        flexDirection: 'column',
        gap: '16px',
        padding: '24px',
        backgroundColor: '#ffffff',
        borderRadius: '8px',
        boxShadow: '0 2px 8px rgba(0, 0, 0, 0.1)',
        maxWidth: '400px',
        width: '100%',
      }}
    >
      <h2
        style={{
          margin: '0 0 8px 0',
          fontSize: '20px',
          textAlign: 'center',
        }}
      >
        Sign In
      </h2>

      {displayError && (
        <div
          style={{
            padding: '8px 12px',
            backgroundColor: '#ffebee',
            borderRadius: '4px',
            color: '#c62828',
            fontSize: '14px',
          }}
        >
          {displayError}
        </div>
      )}

      <div style={{ display: 'flex', flexDirection: 'column', gap: '4px' }}>
        <label htmlFor="login-email" style={{ fontSize: '14px', fontWeight: '500' }}>
          Email
        </label>
        <input
          id="login-email"
          type="email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          placeholder="you@example.com"
          disabled={isLoading}
          style={{
            padding: '10px 12px',
            border: '1px solid #e0e0e0',
            borderRadius: '4px',
            fontSize: '14px',
          }}
        />
      </div>

      <div style={{ display: 'flex', flexDirection: 'column', gap: '4px' }}>
        <label htmlFor="login-password" style={{ fontSize: '14px', fontWeight: '500' }}>
          Password
        </label>
        <input
          id="login-password"
          type="password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          placeholder="Enter password"
          disabled={isLoading}
          style={{
            padding: '10px 12px',
            border: '1px solid #e0e0e0',
            borderRadius: '4px',
            fontSize: '14px',
          }}
        />
      </div>

      <button
        type="submit"
        disabled={isLoading}
        style={{
          padding: '12px',
          backgroundColor: isLoading ? '#999999' : '#1976d2',
          color: '#ffffff',
          border: 'none',
          borderRadius: '4px',
          fontSize: '14px',
          fontWeight: '600',
          cursor: isLoading ? 'not-allowed' : 'pointer',
          marginTop: '8px',
        }}
      >
        {isLoading ? 'Signing in...' : 'Sign In'}
      </button>

      {onSwitchToRegister && (
        <p
          style={{
            margin: '8px 0 0 0',
            fontSize: '14px',
            textAlign: 'center',
            color: '#666666',
          }}
        >
          Don't have an account?{' '}
          <button
            type="button"
            onClick={onSwitchToRegister}
            style={{
              background: 'none',
              border: 'none',
              color: '#1976d2',
              cursor: 'pointer',
              padding: 0,
              fontSize: '14px',
              textDecoration: 'underline',
            }}
          >
            Register
          </button>
        </p>
      )}
    </form>
  );
};

export default LoginForm;
