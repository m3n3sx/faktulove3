/**
 * Keyboard shortcuts system for FaktuLove application
 * Provides global and context-specific keyboard shortcuts
 */

import React from 'react';

export interface KeyboardShortcut {
  key: string;
  ctrlKey?: boolean;
  altKey?: boolean;
  shiftKey?: boolean;
  metaKey?: boolean;
  description: string;
  action: () => void;
  context?: string;
  disabled?: boolean;
}

export interface ShortcutGroup {
  name: string;
  description: string;
  shortcuts: KeyboardShortcut[];
}

/**
 * Keyboard shortcut manager class
 */
export class KeyboardShortcutManager {
  private shortcuts: Map<string, KeyboardShortcut> = new Map();
  private contextStack: string[] = [];
  private isEnabled: boolean = true;
  private helpModalOpen: boolean = false;

  constructor() {
    this.setupGlobalListener();
    this.registerDefaultShortcuts();
  }

  /**
   * Register a keyboard shortcut
   */
  public register(shortcut: KeyboardShortcut): void {
    const key = this.getShortcutKey(shortcut);
    this.shortcuts.set(key, shortcut);
  }

  /**
   * Unregister a keyboard shortcut
   */
  public unregister(shortcut: Partial<KeyboardShortcut>): void {
    const key = this.getShortcutKey(shortcut as KeyboardShortcut);
    this.shortcuts.delete(key);
  }

  /**
   * Enable/disable keyboard shortcuts
   */
  public setEnabled(enabled: boolean): void {
    this.isEnabled = enabled;
  }

  /**
   * Push context to stack (for context-specific shortcuts)
   */
  public pushContext(context: string): void {
    this.contextStack.push(context);
  }

  /**
   * Pop context from stack
   */
  public popContext(): string | undefined {
    return this.contextStack.pop();
  }

  /**
   * Get current context
   */
  public getCurrentContext(): string | undefined {
    return this.contextStack[this.contextStack.length - 1];
  }

  /**
   * Get all shortcuts for current context
   */
  public getContextShortcuts(): KeyboardShortcut[] {
    const currentContext = this.getCurrentContext();
    return Array.from(this.shortcuts.values()).filter(
      shortcut => !shortcut.context || shortcut.context === currentContext
    );
  }

  /**
   * Show keyboard shortcuts help
   */
  public showHelp(): void {
    if (this.helpModalOpen) return;
    
    this.helpModalOpen = true;
    const shortcuts = this.getContextShortcuts();
    const helpContent = this.generateHelpContent(shortcuts);
    
    // Create help modal
    const modal = document.createElement('div');
    modal.className = 'keyboard-shortcuts-help';
    modal.setAttribute('role', 'dialog');
    modal.setAttribute('aria-labelledby', 'shortcuts-title');
    modal.setAttribute('aria-modal', 'true');
    modal.innerHTML = helpContent;
    
    // Add close functionality
    const closeButton = modal.querySelector('.close-button');
    const handleClose = () => {
      document.body.removeChild(modal);
      this.helpModalOpen = false;
    };
    
    closeButton?.addEventListener('click', handleClose);
    modal.addEventListener('keydown', (e) => {
      if (e.key === 'Escape') {
        handleClose();
      }
    });
    
    document.body.appendChild(modal);
    
    // Focus close button
    (closeButton as HTMLElement)?.focus();
  }

  private setupGlobalListener(): void {
    document.addEventListener('keydown', (event) => {
      if (!this.isEnabled) return;
      
      // Don't handle shortcuts when typing in inputs (unless specifically allowed)
      const target = event.target as HTMLElement;
      const isInputElement = target.tagName === 'INPUT' || 
                            target.tagName === 'TEXTAREA' || 
                            target.contentEditable === 'true';
      
      if (isInputElement && !event.ctrlKey && !event.altKey && !event.metaKey) {
        return;
      }
      
      const shortcutKey = this.getEventKey(event);
      const shortcut = this.shortcuts.get(shortcutKey);
      
      if (shortcut && !shortcut.disabled) {
        // Check context
        const currentContext = this.getCurrentContext();
        if (shortcut.context && shortcut.context !== currentContext) {
          return;
        }
        
        event.preventDefault();
        shortcut.action();
      }
    });
  }

