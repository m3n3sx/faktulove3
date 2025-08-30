/**
 * Screen Reader Demo
 * Demonstrates comprehensive screen reader and ARIA support
 */

import React, { useState } from 'react';
import {
  LiveRegion,
  PoliteLiveRegion,
  AssertiveLiveRegion,
  StatusRegion,
  AlertRegion,
  useLiveRegion,
  AriaLabel,
  NIPLabel,
  CurrencyLabel,
  DateLabel,
  VATLabel,
  ScreenReaderOnly,
  VisuallyHidden,
  AriaDescription,
  AriaErrorMessage,
  LoadingAnnouncement,
  SuccessAnnouncement,
  ProgressAnnouncement,
  FormErrorAnnouncer,
  PolishBusinessFormErrorAnnouncer,
  useFormErrorAnnouncer,
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

export const ScreenReaderDemo: React.FC = () => {
  const [politeMessage, setPoliteMessage] = useState('');
  const [assertiveMessage, setAssertiveMessage] = useState('');
  const [statusMessage, setStatusMessage] = useState('');
  const [alertMessage, setAlertMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [showSuccess, setShowSuccess] = useState(false);
  const [progress, setProgress] = useState({ current: 0, total: 10 });
  const [formErrors, setFormErrors] = useState([]);
  const [businessFormErrors, setBusinessFormErrors] = useState([]);

  const { 
    announcePolite, 
    announceAssertive, 
    announceError, 
    announceSuccess,
    announceLoading,
    announceNavigation,
    clear 
  } = useLiveRegion();

  const {
    announceFieldError,
    announceFieldSuccess,
    announceFormSubmission,
    announceFormSuccess,
    announceNIPValidation,
    announceCurrencyValidation,
    announceDateValidation,
    announceVATValidation,
  } = useFormErrorAnnouncer();

  const handlePoliteAnnouncement = () => {
    const message = 'To jest spokojne ogłoszenie, które nie przerywa czytania.';
    setPoliteMessage(message);
    announcePolite(message);
  };

  const handleAssertiveAnnouncement = () => {
    const message = 'To jest pilne ogłoszenie, które przerywa czytanie!';
    setAssertiveMessage(message);
    announceAssertive(message);
  };

  const handleStatusUpdate = () => {
    const message = 'Status został zaktualizowany.';
    setStatusMessage(message);
    announcePolite(message);
  };

  const handleAlert = () => {
    const message = 'Uwaga! Wystąpił błąd w systemie.';
    setAlertMessage(message);
    announceError(message);
  };

  const handleLoadingDemo = () => {
    setIsLoading(true);
    announceLoading('Ładowanie danych faktury...');
    
    setTimeout(() => {
      setIsLoading(false);
      setShowSuccess(true);
      announceSuccess('Dane faktury zostały załadowane pomyślnie');
      
      setTimeout(() => setShowSuccess(false), 3000);
    }, 2000);
  };

  const handleProgressDemo = () => {
    setProgress({ current: 0, total: 10 });
    
    const interval = setInterval(() => {
      setProgress(prev => {
        const newCurrent = prev.current + 1;
        if (newCurrent >= prev.total) {
          clearInterval(interval);
          announceSuccess('Przetwarzanie zakończone pomyślnie');
          return prev;
        }
        return { ...prev, current: newCurrent };
      });
    }, 500);
  };

  const handleFormValidation = () => {
    const errors = [
      { field: 'name', message: 'Nazwa firmy jest wymagana', type: 'required' },
      { field: 'email', message: 'Nieprawidłowy adres email', type: 'invalid' },
      { field: 'phone', message: 'Numer telefonu musi mieć 9 cyfr', type: 'format' },
    ];
    
    setFormErrors(errors);
    announceError(`Znaleziono ${errors.length} błędów w formularzu`);
  };

  const handleBusinessFormValidation = () => {
    const errors = [
      { field: 'nip', message: 'Nieprawidłowy numer NIP', type: 'business' },
      { field: 'amount', message: 'Kwota musi być większa od 0', type: 'business' },
      { field: 'vat-rate', message: 'Wybierz stawkę VAT', type: 'required' },
    ];
    
    setBusinessFormErrors(errors);
    announceError(`Znaleziono błędy w danych biznesowych`);
  };

  const handleFieldValidation = (field: string, isValid: boolean) => {
    switch (field) {
      case 'nip':
        announceNIPValidation(isValid);
        break;
      case 'currency':
        announceCurrencyValidation(isValid);
        break;
      case 'date':
        announceDateValidation(isValid);
        break;
      case 'vat':
        announceVATValidation(isValid);
        break;
    }
  };

  const handleNavigation = (destination: string) => {
    announceNavigation(`Przechodzenie do sekcji: ${destination}`);
  };

  const clearAllMessages = () => {
    setPoliteMessage('');
    setAssertiveMessage('');
    setStatusMessage('');
    setAlertMessage('');
    setFormErrors([]);
    setBusinessFormErrors([]);
    clear();
  };

  const invoiceData = [
    { 
      id: 1, 
      number: 'FV/2023/001', 
      client: 'ABC Sp. z o.o.', 
      amount: '1,234.56 zł', 
      status: 'Opłacona',
      'aria-label': 'Faktura FV/2023/001 dla ABC Sp. z o.o. na kwotę 1,234.56 zł, status: Opłacona'
    },
    { 
      id: 2, 
      number: 'FV/2023/002', 
      client: 'XYZ S.A.', 
      amount: '2,345.67 zł', 
      status: 'Oczekująca',
      'aria-label': 'Faktura FV/2023/002 dla XYZ S.A. na kwotę 2,345.67 zł, status: Oczekująca'
    },
  ];

  const tableColumns = [
    { 
      key: 'number', 
      header: 'Numer faktury',
      'aria-label': 'Numer faktury, sortowanie dostępne'
    },
    { 
      key: 'client', 
      header: 'Klient',
      'aria-label': 'Nazwa klienta, sortowanie dostępne'
    },
    { 
      key: 'amount', 
      header: 'Kwota',
      'aria-label': 'Kwota faktury w złotych, sortowanie dostępne'
    },
    { 
      key: 'status', 
      header: 'Status',
      'aria-label': 'Status płatności faktury'
    },
  ];

  return (
    <div className="screen-reader-demo">
      {/* Live Regions for Announcements */}
      <PoliteLiveRegion message={politeMessage} />
      <AssertiveLiveRegion message={assertiveMessage} />
      <StatusRegion message={statusMessage} />
      <AlertRegion message={alertMessage} />

      {/* Main Content */}
      <main id="main-content" tabIndex={-1}>
        <div className="demo-container">
          <h1>Demo wsparcia czytników ekranu</h1>
          
          <ScreenReaderOnly>
            Ta strona demonstruje funkcje dostępności dla czytników ekranu.
            Użyj czytnika ekranu aby usłyszeć ogłoszenia i opisy elementów.
          </ScreenReaderOnly>

          {/* Live Region Demonstrations */}
          <Card className="mb-6">
            <h2>Ogłoszenia na żywo</h2>
            <AriaDescription>
              Poniższe przyciski demonstrują różne typy ogłoszeń dla czytników ekranu.
            </AriaDescription>
            
            <div className="demo-buttons">
              <Button onClick={handlePoliteAnnouncement}>
                Spokojne ogłoszenie
                <ScreenReaderOnly> - nie przerywa czytania</ScreenReaderOnly>
              </Button>
              
              <Button onClick={handleAssertiveAnnouncement} variant="secondary">
                Pilne ogłoszenie
                <ScreenReaderOnly> - przerywa czytanie</ScreenReaderOnly>
              </Button>
              
              <Button onClick={handleStatusUpdate} variant="outline">
                Aktualizacja statusu
              </Button>
              
              <Button onClick={handleAlert} variant="destructive">
                Alert błędu
              </Button>
              
              <Button onClick={clearAllMessages} variant="ghost">
                Wyczyść wszystkie
              </Button>
            </div>
          </Card>

          {/* Loading and Progress Demonstrations */}
          <Card className="mb-6">
            <h2>Stany ładowania i postępu</h2>
            
            <div className="demo-section">
              <Button onClick={handleLoadingDemo} disabled={isLoading}>
                {isLoading ? 'Ładowanie...' : 'Rozpocznij ładowanie'}
              </Button>
              
              {isLoading && (
                <LoadingAnnouncement message="Ładowanie danych faktury..." />
              )}
              
              {showSuccess && (
                <SuccessAnnouncement message="Dane faktury zostały załadowane pomyślnie" />
              )}
            </div>
            
            <div className="demo-section">
              <Button onClick={handleProgressDemo}>
                Rozpocznij przetwarzanie
              </Button>
              
              {progress.current > 0 && progress.current < progress.total && (
                <ProgressAnnouncement
                  current={progress.current}
                  total={progress.total}
                  label="Przetwarzanie faktur"
                />
              )}
            </div>
          </Card>

          {/* Form Error Demonstrations */}
          <Card className="mb-6">
            <h2>Ogłaszanie błędów formularza</h2>
            
            <div className="demo-section">
              <h3>Standardowe błędy formularza</h3>
              <Button onClick={handleFormValidation}>
                Pokaż błędy formularza
              </Button>
              <Button onClick={() => setFormErrors([])} variant="outline">
                Wyczyść błędy
              </Button>
              
              <FormErrorAnnouncer
                errors={formErrors}
                onErrorClick={(fieldId) => {
                  announceNavigation(`Przechodzenie do pola: ${fieldId}`);
                  const field = document.getElementById(fieldId);
                  if (field) field.focus();
                }}
              />
            </div>
            
            <div className="demo-section">
              <h3>Błędy formularza biznesowego</h3>
              <Button onClick={handleBusinessFormValidation}>
                Pokaż błędy biznesowe
              </Button>
              <Button onClick={() => setBusinessFormErrors([])} variant="outline">
                Wyczyść błędy
              </Button>
              
              <PolishBusinessFormErrorAnnouncer
                errors={businessFormErrors}
                onErrorClick={(fieldId) => {
                  announceNavigation(`Przechodzenie do pola biznesowego: ${fieldId}`);
                }}
              />
            </div>
          </Card>

          {/* Polish Business Form with ARIA Labels */}
          <Card className="mb-6">
            <h2>Formularz biznesowy z etykietami ARIA</h2>
            
            <Form className="polish-business-form">
              <div className="form-grid">
                <div className="form-field">
                  <NIPLabel 
                    htmlFor="demo-nip" 
                    required 
                    error={businessFormErrors.find(e => e.field === 'nip')?.message}
                  />
                  <NIPValidator
                    id="demo-nip"
                    aria-describedby="nip-help"
                    aria-invalid={businessFormErrors.some(e => e.field === 'nip')}
                    onValidation={(isValid) => handleFieldValidation('nip', isValid)}
                  />
                  <AriaDescription id="nip-help">
                    Wprowadź 10-cyfrowy numer NIP bez kresek i spacji
                  </AriaDescription>
                </div>

                <div className="form-field">
                  <CurrencyLabel 
                    htmlFor="demo-amount" 
                    required
                    error={businessFormErrors.find(e => e.field === 'amount')?.message}
                  />
                  <CurrencyInput
                    id="demo-amount"
                    currency="PLN"
                    aria-describedby="amount-help"
                    aria-invalid={businessFormErrors.some(e => e.field === 'amount')}
                    onValidation={(isValid) => handleFieldValidation('currency', isValid)}
                  />
                  <AriaDescription id="amount-help">
                    Wprowadź kwotę w złotych polskich, np. 1234.56
                  </AriaDescription>
                </div>

                <div className="form-field">
                  <VATLabel 
                    htmlFor="demo-vat" 
                    required
                    error={businessFormErrors.find(e => e.field === 'vat-rate')?.message}
                  />
                  <VATRateSelector
                    id="demo-vat"
                    rates={[0, 5, 8, 23]}
                    aria-describedby="vat-help"
                    aria-invalid={businessFormErrors.some(e => e.field === 'vat-rate')}
                    onValidation={(isValid) => handleFieldValidation('vat', isValid)}
                  />
                  <AriaDescription id="vat-help">
                    Wybierz odpowiednią stawkę VAT dla faktury
                  </AriaDescription>
                </div>

                <div className="form-field">
                  <DateLabel 
                    htmlFor="demo-date" 
                    required
                  />
                  <DatePicker
                    id="demo-date"
                    format="DD.MM.YYYY"
                    aria-describedby="date-help"
                    onValidation={(isValid) => handleFieldValidation('date', isValid)}
                  />
                  <AriaDescription id="date-help">
                    Wprowadź datę w formacie DD.MM.YYYY, np. 31.12.2023
                  </AriaDescription>
                </div>
              </div>
            </Form>
          </Card>

          {/* Accessible Table */}
          <Card className="mb-6">
            <h2>Tabela z wsparciem ARIA</h2>
            <AriaDescription>
              Tabela faktur z pełnym wsparciem dla czytników ekranu.
              Użyj strzałek aby poruszać się po komórkach.
            </AriaDescription>
            
            <Table
              data={invoiceData}
              columns={tableColumns}
              caption="Lista faktur z ostatniego miesiąca - 2 pozycje"
              sortable
              onSort={(column, direction) => {
                announcePolite(`Sortowanie według ${column} ${direction === 'asc' ? 'rosnąco' : 'malejąco'}`);
              }}
              onCellFocus={(row, column) => {
                const cellContent = row[column];
                announceNavigation(`Komórka ${column}: ${cellContent}`);
              }}
            />
          </Card>

          {/* Navigation Announcements */}
          <Card className="mb-6">
            <h2>Ogłoszenia nawigacji</h2>
            <AriaDescription>
              Poniższe przyciski demonstrują ogłoszenia nawigacji.
            </AriaDescription>
            
            <nav role="navigation" aria-label="Demo nawigacji">
              <div className="nav-buttons">
                <Button 
                  variant="ghost"
                  onClick={() => handleNavigation('Faktury')}
                >
                  Faktury
                </Button>
                <Button 
                  variant="ghost"
                  onClick={() => handleNavigation('Kontrahenci')}
                >
                  Kontrahenci
                </Button>
                <Button 
                  variant="ghost"
                  onClick={() => handleNavigation('OCR')}
                >
                  OCR
                </Button>
                <Button 
                  variant="ghost"
                  onClick={() => handleNavigation('Raporty')}
                >
                  Raporty
                </Button>
              </div>
            </nav>
          </Card>

          {/* Hidden Content Examples */}
          <Card>
            <h2>Ukryta zawartość dla czytników ekranu</h2>
            
            <div className="hidden-content-examples">
              <p>
                Ten tekst jest widoczny dla wszystkich.
                <ScreenReaderOnly>
                  Ten tekst jest dostępny tylko dla czytników ekranu.
                </ScreenReaderOnly>
              </p>
              
              <p>
                Przycisk z ukrytym opisem:
                <Button>
                  Usuń
                  <ScreenReaderOnly> fakturę FV/2023/001</ScreenReaderOnly>
                </Button>
              </p>
              
              <p>
                Ukryta zawartość z możliwością fokusa:
                <VisuallyHidden focusable>
                  Ta zawartość stanie się widoczna po otrzymaniu fokusa
                </VisuallyHidden>
              </p>
            </div>
          </Card>
        </div>
      </main>

      <style jsx>{`
        .screen-reader-demo {
          min-height: 100vh;
          background: var(--ds-color-gray-50);
        }

        .demo-container {
          max-width: 1200px;
          margin: 0 auto;
          padding: 2rem;
        }

        .demo-buttons {
          display: flex;
          gap: 1rem;
          flex-wrap: wrap;
          margin-top: 1rem;
        }

        .demo-section {
          margin: 1.5rem 0;
          padding: 1rem;
          border: 1px solid var(--ds-color-gray-200);
          border-radius: 6px;
          background: var(--ds-color-white);
        }

        .demo-section h3 {
          margin: 0 0 1rem;
          font-size: 16px;
          font-weight: 600;
          color: var(--ds-color-gray-800);
        }

        .form-grid {
          display: grid;
          grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
          gap: 1.5rem;
          margin: 1.5rem 0;
        }

        .form-field {
          display: flex;
          flex-direction: column;
          gap: 0.5rem;
        }

        .nav-buttons {
          display: flex;
          gap: 0.5rem;
          flex-wrap: wrap;
        }

        .hidden-content-examples {
          display: flex;
          flex-direction: column;
          gap: 1rem;
        }

        @media (max-width: 768px) {
          .demo-container {
            padding: 1rem;
          }
          
          .demo-buttons {
            flex-direction: column;
          }
          
          .form-grid {
            grid-template-columns: 1fr;
          }
        }
      `}</style>
    </div>
  );
};

export default ScreenReaderDemo;