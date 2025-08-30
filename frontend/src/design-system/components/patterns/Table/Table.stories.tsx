import type { Meta, StoryObj } from '@storybook/react';
import React, { useState } from 'react';
import { Table, TableColumn, SortConfig, PaginationConfig } from './Table';
import { Button } from '../../primitives/Button/Button';

const meta: Meta<typeof Table> = {
  title: 'Design System/Patterns/Table',
  component: Table,
  parameters: {
    docs: {
      description: {
        component: 'Table component for displaying data with sorting, pagination, row selection, and Polish-specific formatting. Includes responsive design and accessibility features.',
      },
    },
    a11y: {
      config: {
        rules: [
          { id: 'color-contrast', enabled: true },
          { id: 'aria-required-attr', enabled: true },
        ],
      },
    },
  },
  argTypes: {
    variant: {
      control: 'select',
      options: ['default', 'striped', 'bordered'],
      description: 'Visual style variant of the table',
    },
    size: {
      control: 'select',
      options: ['sm', 'md', 'lg'],
      description: 'Size of the table text and padding',
    },
    sortable: {
      control: 'boolean',
      description: 'Whether columns can be sorted',
    },
    selectable: {
      control: 'boolean',
      description: 'Whether rows can be selected',
    },
    loading: {
      control: 'boolean',
      description: 'Whether to show loading state',
    },
    stickyHeader: {
      control: 'boolean',
      description: 'Whether the header should stick to top when scrolling',
    },
  },
};

export default meta;
type Story = StoryObj<typeof Table>;

// Sample invoice data
const invoiceData = [
  {
    id: '1',
    number: 'FV/2025/001',
    client: 'ABC Sp. z o.o.',
    nip: '123-456-78-90',
    amount: 1230.50,
    netAmount: 1000.41,
    vatAmount: 230.09,
    issueDate: '2025-01-15',
    dueDate: '2025-02-14',
    status: 'Opłacona',
    paymentMethod: 'Przelew',
  },
  {
    id: '2',
    number: 'FV/2025/002',
    client: 'XYZ S.A.',
    nip: '987-654-32-10',
    amount: 2500.00,
    netAmount: 2032.52,
    vatAmount: 467.48,
    issueDate: '2025-01-20',
    dueDate: '2025-02-19',
    status: 'Wysłana',
    paymentMethod: 'Gotówka',
  },
  {
    id: '3',
    number: 'FV/2025/003',
    client: 'DEF Sp. j.',
    nip: '456-789-01-23',
    amount: 750.75,
    netAmount: 610.37,
    vatAmount: 140.38,
    issueDate: '2025-01-25',
    dueDate: '2025-02-24',
    status: 'Szkic',
    paymentMethod: 'Karta',
  },
  {
    id: '4',
    number: 'FV/2025/004',
    client: 'GHI Sp. z o.o.',
    nip: '789-012-34-56',
    amount: 3200.00,
    netAmount: 2601.63,
    vatAmount: 598.37,
    issueDate: '2025-01-28',
    dueDate: '2025-02-27',
    status: 'Przeterminowana',
    paymentMethod: 'Przelew',
  },
  {
    id: '5',
    number: 'FV/2025/005',
    client: 'JKL S.A.',
    nip: '012-345-67-89',
    amount: 1800.25,
    netAmount: 1463.62,
    vatAmount: 336.63,
    issueDate: '2025-02-01',
    dueDate: '2025-03-03',
    status: 'Opłacona',
    paymentMethod: 'Przelew',
  },
];

// Basic table columns
const basicColumns: TableColumn[] = [
  { key: 'number', header: 'Numer faktury', sortable: true },
  { key: 'client', header: 'Klient', sortable: true },
  { key: 'amount', header: 'Kwota', format: 'currency', align: 'right', sortable: true },
  { key: 'issueDate', header: 'Data wystawienia', format: 'date', sortable: true },
  { key: 'status', header: 'Status', sortable: false },
];

