/**
 * usePageTranslation - Hook for translating entire page content.
 *
 * Provides DOM-level translation by:
 * - Collecting text nodes from the page
 * - Batching translation API calls
 * - Updating DOM with translated content
 * - Preserving original text for restoration
 * - Avoiding double-translation and infinite loops
 */

import { useEffect, useRef, useCallback } from 'react';
import { usePageTranslationContext } from '../contexts/PageTranslationContext';
import { api } from '../services/api';

const TRANSLATED_ATTR = 'data-translated';
const ORIGINAL_TEXT_ATTR = 'data-original-text';
const SEPARATOR = '|||SEP|||';

/**
 * Selectors for elements to exclude from translation.
 */
const EXCLUDE_SELECTORS = [
  'script',
  'style',
  'code',
  'pre',
  'noscript',
  'iframe',
  '[data-no-translate]',
  '.no-translate',
].join(', ');

/**
 * Check if an element should be excluded from translation.
 */
function shouldExcludeElement(element: Element): boolean {
  // Exclude if element matches exclude selectors
  if (element.matches(EXCLUDE_SELECTORS)) {
    return true;
  }

  // Exclude if parent matches exclude selectors
  if (element.closest(EXCLUDE_SELECTORS)) {
    return true;
  }

  return false;
}

/**
 * Check if a text node should be translated.
 */
function shouldTranslateTextNode(node: Text): boolean {
  const text = node.textContent?.trim();
  if (!text || text.length === 0) {
    return false;
  }

  // Must have a parent element
  if (!node.parentElement) {
    return false;
  }

  // Check if parent should be excluded
  if (shouldExcludeElement(node.parentElement)) {
    return false;
  }

  // Skip if already translated
  if (node.parentElement.hasAttribute(TRANSLATED_ATTR)) {
    return false;
  }

  return true;
}

/**
 * Collect all translatable text nodes from the page.
 */
function collectTextNodes(rootElement: Element): Text[] {
  const textNodes: Text[] = [];
  const walker = document.createTreeWalker(
    rootElement,
    NodeFilter.SHOW_TEXT,
    {
      acceptNode: (node) => {
        const textNode = node as Text;
        return shouldTranslateTextNode(textNode)
          ? NodeFilter.FILTER_ACCEPT
          : NodeFilter.FILTER_SKIP;
      },
    }
  );

  let currentNode = walker.nextNode();
  while (currentNode) {
    textNodes.push(currentNode as Text);
    currentNode = walker.nextNode();
  }

  return textNodes;
}

/**
 * Restore original text for all translated elements.
 */
function restoreOriginalText(rootElement: Element): void {
  const translatedElements = rootElement.querySelectorAll(`[${TRANSLATED_ATTR}]`);
  translatedElements.forEach((element) => {
    const originalText = element.getAttribute(ORIGINAL_TEXT_ATTR);
    if (originalText !== null) {
      // Find the text node child and restore
      const textNode = Array.from(element.childNodes).find(
        (node) => node.nodeType === Node.TEXT_NODE
      ) as Text | undefined;

      if (textNode) {
        textNode.textContent = originalText;
      }

      // Remove translation attributes
      element.removeAttribute(TRANSLATED_ATTR);
      element.removeAttribute(ORIGINAL_TEXT_ATTR);
    }
  });
}

/**
 * Get page slug for translation caching.
 */
function getPageSlug(): string {
  if (typeof window === 'undefined') return 'page';

  // Use pathname as slug (sanitized)
  const pathname = window.location.pathname;
  const slug = pathname
    .replace(/^\/+|\/+$/g, '') // Remove leading/trailing slashes
    .replace(/[^a-z0-9-_]/gi, '-') // Replace invalid chars
    .replace(/-+/g, '-') // Collapse multiple dashes
    || 'home';

  return `page-${slug}`;
}

/**
 * Hook for page-level translation.
 *
 * @param options - Configuration options
 * @param options.rootSelector - CSS selector for root element to translate (default: 'main, article, .markdown')
 */
