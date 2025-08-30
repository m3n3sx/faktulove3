import React from 'react';
import { render, screen } from '@testing-library/react';
import { jest } from '@jest/globals';
import OCRConfidenceIndicator, { 
  OCRFieldConfidence, 
  OCRConfidenceComparison, 
  OCRConfidenceTrend,
  OCRConfidenceSummary 
} from '../OCRConfidenceIndicator';
import { DesignSystemProvider } from '../../design-system/providers/DesignSystemProvider';

// Test wrapper
const TestWrapper = ({ children }) => (
  <DesignSystemProvider>
    {children}
  </DesignSystemProvider>
);

describe('OCRConfidenceIndicator', () => {
  it('renders excellent confidence correctly', () => {
    render(
      <TestWrapper>
        <OCRConfidenceIndicator confidence={96.5} showDescription={true} />
      </TestWrapper>
    );

    expect(screen.getByText('97%')).toBeInTheDocument();
    expect(screen.getByText('Doskonała pewność')).toBeInTheDocument();
    expect(screen.getByText('Dane bardzo wiarygodne, minimalne ryzyko błędów')).toBeInTheDocument();
  });

  it('renders high confidence correctly', () => {
    render(
      <TestWrapper>
        <OCRConfidenceIndicator confidence={88.3} showDescription={true} />
      </TestWrapper>
    );

    expect(screen.getByText('88%')).toBeInTheDocument();
    expect(screen.getByText('Wysoka pewność')).toBeInTheDocument();
    expect(screen.getByText('Dane wiarygodne, niewielkie ryzyko błędów')).toBeInTheDocument();
  });

  it('renders medium confidence correctly', () => {
    render(
      <TestWrapper>
        <OCRConfidenceIndicator confidence={75.0} showDescription={true} />
      </TestWrapper>
    );

    expect(screen.getByText('75%')).toBeInTheDocument();
    expect(screen.getByText('Średnia pewność')).toBeInTheDocument();
    expect(screen.getByText('Zalecana weryfikacja kluczowych danych')).toBeInTheDocument();
  });

  it('renders low confidence correctly', () => {
    render(
      <TestWrapper>
        <OCRConfidenceIndicator confidence={60.0} showDescription={true} />
      </TestWrapper>
    );

    expect(screen.getByText('60%')).toBeInTheDocument();
    expect(screen.getByText('Niska pewność')).toBeInTheDocument();
    expect(screen.getByText('Wymagana weryfikacja większości danych')).toBeInTheDocument();
  });

  it('renders very low confidence correctly', () => {
    render(
      <TestWrapper>
        <OCRConfidenceIndicator confidence={30.0} showDescription={true} />
      </TestWrapper>
    );

    expect(screen.getByText('30%')).toBeInTheDocument();
    expect(screen.getByText('Bardzo niska pewność')).toBeInTheDocument();
    expect(screen.getByText('Wymagana dokładna weryfikacja wszystkich danych')).toBeInTheDocument();
  });

  it('handles null confidence', () => {
    render(
      <TestWrapper>
        <OCRConfidenceIndicator confidence={null} showDescription={true} />
      </TestWrapper>
    );

    expect(screen.getByText('Nieznana')).toBeInTheDocument();
    expect(screen.getByText('Brak informacji o pewności')).toBeInTheDocument();
  });

  it('renders with progress bar', () => {
    render(
      <TestWrapper>
        <OCRConfidenceIndicator 
          confidence={85.5} 
          showProgress={true} 
          showDescription={true} 
        />
      </TestWrapper>
    );

    expect(screen.getByText('86%')).toBeInTheDocument();
    expect(screen.getByText('Pewność OCR: Wysoka')).toBeInTheDocument();
    // Progress bar should be rendered (check for progress role or specific class)
    expect(screen.getByRole('progressbar')).toBeInTheDocument();
  });

  it('applies custom className', () => {
    const { container } = render(
      <TestWrapper>
        <OCRConfidenceIndicator confidence={80} className="custom-class" />
      </TestWrapper>
    );

    expect(container.firstChild).toHaveClass('custom-class');
  });

  it('handles different sizes', () => {
    render(
      <TestWrapper>
        <OCRConfidenceIndicator confidence={80} size="lg" />
      </TestWrapper>
    );

    expect(screen.getByText('80%')).toBeInTheDocument();
  });
});

