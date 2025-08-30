import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { jest } from '@jest/globals';
import axios from 'axios';
import OCRResultsPage from '../OCRResultsPage';
import { DesignSystemProvider } from '../../design-system/providers/DesignSystemProvider';

// Mock axios
jest.mock('axios');
const mockedAxios = axios;

// Mock window.location
delete window.location;
window.location = { href: '' };

// Test wrapper with design system provider
const TestWrapper = ({ children }) => (
  <DesignSystemProvider>
    {children}
  </DesignSystemProvider>
);

// Sample OCR results data
const mockOCRResults = {
  results: [
    {
      id: '1',
      document: {
        original_filename: 'faktura_001.pdf',
        file_size: 245760,
      },
      created_at: '2025-01-15T10:30:00Z',
      confidence_score: 95.5,
      extracted_data: {
        invoice_number: 'FV/2025/001',
        invoice_date: '2025-01-15',
        supplier_name: 'ABC Sp. z o.o.',
        total_amount: '1230.50',
        net_amount: '1000.41',
        currency: 'PLN',
      },
      faktura: null,
    },
    {
      id: '2',
      document: {
        original_filename: 'invoice_002.jpg',
        file_size: 512000,
      },
      created_at: '2025-01-16T14:20:00Z',
      confidence_score: 78.2,
      extracted_data: {
        invoice_number: 'INV-2025-002',
        invoice_date: '2025-01-16',
        supplier_name: 'XYZ S.A.',
        total_amount: '2500.00',
        net_amount: '2032.52',
        currency: 'PLN',
      },
      faktura: {
        id: '123',
        numer: 'FV/2025/002',
      },
    },
  ],
  count: 2,
  stats: {
    total: 2,
    highConfidence: 1,
    needsReview: 1,
    withInvoice: 1,
  },
};