  private registerDefaultShortcuts(): void {
    // Global shortcuts
    this.register({
      key: '?',
      shiftKey: true,
      description: 'Pokaż skróty klawiszowe',
      action: () => this.showHelp(),
    });

    this.register({
      key: 'h',
      ctrlKey: true,
      description: 'Pokaż skróty klawiszowe',
      action: () => this.showHelp(),
    });

    // Navigation shortcuts
    this.register({
      key: 'g',
      ctrlKey: true,
      description: 'Przejdź do głównej nawigacji',
      action: () => this.focusMainNavigation(),
    });

    this.register({
      key: 'm',
      ctrlKey: true,
      description: 'Przejdź do głównej zawartości',
      action: () => this.focusMainContent(),
    });

    this.register({
      key: 's',
      ctrlKey: true,
      description: 'Przejdź do wyszukiwania',
      action: () => this.focusSearch(),
    });

    // Form shortcuts
    this.register({
      key: 'Enter',
      ctrlKey: true,
      description: 'Zapisz formularz',
      action: () => this.submitCurrentForm(),
      context: 'form',
    });

    this.register({
      key: 'Escape',
      description: 'Anuluj/Zamknij',
      action: () => this.handleEscape(),
    });

    // Invoice-specific shortcuts
    this.register({
      key: 'n',
      ctrlKey: true,
      description: 'Nowa faktura',
      action: () => this.createNewInvoice(),
      context: 'invoices',
    });

    this.register({
      key: 'e',
      ctrlKey: true,
      description: 'Edytuj fakturę',
      action: () => this.editCurrentInvoice(),
      context: 'invoices',
    });

    this.register({
      key: 'd',
      ctrlKey: true,
      description: 'Usuń fakturę',
      action: () => this.deleteCurrentInvoice(),
      context: 'invoices',
    });

    // OCR shortcuts
    this.register({
      key: 'u',
      ctrlKey: true,
      description: 'Prześlij dokument',
      action: () => this.uploadDocument(),
      context: 'ocr',
    });

    this.register({
      key: 'r',
      ctrlKey: true,
      description: 'Ponów przetwarzanie OCR',
      action: () => this.retryOCR(),
      context: 'ocr',
    });
  }

  private getShortcutKey(shortcut: KeyboardShortcut): string {
    const parts = [];
    if (shortcut.ctrlKey) parts.push('ctrl');
    if (shortcut.altKey) parts.push('alt');
    if (shortcut.shiftKey) parts.push('shift');
    if (shortcut.metaKey) parts.push('meta');
    parts.push(shortcut.key.toLowerCase());
    return parts.join('+');
  }

  private getEventKey(event: KeyboardEvent): string {
    const parts = [];
    if (event.ctrlKey) parts.push('ctrl');
    if (event.altKey) parts.push('alt');
    if (event.shiftKey) parts.push('shift');
    if (event.metaKey) parts.push('meta');
    parts.push(event.key.toLowerCase());
    return parts.join('+');
  }

  private generateHelpContent(shortcuts: KeyboardShortcut[]): string {
    const groups = this.groupShortcuts(shortcuts);
    
    let content = `
      <div class="shortcuts-modal">
        <div class="shortcuts-header">
          <h2 id="shortcuts-title">Skróty klawiszowe</h2>
          <button class="close-button" aria-label="Zamknij">×</button>
        </div>
        <div class="shortcuts-content">
    `;
    
    groups.forEach(group => {
      content += `
        <div class="shortcut-group">
          <h3>${group.name}</h3>
          <dl class="shortcut-list">
      `;
      
      group.shortcuts.forEach(shortcut => {
        const keyCombo = this.formatKeyCombo(shortcut);
        content += `
          <dt class="shortcut-key">${keyCombo}</dt>
          <dd class="shortcut-description">${shortcut.description}</dd>
        `;
      });
      
      content += `
          </dl>
        </div>
      `;
    });
    
    content += `
        </div>
      </div>
    `;
    
    return content;
  }