describe('OCRFieldConfidence', () => {
  it('renders field confidence correctly', () => {
    render(
      <TestWrapper>
        <OCRFieldConfidence 
          fieldName="invoice_number" 
          confidence={0.92} 
          showLabel={true} 
        />
      </TestWrapper>
    );

    expect(screen.getByText('Invoice number:')).toBeInTheDocument();
    expect(screen.getByText('92%')).toBeInTheDocument();
  });

  it('handles field name formatting', () => {
    render(
      <TestWrapper>
        <OCRFieldConfidence 
          fieldName="supplier_nip" 
          confidence={0.85} 
          showLabel={true} 
        />
      </TestWrapper>
    );

    expect(screen.getByText('Supplier nip:')).toBeInTheDocument();
  });

  it('renders without label', () => {
    render(
      <TestWrapper>
        <OCRFieldConfidence 
          fieldName="total_amount" 
          confidence={0.78} 
          showLabel={false} 
        />
      </TestWrapper>
    );

    expect(screen.queryByText('Total amount:')).not.toBeInTheDocument();
    expect(screen.getByText('78%')).toBeInTheDocument();
  });

  it('handles null confidence', () => {
    const { container } = render(
      <TestWrapper>
        <OCRFieldConfidence 
          fieldName="test_field" 
          confidence={null} 
        />
      </TestWrapper>
    );

    expect(container.firstChild).toBeNull();
  });

  it('uses correct badge variants based on confidence', () => {
    const { rerender } = render(
      <TestWrapper>
        <OCRFieldConfidence fieldName="test" confidence={0.95} />
      </TestWrapper>
    );
    expect(screen.getByText('95%')).toBeInTheDocument();

    rerender(
      <TestWrapper>
        <OCRFieldConfidence fieldName="test" confidence={0.75} />
      </TestWrapper>
    );
    expect(screen.getByText('75%')).toBeInTheDocument();

    rerender(
      <TestWrapper>
        <OCRFieldConfidence fieldName="test" confidence={0.60} />
      </TestWrapper>
    );
    expect(screen.getByText('60%')).toBeInTheDocument();
  });
});

describe('OCRConfidenceComparison', () => {
  it('shows improvement correctly', () => {
    render(
      <TestWrapper>
        <OCRConfidenceComparison 
          originalConfidence={75.0} 
          currentConfidence={85.0} 
        />
      </TestWrapper>
    );

    expect(screen.getByText('Oryginalna:')).toBeInTheDocument();
    expect(screen.getByText('Aktualna:')).toBeInTheDocument();
    expect(screen.getByText('75%')).toBeInTheDocument();
    expect(screen.getByText('85%')).toBeInTheDocument();
    expect(screen.getByText('↗')).toBeInTheDocument();
    expect(screen.getByText('+10.0%')).toBeInTheDocument();
  });

  it('shows decline correctly', () => {
    render(
      <TestWrapper>
        <OCRConfidenceComparison 
          originalConfidence={85.0} 
          currentConfidence={70.0} 
        />
      </TestWrapper>
    );

    expect(screen.getByText('↘')).toBeInTheDocument();
    expect(screen.getByText('-15.0%')).toBeInTheDocument();
  });

  it('hides trend for small differences', () => {
    render(
      <TestWrapper>
        <OCRConfidenceComparison 
          originalConfidence={85.0} 
          currentConfidence={85.5} 
        />
      </TestWrapper>
    );

    expect(screen.queryByText('↗')).not.toBeInTheDocument();
    expect(screen.queryByText('+0.5%')).not.toBeInTheDocument();
  });
});