export function usePageTranslation(options: {
  rootSelector?: string;
} = {}) {
  const {
    isEnabled,
    language,
    isTranslating,
    setIsTranslating,
    setError,
  } = usePageTranslationContext();

  const { rootSelector = 'main, article, .markdown' } = options;

  // Track if translation has been attempted for current page state
  const lastTranslationKey = useRef<string>('');
  const isTranslatingRef = useRef(false);

  /**
   * Translate the page content.
   */
  const translatePage = useCallback(async () => {
    if (typeof window === 'undefined') return;
    if (isTranslatingRef.current) return; // Prevent concurrent translations

    const currentKey = `${window.location.pathname}-${language}-${isEnabled}`;
    if (lastTranslationKey.current === currentKey) {
      return; // Already translated this state
    }

    // Find root element
    const rootElement = document.querySelector(rootSelector);
    if (!rootElement) {
      console.warn(`[PageTranslation] Root element not found: ${rootSelector}`);
      return;
    }

    try {
      isTranslatingRef.current = true;
      setIsTranslating(true);
      setError(null);

      if (!isEnabled) {
        // Restore original text
        restoreOriginalText(rootElement);
        lastTranslationKey.current = currentKey;
        return;
      }

      // Collect text nodes
      const textNodes = collectTextNodes(rootElement);
      if (textNodes.length === 0) {
        console.warn('[PageTranslation] No text nodes found to translate');
        lastTranslationKey.current = currentKey;
        return;
      }

      // Extract original texts
      const originalTexts = textNodes.map((node) => node.textContent?.trim() || '');

      // Combine texts with separator for batch translation
      const combinedText = originalTexts.join(SEPARATOR);

      // Call translation API
      const pageSlug = getPageSlug();
      const response = await api.requestTranslation(pageSlug, combinedText, language);

      // Handle pending/in-progress response
      if ('status' in response && response.status !== 'completed') {
        // Poll for completion
        let attempts = 0;
        const maxAttempts = 20;
        const pollInterval = 3000;

        const poll = async (): Promise<void> => {
          attempts++;
          if (attempts > maxAttempts) {
            throw new Error('Translation timeout - please try again');
          }

          const pollResponse = await api.getTranslation(pageSlug, language);

          if ('content' in pollResponse) {
            // Completed
            applyTranslation(pollResponse.content, textNodes, originalTexts);
            lastTranslationKey.current = currentKey;
          } else {
            // Still pending, continue polling
            setTimeout(poll, pollInterval);
          }
        };

        setTimeout(poll, pollInterval);
        return;
      }

      // Apply translation immediately if completed
      if ('content' in response) {
        applyTranslation(response.content, textNodes, originalTexts);
        lastTranslationKey.current = currentKey;
      }
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Translation failed';
      console.error('[PageTranslation] Translation error:', err);
      setError(errorMessage);

      // Restore original text on error
      restoreOriginalText(rootElement);
    } finally {
      isTranslatingRef.current = false;
      setIsTranslating(false);
    }
  }, [isEnabled, language, rootSelector, setIsTranslating, setError]);

  /**
   * Apply translated content to text nodes.
   */
  const applyTranslation = useCallback((
    translatedContent: string,
    textNodes: Text[],
    originalTexts: string[]
  ) => {
    // Split translated content
    const translatedTexts = translatedContent.split(SEPARATOR);

    // Apply to each text node
    textNodes.forEach((node, index) => {
      const translatedText = translatedTexts[index];
      const originalText = originalTexts[index];

      if (translatedText && node.parentElement) {
        // Store original text as attribute
        node.parentElement.setAttribute(ORIGINAL_TEXT_ATTR, originalText);
        node.parentElement.setAttribute(TRANSLATED_ATTR, 'true');

        // Update text content
        node.textContent = translatedText;
      }
    });
  }, []);

  /**
   * Effect to trigger translation when state changes.
   */
  useEffect(() => {
    // Debounce to avoid rapid re-translations
    const timeoutId = setTimeout(() => {
      translatePage();
    }, 100);

    return () => clearTimeout(timeoutId);
  }, [translatePage]);

  /**
   * Effect to handle navigation (Docusaurus-specific).
   */
  useEffect(() => {
    if (typeof window === 'undefined') return;

    // Reset translation key on navigation
    const handleNavigation = () => {
      lastTranslationKey.current = '';
      // Small delay to let Docusaurus render new content
      setTimeout(() => {
        if (isEnabled) {
          translatePage();
        }
      }, 300);
    };

    // Listen for Docusaurus route changes
    window.addEventListener('popstate', handleNavigation);

    // Listen for custom Docusaurus events (if available)
    if ('docusaurus' in window) {
      // Docusaurus v3 uses history API
      const originalPushState = window.history.pushState;
      const originalReplaceState = window.history.replaceState;

      window.history.pushState = function(...args) {
        originalPushState.apply(this, args);
        handleNavigation();
      };

      window.history.replaceState = function(...args) {
        originalReplaceState.apply(this, args);
        handleNavigation();
      };

      return () => {
        window.history.pushState = originalPushState;
        window.history.replaceState = originalReplaceState;
        window.removeEventListener('popstate', handleNavigation);
      };
    }

    return () => {
      window.removeEventListener('popstate', handleNavigation);
    };
  }, [isEnabled, translatePage]);

  return {
    isTranslating,
    translatePage,
  };
}

export default usePageTranslation;
