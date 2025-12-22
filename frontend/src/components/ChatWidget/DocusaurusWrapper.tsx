/**
 * Docusaurus integration wrapper for ChatWidget.
 *
 * T038 [US1] - Integrates ChatWidget with Docusaurus layout.
 *
 * This component wraps the ChatWidget for use in a Docusaurus site,
 * providing positioning and state management for the floating chat interface.
 */

import React, { useState, useCallback } from 'react';
import { ChatWidget } from './index';

export interface DocusaurusChatWrapperProps {
  /**
   * Widget title.
   */
  title?: string;

  /**
   * Default minimized state.
   */
  defaultMinimized?: boolean;

  /**
   * Position of the widget.
   */
  position?: 'bottom-right' | 'bottom-left';
}

/**
 * Docusaurus-integrated ChatWidget wrapper.
 *
 * Usage in Docusaurus:
 * 1. Add this component to your theme's Root.tsx or Layout
 * 2. Or use swizzling to add to the theme
 *
 * @example
 * // In src/theme/Root.tsx
 * import { DocusaurusChatWrapper } from '@site/src/components/ChatWidget/DocusaurusWrapper';
 *
 * export default function Root({ children }) {
 *   return (
 *     <>
 *       {children}
 *       <DocusaurusChatWrapper title="Book Assistant" />
 *     </>
 *   );
 * }
 */
export const DocusaurusChatWrapper: React.FC<DocusaurusChatWrapperProps> = ({
  title = 'Book Assistant',
  defaultMinimized = true,
  position = 'bottom-right',
}) => {
  const [isMinimized, setIsMinimized] = useState(defaultMinimized);

  const handleToggleMinimize = useCallback(() => {
    setIsMinimized((prev) => !prev);
  }, []);

  const handleError = useCallback((error: Error) => {
    console.error('Chat error:', error);
    // In production, you might want to send this to an error tracking service
  }, []);

  const positionStyles: React.CSSProperties = {
    position: 'fixed',
    bottom: '20px',
    zIndex: 1000,
    ...(position === 'bottom-right'
      ? { right: '20px' }
      : { left: '20px' }),
  };

  const expandedStyles: React.CSSProperties = {
    ...positionStyles,
    width: 'min(400px, calc(100vw - 40px))',
    height: 'min(600px, calc(100vh - 100px))',
  };

  if (isMinimized) {
    return (
      <div style={positionStyles}>
        <ChatWidget
          title={title}
          minimized={true}
          onToggleMinimize={handleToggleMinimize}
          onError={handleError}
        />
      </div>
    );
  }

  return (
    <div style={expandedStyles}>
      <ChatWidget
        title={title}
        minimized={false}
        onToggleMinimize={handleToggleMinimize}
        onError={handleError}
      />
    </div>
  );
};

export default DocusaurusChatWrapper;
