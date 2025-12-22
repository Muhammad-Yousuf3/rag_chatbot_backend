/**
 * useTextSelection React hook for managing text selection.
 *
 * T046 [US2] - Provides text selection state management and event handling.
 */

import { useState, useCallback, useEffect, useRef } from 'react';

export interface TextSelectionState {
  text: string;
  startOffset: number;
  endOffset: number;
  anchorNode: Node | null;
}

export interface UseTextSelectionOptions {
  /**
   * Minimum characters required for a valid selection.
   */
  minLength?: number;

  /**
   * Maximum characters allowed for a selection.
   */
  maxLength?: number;

  /**
   * Container element to limit selection scope.
   */
  containerRef?: React.RefObject<HTMLElement>;

  /**
   * Callback when selection changes.
   */
  onSelectionChange?: (selection: TextSelectionState | null) => void;
}

export interface UseTextSelectionReturn {
  /**
   * Current selected text (trimmed).
   */
  selectedText: string;

  /**
   * Full selection state including offsets.
   */
  selection: TextSelectionState | null;

  /**
   * Whether current selection is valid (meets min/max requirements).
   */
  isValidSelection: boolean;

  /**
   * Clear the current selection.
   */
  clearSelection: () => void;

  /**
   * Manually set selected text (for programmatic selection).
   */
  setSelectedText: (text: string) => void;

  /**
   * Error message if selection is invalid.
   */
  validationError: string | null;
}

/**
 * Custom hook for managing text selection from the page.
 *
 * @param options - Configuration options
 * @returns Selection state and actions
 */
export function useTextSelection(
  options: UseTextSelectionOptions = {}
): UseTextSelectionReturn {
  const {
    minLength = 10,
    maxLength = 50000,
    containerRef,
    onSelectionChange,
  } = options;

  const [selection, setSelection] = useState<TextSelectionState | null>(null);
  const [validationError, setValidationError] = useState<string | null>(null);

  // Ref to track if we should process selections
  const isProcessingRef = useRef(false);

  /**
   * Validate selection text.
   */
  const validateSelection = useCallback(
    (text: string): string | null => {
      const trimmed = text.trim();

      if (!trimmed) {
        return 'Selection is empty';
      }

      if (trimmed.length < minLength) {
        return `Selection must be at least ${minLength} characters`;
      }

      if (trimmed.length > maxLength) {
        return `Selection cannot exceed ${maxLength} characters`;
      }

      return null;
    },
    [minLength, maxLength]
  );

  /**
   * Handle selection change from browser.
   */
  const handleSelectionChange = useCallback(() => {
    if (isProcessingRef.current) return;

    const windowSelection = window.getSelection();

    if (!windowSelection || windowSelection.isCollapsed) {
      // No selection or collapsed selection
      if (selection) {
        setSelection(null);
        setValidationError(null);
        onSelectionChange?.(null);
      }
      return;
    }

    const selectedText = windowSelection.toString();

    // Check if selection is within container (if specified)
    if (containerRef?.current) {
      const range = windowSelection.getRangeAt(0);
      if (!containerRef.current.contains(range.commonAncestorContainer)) {
        return; // Selection is outside our container
      }
    }

    const newSelection: TextSelectionState = {
      text: selectedText,
      startOffset: windowSelection.anchorOffset,
      endOffset: windowSelection.focusOffset,
      anchorNode: windowSelection.anchorNode,
    };

    setSelection(newSelection);

    const error = validateSelection(selectedText);
    setValidationError(error);

    onSelectionChange?.(newSelection);
  }, [selection, containerRef, validateSelection, onSelectionChange]);

  /**
   * Clear selection.
   */
  const clearSelection = useCallback(() => {
    isProcessingRef.current = true;

    window.getSelection()?.removeAllRanges();
    setSelection(null);
    setValidationError(null);
    onSelectionChange?.(null);

    // Reset flag after a short delay
    setTimeout(() => {
      isProcessingRef.current = false;
    }, 100);
  }, [onSelectionChange]);

  /**
   * Manually set selected text.
   */
  const setSelectedText = useCallback(
    (text: string) => {
      const trimmed = text.trim();
      const error = validateSelection(trimmed);

      setSelection({
        text: trimmed,
        startOffset: 0,
        endOffset: trimmed.length,
        anchorNode: null,
      });
      setValidationError(error);
    },
    [validateSelection]
  );

  // Listen for selection changes
  useEffect(() => {
    document.addEventListener('selectionchange', handleSelectionChange);

    return () => {
      document.removeEventListener('selectionchange', handleSelectionChange);
    };
  }, [handleSelectionChange]);

  const selectedText = selection?.text.trim() || '';
  const isValidSelection = selectedText.length > 0 && validationError === null;

  return {
    selectedText,
    selection,
    isValidSelection,
    clearSelection,
    setSelectedText,
    validationError,
  };
}

export default useTextSelection;