// Comprehensive table columns
const comprehensiveColumns: TableColumn[] = [
  { key: 'number', header: 'Numer faktury', sortable: true, width: '120px' },
  { key: 'client', header: 'Nabywca', sortable: true },
  { key: 'nip', header: 'NIP', sortable: true, width: '130px' },
  { key: 'netAmount', header: 'Kwota netto', format: 'currency', align: 'right', sortable: true, width: '120px' },
  { key: 'vatAmount', header: 'VAT', format: 'currency', align: 'right', sortable: true, width: '100px' },
  { key: 'amount', header: 'Kwota brutto', format: 'currency', align: 'right', sortable: true, width: '120px' },
  { key: 'issueDate', header: 'Data wystawienia', format: 'date', sortable: true, width: '130px' },
  { key: 'dueDate', header: 'Termin płatności', format: 'date', sortable: true, width: '130px' },
  { 
    key: 'status', 
    header: 'Status',
    sortable: true,
    width: '120px',
    customFormat: (value: string) => (
      <span className={`px-2 py-1 rounded-md-full text-xs font-medium ${
        value === 'Opłacona' ? 'bg-success-100 text-success-800' :
        value === 'Wysłana' ? 'bg-primary-100 text-primary-800' :
        value === 'Przeterminowana' ? 'bg-error-100 text-error-800' :
        'bg-neutral-100 text-neutral-800'
      }`}>
        {value}
      </span>
    ),
  },
  {
    key: 'actions',
    header: 'Akcje',
    sortable: false,
    width: '120px',
    customFormat: (_, row) => (
      <div className="flex gap-1">
        <Button size="xs" variant="secondary">Edytuj</Button>
        <Button size="xs" variant="secondary">PDF</Button>
      </div>
    ),
  },
];

// Basic table
export const Basic: Story = {
  render: (args) => (
    <Table {...args} data={invoiceData.slice(0, 3)} columns={basicColumns} />
  ),
  args: {
    variant: 'default',
    size: 'md',
    sortable: true,
  },
};

// Table with all features
export const Comprehensive: Story = {
  render: (args) => {
    const [sortConfig, setSortConfig] = useState<SortConfig>({ key: 'issueDate', direction: 'desc' });
    const [selectedRows, setSelectedRows] = useState<string[]>([]);
    const [pagination, setPagination] = useState<PaginationConfig>({
      page: 1,
      pageSize: 3,
      total: invoiceData.length,
    });

    const handleSort = (newSortConfig: SortConfig) => {
      setSortConfig(newSortConfig);
    };

    const handlePageChange = (page: number) => {
      setPagination(prev => ({ ...prev, page }));
    };

    const handlePageSizeChange = (pageSize: number) => {
      setPagination(prev => ({ ...prev, pageSize, page: 1 }));
    };

    // Get paginated data
    const startIndex = (pagination.page - 1) * pagination.pageSize;
    const paginatedData = invoiceData.slice(startIndex, startIndex + pagination.pageSize);

    return (
      <div className="space-y-4">
        <div className="flex items-center justify-between">
          <h3 className="text-lg font-semibold">Faktury VAT</h3>
          <div className="flex gap-2">
            <Button variant="secondary" size="sm">Eksportuj</Button>
            <Button variant="primary" size="sm">Nowa faktura</Button>
          </div>
        </div>
        
        <Table
          {...args}
          data={paginatedData}
          columns={comprehensiveColumns}
          sortConfig={sortConfig}
          onSort={handleSort}
          pagination={pagination}
          onPageChange={handlePageChange}
          onPageSizeChange={handlePageSizeChange}
          selectedRows={selectedRows}
          onSelectionChange={setSelectedRows}
        />
        
        {selectedRows.length > 0 && (
          <div className="bg-primary-50 border border-primary-200 rounded-md-lg p-4">
            <p className="text-sm text-primary-800">
              Zaznaczono {selectedRows.length} {selectedRows.length === 1 ? 'fakturę' : 'faktury'}
            </p>
            <div className="flex gap-2 mt-2">
              <Button size="sm" variant="primary">Wyślij email</Button>
              <Button size="sm" variant="secondary">Pobierz PDF</Button>
              <Button size="sm" variant="secondary" onClick={() => setSelectedRows([])}>
                Odznacz wszystkie
              </Button>
            </div>
          </div>
        )}
      </div>
    );
  },
  args: {
    variant: 'default',
    size: 'md',
    sortable: true,
    selectable: true,
  },
};

