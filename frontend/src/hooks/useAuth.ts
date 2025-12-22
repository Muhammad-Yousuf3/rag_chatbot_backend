/**
 * useAuth React hook for authentication state management.
 *
 * T083 [US4] - Provides authentication state and actions.
 */

import { useState, useCallback, useEffect, useMemo } from 'react';
import { api, UserResponse } from '../services/api';

export type AuthStatus = 'idle' | 'loading' | 'authenticated' | 'unauthenticated';

export interface UseAuthOptions {
  /**
   * Callback when authentication succeeds.
   */
  onAuthSuccess?: (user: UserResponse) => void;

  /**
   * Callback when logout occurs.
   */
  onLogout?: () => void;

  /**
   * Whether to persist auth token in localStorage.
   */
  persistToken?: boolean;
}

export interface UseAuthReturn {
  /**
   * Current user if authenticated.
   */
  user: UserResponse | null;

  /**
   * Authentication status.
   */
  status: AuthStatus;

  /**
   * Whether user is authenticated.
   */
  isAuthenticated: boolean;

  /**
   * Whether authentication is loading.
   */
  isLoading: boolean;

  /**
   * Error message if authentication failed.
   */
  error: string | null;

  /**
   * Access token if authenticated.
   */
  token: string | null;

  /**
   * Register a new user.
   */
  register: (email: string, password: string, displayName?: string) => Promise<void>;

  /**
   * Login with email and password.
   */
  login: (email: string, password: string) => Promise<void>;

  /**
   * Logout the current user.
   */
  logout: () => void;

  /**
   * Update user preferences.
   */
  updatePreferences: (preferences: {
    experience_level?: string;
    preferred_language?: string;
  }) => Promise<void>;

  /**
   * Refresh user data from server.
   */
  refreshUser: () => Promise<void>;
}

const TOKEN_STORAGE_KEY = 'rag_chatbot_auth_token';

/**
 * Custom hook for managing authentication state.
 *
 * @param options - Configuration options
 * @returns Authentication state and actions
 */
export function useAuth(options: UseAuthOptions = {}): UseAuthReturn {
  const { onAuthSuccess, onLogout, persistToken = true } = options;

  const [user, setUser] = useState<UserResponse | null>(null);
  const [status, setStatus] = useState<AuthStatus>('idle');
  const [error, setError] = useState<string | null>(null);
  const [token, setToken] = useState<string | null>(null);

  /**
   * Save token to storage.
   */
  const saveToken = useCallback(
    (newToken: string) => {
      setToken(newToken);
      if (persistToken) {
        localStorage.setItem(TOKEN_STORAGE_KEY, newToken);
      }
    },
    [persistToken]
  );

  /**
   * Clear token from storage.
   */
  const clearToken = useCallback(() => {
    setToken(null);
    localStorage.removeItem(TOKEN_STORAGE_KEY);
  }, []);

  /**
   * Load token from storage on mount.
   */
  useEffect(() => {
    const storedToken = localStorage.getItem(TOKEN_STORAGE_KEY);
    if (storedToken) {
      setToken(storedToken);
      setStatus('loading');
      // Validate token by fetching current user
      api
        .getCurrentUser(storedToken)
        .then((userData) => {
          setUser(userData);
          setStatus('authenticated');
          onAuthSuccess?.(userData);
        })
        .catch(() => {
          clearToken();
          setStatus('unauthenticated');
        });
    } else {
      setStatus('unauthenticated');
    }
  }, [clearToken, onAuthSuccess]);

  /**
   * Register a new user.
   */
  const register = useCallback(
    async (email: string, password: string, displayName?: string): Promise<void> => {
      setStatus('loading');
      setError(null);

      try {
        const response = await api.register(email, password, displayName);
        saveToken(response.access_token);
        setUser(response.user);
        setStatus('authenticated');
        onAuthSuccess?.(response.user);
      } catch (err) {
        setStatus('unauthenticated');
        const message = err instanceof Error ? err.message : 'Registration failed';
        setError(message);
        throw err;
      }
    },
    [saveToken, onAuthSuccess]
  );

  /**
   * Login with email and password.
   */
  const login = useCallback(
    async (email: string, password: string): Promise<void> => {
      setStatus('loading');
      setError(null);

      try {
        const response = await api.login(email, password);
        saveToken(response.access_token);
        setUser(response.user);
        setStatus('authenticated');
        onAuthSuccess?.(response.user);
      } catch (err) {
        setStatus('unauthenticated');
        const message = err instanceof Error ? err.message : 'Login failed';
        setError(message);
        throw err;
      }
    },
    [saveToken, onAuthSuccess]
  );

  /**
   * Logout the current user.
   */
  const logout = useCallback(() => {
    clearToken();
    setUser(null);
    setStatus('unauthenticated');
    setError(null);
    onLogout?.();
  }, [clearToken, onLogout]);

  /**
   * Update user preferences.
   */
  const updatePreferences = useCallback(
    async (preferences: {
      experience_level?: string;
      preferred_language?: string;
    }): Promise<void> => {
      if (!token) {
        throw new Error('Not authenticated');
      }

      try {
        const updatedUser = await api.updatePreferences(token, preferences);
        setUser(updatedUser);
      } catch (err) {
        const message = err instanceof Error ? err.message : 'Failed to update preferences';
        setError(message);
        throw err;
      }
    },
    [token]
  );

  /**
   * Refresh user data from server.
   */
  const refreshUser = useCallback(async (): Promise<void> => {
    if (!token) {
      return;
    }

    try {
      const userData = await api.getCurrentUser(token);
      setUser(userData);
    } catch (err) {
      // Token might be invalid, log out
      logout();
    }
  }, [token, logout]);

  const isAuthenticated = useMemo(() => status === 'authenticated', [status]);
  const isLoading = useMemo(() => status === 'loading', [status]);

  return {
    user,
    status,
    isAuthenticated,
    isLoading,
    error,
    token,
    register,
    login,
    logout,
    updatePreferences,
    refreshUser,
  };
}

export default useAuth;
