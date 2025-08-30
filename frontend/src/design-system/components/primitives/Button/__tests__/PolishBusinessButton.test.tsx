// Polish Business Button Tests
import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { axe, toHaveNoViolations } from 'jest-axe';
import { 
  PolishBusinessButton, 
  InvoiceActionButton, 
  VATRateButton, 
  StatusToggleButton 
} from '../PolishBusinessButton';

expect.extend(toHaveNoViolations);

describe('Polish Business Button Components', () => {
  describe('PolishBusinessButton', () => {
    it('renders with default invoice variant', () => {
      render(<PolishBusinessButton>Faktura</PolishBusinessButton>);
      
      const button = screen.getByRole('button');
      expect(button).toBeInTheDocument();
      expect(button).toHaveTextContent('Faktura');
      expect(button).toHaveAttribute('aria-label', 'Utwórz fakturę');
    });

    it('maps Polish variants to correct base variants', () => {
      const { rerender } = render(<PolishBusinessButton variant="invoice">Invoice</PolishBusinessButton>);
      let button = screen.getByRole('button');
      expect(button).toHaveClass('bg-primary-600'); // primary variant

      rerender(<PolishBusinessButton variant="contractor">Contractor</PolishBusinessButton>);
      button = screen.getByRole('button');
      expect(button).toHaveClass('bg-white', 'border-primary-600'); // secondary variant

      rerender(<PolishBusinessButton variant="print">Print</PolishBusinessButton>);
      button = screen.getByRole('button');
      expect(button).toHaveClass('bg-transparent'); // ghost variant

      rerender(<PolishBusinessButton variant="cancel">Cancel</PolishBusinessButton>);
      button = screen.getByRole('button');
      expect(button).toHaveClass('bg-error-600'); // danger variant
    });

    it('provides Polish aria labels', () => {
      const { rerender } = render(<PolishBusinessButton variant="payment">Płatność</PolishBusinessButton>);
      expect(screen.getByRole('button')).toHaveAttribute('aria-label', 'Oznacz jako opłacone');

      rerender(<PolishBusinessButton variant="export">Eksport</PolishBusinessButton>);
      expect(screen.getByRole('button')).toHaveAttribute('aria-label', 'Eksportuj dane');

      rerender(<PolishBusinessButton variant="print">Drukuj</PolishBusinessButton>);
      expect(screen.getByRole('button')).toHaveAttribute('aria-label', 'Drukuj dokument');
    });

    it('allows custom aria label override', () => {
      render(
        <PolishBusinessButton variant="invoice" aria-label="Niestandardowa etykieta">
          Faktura
        </PolishBusinessButton>
      );
      
      expect(screen.getByRole('button')).toHaveAttribute('aria-label', 'Niestandardowa etykieta');
    });

    it('meets accessibility standards', async () => {
      const { container } = render(<PolishBusinessButton variant="contractor">Kontrahent</PolishBusinessButton>);
      const results = await axe(container);
      expect(results).toHaveNoViolations();
    });
  });

  describe('InvoiceActionButton', () => {
    it('renders create action correctly', () => {
      render(<InvoiceActionButton action="create">Utwórz</InvoiceActionButton>);
      
      const button = screen.getByRole('button');
      expect(button).toHaveTextContent('Utwórz');
      expect(button).toHaveAttribute('aria-label', 'Utwórz nową fakturę');
      expect(button).toHaveClass('bg-primary-600'); // primary variant
    });

    it('renders edit action correctly', () => {
      render(<InvoiceActionButton action="edit">Edytuj</InvoiceActionButton>);
      
      const button = screen.getByRole('button');
      expect(button).toHaveAttribute('aria-label', 'Edytuj fakturę');
      expect(button).toHaveClass('bg-white', 'border-primary-600'); // secondary variant
    });

    it('renders send action correctly', () => {
      render(<InvoiceActionButton action="send">Wyślij</InvoiceActionButton>);
      
      const button = screen.getByRole('button');
      expect(button).toHaveAttribute('aria-label', 'Wyślij fakturę');
      expect(button).toHaveClass('bg-primary-600'); // primary variant
    });

    it('renders pay action correctly', () => {
      render(<InvoiceActionButton action="pay">Opłać</InvoiceActionButton>);
      
      const button = screen.getByRole('button');
      expect(button).toHaveAttribute('aria-label', 'Oznacz jako opłacone');
      expect(button).toHaveClass('bg-primary-600'); // primary variant
    });

    it('renders cancel action correctly', () => {
      render(<InvoiceActionButton action="cancel">Anuluj</InvoiceActionButton>);
      
      const button = screen.getByRole('button');
      expect(button).toHaveAttribute('aria-label', 'Anuluj fakturę');
      expect(button).toHaveClass('bg-error-600'); // danger variant
    });

    it('renders duplicate action correctly', () => {
      render(<InvoiceActionButton action="duplicate">Duplikuj</InvoiceActionButton>);
      
      const button = screen.getByRole('button');
      expect(button).toHaveAttribute('aria-label', 'Duplikuj fakturę');
      expect(button).toHaveClass('bg-transparent'); // ghost variant
    });

    it('allows custom aria label override', () => {
      render(
        <InvoiceActionButton action="create" aria-label="Niestandardowa etykieta">
          Utwórz
        </InvoiceActionButton>
      );
      
      expect(screen.getByRole('button')).toHaveAttribute('aria-label', 'Niestandardowa etykieta');
    });

    it('meets accessibility standards', async () => {
      const { container } = render(<InvoiceActionButton action="send">Wyślij</InvoiceActionButton>);
      const results = await axe(container);
      expect(results).toHaveNoViolations();
    });
  });

  describe('VATRateButton', () => {
    it('displays standard VAT rate correctly', () => {
      render(<VATRateButton rate={0.23} />);
      
      const button = screen.getByRole('button');
      expect(button).toHaveTextContent('23%');
      expect(button).toHaveAttribute('aria-label', 'Stawka VAT 23 procent');
      expect(button).toHaveClass('font-mono', 'min-w-[3rem]');
    });

    it('displays reduced VAT rates correctly', () => {
      const { rerender } = render(<VATRateButton rate={0.08} />);
      let button = screen.getByRole('button');
      expect(button).toHaveTextContent('8%');
      expect(button).toHaveAttribute('aria-label', 'Stawka VAT 8 procent');

      rerender(<VATRateButton rate={0.05} />);
      button = screen.getByRole('button');
      expect(button).toHaveTextContent('5%');
      expect(button).toHaveAttribute('aria-label', 'Stawka VAT 5 procent');
    });

    it('displays zero VAT rate correctly', () => {
      render(<VATRateButton rate={0} />);
      
      const button = screen.getByRole('button');
      expect(button).toHaveTextContent('0%');
      expect(button).toHaveAttribute('aria-label', 'Stawka VAT zero procent');
    });

    it('displays exempt VAT rate correctly', () => {
      render(<VATRateButton rate={-1} />);
      
      const button = screen.getByRole('button');
      expect(button).toHaveTextContent('zw.');
      expect(button).toHaveAttribute('aria-label', 'Stawka VAT zwolniona');
    });

    it('handles selected state correctly', () => {
      const { rerender } = render(<VATRateButton rate={0.23} selected={false} />);
      let button = screen.getByRole('button');
      expect(button).toHaveClass('bg-white', 'border-primary-600'); // secondary variant
      expect(button).toHaveAttribute('aria-pressed', 'false');

      rerender(<VATRateButton rate={0.23} selected={true} />);
      button = screen.getByRole('button');
      expect(button).toHaveClass('bg-primary-600'); // primary variant
      expect(button).toHaveAttribute('aria-pressed', 'true');
    });

    it('allows custom aria label override', () => {
      render(<VATRateButton rate={0.23} aria-label="Niestandardowa stawka VAT" />);
      
      expect(screen.getByRole('button')).toHaveAttribute('aria-label', 'Niestandardowa stawka VAT');
    });

    it('meets accessibility standards', async () => {
      const { container } = render(<VATRateButton rate={0.23} selected={true} />);
      const results = await axe(container);
      expect(results).toHaveNoViolations();
    });
  });

  describe('StatusToggleButton', () => {
    it('renders draft status correctly', () => {
      render(<StatusToggleButton status="draft" />);
      
      const button = screen.getByRole('button');
      expect(button).toHaveTextContent('Szkic');
      expect(button).toHaveAttribute('aria-label', 'Status: Szkic - kliknij aby zmienić');
      expect(button).toHaveClass('bg-transparent'); // ghost variant
      expect(button).toHaveClass('typography-status-badge');
    });

    it('renders sent status correctly', () => {
      render(<StatusToggleButton status="sent" />);
      
      const button = screen.getByRole('button');
      expect(button).toHaveTextContent('Wysłana');
      expect(button).toHaveAttribute('aria-label', 'Status: Wysłana - kliknij aby oznaczyć jako opłacona');
      expect(button).toHaveClass('bg-white', 'border-primary-600'); // secondary variant
    });

    it('renders paid status correctly', () => {
      render(<StatusToggleButton status="paid" />);
      
      const button = screen.getByRole('button');
      expect(button).toHaveTextContent('Opłacona');
      expect(button).toHaveAttribute('aria-label', 'Status: Opłacona');
      expect(button).toHaveClass('bg-primary-600'); // primary variant
    });

    it('renders overdue status correctly', () => {
      render(<StatusToggleButton status="overdue" />);
      
      const button = screen.getByRole('button');
      expect(button).toHaveTextContent('Przeterminowana');
      expect(button).toHaveAttribute('aria-label', 'Status: Przeterminowana - kliknij aby oznaczyć jako opłacona');
      expect(button).toHaveClass('bg-error-600'); // danger variant
    });

    it('renders cancelled status correctly', () => {
      render(<StatusToggleButton status="cancelled" />);
      
      const button = screen.getByRole('button');
      expect(button).toHaveTextContent('Anulowana');
      expect(button).toHaveAttribute('aria-label', 'Status: Anulowana');
      expect(button).toHaveClass('bg-transparent'); // ghost variant
    });

    it('handles status change correctly', async () => {
      const handleStatusChange = jest.fn();
      const user = userEvent.setup();
      
      render(<StatusToggleButton status="draft" onStatusChange={handleStatusChange} />);
      
      const button = screen.getByRole('button');
      await user.click(button);
      
      expect(handleStatusChange).toHaveBeenCalledWith('sent');
    });

    it('handles status change from sent to paid', async () => {
      const handleStatusChange = jest.fn();
      const user = userEvent.setup();
      
      render(<StatusToggleButton status="sent" onStatusChange={handleStatusChange} />);
      
      const button = screen.getByRole('button');
      await user.click(button);
      
      expect(handleStatusChange).toHaveBeenCalledWith('paid');
    });

    it('handles status change from overdue to paid', async () => {
      const handleStatusChange = jest.fn();
      const user = userEvent.setup();
      
      render(<StatusToggleButton status="overdue" onStatusChange={handleStatusChange} />);
      
      const button = screen.getByRole('button');
      await user.click(button);
      
      expect(handleStatusChange).toHaveBeenCalledWith('paid');
    });

    it('does not change status for final states', async () => {
      const handleStatusChange = jest.fn();
      const user = userEvent.setup();
      
      const { rerender } = render(<StatusToggleButton status="paid" onStatusChange={handleStatusChange} />);
      await user.click(screen.getByRole('button'));
      expect(handleStatusChange).not.toHaveBeenCalled();

      rerender(<StatusToggleButton status="cancelled" onStatusChange={handleStatusChange} />);
      await user.click(screen.getByRole('button'));
      expect(handleStatusChange).not.toHaveBeenCalled();
    });

    it('calls original onClick handler', async () => {
      const handleClick = jest.fn();
      const handleStatusChange = jest.fn();
      const user = userEvent.setup();
      
      render(
        <StatusToggleButton 
          status="draft" 
          onStatusChange={handleStatusChange}
          onClick={handleClick}
        />
      );
      
      const button = screen.getByRole('button');
      await user.click(button);
      
      expect(handleStatusChange).toHaveBeenCalledWith('sent');
      expect(handleClick).toHaveBeenCalled();
    });

    it('allows custom aria label override', () => {
      render(<StatusToggleButton status="draft" aria-label="Niestandardowy status" />);
      
      expect(screen.getByRole('button')).toHaveAttribute('aria-label', 'Niestandardowy status');
    });

    it('meets accessibility standards', async () => {
      const { container } = render(<StatusToggleButton status="sent" />);
      const results = await axe(container);
      expect(results).toHaveNoViolations();
    });
  });

  describe('Integration Tests', () => {
    it('all Polish business buttons work together', () => {
      render(
        <div>
          <PolishBusinessButton variant="invoice">Faktura</PolishBusinessButton>
          <InvoiceActionButton action="create">Utwórz</InvoiceActionButton>
          <VATRateButton rate={0.23} selected={true} />
          <StatusToggleButton status="paid" />
        </div>
      );
      
      expect(screen.getByText('Faktura')).toBeInTheDocument();
      expect(screen.getByText('Utwórz')).toBeInTheDocument();
      expect(screen.getByText('23%')).toBeInTheDocument();
      expect(screen.getByText('Opłacona')).toBeInTheDocument();
    });

    it('maintains consistent sizing across variants', () => {
      render(
        <div>
          <VATRateButton rate={0.23} size="sm" />
          <StatusToggleButton status="paid" size="sm" />
        </div>
      );
      
      const buttons = screen.getAllByRole('button');
      buttons.forEach(button => {
        expect(button).toHaveClass('h-8'); // sm size height
      });
    });

    it('supports all common button props', () => {
      const handleClick = jest.fn();
      
      render(
        <PolishBusinessButton
          variant="invoice"
          size="lg"
          disabled={false}
          onClick={handleClick}
          className="custom-class"
          testId="polish-button"
        >
          Test
        </PolishBusinessButton>
      );
      
      const button = screen.getByTestId('polish-button');
      expect(button).toHaveClass('custom-class', 'h-12'); // lg size
      expect(button).not.toBeDisabled();
    });
  });
});