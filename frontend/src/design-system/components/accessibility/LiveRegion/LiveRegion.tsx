/**
 * Live Region Component
 * Provides screen reader announcements for dynamic content updates
 */

import React, { useEffect, useRef } from 'react';
import { ScreenReaderAnnouncer } from '../../../utils/ariaUtils';
import './LiveRegion.css';

export interface LiveRegionProps {
  /** The message to announce */
  message: string;
  /** Politeness level for announcements */
  politeness?: 'polite' | 'assertive' | 'off';
  /** Whether the announcement should be atomic */
  atomic?: boolean;
  /** What changes should be announced */
  relevant?: 'additions' | 'removals' | 'text' | 'all';
  /** Additional CSS class */
  className?: string;
  /** Whether to clear the message after announcement */
  clearAfterAnnouncement?: boolean;
  /** Delay before clearing (in ms) */
  clearDelay?: number;
}

export const LiveRegion: React.FC<LiveRegionProps> = ({
  message,
  politeness = 'polite',
  atomic = true,
  relevant = 'additions text',
  className = '',
  clearAfterAnnouncement = true,
  clearDelay = 1000,
}) => {
  const regionRef = useRef<HTMLDivElement>(null);
  const timeoutRef = useRef<NodeJS.Timeout | null>(null);

  useEffect(() => {
    if (message && regionRef.current) {
      // Clear any existing timeout
      if (timeoutRef.current) {
        clearTimeout(timeoutRef.current);
      }

      // Set the message
      regionRef.current.textContent = message;

      // Clear the message after delay if requested
      if (clearAfterAnnouncement && clearDelay > 0) {
        timeoutRef.current = setTimeout(() => {
          if (regionRef.current) {
            regionRef.current.textContent = '';
          }
        }, clearDelay);
      }
    }

    return () => {
      if (timeoutRef.current) {
        clearTimeout(timeoutRef.current);
      }
    };
  }, [message, clearAfterAnnouncement, clearDelay]);

  if (politeness === 'off') {
    return null;
  }

  return (
    <div
      ref={regionRef}
      className={`live-region ${className}`}
      aria-live={politeness}
      aria-atomic={atomic}
      aria-relevant={relevant as any}
      role={politeness === 'assertive' ? 'alert' : 'status'}
    />
  );
};

/**
 * Polite Live Region - for non-urgent announcements
 */
export const PoliteLiveRegion: React.FC<Omit<LiveRegionProps, 'politeness'>> = (props) => (
  <LiveRegion {...props} politeness="polite" />
);

/**
 * Assertive Live Region - for urgent announcements
 */
export const AssertiveLiveRegion: React.FC<Omit<LiveRegionProps, 'politeness'>> = (props) => (
  <LiveRegion {...props} politeness="assertive" />
);

/**
 * Status Region - for status updates
 */
export const StatusRegion: React.FC<Omit<LiveRegionProps, 'politeness' | 'relevant'>> = (props) => (
  <LiveRegion {...props} politeness="polite" relevant="text" />
);

/**
 * Alert Region - for error messages and urgent notifications
 */
export const AlertRegion: React.FC<Omit<LiveRegionProps, 'politeness' | 'relevant'>> = (props) => (
  <LiveRegion {...props} politeness="assertive" relevant="additions" />
);

/**
 * Hook for using live regions programmatically
 */
export const useLiveRegion = () => {
  const announcer = ScreenReaderAnnouncer.getInstance();

  const announcePolite = (message: string) => {
    announcer.announcePolite(message);
  };

  const announceAssertive = (message: string) => {
    announcer.announceAssertive(message);
  };

  const announceError = (message: string) => {
    announcer.announceError(message);
  };

  const announceSuccess = (message: string) => {
    announcer.announceSuccess(message);
  };

  const announceLoading = (message?: string) => {
    announcer.announceLoading(message);
  };

  const announceNavigation = (message: string) => {
    announcer.announceNavigation(message);
  };

  const clear = () => {
    announcer.clear();
  };

  return {
    announcePolite,
    announceAssertive,
    announceError,
    announceSuccess,
    announceLoading,
    announceNavigation,
    clear,
  };
};

export default LiveRegion;