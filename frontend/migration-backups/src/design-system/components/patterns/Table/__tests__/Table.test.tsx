import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { axe, toHaveNoViolations } from 'jest-axe';
import { Table, formatPolishCurrency, formatPolishDate, formatPolishDateTime, formatPolishNumber } from '../Table';

expect.extend(toHaveNoViolations);

// Mock data for testing
const mockInvoiceData = [
  {
    id: '1',
    number: 'FV/2025/001',
    client: 'ABC Sp. z o.o.',
    amount: 1000.50,
    date: '2025-01-15',
    status: 'Opłacona',
  },
  {
    id: '2',
    number: 'FV/2025/002',
    client: 'XYZ S.A.',
    amount: 2500.00,
    date: '2025-01-20',
    status: 'Wysłana',
  },
  {
    id: '3',
    number: 'FV/2025/003',
    client: 'DEF Sp. j.',
    amount: 750.75,
    date: '2025-01-25',
    status: 'Szkic',
  },
];

const mockColumns = [
  { key: 'number', header: 'Numer faktury', sortable: true },
  { key: 'client', header: 'Klient', sortable: true },
  { key: 'amount', header: 'Kwota', format: 'currency' as const, align: 'right' as const, sortable: true },
  { key: 'date', header: 'Data', format: 'date' as const, sortable: true },
  { key: 'status', header: 'Status', sortable: false },
];

describe('Polish Formatting Functions', () => {
  describe('formatPolishCurrency', () => {
    it('formats currency correctly', () => {
      expect(formatPolishCurrency(1000.50)).toBe('1 000,50 zł');
      expect(formatPolishCurrency(0)).toBe('0,00 zł');
      expect(formatPolishCurrency(1234567.89)).toBe('1 234 567,89 zł');
    });
  });

  describe('formatPolishDate', () => {
    it('formats date correctly', () => {
      const date = new Date('2025-01-15');
      expect(formatPolishDate(date)).toBe('15.01.2025');
      expect(formatPolishDate('2025-01-15')).toBe('15.01.2025');
    });
  });

  describe('formatPolishDateTime', () => {
    it('formats datetime correctly', () => {
      const date = new Date('2025-01-15T14:30:00');
      expect(formatPolishDateTime(date)).toBe('15.01.2025, 14:30');
    });
  });

  describe('formatPolishNumber', () => {
    it('formats numbers correctly', () => {
      expect(formatPolishNumber(1000)).toBe('1 000');
      expect(formatPolishNumber(1234567)).toBe('1 234 567');
    });
  });
});

