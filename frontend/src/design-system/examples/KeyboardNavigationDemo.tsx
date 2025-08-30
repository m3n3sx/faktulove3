/**
 * Keyboard Navigation Demo
 * Demonstrates comprehensive keyboard navigation features
 */

import React, { useState } from 'react';
import {
  SkipLinks,
  KeyboardShortcutsHelp,
  Button,
  Input,
  Select,
  Card,
  Table,
  Form,
  CurrencyInput,
  NIPValidator,
  VATRateSelector,
  DatePicker,
} from '../index';
import {
  useKeyboardShortcuts,
  useFocusTrap,
  useDropdownNavigation,
  useArrowNavigation,
  usePolishFormNavigation,
  useTableNavigation,
} from '../hooks/useKeyboardNavigation';
import { keyboardShortcuts } from '../utils/keyboardShortcuts';

export const KeyboardNavigationDemo: React.FC = () => {
  const [showHelp, setShowHelp] = useState(false);
  const [showModal, setShowModal] = useState(false);
  const [showDropdown, setShowDropdown] = useState(false);
  const [selectedTab, setSelectedTab] = useState(0);

  // Set up keyboard shortcuts for this demo
  useKeyboardShortcuts([
    {
      key: '?',
      shiftKey: true,
      description: 'Pokaż pomoc',
      action: () => setShowHelp(true),
    },
    {
      key: 'm',
      ctrlKey: true,
      description: 'Otwórz modal',
      action: () => setShowModal(true),
    },
    {
      key: 'd',
      ctrlKey: true,
      description: 'Otwórz dropdown',
      action: () => setShowDropdown(!showDropdown),
    },
  ], 'demo');

  // Focus trap for modal
  const modalRef = useFocusTrap(showModal);

  // Dropdown navigation
  const { triggerRef, dropdownRef } = useDropdownNavigation(showDropdown);

  // Arrow navigation for tabs
  const tabsRef = useArrowNavigation({
    orientation: 'horizontal',
    itemSelector: '[role="tab"]',
  });

  // Polish form navigation
  const {
    formRef,
    errors,
    createErrorSummary,
    clearErrorSummary,
  } = usePolishFormNavigation();

  // Table navigation
  const tableRef = useTableNavigation();

  const handleFormSubmit = (data: any) => {
    // Simulate validation errors
    const formErrors = [
      { field: 'nip', message: 'Nieprawidłowy numer NIP' },
      { field: 'amount', message: 'Kwota jest wymagana' },
    ];
    
    if (formErrors.length > 0) {
      createErrorSummary(formErrors);
    } else {
      clearErrorSummary();
      console.log('Form submitted:', data);
    }
  };

  const invoiceData = [
    { id: 1, number: 'FV/2023/001', client: 'ABC Sp. z o.o.', amount: '1,234.56 zł', status: 'Opłacona' },
    { id: 2, number: 'FV/2023/002', client: 'XYZ S.A.', amount: '2,345.67 zł', status: 'Oczekująca' },
    { id: 3, number: 'FV/2023/003', client: 'DEF Sp. j.', amount: '3,456.78 zł', status: 'Przeterminowana' },
  ];

  const tableColumns = [
    { key: 'number', header: 'Numer faktury' },
    { key: 'client', header: 'Klient' },
    { key: 'amount', header: 'Kwota' },
    { key: 'status', header: 'Status' },
  ];

  return (
    <div className="keyboard-navigation-demo">
      {/* Skip Links */}
      <SkipLinks />

      {/* Main Navigation */}
      <nav id="main-navigation" role="navigation" aria-label="Główna nawigacja">
        <div className="nav-container">
          <Button variant="ghost">Faktury</Button>
          <Button variant="ghost">Kontrahenci</Button>
          <Button variant="ghost">OCR</Button>
          <Button variant="ghost">Raporty</Button>
        </div>
      </nav>

      {/* Main Content */}
      <main id="main-content" tabindex="-1">
        <div className="demo-container">
          <h1>Demo nawigacji klawiszowej</h1>
          <p>
            Użyj <kbd>Shift + ?</kbd> aby zobaczyć dostępne skróty klawiszowe.
            Użyj <kbd>Tab</kbd> aby poruszać się po elementach.
          </p>

          {/* Tab Navigation Example */}
          <Card className="mb-6">
            <h2>Nawigacja zakładkami</h2>
            <div ref={tabsRef} role="tablist" aria-label="Przykładowe zakładki">
              {['Faktury', 'Kontrahenci', 'Raporty'].map((tab, index) => (
                <button
                  key={index}
                  role="tab"
                  aria-selected={selectedTab === index}
                  aria-controls={`tabpanel-${index}`}
                  tabIndex={selectedTab === index ? 0 : -1}
                  onClick={() => setSelectedTab(index)}
                  className={`tab ${selectedTab === index ? 'active' : ''}`}
                >
                  {tab}
                </button>
              ))}
            </div>
            <div
              id={`tabpanel-${selectedTab}`}
              role="tabpanel"
              aria-labelledby={`tab-${selectedTab}`}
              className="tab-content"
            >
              <p>Zawartość zakładki: {['Faktury', 'Kontrahenci', 'Raporty'][selectedTab]}</p>
            </div>
          </Card>

          {/* Polish Business Form */}
          <Card className="mb-6">
            <h2>Formularz biznesowy</h2>
            <Form
              ref={formRef}
              onSubmit={handleFormSubmit}
              className="polish-form-navigation"
            >
              <div className="form-grid">
                <NIPValidator
                  id="nip"
                  label="Numer NIP"
                  required
                  aria-describedby="nip-help"
                />
                <div id="nip-help" className="help-text">
                  Wprowadź 10-cyfrowy numer NIP
                </div>

                <CurrencyInput
                  id="amount"
                  label="Kwota"
                  currency="PLN"
                  required
                />

                <VATRateSelector
                  id="vat-rate"
                  label="Stawka VAT"
                  rates={[0, 5, 8, 23]}
                  required
                />

                <DatePicker
                  id="date"
                  label="Data faktury"
                  format="DD.MM.YYYY"
                  required
                />
              </div>

              <div className="form-actions">
                <Button type="button" variant="secondary">
                  Anuluj
                </Button>
                <Button type="submit" variant="primary">
                  Zapisz (Ctrl+Enter)
                </Button>
              </div>
            </Form>
          </Card>

          {/* Table Navigation */}
          <Card className="mb-6">
            <h2>Nawigacja w tabeli</h2>
            <p>Użyj strzałek aby poruszać się po komórkach tabeli.</p>
            <Table
              ref={tableRef}
              data={invoiceData}
              columns={tableColumns}
              className="table-keyboard-navigation"
              caption="Lista faktur z nawigacją klawiszową"
            />
          </Card>

          {/* Dropdown Navigation */}
          <Card className="mb-6">
            <h2>Nawigacja w dropdown</h2>
            <div className="dropdown-keyboard-navigation">
              <Button
                ref={triggerRef}
                onClick={() => setShowDropdown(!showDropdown)}
                aria-expanded={showDropdown}
                aria-haspopup="menu"
                className="dropdown-trigger"
              >
                Akcje {showDropdown ? '▲' : '▼'}
              </Button>
              {showDropdown && (
                <div
                  ref={dropdownRef}
                  role="menu"
                  className="dropdown-menu"
                  aria-label="Menu akcji"
                >
                  <button role="menuitem" className="dropdown-item">
                    Edytuj
                  </button>
                  <button role="menuitem" className="dropdown-item">
                    Usuń
                  </button>
                  <button role="menuitem" className="dropdown-item">
                    Duplikuj
                  </button>
                </div>
              )}
            </div>
          </Card>

          {/* Action Buttons */}
          <Card>
            <h2>Akcje</h2>
            <div className="action-buttons">
              <Button onClick={() => setShowModal(true)}>
                Otwórz modal (Ctrl+M)
              </Button>
              <Button onClick={() => setShowHelp(true)}>
                Pokaż pomoc (Shift+?)
              </Button>
              <Button onClick={() => keyboardShortcuts.showHelp()}>
                Skróty klawiszowe
              </Button>
            </div>
          </Card>
        </div>
      </main>

      {/* Modal Example */}
      {showModal && (
        <div className="modal-keyboard-navigation">
          <div
            ref={modalRef}
            role="dialog"
            aria-labelledby="modal-title"
            aria-modal="true"
            className="modal-content"
          >
            <h2 id="modal-title">Przykładowy modal</h2>
            <p>
              Ten modal ma aktywną pułapkę fokusa. Użyj <kbd>Tab</kbd> aby poruszać się
              po elementach, <kbd>Esc</kbd> aby zamknąć.
            </p>
            <div className="modal-form">
              <Input label="Nazwa" placeholder="Wprowadź nazwę" />
              <Input label="Email" type="email" placeholder="email@example.com" />
              <Select
                label="Kategoria"
                options={[
                  { value: 'a', label: 'Kategoria A' },
                  { value: 'b', label: 'Kategoria B' },
                ]}
              />
            </div>
            <div className="modal-actions">
              <Button
                variant="secondary"
                onClick={() => setShowModal(false)}
              >
                Anuluj
              </Button>
              <Button
                variant="primary"
                onClick={() => setShowModal(false)}
              >
                Zapisz
              </Button>
            </div>
          </div>
        </div>
      )}

      {/* Keyboard Shortcuts Help */}
      <KeyboardShortcutsHelp
        isOpen={showHelp}
        onClose={() => setShowHelp(false)}
      />

      <style jsx>{`
        .keyboard-navigation-demo {
          min-height: 100vh;
        }

        .nav-container {
          display: flex;
          gap: 1rem;
          padding: 1rem;
          background: var(--ds-color-gray-50);
          border-bottom: 1px solid var(--ds-color-gray-200);
        }

        .demo-container {
          max-width: 1200px;
          margin: 0 auto;
          padding: 2rem;
        }

        .tab {
          padding: 0.5rem 1rem;
          border: 1px solid var(--ds-color-gray-300);
          background: var(--ds-color-white);
          cursor: pointer;
          border-radius: 4px 4px 0 0;
          margin-right: 2px;
        }

        .tab.active {
          background: var(--ds-color-primary-50);
          border-bottom-color: var(--ds-color-primary-50);
        }

        .tab:focus-visible {
          outline: 2px solid var(--ds-color-primary-500);
          outline-offset: 2px;
        }

        .tab-content {
          padding: 1rem;
          border: 1px solid var(--ds-color-gray-300);
          border-top: none;
          background: var(--ds-color-primary-50);
        }

        .form-grid {
          display: grid;
          grid-template-columns: 1fr 1fr;
          gap: 1rem;
          margin-bottom: 1.5rem;
        }

        .form-actions {
          display: flex;
          gap: 1rem;
          justify-content: flex-end;
        }

        .help-text {
          font-size: 0.875rem;
          color: var(--ds-color-gray-600);
          grid-column: span 2;
          margin-top: -0.5rem;
        }

        .dropdown-keyboard-navigation {
          position: relative;
          display: inline-block;
        }

        .dropdown-menu {
          position: absolute;
          top: 100%;
          left: 0;
          background: var(--ds-color-white);
          border: 1px solid var(--ds-color-gray-300);
          border-radius: 4px;
          box-shadow: var(--ds-shadow-md);
          z-index: 100;
          min-width: 150px;
        }

        .dropdown-item {
          display: block;
          width: 100%;
          padding: 0.5rem 0.75rem;
          border: none;
          background: none;
          text-align: left;
          cursor: pointer;
          color: var(--ds-color-gray-700);
        }

        .dropdown-item:hover,
        .dropdown-item:focus {
          background: var(--ds-color-primary-50);
          color: var(--ds-color-primary-700);
          outline: none;
        }

        .action-buttons {
          display: flex;
          gap: 1rem;
          flex-wrap: wrap;
        }

        .modal-keyboard-navigation {
          position: fixed;
          top: 0;
          left: 0;
          right: 0;
          bottom: 0;
          background: rgba(0, 0, 0, 0.5);
          display: flex;
          align-items: center;
          justify-content: center;
          z-index: 1000;
        }

        .modal-content {
          background: var(--ds-color-white);
          border-radius: 8px;
          box-shadow: var(--ds-shadow-lg);
          padding: 2rem;
          max-width: 500px;
          width: 90%;
          max-height: 80vh;
          overflow: auto;
        }

        .modal-form {
          margin: 1.5rem 0;
          display: flex;
          flex-direction: column;
          gap: 1rem;
        }

        .modal-actions {
          display: flex;
          gap: 1rem;
          justify-content: flex-end;
        }

        kbd {
          font-family: var(--ds-font-mono);
          font-size: 0.875em;
          background: var(--ds-color-gray-100);
          color: var(--ds-color-gray-700);
          padding: 0.125rem 0.25rem;
          border-radius: 3px;
          border: 1px solid var(--ds-color-gray-300);
        }

        @media (max-width: 768px) {
          .form-grid {
            grid-template-columns: 1fr;
          }
          
          .help-text {
            grid-column: span 1;
          }
          
          .action-buttons {
            flex-direction: column;
          }
        }
      `}</style>
    </div>
  );
};

export default KeyboardNavigationDemo;