// Table variants
export const Variants: Story = {
  render: () => (
    <div className="space-y-8">
      <div>
        <h4 className="text-md font-semibold mb-4">Default</h4>
        <Table data={invoiceData.slice(0, 3)} columns={basicColumns} variant="default" />
      </div>
      
      <div>
        <h4 className="text-md font-semibold mb-4">Striped</h4>
        <Table data={invoiceData.slice(0, 3)} columns={basicColumns} variant="striped" />
      </div>
      
      <div>
        <h4 className="text-md font-semibold mb-4">Bordered</h4>
        <Table data={invoiceData.slice(0, 3)} columns={basicColumns} variant="bordered" />
      </div>
    </div>
  ),
};

// Table sizes
export const Sizes: Story = {
  render: () => (
    <div className="space-y-8">
      <div>
        <h4 className="text-md font-semibold mb-4">Small</h4>
        <Table data={invoiceData.slice(0, 2)} columns={basicColumns} size="sm" />
      </div>
      
      <div>
        <h4 className="text-md font-semibold mb-4">Medium (Default)</h4>
        <Table data={invoiceData.slice(0, 2)} columns={basicColumns} size="md" />
      </div>
      
      <div>
        <h4 className="text-md font-semibold mb-4">Large</h4>
        <Table data={invoiceData.slice(0, 2)} columns={basicColumns} size="lg" />
      </div>
    </div>
  ),
};

// Polish formatting examples
export const PolishFormatting: Story = {
  render: () => {
    const formattingData = [
      {
        id: '1',
        description: 'Kwoty w PLN',
        currency: 1234567.89,
        number: 1234567,
        date: '2025-01-15',
        datetime: '2025-01-15T14:30:00',
      },
      {
        id: '2',
        description: 'Małe kwoty',
        currency: 99.99,
        number: 42,
        date: '2025-12-31',
        datetime: '2025-12-31T23:59:59',
      },
      {
        id: '3',
        description: 'Wartości zerowe',
        currency: 0,
        number: 0,
        date: '2025-06-15',
        datetime: '2025-06-15T12:00:00',
      },
    ];

    const formattingColumns: TableColumn[] = [
      { key: 'description', header: 'Opis' },
      { key: 'currency', header: 'Kwota', format: 'currency', align: 'right' },
      { key: 'number', header: 'Liczba', format: 'number', align: 'right' },
      { key: 'date', header: 'Data', format: 'date', align: 'center' },
      { key: 'datetime', header: 'Data i czas', format: 'datetime', align: 'center' },
    ];

    return (
      <div>
        <h4 className="text-md font-semibold mb-4">Formatowanie polskie</h4>
        <Table data={formattingData} columns={formattingColumns} />
        <div className="mt-4 text-sm text-neutral-600">
          <p>• Kwoty formatowane zgodnie z polskimi standardami (PLN)</p>
          <p>• Daty w formacie DD.MM.YYYY</p>
          <p>• Data i czas w formacie DD.MM.YYYY, HH:MM</p>
          <p>• Liczby z polskimi separatorami tysięcy</p>
        </div>
      </div>
    );
  },
};

// Empty and loading states
export const EmptyAndLoading: Story = {
  render: () => (
    <div className="space-y-8">
      <div>
        <h4 className="text-md font-semibold mb-4">Pusty stan</h4>
        <Table 
          data={[]} 
          columns={basicColumns} 
          emptyMessage="Nie znaleziono żadnych faktur. Utwórz pierwszą fakturę, aby rozpocząć."
        />
      </div>
      
      <div>
        <h4 className="text-md font-semibold mb-4">Stan ładowania</h4>
        <Table data={[]} columns={basicColumns} loading={true} />
      </div>
    </div>
  ),
};

