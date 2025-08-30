/**
 * Keyboard Shortcuts Help Modal
 * Displays available keyboard shortcuts for the current context
 */

import React, { useEffect, useRef } from 'react';
import { useFocusTrap } from '../../../hooks/useKeyboardNavigation';
import { keyboardShortcuts, KeyboardShortcut } from '../../../utils/keyboardShortcuts';
import './KeyboardShortcutsHelp.css';

export interface KeyboardShortcutsHelpProps {
  /** Whether the help modal is open */
  isOpen: boolean;
  /** Function to close the modal */
  onClose: () => void;
  /** Custom shortcuts to display (overrides context shortcuts) */
  customShortcuts?: KeyboardShortcut[];
  /** Additional CSS class */
  className?: string;
}

interface ShortcutGroup {
  name: string;
  shortcuts: KeyboardShortcut[];
}

export const KeyboardShortcutsHelp: React.FC<KeyboardShortcutsHelpProps> = ({
  isOpen,
  onClose,
  customShortcuts,
  className = '',
}) => {
  const modalRef = useFocusTrap(isOpen, {
    escapeDeactivates: true,
  }) as React.RefObject<HTMLDivElement>;
  const closeButtonRef = useRef<HTMLButtonElement>(null);

  // Get shortcuts to display
  const shortcuts = customShortcuts || keyboardShortcuts.getContextShortcuts();
  const groupedShortcuts = groupShortcuts(shortcuts);

  // Focus close button when modal opens
  useEffect(() => {
    if (isOpen && closeButtonRef.current) {
      closeButtonRef.current.focus();
    }
  }, [isOpen]);

  // Handle escape key
  useEffect(() => {
    const handleKeyDown = (event: KeyboardEvent) => {
      if (event.key === 'Escape' && isOpen) {
        onClose();
      }
    };

    if (isOpen) {
      document.addEventListener('keydown', handleKeyDown);
    }

    return () => {
      document.removeEventListener('keydown', handleKeyDown);
    };
  }, [isOpen, onClose]);

  if (!isOpen) return null;

  return (
    <div className={`keyboard-shortcuts-overlay ${className}`} onClick={onClose}>
      <div
        ref={modalRef}
        className="keyboard-shortcuts-modal"
        role="dialog"
        aria-labelledby="shortcuts-title"
        aria-modal="true"
        onClick={(e) => e.stopPropagation()}
      >
        <div className="shortcuts-header">
          <h2 id="shortcuts-title">Skróty klawiszowe</h2>
          <button
            ref={closeButtonRef}
            className="close-button"
            onClick={onClose}
            aria-label="Zamknij okno skrótów klawiszowych"
          >
            ×
          </button>
        </div>
        
        <div className="shortcuts-content">
          {groupedShortcuts.length === 0 ? (
            <p className="no-shortcuts">Brak dostępnych skrótów klawiszowych w tym kontekście.</p>
          ) : (
            groupedShortcuts.map((group, index) => (
              <div key={index} className="shortcut-group">
                <h3>{group.name}</h3>
                <dl className="shortcut-list">
                  {group.shortcuts.map((shortcut, shortcutIndex) => (
                    <React.Fragment key={shortcutIndex}>
                      <dt className="shortcut-key">
                        {formatKeyCombo(shortcut)}
                      </dt>
                      <dd className="shortcut-description">
                        {shortcut.description}
                      </dd>
                    </React.Fragment>
                  ))}
                </dl>
              </div>
            ))
          )}
          
          <div className="shortcuts-footer">
            <p className="shortcuts-note">
              Naciśnij <kbd>Esc</kbd> aby zamknąć to okno
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

/**
 * Group shortcuts by category
 */
function groupShortcuts(shortcuts: KeyboardShortcut[]): ShortcutGroup[] {
  const groups: ShortcutGroup[] = [
    { name: 'Ogólne', shortcuts: [] },
    { name: 'Nawigacja', shortcuts: [] },
    { name: 'Formularze', shortcuts: [] },
    { name: 'Faktury', shortcuts: [] },
    { name: 'OCR', shortcuts: [] },
  ];

  shortcuts.forEach(shortcut => {
    if (shortcut.context === 'invoices') {
      groups[3].shortcuts.push(shortcut);
    } else if (shortcut.context === 'ocr') {
      groups[4].shortcuts.push(shortcut);
    } else if (shortcut.context === 'form') {
      groups[2].shortcuts.push(shortcut);
    } else if (shortcut.key === 'g' || shortcut.key === 'm' || shortcut.key === 's') {
      groups[1].shortcuts.push(shortcut);
    } else {
      groups[0].shortcuts.push(shortcut);
    }
  });

  return groups.filter(group => group.shortcuts.length > 0);
}

/**
 * Format keyboard shortcut combination for display
 */
function formatKeyCombo(shortcut: KeyboardShortcut): string {
  const parts = [];
  
  if (shortcut.ctrlKey) parts.push('Ctrl');
  if (shortcut.altKey) parts.push('Alt');
  if (shortcut.shiftKey) parts.push('Shift');
  if (shortcut.metaKey) parts.push('Cmd');
  
  let key = shortcut.key;
  if (key === ' ') key = 'Space';
  if (key === 'Enter') key = 'Enter';
  if (key === 'Escape') key = 'Esc';
  if (key === '?') key = '?';
  
  parts.push(key);
  return parts.join(' + ');
}

export default KeyboardShortcutsHelp;