describe('OCRConfidenceTrend', () => {
  it('shows rising trend', () => {
    const history = [70.0, 75.0, 82.0];
    
    render(
      <TestWrapper>
        <OCRConfidenceTrend confidenceHistory={history} />
      </TestWrapper>
    );

    expect(screen.getByText('82%')).toBeInTheDocument();
    expect(screen.getByText('↗')).toBeInTheDocument();
    expect(screen.getByText('Rosnąca')).toBeInTheDocument();
    expect(screen.getByText('(+7.0%)')).toBeInTheDocument();
  });

  it('shows falling trend', () => {
    const history = [85.0, 78.0];
    
    render(
      <TestWrapper>
        <OCRConfidenceTrend confidenceHistory={history} />
      </TestWrapper>
    );

    expect(screen.getByText('↘')).toBeInTheDocument();
    expect(screen.getByText('Spadająca')).toBeInTheDocument();
    expect(screen.getByText('(-7.0%)')).toBeInTheDocument();
  });

  it('shows stable trend', () => {
    const history = [80.0, 80.5];
    
    render(
      <TestWrapper>
        <OCRConfidenceTrend confidenceHistory={history} />
      </TestWrapper>
    );

    expect(screen.getByText('→')).toBeInTheDocument();
    expect(screen.getByText('Stabilna')).toBeInTheDocument();
    expect(screen.queryByText(/\([+-]/)).not.toBeInTheDocument();
  });

  it('handles insufficient history', () => {
    const { container } = render(
      <TestWrapper>
        <OCRConfidenceTrend confidenceHistory={[80.0]} />
      </TestWrapper>
    );

    expect(container.firstChild).toBeNull();
  });

  it('handles empty history', () => {
    const { container } = render(
      <TestWrapper>
        <OCRConfidenceTrend confidenceHistory={[]} />
      </TestWrapper>
    );

    expect(container.firstChild).toBeNull();
  });
});

describe('OCRConfidenceSummary', () => {
  const mockFieldConfidences = {
    invoice_number: 0.95,
    invoice_date: 0.88,
    supplier_name: 0.92,
    total_amount: 0.65,
    supplier_nip: 0.45,
  };

  it('calculates and displays summary correctly', () => {
    render(
      <TestWrapper>
        <OCRConfidenceSummary fieldConfidences={mockFieldConfidences} />
      </TestWrapper>
    );

    expect(screen.getByText('Średnia pewność pól')).toBeInTheDocument();
    expect(screen.getByText('Wysoka pewność:')).toBeInTheDocument();
    expect(screen.getByText('Niska pewność:')).toBeInTheDocument();
    expect(screen.getByText('Łącznie:')).toBeInTheDocument();
    expect(screen.getByText('5')).toBeInTheDocument(); // Total fields
  });

  it('counts high and low confidence fields correctly', () => {
    render(
      <TestWrapper>
        <OCRConfidenceSummary fieldConfidences={mockFieldConfidences} />
      </TestWrapper>
    );

    // High confidence (>= 0.9): invoice_number, supplier_name = 2 fields
    expect(screen.getByText('2')).toBeInTheDocument();
    
    // Low confidence (< 0.7): total_amount, supplier_nip = 2 fields
    expect(screen.getByText('2')).toBeInTheDocument();
  });

  it('handles empty field confidences', () => {
    render(
      <TestWrapper>
        <OCRConfidenceSummary fieldConfidences={{}} />
      </TestWrapper>
    );

    expect(screen.getByText('Brak danych o pewności pól')).toBeInTheDocument();
  });

  it('filters out null confidence values', () => {
    const confidencesWithNulls = {
      field1: 0.8,
      field2: null,
      field3: undefined,
      field4: 0.9,
    };

    render(
      <TestWrapper>
        <OCRConfidenceSummary fieldConfidences={confidencesWithNulls} />
      </TestWrapper>
    );

    expect(screen.getByText('2')).toBeInTheDocument(); // Should only count non-null values
  });

  it('applies custom className', () => {
    const { container } = render(
      <TestWrapper>
        <OCRConfidenceSummary 
          fieldConfidences={mockFieldConfidences} 
          className="custom-summary" 
        />
      </TestWrapper>
    );

    expect(container.firstChild).toHaveClass('custom-summary');
  });
});