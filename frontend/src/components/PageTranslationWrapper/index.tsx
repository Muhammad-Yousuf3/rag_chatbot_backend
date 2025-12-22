/**
 * PageTranslationWrapper - Wrapper component that enables page translation.
 *
 * Combines PageTranslationProvider with usePageTranslation hook to provide
 * automatic page translation when enabled.
 *
 * Usage in Docusaurus:
 * Wrap your Root component with this wrapper.
 */

import React, { ReactNode } from 'react';
import { PageTranslationProvider, TranslationLanguage } from '../../contexts/PageTranslationContext';
import { usePageTranslation } from '../../hooks/usePageTranslation';

export interface PageTranslationWrapperProps {
  children: ReactNode;
  /**
   * Default target language.
   */
  defaultLanguage?: TranslationLanguage;
  /**
   * CSS selector for root element to translate.
   * Default: 'main, article, .markdown'
   */
  rootSelector?: string;
}

/**
 * Inner component that uses the translation hook.
 */
const PageTranslationHandler: React.FC<{
  children: ReactNode;
  rootSelector?: string;
}> = ({ children, rootSelector }) => {
  // This hook handles the actual translation logic
  usePageTranslation({ rootSelector });

  return <>{children}</>;
};

/**
 * Wrapper component that provides translation context and automatic translation.
 */
export const PageTranslationWrapper: React.FC<PageTranslationWrapperProps> = ({
  children,
  defaultLanguage = 'ur',
  rootSelector,
}) => {
  return (
    <PageTranslationProvider defaultLanguage={defaultLanguage}>
      <PageTranslationHandler rootSelector={rootSelector}>
        {children}
      </PageTranslationHandler>
    </PageTranslationProvider>
  );
};

export default PageTranslationWrapper;
