/**
 * PageTranslationContext - Global context for full-page translation state.
 *
 * Manages translation state across the entire application including:
 * - Translation enabled/disabled state
 * - Target language
 * - Persistence via localStorage
 * - Navigation handling
 */

import React, { createContext, useContext, useState, useCallback, useEffect, ReactNode } from 'react';

export type TranslationLanguage = 'ur' | 'en';

export interface PageTranslationState {
  /**
   * Whether translation is currently active.
   */
  isEnabled: boolean;

  /**
   * Target language for translation.
   */
  language: TranslationLanguage;

  /**
   * Whether a translation is currently in progress.
   */
  isTranslating: boolean;

  /**
   * Error message if translation failed.
   */
  error: string | null;
}

export interface PageTranslationContextValue extends PageTranslationState {
  /**
   * Enable translation and start translating the page.
   */
  enableTranslation: () => void;

  /**
   * Disable translation and restore original text.
   */
  disableTranslation: () => void;

  /**
   * Toggle translation on/off.
   */
  toggleTranslation: () => void;

  /**
   * Set target language.
   */
  setLanguage: (language: TranslationLanguage) => void;

  /**
   * Set translating state.
   */
  setIsTranslating: (isTranslating: boolean) => void;

  /**
   * Set error message.
   */
  setError: (error: string | null) => void;

  /**
   * Trigger re-translation (useful after navigation).
   */
  retranslate: () => void;
}

const PageTranslationContext = createContext<PageTranslationContextValue | undefined>(undefined);

const STORAGE_KEY = 'rag-chatbot-translation-enabled';
const LANGUAGE_KEY = 'rag-chatbot-translation-language';

export interface PageTranslationProviderProps {
  children: ReactNode;
  /**
   * Default language (default: 'ur').
   */
  defaultLanguage?: TranslationLanguage;
}

/**
 * Provider component for page translation state.
 */
export const PageTranslationProvider: React.FC<PageTranslationProviderProps> = ({
  children,
  defaultLanguage = 'ur',
}) => {
  // Initialize state from localStorage
  const [isEnabled, setIsEnabled] = useState<boolean>(() => {
    if (typeof window === 'undefined') return false;
    const stored = localStorage.getItem(STORAGE_KEY);
    return stored === 'true';
  });

  const [language, setLanguageState] = useState<TranslationLanguage>(() => {
    if (typeof window === 'undefined') return defaultLanguage;
    const stored = localStorage.getItem(LANGUAGE_KEY);
    return (stored as TranslationLanguage) || defaultLanguage;
  });

  const [isTranslating, setIsTranslating] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [retranslateCounter, setRetranslateCounter] = useState(0);

  /**
   * Enable translation.
   */
  const enableTranslation = useCallback(() => {
    setIsEnabled(true);
    setError(null);
    if (typeof window !== 'undefined') {
      localStorage.setItem(STORAGE_KEY, 'true');
    }
  }, []);

  /**
   * Disable translation.
   */
  const disableTranslation = useCallback(() => {
    setIsEnabled(false);
    setError(null);
    if (typeof window !== 'undefined') {
      localStorage.setItem(STORAGE_KEY, 'false');
    }
  }, []);

  /**
   * Toggle translation.
   */
  const toggleTranslation = useCallback(() => {
    if (isEnabled) {
      disableTranslation();
    } else {
      enableTranslation();
    }
  }, [isEnabled, enableTranslation, disableTranslation]);

  /**
   * Set language.
   */
  const setLanguage = useCallback((newLanguage: TranslationLanguage) => {
    setLanguageState(newLanguage);
    if (typeof window !== 'undefined') {
      localStorage.setItem(LANGUAGE_KEY, newLanguage);
    }
    // Trigger retranslation if already enabled
    if (isEnabled) {
      setRetranslateCounter((prev) => prev + 1);
    }
  }, [isEnabled]);

  /**
   * Trigger retranslation.
   */
  const retranslate = useCallback(() => {
    if (isEnabled) {
      setRetranslateCounter((prev) => prev + 1);
    }
  }, [isEnabled]);

  const contextValue: PageTranslationContextValue = {
    isEnabled,
    language,
    isTranslating,
    error,
    enableTranslation,
    disableTranslation,
    toggleTranslation,
    setLanguage,
    setIsTranslating,
    setError,
    retranslate,
  };

  return (
    <PageTranslationContext.Provider value={contextValue}>
      {children}
    </PageTranslationContext.Provider>
  );
};

/**
 * Hook to access page translation context.
 */
export function usePageTranslationContext(): PageTranslationContextValue {
  const context = useContext(PageTranslationContext);
  if (!context) {
    throw new Error('usePageTranslationContext must be used within PageTranslationProvider');
  }
  return context;
}

export default PageTranslationContext;
