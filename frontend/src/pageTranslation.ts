/**
 * Page Translation Module
 *
 * Provides full-page translation functionality for Docusaurus sites.
 *
 * @module pageTranslation
 */

// Context and Provider
export {
  PageTranslationProvider,
  usePageTranslationContext,
  type PageTranslationState,
  type PageTranslationContextValue,
  type TranslationLanguage,
} from './contexts/PageTranslationContext';

// Hooks
export { usePageTranslation } from './hooks/usePageTranslation';

// Components
export { NavbarTranslateButton } from './components/NavbarTranslateButton';
export { PageTranslationWrapper } from './components/PageTranslationWrapper';

// Re-export types from existing translation module for convenience
export type { TranslationStatus } from './hooks/useTranslation';
