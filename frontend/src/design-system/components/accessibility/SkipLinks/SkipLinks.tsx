/**
 * Skip Links component for keyboard navigation
 * Provides quick navigation to main content areas
 */

import React from 'react';
import { useSkipLinks } from '../../../hooks/useKeyboardNavigation';
import './SkipLinks.css';

export interface SkipLinksProps {
  /** Custom skip link targets */
  links?: Array<{
    href: string;
    label: string;
    targetId?: string;
  }>;
  /** Additional CSS class */
  className?: string;
}

/**
 * Default skip links for Polish business application
 */
const defaultLinks = [
  {
    href: '#main-content',
    label: 'Przejdź do głównej zawartości',
    targetId: 'main-content',
  },
  {
    href: '#main-navigation',
    label: 'Przejdź do nawigacji',
    targetId: 'main-navigation',
  },
  {
    href: '#search',
    label: 'Przejdź do wyszukiwania',
    targetId: 'search',
  },
];

export const SkipLinks: React.FC<SkipLinksProps> = ({
  links = defaultLinks,
  className = '',
}) => {
  const { skipToContent } = useSkipLinks();

  const handleSkipClick = (event: React.MouseEvent<HTMLAnchorElement>, targetId?: string) => {
    event.preventDefault();
    
    if (targetId) {
      skipToContent(targetId);
    } else {
      // Fallback to href
      const href = (event.target as HTMLAnchorElement).getAttribute('href');
      if (href && href.startsWith('#')) {
        skipToContent(href.substring(1));
      }
    }
  };

  return (
    <div className={`skip-links ${className}`} role="navigation" aria-label="Skróty nawigacyjne">
      {links.map((link, index) => (
        <a
          key={index}
          href={link.href}
          className="skip-link"
          onClick={(e) => handleSkipClick(e, link.targetId)}
        >
          {link.label}
        </a>
      ))}
    </div>
  );
};

export default SkipLinks;