// Responsive table with sticky header
export const ResponsiveWithStickyHeader: Story = {
  render: () => {
    const wideColumns: TableColumn[] = [
      { key: 'number', header: 'Numer faktury', width: '150px' },
      { key: 'client', header: 'Pełna nazwa nabywcy', width: '250px' },
      { key: 'nip', header: 'NIP', width: '130px' },
      { key: 'netAmount', header: 'Kwota netto', format: 'currency', align: 'right', width: '120px' },
      { key: 'vatAmount', header: 'Kwota VAT', format: 'currency', align: 'right', width: '120px' },
      { key: 'amount', header: 'Kwota brutto', format: 'currency', align: 'right', width: '120px' },
      { key: 'issueDate', header: 'Data wystawienia', format: 'date', width: '130px' },
      { key: 'dueDate', header: 'Termin płatności', format: 'date', width: '130px' },
      { key: 'paymentMethod', header: 'Sposób płatności', width: '130px' },
      { key: 'status', header: 'Status płatności', width: '130px' },
    ];

    return (
      <div className="space-y-4">
        <h4 className="text-md font-semibold">Responsywna tabela z przyklejonym nagłówkiem</h4>
        <p className="text-sm text-neutral-600">
          Przewiń w poziomie i w pionie, aby zobaczyć zachowanie tabeli.
        </p>
        <div className="h-96 overflow-auto border border-neutral-200 rounded-md-lg">
          <Table 
            data={[...invoiceData, ...invoiceData, ...invoiceData]} // Duplicate data for scrolling
            columns={wideColumns}
            stickyHeader={true}
            variant="striped"
          />
        </div>
      </div>
    );
  },
};

// Interactive sorting example
export const InteractiveSorting: Story = {
  render: () => {
    const [sortConfig, setSortConfig] = useState<SortConfig>({ key: 'amount', direction: 'desc' });

    return (
      <div className="space-y-4">
        <div>
          <h4 className="text-md font-semibold mb-2">Interaktywne sortowanie</h4>
          <p className="text-sm text-neutral-600 mb-4">
            Kliknij nagłówki kolumn, aby sortować dane. Aktualne sortowanie: <strong>{sortConfig.key}</strong> ({sortConfig.direction === 'asc' ? 'rosnąco' : 'malejąco'})
          </p>
        </div>
        
        <Table
          data={invoiceData}
          columns={basicColumns}
          sortConfig={sortConfig}
          onSort={setSortConfig}
        />
      </div>
    );
  },
};

// Custom row actions
export const WithCustomActions: Story = {
  render: () => {
    const [selectedRows, setSelectedRows] = useState<string[]>([]);

    const actionsColumns: TableColumn[] = [
      ...basicColumns.slice(0, -1), // Remove status column
      { 
        key: 'status', 
        header: 'Status',
        customFormat: (value: string) => (
          <span className={`px-2 py-1 rounded-md-full text-xs font-medium ${
            value === 'Opłacona' ? 'bg-success-100 text-success-800' :
            value === 'Wysłana' ? 'bg-primary-100 text-primary-800' :
            value === 'Przeterminowana' ? 'bg-error-100 text-error-800' :
            'bg-neutral-100 text-neutral-800'
          }`}>
            {value}
          </span>
        ),
      },
      {
        key: 'actions',
        header: 'Akcje',
        sortable: false,
        align: 'center',
        customFormat: (_, row) => (
          <div className="flex gap-1 justify-center">
            <Button 
              size="xs" 
              variant="secondary"
              onClick={() => alert(`Edytuj fakturę ${row.number}`)}
            >
              Edytuj
            </Button>
            <Button 
              size="xs" 
              variant="secondary"
              onClick={() => alert(`Pobierz PDF faktury ${row.number}`)}
            >
              PDF
            </Button>
            <Button 
              size="xs" 
              variant="secondary"
              onClick={() => alert(`Wyślij email z fakturą ${row.number}`)}
            >
              Email
            </Button>
          </div>
        ),
      },
    ];

    return (
      <div className="space-y-4">
        <h4 className="text-md font-semibold">Tabela z akcjami</h4>
        
        <Table
          data={invoiceData.slice(0, 4)}
          columns={actionsColumns}
          selectable={true}
          selectedRows={selectedRows}
          onSelectionChange={setSelectedRows}
        />
        
        {selectedRows.length > 0 && (
          <div className="bg-primary-50 border border-primary-200 rounded-md-lg p-4">
            <div className="flex items-center justify-between">
              <span className="text-sm text-primary-800">
                Zaznaczono {selectedRows.length} {selectedRows.length === 1 ? 'element' : 'elementy'}
              </span>
              <div className="flex gap-2">
                <Button size="sm" variant="primary">Akcja grupowa</Button>
                <Button size="sm" variant="secondary" onClick={() => setSelectedRows([])}>
                  Wyczyść zaznaczenie
                </Button>
              </div>
            </div>
          </div>
        )}
      </div>
    );
  },
};