  private groupShortcuts(shortcuts: KeyboardShortcut[]): ShortcutGroup[] {
    const groups: ShortcutGroup[] = [
      { name: 'Ogólne', description: 'Podstawowe skróty', shortcuts: [] },
      { name: 'Nawigacja', description: 'Poruszanie się po aplikacji', shortcuts: [] },
      { name: 'Formularze', description: 'Praca z formularzami', shortcuts: [] },
      { name: 'Faktury', description: 'Zarządzanie fakturami', shortcuts: [] },
      { name: 'OCR', description: 'Przetwarzanie dokumentów', shortcuts: [] },
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

  private formatKeyCombo(shortcut: KeyboardShortcut): string {
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

  // Navigation action implementations
  private focusMainNavigation(): void {
    const nav = document.querySelector('nav[role="navigation"], .main-navigation, #main-nav');
    if (nav) {
      const firstFocusable = nav.querySelector('a, button') as HTMLElement;
      firstFocusable?.focus();
    }
  }

  private focusMainContent(): void {
    const main = document.querySelector('main, [role="main"], #main-content');
    if (main) {
      (main as HTMLElement).focus();
    }
  }

  private focusSearch(): void {
    const search = document.querySelector('input[type="search"], .search-input, #search');
    if (search) {
      (search as HTMLElement).focus();
    }
  }

  private submitCurrentForm(): void {
    const activeElement = document.activeElement;
    const form = activeElement?.closest('form');
    if (form) {
      const submitButton = form.querySelector('button[type="submit"], input[type="submit"]') as HTMLButtonElement;
      if (submitButton) {
        submitButton.click();
      }
    }
  }

  private handleEscape(): void {
    // Close modals, dropdowns, etc.
    const modal = document.querySelector('[role="dialog"][aria-modal="true"]');
    if (modal) {
      const closeButton = modal.querySelector('.close-button, [aria-label*="zamknij"], [aria-label*="Zamknij"]') as HTMLButtonElement;
      closeButton?.click();
      return;
    }
    
    // Close dropdowns
    const dropdown = document.querySelector('[aria-expanded="true"]');
    if (dropdown) {
      (dropdown as HTMLElement).click();
      return;
    }
    
    // Clear search
    const searchInput = document.querySelector('input[type="search"]:focus') as HTMLInputElement;
    if (searchInput && searchInput.value) {
      searchInput.value = '';
      searchInput.dispatchEvent(new Event('input', { bubbles: true }));
    }
  }

  // Business-specific action implementations
  private createNewInvoice(): void {
    const newButton = document.querySelector('[data-action="new-invoice"], .new-invoice-button') as HTMLButtonElement;
    newButton?.click();
  }

  private editCurrentInvoice(): void {
    const editButton = document.querySelector('[data-action="edit-invoice"], .edit-invoice-button') as HTMLButtonElement;
    editButton?.click();
  }

  private deleteCurrentInvoice(): void {
    const deleteButton = document.querySelector('[data-action="delete-invoice"], .delete-invoice-button') as HTMLButtonElement;
    deleteButton?.click();
  }

  private uploadDocument(): void {
    const uploadButton = document.querySelector('[data-action="upload-document"], .upload-button') as HTMLButtonElement;
    uploadButton?.click();
  }

  private retryOCR(): void {
    const retryButton = document.querySelector('[data-action="retry-ocr"], .retry-ocr-button') as HTMLButtonElement;
    retryButton?.click();
  }
}

/**
 * Global keyboard shortcut manager instance
 */
export const keyboardShortcuts = new KeyboardShortcutManager();

/**
 * React hook for using keyboard shortcuts in components
 */
export const useKeyboardShortcuts = (shortcuts: KeyboardShortcut[], context?: string) => {
  React.useEffect(() => {
    // Register shortcuts
    shortcuts.forEach(shortcut => {
      if (context) {
        shortcut.context = context;
      }
      keyboardShortcuts.register(shortcut);
    });

    // Push context if provided
    if (context) {
      keyboardShortcuts.pushContext(context);
    }

    // Cleanup
    return () => {
      shortcuts.forEach(shortcut => {
        keyboardShortcuts.unregister(shortcut);
      });
      
      if (context) {
        keyboardShortcuts.popContext();
      }
    };
  }, [shortcuts, context]);
};

/**
 * Skip links component for keyboard navigation
 */
export const SkipLinks: React.FC = () => {
  return (
    <div className="skip-links">
      <a href="#main-content" className="skip-link">
        Przejdź do głównej zawartości
      </a>
      <a href="#main-navigation" className="skip-link">
        Przejdź do nawigacji
      </a>
      <a href="#search" className="skip-link">
        Przejdź do wyszukiwania
      </a>
    </div>
  );
};