describe('Table Component', () => {
  describe('Basic Functionality', () => {
    it('renders table with data', () => {
      render(<Table data={mockInvoiceData} columns={mockColumns} />);

      expect(screen.getByRole('table')).toBeInTheDocument();
      expect(screen.getByText('FV/2025/001')).toBeInTheDocument();
      expect(screen.getByText('ABC Sp. z o.o.')).toBeInTheDocument();
      expect(screen.getByText('1 000,50 zł')).toBeInTheDocument();
    });

    it('renders column headers', () => {
      render(<Table data={mockInvoiceData} columns={mockColumns} />);

      expect(screen.getByText('Numer faktury')).toBeInTheDocument();
      expect(screen.getByText('Klient')).toBeInTheDocument();
      expect(screen.getByText('Kwota')).toBeInTheDocument();
      expect(screen.getByText('Data')).toBeInTheDocument();
      expect(screen.getByText('Status')).toBeInTheDocument();
    });

    it('displays empty message when no data', () => {
      render(<Table data={[]} columns={mockColumns} emptyMessage="Brak faktur" />);

      expect(screen.getByText('Brak faktur')).toBeInTheDocument();
    });

    it('displays loading state', () => {
      render(<Table data={[]} columns={mockColumns} loading={true} />);

      expect(screen.getByText('Ładowanie...')).toBeInTheDocument();
    });
  });

  describe('Sorting', () => {
    it('sorts data when column header is clicked', async () => {
      const user = userEvent.setup();
      render(<Table data={mockInvoiceData} columns={mockColumns} />);

      const clientHeader = screen.getByRole('button', { name: /Sortuj według Klient/ });
      await user.click(clientHeader);

      // Check if data is sorted alphabetically
      const rows = screen.getAllByRole('row');
      expect(rows[1]).toHaveTextContent('ABC Sp. z o.o.');
      expect(rows[2]).toHaveTextContent('DEF Sp. j.');
      expect(rows[3]).toHaveTextContent('XYZ S.A.');
    });

    it('toggles sort direction on repeated clicks', async () => {
      const user = userEvent.setup();
      render(<Table data={mockInvoiceData} columns={mockColumns} />);

      const clientHeader = screen.getByRole('button', { name: /Sortuj według Klient/ });
      
      // First click - ascending
      await user.click(clientHeader);
      expect(clientHeader).toHaveTextContent('↑');

      // Second click - descending
      await user.click(clientHeader);
      expect(clientHeader).toHaveTextContent('↓');
    });

    it('calls onSort callback when provided', async () => {
      const user = userEvent.setup();
      const onSort = jest.fn();
      render(<Table data={mockInvoiceData} columns={mockColumns} onSort={onSort} />);

      const clientHeader = screen.getByRole('button', { name: /Sortuj według Klient/ });
      await user.click(clientHeader);

      expect(onSort).toHaveBeenCalledWith({ key: 'client', direction: 'asc' });
    });

    it('does not sort non-sortable columns', () => {
      render(<Table data={mockInvoiceData} columns={mockColumns} />);

      const statusHeader = screen.getByText('Status');
      expect(statusHeader.tagName).toBe('TH');
      expect(statusHeader.querySelector('button')).toBeNull();
    });

    it('disables sorting when sortable prop is false', () => {
      render(<Table data={mockInvoiceData} columns={mockColumns} sortable={false} />);

      const clientHeader = screen.getByText('Klient');
      expect(clientHeader.tagName).toBe('TH');
      expect(clientHeader.querySelector('button')).toBeNull();
    });
  });

  describe('Row Selection', () => {
    it('renders selection checkboxes when selectable', () => {
      render(<Table data={mockInvoiceData} columns={mockColumns} selectable={true} />);

      const checkboxes = screen.getAllByRole('checkbox');
      expect(checkboxes).toHaveLength(4); // 3 rows + 1 select all
    });

    it('handles individual row selection', async () => {
      const user = userEvent.setup();
      const onSelectionChange = jest.fn();
      
      render(
        <Table 
          data={mockInvoiceData} 
          columns={mockColumns} 
          selectable={true}
          onSelectionChange={onSelectionChange}
        />
      );

      const firstRowCheckbox = screen.getAllByRole('checkbox')[1]; // Skip select all
      await user.click(firstRowCheckbox);

      expect(onSelectionChange).toHaveBeenCalledWith(['1']);
    });

    it('handles select all functionality', async () => {
      const user = userEvent.setup();
      const onSelectionChange = jest.fn();
      
      render(
        <Table 
          data={mockInvoiceData} 
          columns={mockColumns} 
          selectable={true}
          onSelectionChange={onSelectionChange}
        />
      );

      const selectAllCheckbox = screen.getByLabelText('Zaznacz wszystkie wiersze');
      await user.click(selectAllCheckbox);

      expect(onSelectionChange).toHaveBeenCalledWith(['1', '2', '3']);
    });

    it('shows indeterminate state for partial selection', () => {
      render(
        <Table 
          data={mockInvoiceData} 
          columns={mockColumns} 
          selectable={true}
          selectedRows={['1']}
        />
      );

      const selectAllCheckbox = screen.getByLabelText('Zaznacz wszystkie wiersze') as HTMLInputElement;
      expect(selectAllCheckbox.indeterminate).toBe(true);
    });
  });

  describe('Formatting', () => {
    it('formats currency values correctly', () => {
      render(<Table data={mockInvoiceData} columns={mockColumns} />);

      expect(screen.getByText('1 000,50 zł')).toBeInTheDocument();
      expect(screen.getByText('2 500,00 zł')).toBeInTheDocument();
      expect(screen.getByText('750,75 zł')).toBeInTheDocument();
    });

    it('formats date values correctly', () => {
      render(<Table data={mockInvoiceData} columns={mockColumns} />);

      expect(screen.getByText('15.01.2025')).toBeInTheDocument();
      expect(screen.getByText('20.01.2025')).toBeInTheDocument();
      expect(screen.getByText('25.01.2025')).toBeInTheDocument();
    });

    it('uses custom format function when provided', () => {
      const customColumns = [
        {
          key: 'status',
          header: 'Status',
          customFormat: (value: string) => (
            <span className={`badge ${value === 'Opłacona' ? 'success' : 'warning'}`}>
              {value}
            </span>
          ),
        },
      ];

      render(<Table data={mockInvoiceData} columns={customColumns} />);

      expect(screen.getByText('Opłacona')).toHaveClass('badge', 'success');
      expect(screen.getByText('Wysłana')).toHaveClass('badge', 'warning');
    });

    it('handles null and undefined values', () => {
      const dataWithNulls = [
        { id: '1', name: 'Test', value: null, amount: undefined },
      ];
      const columnsWithNulls = [
        { key: 'name', header: 'Name' },
        { key: 'value', header: 'Value' },
        { key: 'amount', header: 'Amount', format: 'currency' as const },
      ];

      render(<Table data={dataWithNulls} columns={columnsWithNulls} />);

      const nullCells = screen.getAllByText('-');
      expect(nullCells).toHaveLength(2);
    });
  });

  describe('Pagination', () => {
    const paginationConfig = {
      page: 1,
      pageSize: 2,
      total: 10,
    };

    it('renders pagination controls', () => {
      render(
        <Table 
          data={mockInvoiceData} 
          columns={mockColumns} 
          pagination={paginationConfig}
        />
      );

      expect(screen.getByText('Wyświetlanie 1 do 2 z 10 wyników')).toBeInTheDocument();
      expect(screen.getByRole('button', { name: 'Poprzednia' })).toBeInTheDocument();
      expect(screen.getByRole('button', { name: 'Następna' })).toBeInTheDocument();
    });

    it('handles page changes', async () => {
      const user = userEvent.setup();
      const onPageChange = jest.fn();
      
      render(
        <Table 
          data={mockInvoiceData} 
          columns={mockColumns} 
          pagination={paginationConfig}
          onPageChange={onPageChange}
        />
      );

      const nextButton = screen.getByRole('button', { name: 'Następna' });
      await user.click(nextButton);

      expect(onPageChange).toHaveBeenCalledWith(2);
    });

    it('handles page size changes', async () => {
      const user = userEvent.setup();
      const onPageSizeChange = jest.fn();
      
      render(
        <Table 
          data={mockInvoiceData} 
          columns={mockColumns} 
          pagination={paginationConfig}
          onPageSizeChange={onPageSizeChange}
        />
      );

      const pageSizeSelect = screen.getByLabelText('Wierszy na stronę:');
      await user.selectOptions(pageSizeSelect, '25');

      expect(onPageSizeChange).toHaveBeenCalledWith(25);
    });

    it('disables previous button on first page', () => {
      render(
        <Table 
          data={mockInvoiceData} 
          columns={mockColumns} 
          pagination={{ ...paginationConfig, page: 1 }}
        />
      );

      const prevButton = screen.getByRole('button', { name: 'Poprzednia' });
      expect(prevButton).toBeDisabled();
    });

    it('disables next button on last page', () => {
      render(
        <Table 
          data={mockInvoiceData} 
          columns={mockColumns} 
          pagination={{ ...paginationConfig, page: 5, total: 10 }}
        />
      );

      const nextButton = screen.getByRole('button', { name: 'Następna' });
      expect(nextButton).toBeDisabled();
    });
  });

  describe('Table Variants', () => {
    it('applies striped variant styles', () => {
      render(<Table data={mockInvoiceData} columns={mockColumns} variant="striped" />);

      const table = screen.getByRole('table');
      expect(table).toHaveClass('border', 'border-neutral-200');
    });

    it('applies bordered variant styles', () => {
      render(<Table data={mockInvoiceData} columns={mockColumns} variant="bordered" />);

      const table = screen.getByRole('table');
      expect(table).toHaveClass('border-2', 'border-neutral-300');
    });
  });

  describe('Table Sizes', () => {
    it('applies small size styles', () => {
      render(<Table data={mockInvoiceData} columns={mockColumns} size="sm" />);

      const table = screen.getByRole('table');
      expect(table).toHaveClass('text-sm');
    });

    it('applies large size styles', () => {
      render(<Table data={mockInvoiceData} columns={mockColumns} size="lg" />);

      const table = screen.getByRole('table');
      expect(table).toHaveClass('text-lg');
    });
  });

  describe('Accessibility', () => {
    it('meets accessibility standards', async () => {
      const { container } = render(
        <Table 
          data={mockInvoiceData} 
          columns={mockColumns}
          selectable={true}
          pagination={{ page: 1, pageSize: 10, total: 3 }}
        />
      );

      const results = await axe(container);
      expect(results).toHaveNoViolations();
    });

    it('provides proper ARIA labels for sorting', () => {
      render(<Table data={mockInvoiceData} columns={mockColumns} />);

      const sortButton = screen.getByRole('button', { name: 'Sortuj według Klient' });
      expect(sortButton).toBeInTheDocument();
    });

    it('provides proper ARIA labels for selection', () => {
      render(<Table data={mockInvoiceData} columns={mockColumns} selectable={true} />);

      expect(screen.getByLabelText('Zaznacz wszystkie wiersze')).toBeInTheDocument();
      expect(screen.getByLabelText('Zaznacz wiersz 1')).toBeInTheDocument();
    });

    it('provides proper ARIA labels for pagination', () => {
      render(
        <Table 
          data={mockInvoiceData} 
          columns={mockColumns} 
          pagination={{ page: 2, pageSize: 10, total: 30 }}
        />
      );

      expect(screen.getByLabelText('Poprzednia strona')).toBeInTheDocument();
      expect(screen.getByLabelText('Następna strona')).toBeInTheDocument();
      expect(screen.getByLabelText('Strona 1')).toBeInTheDocument();
      expect(screen.getByLabelText('Strona 2')).toHaveAttribute('aria-current', 'page');
    });
  });

  describe('Keyboard Navigation', () => {
    it('supports keyboard navigation for sorting', async () => {
      const user = userEvent.setup();
      render(<Table data={mockInvoiceData} columns={mockColumns} />);

      const sortButton = screen.getByRole('button', { name: /Sortuj według Klient/ });
      sortButton.focus();
      
      await user.keyboard('{Enter}');
      expect(sortButton).toHaveTextContent('↑');
    });

    it('supports keyboard navigation for pagination', async () => {
      const user = userEvent.setup();
      const onPageChange = jest.fn();
      
      render(
        <Table 
          data={mockInvoiceData} 
          columns={mockColumns} 
          pagination={{ page: 1, pageSize: 10, total: 30 }}
          onPageChange={onPageChange}
        />
      );

      const nextButton = screen.getByRole('button', { name: 'Następna' });
      nextButton.focus();
      
      await user.keyboard('{Enter}');
      expect(onPageChange).toHaveBeenCalledWith(2);
    });
  });

  describe('Polish Business Context', () => {
    it('renders invoice table with Polish formatting', () => {
      const polishInvoiceData = [
        {
          id: '1',
          number: 'FV/2025/001',
          client: 'Firma ABC Sp. z o.o.',
          nip: '123-456-78-90',
          amount: 1230.50,
          netAmount: 1000.41,
          vatAmount: 230.09,
          issueDate: '2025-01-15',
          dueDate: '2025-02-14',
          status: 'Opłacona',
        },
      ];

      const polishColumns = [
        { key: 'number', header: 'Numer faktury' },
        { key: 'client', header: 'Nabywca' },
        { key: 'nip', header: 'NIP' },
        { key: 'netAmount', header: 'Kwota netto', format: 'currency' as const, align: 'right' as const },
        { key: 'vatAmount', header: 'VAT', format: 'currency' as const, align: 'right' as const },
        { key: 'amount', header: 'Kwota brutto', format: 'currency' as const, align: 'right' as const },
        { key: 'issueDate', header: 'Data wystawienia', format: 'date' as const },
        { key: 'dueDate', header: 'Termin płatności', format: 'date' as const },
        { 
          key: 'status', 
          header: 'Status',
          customFormat: (value: string) => (
            <span className={`px-2 py-1 rounded-full text-xs ${
              value === 'Opłacona' ? 'bg-success-100 text-success-800' :
              value === 'Wysłana' ? 'bg-primary-100 text-primary-800' :
              'bg-neutral-100 text-neutral-800'
            }`}>
              {value}
            </span>
          ),
        },
      ];

      render(<Table data={polishInvoiceData} columns={polishColumns} />);

      expect(screen.getByText('FV/2025/001')).toBeInTheDocument();
      expect(screen.getByText('Firma ABC Sp. z o.o.')).toBeInTheDocument();
      expect(screen.getByText('123-456-78-90')).toBeInTheDocument();
      expect(screen.getByText('1 000,41 zł')).toBeInTheDocument();
      expect(screen.getByText('230,09 zł')).toBeInTheDocument();
      expect(screen.getByText('1 230,50 zł')).toBeInTheDocument();
      expect(screen.getByText('15.01.2025')).toBeInTheDocument();
      expect(screen.getByText('14.02.2025')).toBeInTheDocument();
    });
  });
});