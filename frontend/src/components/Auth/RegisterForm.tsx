/**
 * RegisterForm component for user registration.
 *
 * T082 [US4] - Provides registration form UI.
 */

import React, { useState, useCallback } from 'react';

export interface RegisterFormProps {
  /**
   * Callback when registration is submitted.
   */
  onSubmit: (email: string, password: string, displayName?: string) => Promise<void>;

  /**
   * Callback to switch to login mode.
   */
  onSwitchToLogin?: () => void;

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
 * RegisterForm component.
 */
export const RegisterForm: React.FC<RegisterFormProps> = ({
  onSubmit,
  onSwitchToLogin,
  isLoading = false,
  error = null,
  className = '',
}) => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [displayName, setDisplayName] = useState('');
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

      if (password.length < 8) {
        setLocalError('Password must be at least 8 characters');
        return;
      }

      if (password !== confirmPassword) {
        setLocalError('Passwords do not match');
        return;
      }

      try {
        await onSubmit(email, password, displayName || undefined);
      } catch (err) {
        // Error is handled by parent via error prop
      }
    },
    [email, password, confirmPassword, displayName, onSubmit]
  );

  const displayError = error || localError;

  return (
    <form
      className={`auth-form register-form ${className}`}
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
        Create Account
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
        <label htmlFor="register-name" style={{ fontSize: '14px', fontWeight: '500' }}>
          Display Name (optional)
        </label>
        <input
          id="register-name"
          type="text"
          value={displayName}
          onChange={(e) => setDisplayName(e.target.value)}
          placeholder="Your name"
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
        <label htmlFor="register-email" style={{ fontSize: '14px', fontWeight: '500' }}>
          Email
        </label>
        <input
          id="register-email"
          type="email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          placeholder="you@example.com"
          disabled={isLoading}
          required
          style={{
            padding: '10px 12px',
            border: '1px solid #e0e0e0',
            borderRadius: '4px',
            fontSize: '14px',
          }}
        />
      </div>

      <div style={{ display: 'flex', flexDirection: 'column', gap: '4px' }}>
        <label htmlFor="register-password" style={{ fontSize: '14px', fontWeight: '500' }}>
          Password
        </label>
        <input
          id="register-password"
          type="password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          placeholder="At least 8 characters"
          disabled={isLoading}
          required
          minLength={8}
          style={{
            padding: '10px 12px',
            border: '1px solid #e0e0e0',
            borderRadius: '4px',
            fontSize: '14px',
          }}
        />
      </div>

      <div style={{ display: 'flex', flexDirection: 'column', gap: '4px' }}>
        <label
          htmlFor="register-confirm-password"
          style={{ fontSize: '14px', fontWeight: '500' }}
        >
          Confirm Password
        </label>
        <input
          id="register-confirm-password"
          type="password"
          value={confirmPassword}
          onChange={(e) => setConfirmPassword(e.target.value)}
          placeholder="Confirm password"
          disabled={isLoading}
          required
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
          backgroundColor: isLoading ? '#999999' : '#2e7d32',
          color: '#ffffff',
          border: 'none',
          borderRadius: '4px',
          fontSize: '14px',
          fontWeight: '600',
          cursor: isLoading ? 'not-allowed' : 'pointer',
          marginTop: '8px',
        }}
      >
        {isLoading ? 'Creating account...' : 'Create Account'}
      </button>

      {onSwitchToLogin && (
        <p
          style={{
            margin: '8px 0 0 0',
            fontSize: '14px',
            textAlign: 'center',
            color: '#666666',
          }}
        >
          Already have an account?{' '}
          <button
            type="button"
            onClick={onSwitchToLogin}
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
            Sign In
          </button>
        </p>
      )}
    </form>
  );
};

export default RegisterForm;
