# Polish Business Component Usage Examples

This document provides comprehensive examples of using design system components for Polish business applications, specifically tailored for FaktuLove's invoice management system.

## Table of Contents

1. [Invoice Management Examples](#invoice-management-examples)
2. [Contractor Management Examples](#contractor-management-examples)
3. [Company Settings Examples](#company-settings-examples)
4. [OCR Processing Examples](#ocr-processing-examples)
5. [Reporting and Analytics Examples](#reporting-and-analytics-examples)
6. [User Management Examples](#user-management-examples)

## Invoice Management Examples

### Complete Invoice Form

```jsx
import React, { useState } from 'react';
import {
  Form,
  Grid,
  Card,
  Button,
  Input,
  Select,
  Textarea,
  Text,
  Stack,
  Divider
} from '@design-system/components';
import {
  CurrencyInput,
  NIPValidator,
  VATRateSelector,
  DatePicker,
  InvoiceNumberGenerator,
  ComplianceIndicator
} from '@design-system/business';

const InvoiceForm = ({ invoice, companies, contractors, onSubmit }) => {
  const [formData, setFormData] = useState({
    number: invoice?.number || '',
    issueDate: invoice?.issueDate || new Date(),
    saleDate: invoice?.saleDate || new Date(),
    dueDate: invoice?.dueDate || new Date(),
    companyId: invoice?.companyId || '',
    contractorId: invoice?.contractorId || '',
    items: invoice?.items || [
      {
        name: '',
        quantity: 1,
        unit: 'szt.',
        netPrice: 0,
        vatRate: 23,
        netAmount: 0,
        vatAmount: 0,
        grossAmount: 0
      }
    ],
    notes: invoice?.notes || '',
    paymentMethod: invoice?.paymentMethod || 'transfer'
  });

  const [validation, setValidation] = useState({});
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleSubmit = async (data) => {
    setIsSubmitting(true);
    try {
      await onSubmit(data);
    } finally {
      setIsSubmitting(false);
    }
  };

  const addInvoiceItem = () => {
    setFormData(prev => ({
      ...prev,
      items: [...prev.items, {
        name: '',
        quantity: 1,
        unit: 'szt.',
        netPrice: 0,
        vatRate: 23,
        netAmount: 0,
        vatAmount: 0,
        grossAmount: 0
      }]
    }));
  };

  const updateInvoiceItem = (index, field, value) => {
    setFormData(prev => {
      const newItems = [...prev.items];
      newItems[index] = { ...newItems[index], [field]: value };
      
      // Recalculate amounts
      if (field === 'quantity' || field === 'netPrice' || field === 'vatRate') {
        const item = newItems[index];
        item.netAmount = item.quantity * item.netPrice;
        item.vatAmount = item.netAmount * (item.vatRate / 100);
        item.grossAmount = item.netAmount + item.vatAmount;
      }
      
      return { ...prev, items: newItems };
    });
  };

  const calculateTotals = () => {
    return formData.items.reduce((totals, item) => ({
      net: totals.net + item.netAmount,
      vat: totals.vat + item.vatAmount,
      gross: totals.gross + item.grossAmount
    }), { net: 0, vat: 0, gross: 0 });
  };

  const totals = calculateTotals();

  return (
    <Form 
      initialValues={formData}
      onSubmit={handleSubmit}
      validation="polish-invoice"
    >
      <Stack gap="lg">
        {/* Header */}
        <Card variant="elevated">
          <Card.Header>
            <Stack direction="row" justify="between" align="center">
              <Text variant="heading-lg">
                {invoice ? 'Edytuj fakturę' : 'Nowa faktura'}
              </Text>
              <ComplianceIndicator 
                type="invoice"
                status="compliant"
                regulations={['VAT', 'KSeF']}
              />
            </Stack>
          </Card.Header>
          
          <Card.Body>
            <Grid cols={3} gap="md">
              <InvoiceNumberGenerator
                label="Numer faktury"
                value={formData.number}
                onChange={(number) => setFormData(prev => ({ ...prev, number }))}
                pattern="FV/{YYYY}/{MM}/{###}"
                required
              />
              
              <DatePicker
                label="Data wystawienia"
                value={formData.issueDate}
                onChange={(date) => setFormData(prev => ({ ...prev, issueDate: date }))}
                format="DD.MM.YYYY"
                locale="pl"
                required
              />
              
              <DatePicker
                label="Data sprzedaży"
                value={formData.saleDate}
                onChange={(date) => setFormData(prev => ({ ...prev, saleDate: date }))}
                format="DD.MM.YYYY"
                locale="pl"
                required
              />
            </Grid>
          </Card.Body>
        </Card>

        {/* Company and Contractor */}
        <Grid cols={2} gap="lg">
          <Card variant="outlined">
            <Card.Header>
              <Text variant="heading-md">Sprzedawca</Text>
            </Card.Header>
            <Card.Body>
              <Select
                label="Firma"
                value={formData.companyId}
                onChange={(companyId) => setFormData(prev => ({ ...prev, companyId }))}
                options={companies.map(company => ({
                  value: company.id,
                  label: `${company.name} (${company.nip})`
                }))}
                required
              />
            </Card.Body>
          </Card>

          <Card variant="outlined">
            <Card.Header>
              <Text variant="heading-md">Nabywca</Text>
            </Card.Header>
            <Card.Body>
              <Stack gap="md">
                <Select
                  label="Kontrahent"
                  value={formData.contractorId}
                  onChange={(contractorId) => setFormData(prev => ({ ...prev, contractorId }))}
                  options={contractors.map(contractor => ({
                    value: contractor.id,
                    label: `${contractor.name} (${contractor.nip})`
                  }))}
                  searchable
                  clearable
                  required
                />
                
                <Button 
                  variant="ghost" 
                  size="sm"
                  onClick={() => {/* Open contractor form */}}
                >
                  + Dodaj nowego kontrahenta
                </Button>
              </Stack>
            </Card.Body>
          </Card>
        </Grid>

        {/* Invoice Items */}
        <Card variant="outlined">
          <Card.Header>
            <Stack direction="row" justify="between" align="center">
              <Text variant="heading-md">Pozycje faktury</Text>
              <Button variant="outline" size="sm" onClick={addInvoiceItem}>
                + Dodaj pozycję
              </Button>
            </Stack>
          </Card.Header>
          
          <Card.Body>
            <Stack gap="md">
              {formData.items.map((item, index) => (
                <Card key={index} variant="ghost">
                  <Card.Body>
                    <Grid cols={7} gap="sm" align="end">
                      <Input
                        label="Nazwa towaru/usługi"
                        value={item.name}
                        onChange={(value) => updateInvoiceItem(index, 'name', value)}
                        required
                      />
                      
                      <Input
                        label="Ilość"
                        type="number"
                        value={item.quantity}
                        onChange={(value) => updateInvoiceItem(index, 'quantity', parseFloat(value))}
                        min={0}
                        step={0.01}
                        required
                      />
                      
                      <Select
                        label="Jednostka"
                        value={item.unit}
                        onChange={(value) => updateInvoiceItem(index, 'unit', value)}
                        options={[
                          { value: 'szt.', label: 'szt.' },
                          { value: 'kg', label: 'kg' },
                          { value: 'm', label: 'm' },
                          { value: 'm²', label: 'm²' },
                          { value: 'godz.', label: 'godz.' },
                          { value: 'usł.', label: 'usł.' }
                        ]}
                      />
                      
                      <CurrencyInput
                        label="Cena netto"
                        value={item.netPrice}
                        onChange={(value) => updateInvoiceItem(index, 'netPrice', value)}
                        currency="PLN"
                        required
                      />
                      
                      <VATRateSelector
                        label="VAT %"
                        value={item.vatRate}
                        onChange={(value) => updateInvoiceItem(index, 'vatRate', value)}
                        required
                      />
                      
                      <CurrencyInput
                        label="Wartość netto"
                        value={item.netAmount}
                        currency="PLN"
                        readOnly
                      />
                      
                      <Button
                        variant="ghost"
                        size="sm"
                        color="danger"
                        onClick={() => {
                          setFormData(prev => ({
                            ...prev,
                            items: prev.items.filter((_, i) => i !== index)
                          }));
                        }}
                        disabled={formData.items.length === 1}
                      >
                        Usuń
                      </Button>
                    </Grid>
                  </Card.Body>
                </Card>
              ))}
            </Stack>
          </Card.Body>
        </Card>

        {/* Totals */}
        <Card variant="elevated">
          <Card.Header>
            <Text variant="heading-md">Podsumowanie</Text>
          </Card.Header>
          
          <Card.Body>
            <Grid cols={3} gap="md">
              <Stack gap="xs">
                <Text variant="body-sm" color="muted">Wartość netto</Text>
                <Text variant="heading-sm">
                  {new Intl.NumberFormat('pl-PL', {
                    style: 'currency',
                    currency: 'PLN'
                  }).format(totals.net)}
                </Text>
              </Stack>
              
              <Stack gap="xs">
                <Text variant="body-sm" color="muted">VAT</Text>
                <Text variant="heading-sm">
                  {new Intl.NumberFormat('pl-PL', {
                    style: 'currency',
                    currency: 'PLN'
                  }).format(totals.vat)}
                </Text>
              </Stack>
              
              <Stack gap="xs">
                <Text variant="body-sm" color="muted">Wartość brutto</Text>
                <Text variant="heading-lg" color="primary">
                  {new Intl.NumberFormat('pl-PL', {
                    style: 'currency',
                    currency: 'PLN'
                  }).format(totals.gross)}
                </Text>
              </Stack>
            </Grid>
          </Card.Body>
        </Card>

        {/* Payment Details */}
        <Card variant="outlined">
          <Card.Header>
            <Text variant="heading-md">Płatność</Text>
          </Card.Header>
          
          <Card.Body>
            <Grid cols={2} gap="md">
              <Select
                label="Sposób płatności"
                value={formData.paymentMethod}
                onChange={(value) => setFormData(prev => ({ ...prev, paymentMethod: value }))}
                options={[
                  { value: 'transfer', label: 'Przelew bankowy' },
                  { value: 'cash', label: 'Gotówka' },
                  { value: 'card', label: 'Karta płatnicza' },
                  { value: 'blik', label: 'BLIK' }
                ]}
                required
              />
              
              <DatePicker
                label="Termin płatności"
                value={formData.dueDate}
                onChange={(date) => setFormData(prev => ({ ...prev, dueDate: date }))}
                format="DD.MM.YYYY"
                locale="pl"
                minDate={formData.issueDate}
                required
              />
            </Grid>
            
            <Textarea
              label="Uwagi"
              value={formData.notes}
              onChange={(value) => setFormData(prev => ({ ...prev, notes: value }))}
              placeholder="Dodatkowe informacje o fakturze..."
              rows={3}
              maxLength={500}
              showCharCount
            />
          </Card.Body>
        </Card>

        {/* Actions */}
        <Card variant="ghost">
          <Card.Body>
            <Stack direction="row" gap="md" justify="end">
              <Button variant="outline" size="lg">
                Anuluj
              </Button>
              <Button variant="ghost" size="lg">
                Zapisz jako szkic
              </Button>
              <Button 
                type="submit" 
                variant="primary" 
                size="lg"
                loading={isSubmitting}
              >
                {invoice ? 'Zaktualizuj fakturę' : 'Wystaw fakturę'}
              </Button>
            </Stack>
          </Card.Body>
        </Card>
      </Stack>
    </Form>
  );
};

export default InvoiceForm;
```

### Invoice List with Filtering

```jsx
import React, { useState, useMemo } from 'react';
import {
  Table,
  Input,
  Select,
  Button,
  Badge,
  Text,
  Stack,
  Card,
  Pagination,
  Checkbox
} from '@design-system/components';
import {
  DatePicker,
  CurrencyDisplay,
  StatusIndicator
} from '@design-system/business';

const InvoiceList = ({ invoices, onEdit, onDelete, onExport }) => {
  const [filters, setFilters] = useState({
    search: '',
    status: '',
    dateFrom: null,
    dateTo: null,
    contractor: '',
    minAmount: '',
    maxAmount: ''
  });
  
  const [selectedInvoices, setSelectedInvoices] = useState([]);
  const [currentPage, setCurrentPage] = useState(1);
  const [pageSize, setPageSize] = useState(25);

  const filteredInvoices = useMemo(() => {
    return invoices.filter(invoice => {
      if (filters.search && !invoice.number.toLowerCase().includes(filters.search.toLowerCase()) &&
          !invoice.contractor.name.toLowerCase().includes(filters.search.toLowerCase())) {
        return false;
      }
      
      if (filters.status && invoice.status !== filters.status) {
        return false;
      }
      
      if (filters.dateFrom && new Date(invoice.issueDate) < filters.dateFrom) {
        return false;
      }
      
      if (filters.dateTo && new Date(invoice.issueDate) > filters.dateTo) {
        return false;
      }
      
      if (filters.contractor && invoice.contractor.id !== filters.contractor) {
        return false;
      }
      
      if (filters.minAmount && invoice.grossAmount < parseFloat(filters.minAmount)) {
        return false;
      }
      
      if (filters.maxAmount && invoice.grossAmount > parseFloat(filters.maxAmount)) {
        return false;
      }
      
      return true;
    });
  }, [invoices, filters]);

  const paginatedInvoices = useMemo(() => {
    const startIndex = (currentPage - 1) * pageSize;
    return filteredInvoices.slice(startIndex, startIndex + pageSize);
  }, [filteredInvoices, currentPage, pageSize]);

  const handleSelectAll = (checked) => {
    if (checked) {
      setSelectedInvoices(paginatedInvoices.map(invoice => invoice.id));
    } else {
      setSelectedInvoices([]);
    }
  };

  const handleSelectInvoice = (invoiceId, checked) => {
    if (checked) {
      setSelectedInvoices(prev => [...prev, invoiceId]);
    } else {
      setSelectedInvoices(prev => prev.filter(id => id !== invoiceId));
    }
  };

  const getStatusVariant = (status) => {
    const variants = {
      draft: 'secondary',
      sent: 'info',
      paid: 'success',
      overdue: 'danger',
      cancelled: 'warning'
    };
    return variants[status] || 'secondary';
  };

  const getStatusLabel = (status) => {
    const labels = {
      draft: 'Szkic',
      sent: 'Wysłana',
      paid: 'Opłacona',
      overdue: 'Przeterminowana',
      cancelled: 'Anulowana'
    };
    return labels[status] || status;
  };

  const columns = [
    {
      key: 'select',
      header: (
        <Checkbox
          checked={selectedInvoices.length === paginatedInvoices.length && paginatedInvoices.length > 0}
          indeterminate={selectedInvoices.length > 0 && selectedInvoices.length < paginatedInvoices.length}
          onChange={handleSelectAll}
          aria-label="Zaznacz wszystkie faktury"
        />
      ),
      render: (_, invoice) => (
        <Checkbox
          checked={selectedInvoices.includes(invoice.id)}
          onChange={(checked) => handleSelectInvoice(invoice.id, checked)}
          aria-label={`Zaznacz fakturę ${invoice.number}`}
        />
      ),
      width: '50px'
    },
    {
      key: 'number',
      header: 'Numer faktury',
      render: (number, invoice) => (
        <Button
          variant="link"
          onClick={() => onEdit(invoice.id)}
        >
          {number}
        </Button>
      ),
      sortable: true
    },
    {
      key: 'issueDate',
      header: 'Data wystawienia',
      render: (date) => new Intl.DateTimeFormat('pl-PL').format(new Date(date)),
      sortable: true
    },
    {
      key: 'contractor',
      header: 'Kontrahent',
      render: (contractor) => (
        <Stack gap="xs">
          <Text variant="body-medium" weight="medium">
            {contractor.name}
          </Text>
          <Text variant="body-sm" color="muted">
            NIP: {contractor.nip}
          </Text>
        </Stack>
      ),
      sortable: true
    },
    {
      key: 'grossAmount',
      header: 'Kwota brutto',
      render: (amount) => (
        <CurrencyDisplay
          amount={amount}
          currency="PLN"
          locale="pl-PL"
        />
      ),
      sortable: true,
      align: 'right'
    },
    {
      key: 'status',
      header: 'Status',
      render: (status) => (
        <Badge variant={getStatusVariant(status)}>
          {getStatusLabel(status)}
        </Badge>
      ),
      sortable: true
    },
    {
      key: 'dueDate',
      header: 'Termin płatności',
      render: (dueDate, invoice) => {
        const isOverdue = new Date(dueDate) < new Date() && invoice.status !== 'paid';
        return (
          <Stack gap="xs">
            <Text 
              variant="body-sm" 
              color={isOverdue ? 'danger' : 'default'}
            >
              {new Intl.DateTimeFormat('pl-PL').format(new Date(dueDate))}
            </Text>
            {isOverdue && (
              <StatusIndicator
                status="overdue"
                message="Przeterminowana"
                size="sm"
              />
            )}
          </Stack>
        );
      },
      sortable: true
    },
    {
      key: 'actions',
      header: 'Akcje',
      render: (_, invoice) => (
        <Stack direction="row" gap="xs">
          <Button
            variant="ghost"
            size="sm"
            onClick={() => onEdit(invoice.id)}
          >
            Edytuj
          </Button>
          <Button
            variant="ghost"
            size="sm"
            onClick={() => window.open(`/invoices/${invoice.id}/pdf`, '_blank')}
          >
            PDF
          </Button>
          <Button
            variant="ghost"
            size="sm"
            color="danger"
            onClick={() => onDelete(invoice.id)}
          >
            Usuń
          </Button>
        </Stack>
      ),
      width: '150px'
    }
  ];

  return (
    <Stack gap="lg">
      {/* Filters */}
      <Card variant="outlined">
        <Card.Header>
          <Text variant="heading-md">Filtry</Text>
        </Card.Header>
        
        <Card.Body>
          <Grid cols={4} gap="md">
            <Input
              label="Szukaj"
              placeholder="Numer faktury lub kontrahent..."
              value={filters.search}
              onChange={(value) => setFilters(prev => ({ ...prev, search: value }))}
              clearable
            />
            
            <Select
              label="Status"
              value={filters.status}
              onChange={(value) => setFilters(prev => ({ ...prev, status: value }))}
              options={[
                { value: '', label: 'Wszystkie' },
                { value: 'draft', label: 'Szkice' },
                { value: 'sent', label: 'Wysłane' },
                { value: 'paid', label: 'Opłacone' },
                { value: 'overdue', label: 'Przeterminowane' },
                { value: 'cancelled', label: 'Anulowane' }
              ]}
              clearable
            />
            
            <DatePicker
              label="Data od"
              value={filters.dateFrom}
              onChange={(date) => setFilters(prev => ({ ...prev, dateFrom: date }))}
              format="DD.MM.YYYY"
              locale="pl"
              clearable
            />
            
            <DatePicker
              label="Data do"
              value={filters.dateTo}
              onChange={(date) => setFilters(prev => ({ ...prev, dateTo: date }))}
              format="DD.MM.YYYY"
              locale="pl"
              minDate={filters.dateFrom}
              clearable
            />
          </Grid>
          
          <Grid cols={3} gap="md" className="mt-4">
            <Input
              label="Kwota od"
              type="number"
              value={filters.minAmount}
              onChange={(value) => setFilters(prev => ({ ...prev, minAmount: value }))}
              placeholder="0.00"
              step="0.01"
            />
            
            <Input
              label="Kwota do"
              type="number"
              value={filters.maxAmount}
              onChange={(value) => setFilters(prev => ({ ...prev, maxAmount: value }))}
              placeholder="0.00"
              step="0.01"
            />
            
            <Stack justify="end">
              <Button
                variant="outline"
                onClick={() => setFilters({
                  search: '',
                  status: '',
                  dateFrom: null,
                  dateTo: null,
                  contractor: '',
                  minAmount: '',
                  maxAmount: ''
                })}
              >
                Wyczyść filtry
              </Button>
            </Stack>
          </Grid>
        </Card.Body>
      </Card>

      {/* Actions */}
      {selectedInvoices.length > 0 && (
        <Card variant="info">
          <Card.Body>
            <Stack direction="row" justify="between" align="center">
              <Text variant="body-medium">
                Zaznaczono {selectedInvoices.length} faktur
              </Text>
              
              <Stack direction="row" gap="sm">
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => onExport(selectedInvoices)}
                >
                  Eksportuj zaznaczone
                </Button>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => {/* Bulk email */}}
                >
                  Wyślij email
                </Button>
                <Button
                  variant="outline"
                  size="sm"
                  color="danger"
                  onClick={() => {/* Bulk delete */}}
                >
                  Usuń zaznaczone
                </Button>
              </Stack>
            </Stack>
          </Card.Body>
        </Card>
      )}

      {/* Table */}
      <Card variant="elevated">
        <Card.Header>
          <Stack direction="row" justify="between" align="center">
            <Text variant="heading-md">
              Faktury ({filteredInvoices.length})
            </Text>
            
            <Stack direction="row" gap="sm">
              <Select
                value={pageSize}
                onChange={setPageSize}
                options={[
                  { value: 10, label: '10 na stronę' },
                  { value: 25, label: '25 na stronę' },
                  { value: 50, label: '50 na stronę' },
                  { value: 100, label: '100 na stronę' }
                ]}
                size="sm"
              />
              
              <Button
                variant="primary"
                onClick={() => onEdit('new')}
              >
                + Nowa faktura
              </Button>
            </Stack>
          </Stack>
        </Card.Header>
        
        <Card.Body padding="none">
          <Table
            data={paginatedInvoices}
            columns={columns}
            sortable
            hoverable
            emptyMessage="Brak faktur spełniających kryteria"
          />
        </Card.Body>
        
        <Card.Footer>
          <Pagination
            currentPage={currentPage}
            totalPages={Math.ceil(filteredInvoices.length / pageSize)}
            onPageChange={setCurrentPage}
            showInfo
            showSizeChanger
            pageSizeOptions={[10, 25, 50, 100]}
            pageSize={pageSize}
            onPageSizeChange={setPageSize}
          />
        </Card.Footer>
      </Card>
    </Stack>
  );
};

export default InvoiceList;
```

## Contractor Management Examples

### Contractor Form with NIP Validation

```jsx
import React, { useState } from 'react';
import {
  Form,
  Grid,
  Card,
  Button,
  Input,
  Select,
  Text,
  Stack,
  Alert
} from '@design-system/components';
import {
  NIPValidator,
  REGONValidator,
  AddressInput,
  CompanyTypeSelector
} from '@design-system/business';

const ContractorForm = ({ contractor, onSubmit, onCancel }) => {
  const [formData, setFormData] = useState({
    name: contractor?.name || '',
    nip: contractor?.nip || '',
    regon: contractor?.regon || '',
    companyType: contractor?.companyType || 'company',
    address: contractor?.address || {
      street: '',
      houseNumber: '',
      apartmentNumber: '',
      postalCode: '',
      city: '',
      country: 'Polska'
    },
    contact: contractor?.contact || {
      email: '',
      phone: '',
      website: ''
    },
    bankAccount: contractor?.bankAccount || '',
    notes: contractor?.notes || ''
  });

  const [validation, setValidation] = useState({
    nip: { isValid: false, message: '' },
    regon: { isValid: false, message: '' }
  });

  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleSubmit = async (data) => {
    // Validate required fields
    if (!validation.nip.isValid) {
      alert('Proszę wprowadzić poprawny NIP');
      return;
    }

    setIsSubmitting(true);
    try {
      await onSubmit(data);
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleNIPValidation = (isValid, message) => {
    setValidation(prev => ({
      ...prev,
      nip: { isValid, message }
    }));
  };

  const handleREGONValidation = (isValid, message) => {
    setValidation(prev => ({
      ...prev,
      regon: { isValid, message }
    }));
  };

  return (
    <Form 
      initialValues={formData}
      onSubmit={handleSubmit}
      validation="polish-business"
    >
      <Stack gap="lg">
        {/* Basic Information */}
        <Card variant="elevated">
          <Card.Header>
            <Text variant="heading-lg">
              {contractor ? 'Edytuj kontrahenta' : 'Nowy kontrahent'}
            </Text>
          </Card.Header>
          
          <Card.Body>
            <Stack gap="md">
              <Input
                label="Nazwa firmy"
                value={formData.name}
                onChange={(value) => setFormData(prev => ({ ...prev, name: value }))}
                placeholder="Wprowadź nazwę firmy"
                required
                maxLength={255}
              />
              
              <Grid cols={2} gap="md">
                <CompanyTypeSelector
                  label="Typ podmiotu"
                  value={formData.companyType}
                  onChange={(value) => setFormData(prev => ({ ...prev, companyType: value }))}
                  required
                />
                
                <div /> {/* Empty cell for spacing */}
              </Grid>
              
              <Grid cols={2} gap="md">
                <NIPValidator
                  label="NIP"
                  value={formData.nip}
                  onChange={(value) => setFormData(prev => ({ ...prev, nip: value }))}
                  onValidation={handleNIPValidation}
                  required
                  showValidationIcon
                  validateOnBlur
                />
                
                <REGONValidator
                  label="REGON"
                  value={formData.regon}
                  onChange={(value) => setFormData(prev => ({ ...prev, regon: value }))}
                  onValidation={handleREGONValidation}
                  showValidationIcon
                  validateOnBlur
                  optional
                />
              </Grid>
              
              {validation.nip.message && !validation.nip.isValid && (
                <Alert variant="error">
                  {validation.nip.message}
                </Alert>
              )}
            </Stack>
          </Card.Body>
        </Card>

        {/* Address */}
        <Card variant="outlined">
          <Card.Header>
            <Text variant="heading-md">Adres</Text>
          </Card.Header>
          
          <Card.Body>
            <AddressInput
              value={formData.address}
              onChange={(address) => setFormData(prev => ({ ...prev, address }))}
              required
              showCountrySelector
              defaultCountry="Polska"
              validatePostalCode="polish"
            />
          </Card.Body>
        </Card>

        {/* Contact Information */}
        <Card variant="outlined">
          <Card.Header>
            <Text variant="heading-md">Kontakt</Text>
          </Card.Header>
          
          <Card.Body>
            <Grid cols={2} gap="md">
              <Input
                label="Email"
                type="email"
                value={formData.contact.email}
                onChange={(value) => setFormData(prev => ({
                  ...prev,
                  contact: { ...prev.contact, email: value }
                }))}
                validation="email"
                placeholder="kontakt@firma.pl"
              />
              
              <Input
                label="Telefon"
                type="tel"
                value={formData.contact.phone}
                onChange={(value) => setFormData(prev => ({
                  ...prev,
                  contact: { ...prev.contact, phone: value }
                }))}
                validation="polish-phone"
                placeholder="+48 123 456 789"
              />
              
              <Input
                label="Strona internetowa"
                type="url"
                value={formData.contact.website}
                onChange={(value) => setFormData(prev => ({
                  ...prev,
                  contact: { ...prev.contact, website: value }
                }))}
                validation="url"
                placeholder="https://www.firma.pl"
              />
            </Grid>
          </Card.Body>
        </Card>

        {/* Bank Account */}
        <Card variant="outlined">
          <Card.Header>
            <Text variant="heading-md">Dane bankowe</Text>
          </Card.Header>
          
          <Card.Body>
            <Input
              label="Numer konta bankowego"
              value={formData.bankAccount}
              onChange={(value) => setFormData(prev => ({ ...prev, bankAccount: value }))}
              validation="iban"
              placeholder="PL 1234 5678 9012 3456 7890 1234"
              helpText="Wprowadź numer konta w formacie IBAN"
            />
          </Card.Body>
        </Card>

        {/* Notes */}
        <Card variant="outlined">
          <Card.Header>
            <Text variant="heading-md">Uwagi</Text>
          </Card.Header>
          
          <Card.Body>
            <Textarea
              label="Dodatkowe informacje"
              value={formData.notes}
              onChange={(value) => setFormData(prev => ({ ...prev, notes: value }))}
              placeholder="Dodatkowe informacje o kontrahencie..."
              rows={4}
              maxLength={1000}
              showCharCount
            />
          </Card.Body>
        </Card>

        {/* Actions */}
        <Card variant="ghost">
          <Card.Body>
            <Stack direction="row" gap="md" justify="end">
              <Button 
                variant="outline" 
                size="lg"
                onClick={onCancel}
              >
                Anuluj
              </Button>
              <Button 
                type="submit" 
                variant="primary" 
                size="lg"
                loading={isSubmitting}
                disabled={!validation.nip.isValid}
              >
                {contractor ? 'Zaktualizuj' : 'Dodaj kontrahenta'}
              </Button>
            </Stack>
          </Card.Body>
        </Card>
      </Stack>
    </Form>
  );
};

export default ContractorForm;
```

This comprehensive documentation provides real-world examples of using the design system components for Polish business applications, specifically tailored for FaktuLove's invoice management system. The examples demonstrate proper usage of Polish business validation, formatting, and compliance features.