describe('OCRResultsPage', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    mockedAxios.get.mockResolvedValue({ data: mockOCRResults });
  });

  it('renders page header correctly', async () => {
    render(
      <TestWrapper>
        <OCRResultsPage />
      </TestWrapper>
    );

    expect(screen.getByText('Wyniki OCR')).toBeInTheDocument();
    expect(screen.getByText('Przegląd i zarządzanie wynikami przetwarzania dokumentów')).toBeInTheDocument();
    expect(screen.getByText('Prześlij nowy dokument')).toBeInTheDocument();
  });

  it('displays statistics cards', async () => {
    render(
      <TestWrapper>
        <OCRResultsPage />
      </TestWrapper>
    );

    await waitFor(() => {
      expect(screen.getByText('2')).toBeInTheDocument(); // Total results
      expect(screen.getByText('Łącznie wyników')).toBeInTheDocument();
      expect(screen.getByText('Wysoka pewność')).toBeInTheDocument();
      expect(screen.getByText('Wymaga przeglądu')).toBeInTheDocument();
      expect(screen.getByText('Faktury utworzone')).toBeInTheDocument();
    });
  });

  it('displays OCR results in table', async () => {
    render(
      <TestWrapper>
        <OCRResultsPage />
      </TestWrapper>
    );

    await waitFor(() => {
      expect(screen.getByText('faktura_001.pdf')).toBeInTheDocument();
      expect(screen.getByText('invoice_002.jpg')).toBeInTheDocument();
      expect(screen.getByText('FV/2025/001')).toBeInTheDocument();
      expect(screen.getByText('INV-2025-002')).toBeInTheDocument();
    });
  });

  it('shows confidence badges correctly', async () => {
    render(
      <TestWrapper>
        <OCRResultsPage />
      </TestWrapper>
    );

    await waitFor(() => {
      expect(screen.getByText('95.5%')).toBeInTheDocument();
      expect(screen.getByText('78.2%')).toBeInTheDocument();
    });
  });

  it('displays correct action buttons based on status', async () => {
    render(
      <TestWrapper>
        <OCRResultsPage />
      </TestWrapper>
    );

    await waitFor(() => {
      // First result (no invoice) should have "Utwórz" button
      const createButtons = screen.getAllByText('Utwórz');
      expect(createButtons.length).toBeGreaterThan(0);

      // Second result (with invoice) should have "Faktura" button
      const invoiceButtons = screen.getAllByText('Faktura');
      expect(invoiceButtons.length).toBeGreaterThan(0);
    });
  });

  it('handles filter changes', async () => {
    render(
      <TestWrapper>
        <OCRResultsPage />
      </TestWrapper>
    );

    await waitFor(() => {
      const highConfidenceFilter = screen.getByText('Wysoka pewność');
      fireEvent.click(highConfidenceFilter);
    });

    // Should make new API call with filter
    await waitFor(() => {
      expect(mockedAxios.get).toHaveBeenCalledWith(
        expect.stringContaining('status=high-confidence')
      );
    });
  });

  it('handles sorting', async () => {
    render(
      <TestWrapper>
        <OCRResultsPage />
      </TestWrapper>
    );

    await waitFor(() => {
      const confidenceHeader = screen.getByText('Pewność OCR');
      fireEvent.click(confidenceHeader);
    });

    // Should update sort configuration
    expect(mockedAxios.get).toHaveBeenCalledWith(
      expect.stringContaining('sort_by=confidence_score')
    );
  });

  it('handles pagination', async () => {
    render(
      <TestWrapper>
        <OCRResultsPage />
      </TestWrapper>
    );

    await waitFor(() => {
      // Wait for initial load
      expect(screen.getByText('faktura_001.pdf')).toBeInTheDocument();
    });

    // Mock pagination response
    mockedAxios.get.mockResolvedValueOnce({
      data: {
        ...mockOCRResults,
        results: [], // Empty second page
      },
    });

    // Find and click next page button (if exists)
    const nextButton = screen.queryByText('Następna');
    if (nextButton && !nextButton.disabled) {
      fireEvent.click(nextButton);

      await waitFor(() => {
        expect(mockedAxios.get).toHaveBeenCalledWith(
          expect.stringContaining('page=2')
        );
      });
    }
  });

  it('handles row selection', async () => {
    render(
      <TestWrapper>
        <OCRResultsPage />
      </TestWrapper>
    );

    await waitFor(() => {
      const checkboxes = screen.getAllByRole('checkbox');
      // First checkbox should be "select all", skip it
      if (checkboxes.length > 1) {
        fireEvent.click(checkboxes[1]); // Select first row
      }
    });

    // Should show bulk actions
    await waitFor(() => {
      expect(screen.getByText(/Zaznaczono \d+ wynik/)).toBeInTheDocument();
      expect(screen.getByText('Utwórz faktury')).toBeInTheDocument();
      expect(screen.getByText('Eksportuj')).toBeInTheDocument();
    });
  });

  it('handles API errors gracefully', async () => {
    mockedAxios.get.mockRejectedValueOnce(new Error('Network error'));

    render(
      <TestWrapper>
        <OCRResultsPage />
      </TestWrapper>
    );

    await waitFor(() => {
      expect(screen.getByText('Błąd ładowania')).toBeInTheDocument();
      expect(screen.getByText('Nie udało się pobrać wyników OCR')).toBeInTheDocument();
      expect(screen.getByText('Spróbuj ponownie')).toBeInTheDocument();
    });
  });

  it('shows empty state when no results', async () => {
    mockedAxios.get.mockResolvedValueOnce({
      data: {
        results: [],
        count: 0,
        stats: {
          total: 0,
          highConfidence: 0,
          needsReview: 0,
          withInvoice: 0,
        },
      },
    });

    render(
      <TestWrapper>
        <OCRResultsPage />
      </TestWrapper>
    );

    await waitFor(() => {
      expect(screen.getByText('Brak wyników OCR. Prześlij pierwszy dokument, aby rozpocząć przetwarzanie.')).toBeInTheDocument();
    });
  });

  it('navigates to detail page when clicking details button', async () => {
    render(
      <TestWrapper>
        <OCRResultsPage />
      </TestWrapper>
    );

    await waitFor(() => {
      const detailsButtons = screen.getAllByText('Szczegóły');
      fireEvent.click(detailsButtons[0]);
    });

    expect(window.location.href).toBe('/ocr/result/1/');
  });

  it('navigates to upload page when clicking upload button', async () => {
    render(
      <TestWrapper>
        <OCRResultsPage />
      </TestWrapper>
    );

    const uploadButton = screen.getByText('Prześlij nowy dokument');
    fireEvent.click(uploadButton);

    expect(window.location.href).toBe('/upload/');
  });

  it('formats currency amounts correctly', async () => {
    render(
      <TestWrapper>
        <OCRResultsPage />
      </TestWrapper>
    );

    await waitFor(() => {
      // Should display formatted Polish currency
      expect(screen.getByText(/1\s?230,50\s?zł/)).toBeInTheDocument();
      expect(screen.getByText(/2\s?500,00\s?zł/)).toBeInTheDocument();
    });
  });

  it('formats dates correctly', async () => {
    render(
      <TestWrapper>
        <OCRResultsPage />
      </TestWrapper>
    );

    await waitFor(() => {
      // Should display formatted Polish dates
      expect(screen.getByText('15.01.2025')).toBeInTheDocument();
      expect(screen.getByText('16.01.2025')).toBeInTheDocument();
    });
  });
});

describe('OCRResultsPage Integration', () => {
  it('handles complete user workflow', async () => {
    render(
      <TestWrapper>
        <OCRResultsPage />
      </TestWrapper>
    );

    // 1. Page loads with results
    await waitFor(() => {
      expect(screen.getByText('Wyniki OCR')).toBeInTheDocument();
      expect(screen.getByText('faktura_001.pdf')).toBeInTheDocument();
    });

    // 2. User filters by high confidence
    const highConfidenceFilter = screen.getByText('Wysoka pewność');
    fireEvent.click(highConfidenceFilter);

    await waitFor(() => {
      expect(mockedAxios.get).toHaveBeenCalledWith(
        expect.stringContaining('status=high-confidence')
      );
    });

    // 3. User selects a row
    const checkboxes = screen.getAllByRole('checkbox');
    if (checkboxes.length > 1) {
      fireEvent.click(checkboxes[1]);
    }

    // 4. Bulk actions appear
    await waitFor(() => {
      expect(screen.getByText(/Zaznaczono/)).toBeInTheDocument();
    });

    // 5. User clears selection
    const clearButton = screen.getByText('Wyczyść zaznaczenie');
    fireEvent.click(clearButton);

    // 6. Bulk actions disappear
    await waitFor(() => {
      expect(screen.queryByText(/Zaznaczono/)).not.toBeInTheDocument();
    });
  });
});