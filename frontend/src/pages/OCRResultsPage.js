import React, { useState, useEffect, useCallback } from 'react';
import { Table } from '../design-system/components/patterns/Table/Table';
import { Badge } from '../design-system/components/primitives/Badge/Badge';
import { Button } from '../design-system/components/primitives/Button/Button';
import { Card } from '../design-system/components/patterns/Card/Card';
import { Stack } from '../design-system/components/layout/Stack/Stack';
import { Grid } from '../design-system/components/layout/Grid/Grid';
import { Container } from '../design-system/components/layout/Container/Container';
import { InvoiceStatusBadge } from '../design-system/components/business/InvoiceStatusBadge/InvoiceStatusBadge';
import axios from 'axios';

const OCRResultsPage = () => {
  const [ocrResults, setOcrResults] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [selectedRows, setSelectedRows] = useState([]);
  const [sortConfig, setSortConfig] = useState({ key: 'created_at', direction: 'desc' });
  const [pagination, setPagination] = useState({
    page: 1,
    pageSize: 25,
    total: 0,
  });
  const [filters, setFilters] = useState({
    status: 'all',
    confidence: 'all',
  });
  const [stats, setStats] = useState({
    total: 0,
    highConfidence: 0,
    needsReview: 0,
    withInvoice: 0,
  });

  // Fetch OCR results
  const fetchOCRResults = useCallback(async () => {
    setLoading(true);
    try {
      const params = new URLSearchParams({
        page: pagination.page.toString(),
        page_size: pagination.pageSize.toString(),
        sort_by: sortConfig.key,
        sort_direction: sortConfig.direction,
        ...filters,
      });

      const response = await axios.get(`/api/v1/ocr/results/?${params}`);
      const data = response.data;

      setOcrResults(data.results || []);
      setPagination(prev => ({
        ...prev,
        total: data.count || 0,
      }));
      setStats(data.stats || stats);
      setError(null);
    } catch (err) {
      console.error('Error fetching OCR results:', err);
      setError('Nie udało się pobrać wyników OCR');
    } finally {
      setLoading(false);
    }
  }, [pagination.page, pagination.pageSize, sortConfig, filters]);

  useEffect(() => {
    fetchOCRResults();
  }, [fetchOCRResults]);

  // Handle sorting
  const handleSort = (newSortConfig) => {
    setSortConfig(newSortConfig);
  };

  // Handle pagination
  const handlePageChange = (page) => {
    setPagination(prev => ({ ...prev, page }));
  };

  const handlePageSizeChange = (pageSize) => {
    setPagination(prev => ({ ...prev, pageSize, page: 1 }));
  };

  // Handle filters
  const handleFilterChange = (filterType, value) => {
    setFilters(prev => ({ ...prev, [filterType]: value }));
    setPagination(prev => ({ ...prev, page: 1 }));
  };

  // Get confidence badge variant
  const getConfidenceBadge = (confidence) => {
    if (confidence >= 95) {
      return { variant: 'success', text: `${confidence.toFixed(1)}%` };
    } else if (confidence >= 80) {
      return { variant: 'warning', text: `${confidence.toFixed(1)}%` };
    } else {
      return { variant: 'error', text: `${confidence.toFixed(1)}%` };
    }
  };

  // Get status badge
  const getStatusBadge = (result) => {
    if (result.faktura) {
      return { variant: 'success', text: 'Faktura utworzona' };
    } else if (result.confidence_score >= 80) {
      return { variant: 'warning', text: 'Wymaga przeglądu' };
    } else {
      return { variant: 'neutral', text: 'Niska pewność' };
    }
  };

  // Table columns
  const columns = [
    {
      key: 'document_filename',
      header: 'Plik',
      sortable: true,
      customFormat: (value, row) => (
        <div className="flex flex-col">
          <span className="font-medium text-sm truncate max-w-[200px]" title={value}>
            {value}
          </span>
          <span className="text-xs text-neutral-500">
            {row.document?.file_size ? `${(row.document.file_size / 1024).toFixed(1)} KB` : ''}
          </span>
        </div>
      ),
    },
    {
      key: 'created_at',
      header: 'Data przetworzenia',
      format: 'datetime',
      sortable: true,
      width: '150px',
    },
    {
      key: 'confidence_score',
      header: 'Pewność OCR',
      sortable: true,
      align: 'center',
      width: '120px',
      customFormat: (value) => {
        const badge = getConfidenceBadge(value);
        return <Badge variant={badge.variant} size="sm">{badge.text}</Badge>;
      },
    },
    {
      key: 'invoice_number',
      header: 'Numer faktury',
      sortable: true,
      width: '140px',
      customFormat: (value, row) => (
        <div className="flex flex-col">
          <span className="font-medium">
            {row.extracted_data?.invoice_number || '-'}
          </span>
          {row.extracted_data?.invoice_date && (
            <span className="text-xs text-neutral-500">
              {new Date(row.extracted_data.invoice_date).toLocaleDateString('pl-PL')}
            </span>
          )}
        </div>
      ),
    },
    {
      key: 'total_amount',
      header: 'Kwota',
      sortable: true,
      align: 'right',
      width: '120px',
      customFormat: (value, row) => (
        <div className="flex flex-col items-end">
          <span className="font-semibold">
            {row.extracted_data?.total_amount 
              ? `${parseFloat(row.extracted_data.total_amount).toLocaleString('pl-PL', {
                  style: 'currency',
                  currency: row.extracted_data.currency || 'PLN'
                })}`
              : '-'
            }
          </span>
          {row.extracted_data?.net_amount && (
            <span className="text-xs text-neutral-500">
              netto: {parseFloat(row.extracted_data.net_amount).toLocaleString('pl-PL', {
                style: 'currency',
                currency: row.extracted_data.currency || 'PLN'
              })}
            </span>
          )}
        </div>
      ),
    },
    {
      key: 'status',
      header: 'Status',
      sortable: false,
      align: 'center',
      width: '140px',
      customFormat: (value, row) => {
        const status = getStatusBadge(row);
        return <Badge variant={status.variant} size="sm">{status.text}</Badge>;
      },
    },
    {
      key: 'actions',
      header: 'Akcje',
      sortable: false,
      align: 'center',
      width: '160px',
      customFormat: (value, row) => (
        <div className="flex gap-1 justify-center">
          <Button
            size="xs"
            variant="secondary"
            onClick={() => window.location.href = `/ocr/result/${row.id}/`}
          >
            Szczegóły
          </Button>
          {row.faktura ? (
            <Button
              size="xs"
              variant="success"
              onClick={() => window.location.href = `/faktury/${row.faktura.id}/`}
            >
              Faktura
            </Button>
          ) : row.confidence_score >= 80 ? (
            <Button
              size="xs"
              variant="primary"
              onClick={() => window.location.href = `/ocr/result/${row.id}/`}
            >
              Utwórz
            </Button>
          ) : (
            <Button
              size="xs"
              variant="outline"
              onClick={() => window.location.href = `/faktury/dodaj/`}
            >
              Ręcznie
            </Button>
          )}
        </div>
      ),
    },
  ];

  // Filter buttons data
  const filterButtons = [
    { key: 'all', label: 'Wszystkie', count: stats.total },
    { key: 'high-confidence', label: 'Wysoka pewność', count: stats.highConfidence },
    { key: 'needs-review', label: 'Wymaga przeglądu', count: stats.needsReview },
    { key: 'with-invoice', label: 'Z fakturą', count: stats.withInvoice },
  ];

  if (error) {
    return (
      <Container>
        <Card variant="error">
          <div className="text-center py-8">
            <h2 className="text-lg font-semibold text-error-800 mb-2">Błąd ładowania</h2>
            <p className="text-error-600 mb-4">{error}</p>
            <Button variant="primary" onClick={fetchOCRResults}>
              Spróbuj ponownie
            </Button>
          </div>
        </Card>
      </Container>
    );
  }

  return (
    <Container>
      <Stack gap="lg">
        {/* Page Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold text-neutral-900">Wyniki OCR</h1>
            <p className="text-neutral-600 mt-1">
              Przegląd i zarządzanie wynikami przetwarzania dokumentów
            </p>
          </div>
          <Button
            variant="primary"
            onClick={() => window.location.href = '/upload/'}
          >
            Prześlij nowy dokument
          </Button>
        </div>

        {/* Statistics Cards */}
        <Grid cols={{ base: 1, md: 2, lg: 4 }} gap="md">
          <Card>
            <div className="text-center p-4">
              <div className="text-2xl font-bold text-primary-600 mb-1">
                {stats.total}
              </div>
              <div className="text-sm text-neutral-600">Łącznie wyników</div>
            </div>
          </Card>
          <Card>
            <div className="text-center p-4">
              <div className="text-2xl font-bold text-success-600 mb-1">
                {stats.highConfidence}
              </div>
              <div className="text-sm text-neutral-600">Wysoka pewność</div>
            </div>
          </Card>
          <Card>
            <div className="text-center p-4">
              <div className="text-2xl font-bold text-warning-600 mb-1">
                {stats.needsReview}
              </div>
              <div className="text-sm text-neutral-600">Wymaga przeglądu</div>
            </div>
          </Card>
          <Card>
            <div className="text-center p-4">
              <div className="text-2xl font-bold text-success-600 mb-1">
                {stats.withInvoice}
              </div>
              <div className="text-sm text-neutral-600">Faktury utworzone</div>
            </div>
          </Card>
        </Grid>

        {/* Filters */}
        <Card>
          <div className="p-4">
            <div className="flex flex-wrap gap-2">
              {filterButtons.map((filter) => (
                <Button
                  key={filter.key}
                  variant={filters.status === filter.key ? 'primary' : 'secondary'}
                  size="sm"
                  onClick={() => handleFilterChange('status', filter.key)}
                >
                  {filter.label}
                  {filter.count > 0 && (
                    <Badge variant="neutral" size="xs" className="ml-2">
                      {filter.count}
                    </Badge>
                  )}
                </Button>
              ))}
            </div>
          </div>
        </Card>

        {/* Results Table */}
        <Card>
          <Table
            data={ocrResults}
            columns={columns}
            loading={loading}
            sortable={true}
            sortConfig={sortConfig}
            onSort={handleSort}
            selectable={true}
            selectedRows={selectedRows}
            onSelectionChange={setSelectedRows}
            pagination={pagination}
            onPageChange={handlePageChange}
            onPageSizeChange={handlePageSizeChange}
            emptyMessage="Brak wyników OCR. Prześlij pierwszy dokument, aby rozpocząć przetwarzanie."
            variant="default"
            size="md"
          />
        </Card>

        {/* Bulk Actions */}
        {selectedRows.length > 0 && (
          <Card variant="info">
            <div className="p-4">
              <div className="flex items-center justify-between">
                <span className="text-sm text-primary-800">
                  Zaznaczono {selectedRows.length} {selectedRows.length === 1 ? 'wynik' : 'wyniki'}
                </span>
                <div className="flex gap-2">
                  <Button size="sm" variant="primary">
                    Utwórz faktury
                  </Button>
                  <Button size="sm" variant="secondary">
                    Eksportuj
                  </Button>
                  <Button 
                    size="sm" 
                    variant="outline"
                    onClick={() => setSelectedRows([])}
                  >
                    Wyczyść zaznaczenie
                  </Button>
                </div>
              </div>
            </div>
          </Card>
        )}
      </Stack>
    </Container>
  );
};

export default OCRResultsPage;