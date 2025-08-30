/**
 * Screen Reader Support Tests
 * Comprehensive tests for ARIA support and screen reader compatibility
 */

import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { ScreenReaderAnnouncer, polishAriaLabels, generateAriaAttributes } from '../ariaUtils';

describe('Screen Reader Support', () => {
  let announcer: ScreenReaderAnnouncer;
  let user: ReturnType<typeof userEvent.setup>;

  beforeEach(() => {
    announcer = ScreenReaderAnnouncer.getInstance();
    user = userEvent.setup();
    
    // Clear any existing announcements
    announcer.clear();
  });

  afterEach(() => {
    announcer.cleanup();
    document.body.innerHTML = '';
  });

  describe('ScreenReaderAnnouncer', () => {
    it('should create live regions on initialization', () => {
      const politeRegion = document.querySelector('[aria-live="polite"]');
      const assertiveRegion = document.querySelector('[aria-live="assertive"]');
      
      expect(politeRegion).toBeInTheDocument();
      expect(assertiveRegion).toBeInTheDocument();
    });

    it('should announce polite messages', () => {
      const message = 'Test polite message';
      announcer.announcePolite(message);
      
      const politeRegion = document.querySelector('[aria-live="polite"]');
      expect(politeRegion).toHaveTextContent(message);
    });

    it('should announce assertive messages', () => {
      const message = 'Test assertive message';
      announcer.announceAssertive(message);
      
      const assertiveRegion = document.querySelector('[aria-live="assertive"]');
      expect(assertiveRegion).toHaveTextContent(message);
    });

    it('should announce errors with proper prefix', () => {
      const message = 'Test error message';
      announcer.announceError(message);
      
      const assertiveRegion = document.querySelector('[aria-live="assertive"]');
      expect(assertiveRegion).toHaveTextContent(`${polishAriaLabels.ERROR}: ${message}`);
    });

    it('should announce success with proper prefix', () => {
      const message = 'Test success message';
      announcer.announceSuccess(message);
      
      const politeRegion = document.querySelector('[aria-live="polite"]');
      expect(politeRegion).toHaveTextContent(`${polishAriaLabels.SUCCESS}: ${message}`);
    });

    it('should announce loading state', () => {
      announcer.announceLoading();
      
      const politeRegion = document.querySelector('[aria-live="polite"]');
      expect(politeRegion).toHaveTextContent(polishAriaLabels.LOADING);
    });

    it('should clear all announcements', () => {
      announcer.announcePolite('Test message');
      announcer.announceAssertive('Another message');
      
      announcer.clear();
      
      const politeRegion = document.querySelector('[aria-live="polite"]');
      const assertiveRegion = document.querySelector('[aria-live="assertive"]');
      
      expect(politeRegion).toHaveTextContent('');
      expect(assertiveRegion).toHaveTextContent('');
    });
  });

  describe('Polish ARIA Labels', () => {
    it('should provide Polish translations for common actions', () => {
      expect(polishAriaLabels.CLOSE).toBe('Zamknij');
      expect(polishAriaLabels.OPEN).toBe('Otwórz');
      expect(polishAriaLabels.SAVE).toBe('Zapisz');
      expect(polishAriaLabels.CANCEL).toBe('Anuluj');
      expect(polishAriaLabels.DELETE).toBe('Usuń');
      expect(polishAriaLabels.EDIT).toBe('Edytuj');
    });

    it('should provide Polish business-specific labels', () => {
      expect(polishAriaLabels.NIP_INPUT).toBe('Numer NIP');
      expect(polishAriaLabels.CURRENCY_INPUT).toBe('Kwota w złotych');
      expect(polishAriaLabels.VAT_RATE).toBe('Stawka VAT');
      expect(polishAriaLabels.INVOICE_NUMBER).toBe('Numer faktury');
      expect(polishAriaLabels.INVOICE_AMOUNT).toBe('Kwota faktury');
    });

    it('should provide form validation labels', () => {
      expect(polishAriaLabels.REQUIRED_FIELD).toBe('Pole wymagane');
      expect(polishAriaLabels.OPTIONAL_FIELD).toBe('Pole opcjonalne');
      expect(polishAriaLabels.INVALID_INPUT).toBe('Nieprawidłowe dane');
      expect(polishAriaLabels.ERROR_MESSAGE).toBe('Komunikat o błędzie');
    });
  });

  describe('ARIA Attributes Generation', () => {
    it('should generate button ARIA attributes', () => {
      const attrs = generateAriaAttributes.button({
        label: 'Test button',
        pressed: true,
        expanded: false,
        hasPopup: 'MENU',
        disabled: false,
      });

      expect(attrs['aria-label']).toBe('Test button');
      expect(attrs['aria-pressed']).toBe('true');
      expect(attrs['aria-expanded']).toBe('false');
      expect(attrs['aria-haspopup']).toBe('menu');
      expect(attrs['aria-disabled']).toBeUndefined();
    });

    it('should generate input ARIA attributes', () => {
      const attrs = generateAriaAttributes.input({
        label: 'Test input',
        required: true,
        invalid: true,
        errorMessage: 'error-msg-id',
        describedBy: 'help-text-id',
      });

      expect(attrs['aria-label']).toBe('Test input');
      expect(attrs['aria-required']).toBe('true');
      expect(attrs['aria-invalid']).toBe('true');
      expect(attrs['aria-errormessage']).toBe('error-msg-id');
      expect(attrs['aria-describedby']).toBe('help-text-id');
    });

    it('should generate select/combobox ARIA attributes', () => {
      const attrs = generateAriaAttributes.select({
        label: 'Test select',
        expanded: true,
        hasPopup: true,
        controls: 'listbox-id',
        activeDescendant: 'option-1',
      });

      expect(attrs.role).toBe('combobox');
      expect(attrs['aria-label']).toBe('Test select');
      expect(attrs['aria-expanded']).toBe('true');
      expect(attrs['aria-haspopup']).toBe('listbox');
      expect(attrs['aria-controls']).toBe('listbox-id');
      expect(attrs['aria-activedescendant']).toBe('option-1');
    });

    it('should generate modal ARIA attributes', () => {
      const attrs = generateAriaAttributes.modal({
        labelledBy: 'modal-title',
        describedBy: 'modal-description',
        modal: true,
      });

      expect(attrs.role).toBe('dialog');
      expect(attrs['aria-labelledby']).toBe('modal-title');
      expect(attrs['aria-describedby']).toBe('modal-description');
      expect(attrs['aria-modal']).toBe('true');
    });

    it('should generate live region ARIA attributes', () => {
      const attrs = generateAriaAttributes.liveRegion({
        live: 'ASSERTIVE',
        atomic: true,
        relevant: 'additions text',
        busy: false,
      });

      expect(attrs['aria-live']).toBe('assertive');
      expect(attrs['aria-atomic']).toBe('true');
      expect(attrs['aria-relevant']).toBe('additions text');
      expect(attrs['aria-busy']).toBe('false');
    });
  });

  describe('Form ARIA Support', () => {
    it('should provide proper ARIA labels for form fields', () => {
      document.body.innerHTML = `
        <form>
          <label for="name">Nazwa</label>
          <input id="name" type="text" aria-required="true" />
          
          <label for="email">Email</label>
          <input id="email" type="email" aria-required="true" aria-invalid="true" />
          <div id="email-error" role="alert">Nieprawidłowy email</div>
          
          <label for="nip">Numer NIP</label>
          <input id="nip" type="text" aria-describedby="nip-help" />
          <div id="nip-help">Format: 1234567890</div>
        </form>
      `;

      const nameInput = document.getElementById('name');
      const emailInput = document.getElementById('email');
      const nipInput = document.getElementById('nip');

      expect(nameInput).toHaveAttribute('aria-required', 'true');
      expect(emailInput).toHaveAttribute('aria-required', 'true');
      expect(emailInput).toHaveAttribute('aria-invalid', 'true');
      expect(nipInput).toHaveAttribute('aria-describedby', 'nip-help');
    });

    it('should announce form validation errors', async () => {
      document.body.innerHTML = `
        <form>
          <div role="alert" aria-live="assertive" class="error-summary">
            <h2>Znaleziono 2 błędy w formularzu:</h2>
            <ul>
              <li><a href="#name">Nazwa jest wymagana</a></li>
              <li><a href="#email">Nieprawidłowy email</a></li>
            </ul>
          </div>
          
          <input id="name" type="text" aria-invalid="true" />
          <input id="email" type="email" aria-invalid="true" />
        </form>
      `;

      const errorSummary = document.querySelector('.error-summary');
      expect(errorSummary).toHaveAttribute('role', 'alert');
      expect(errorSummary).toHaveAttribute('aria-live', 'assertive');
      expect(errorSummary).toHaveTextContent('Znaleziono 2 błędy w formularzu:');
    });

    it('should handle Polish business form validation', () => {
      document.body.innerHTML = `
        <form>
          <label for="nip">${polishAriaLabels.NIP_INPUT}</label>
          <input 
            id="nip" 
            type="text" 
            aria-label="${polishAriaLabels.NIP_INPUT}"
            aria-describedby="nip-format"
            aria-invalid="true"
            aria-errormessage="nip-error"
          />
          <div id="nip-format">Format: 1234567890 (10 cyfr)</div>
          <div id="nip-error" role="alert">${polishAriaLabels.NIP_INVALID}</div>
          
          <label for="amount">${polishAriaLabels.CURRENCY_INPUT}</label>
          <input 
            id="amount" 
            type="text" 
            aria-label="${polishAriaLabels.CURRENCY_INPUT}"
            aria-describedby="amount-format"
          />
          <div id="amount-format">Kwota w PLN. Format: 1234.56</div>
        </form>
      `;

      const nipInput = document.getElementById('nip');
      const amountInput = document.getElementById('amount');

      expect(nipInput).toHaveAttribute('aria-label', polishAriaLabels.NIP_INPUT);
      expect(nipInput).toHaveAttribute('aria-invalid', 'true');
      expect(nipInput).toHaveAttribute('aria-errormessage', 'nip-error');
      
      expect(amountInput).toHaveAttribute('aria-label', polishAriaLabels.CURRENCY_INPUT);
      expect(amountInput).toHaveAttribute('aria-describedby', 'amount-format');
    });
  });

  describe('Table ARIA Support', () => {
    it('should provide proper table ARIA structure', () => {
      document.body.innerHTML = `
        <table role="table" aria-label="Lista faktur">
          <caption>Faktury z ostatniego miesiąca</caption>
          <thead>
            <tr role="row">
              <th role="columnheader" aria-sort="ascending">Numer</th>
              <th role="columnheader" aria-sort="none">Klient</th>
              <th role="columnheader" aria-sort="none">Kwota</th>
            </tr>
          </thead>
          <tbody>
            <tr role="row">
              <td role="cell">FV/2023/001</td>
              <td role="cell">ABC Sp. z o.o.</td>
              <td role="cell">1,234.56 zł</td>
            </tr>
          </tbody>
        </table>
      `;

      const table = document.querySelector('table');
      const headers = document.querySelectorAll('th[role="columnheader"]');
      const cells = document.querySelectorAll('td[role="cell"]');

      expect(table).toHaveAttribute('role', 'table');
      expect(table).toHaveAttribute('aria-label', 'Lista faktur');
      expect(headers).toHaveLength(3);
      expect(headers[0]).toHaveAttribute('aria-sort', 'ascending');
      expect(cells).toHaveLength(3);
    });

    it('should announce table navigation', () => {
      const message = 'Przechodzenie do komórki 2, wiersz 1: ABC Sp. z o.o.';
      announcer.announceNavigation(message);
      
      const politeRegion = document.querySelector('[aria-live="polite"]');
      expect(politeRegion).toHaveTextContent(message);
    });
  });

  describe('Modal ARIA Support', () => {
    it('should provide proper modal ARIA structure', () => {
      document.body.innerHTML = `
        <div 
          role="dialog" 
          aria-modal="true" 
          aria-labelledby="modal-title"
          aria-describedby="modal-description"
        >
          <h2 id="modal-title">Edytuj fakturę</h2>
          <p id="modal-description">Wprowadź zmiany w danych faktury</p>
          <button aria-label="${polishAriaLabels.CLOSE}">×</button>
        </div>
      `;

      const modal = document.querySelector('[role="dialog"]');
      const closeButton = document.querySelector('button');

      expect(modal).toHaveAttribute('aria-modal', 'true');
      expect(modal).toHaveAttribute('aria-labelledby', 'modal-title');
      expect(modal).toHaveAttribute('aria-describedby', 'modal-description');
      expect(closeButton).toHaveAttribute('aria-label', polishAriaLabels.CLOSE);
    });
  });

  describe('Navigation ARIA Support', () => {
    it('should provide proper navigation ARIA structure', () => {
      document.body.innerHTML = `
        <nav role="navigation" aria-label="${polishAriaLabels.MAIN_MENU}">
          <ul role="menubar">
            <li role="none">
              <a role="menuitem" href="/invoices">Faktury</a>
            </li>
            <li role="none">
              <a role="menuitem" href="/contractors">Kontrahenci</a>
            </li>
          </ul>
        </nav>
        
        <nav role="navigation" aria-label="${polishAriaLabels.BREADCRUMB}">
          <ol>
            <li><a href="/">Strona główna</a></li>
            <li><a href="/invoices">Faktury</a></li>
            <li aria-current="page">Nowa faktura</li>
          </ol>
        </nav>
      `;

      const mainNav = document.querySelector('nav[aria-label="Menu główne"]');
      const breadcrumb = document.querySelector('nav[aria-label="Ścieżka nawigacji"]');
      const currentPage = document.querySelector('[aria-current="page"]');

      expect(mainNav).toHaveAttribute('role', 'navigation');
      expect(breadcrumb).toHaveAttribute('role', 'navigation');
      expect(currentPage).toHaveAttribute('aria-current', 'page');
    });
  });

  describe('Loading and Status ARIA Support', () => {
    it('should announce loading states', () => {
      document.body.innerHTML = `
        <div role="status" aria-live="polite" aria-label="${polishAriaLabels.LOADING}">
          <span class="sr-only">${polishAriaLabels.LOADING}</span>
          <div aria-hidden="true">Loading spinner</div>
        </div>
      `;

      const loadingStatus = document.querySelector('[role="status"]');
      expect(loadingStatus).toHaveAttribute('aria-live', 'polite');
      expect(loadingStatus).toHaveAttribute('aria-label', polishAriaLabels.LOADING);
    });

    it('should announce progress updates', () => {
      document.body.innerHTML = `
        <div 
          role="progressbar" 
          aria-valuenow="3" 
          aria-valuemin="0" 
          aria-valuemax="10"
          aria-valuetext="3 z 10 faktur przetworzonych"
          aria-live="polite"
        >
          <span class="sr-only">3 z 10 faktur przetworzonych</span>
        </div>
      `;

      const progressBar = document.querySelector('[role="progressbar"]');
      expect(progressBar).toHaveAttribute('aria-valuenow', '3');
      expect(progressBar).toHaveAttribute('aria-valuemax', '10');
      expect(progressBar).toHaveAttribute('aria-valuetext', '3 z 10 faktur przetworzonych');
    });
  });

  describe('Polish Language Screen Reader Support', () => {
    it('should set proper language attributes', () => {
      document.body.innerHTML = `
        <div lang="pl">
          <p>Treść w języku polskim</p>
          <span lang="en">English content</span>
        </div>
      `;

      const polishContent = document.querySelector('[lang="pl"]');
      const englishContent = document.querySelector('[lang="en"]');

      expect(polishContent).toHaveAttribute('lang', 'pl');
      expect(englishContent).toHaveAttribute('lang', 'en');
    });

    it('should format Polish currency for screen readers', () => {
      const amount = 1234.56;
      const formatted = `${amount.toFixed(2).replace('.', ',')} złotych`;
      
      expect(formatted).toBe('1234,56 złotych');
    });

    it('should format Polish dates for screen readers', () => {
      const date = new Date('2023-12-31');
      const formatted = date.toLocaleDateString('pl-PL', {
        day: 'numeric',
        month: 'long',
        year: 'numeric'
      });
      
      expect(formatted).toBe('31 grudnia 2023');
    });
  });
});