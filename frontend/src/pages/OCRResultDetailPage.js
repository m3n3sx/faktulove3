import React, { useState, useEffect, useCallback } from 'react';
import { Card } from '../design-system/components/patterns/Card/Card';
import { Button } from '../design-system/components/primitives/Button/Button';
import { Input } from '../design-system/components/primitives/Input/Input';
import { Select } from '../design-system/components/primitives/Select/Select';
import { Textarea } from '../design-system/components/primitives/Textarea/Textarea';
import { Badge } from '../design-system/components/primitives/Badge/Badge';
import { Stack } from '../design-system/components/layout/Stack/Stack';
import { Grid } from '../design-system/components/layout/Grid/Grid';
import { Container } from '../design-system/components/layout/Container/Container';
import { Form } from '../design-system/components/patterns/Form/Form';
import { CurrencyInput } from '../design-system/components/business/CurrencyInput/CurrencyInput';
import { DatePicker } from '../design-system/components/business/DatePicker/DatePicker';
import { NIPValidator } from '../design-system/components/business/NIPValidator/NIPValidator';
import { Progress } from '../design-system/components/primitives/Progress/Progress';
import axios from 'axios';

const OCRResultDetailPage = ({ resultId }) => {
  const [ocrResult, setOcrResult] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [saving, setSaving] = useState(false);
  const [formData, setFormData] = useState({});
  const [validationErrors, setValidationErrors] = useState({});
  const [fieldConfidence, setFieldConfidence] = useState({});

  // Fetch OCR result details
  const fetchOCRResult = useCallback(async () => {
    setLoading(true);
    try {
      const response = await axios.get(`/api/v1/ocr/result/${resultId}/`);
      const data = response.data;
      
      setOcrResult(data);
      setFormData({
        invoice_number: data.extracted_data?.invoice_number || '',
        invoice_date: data.extracted_data?.invoice_date || '',
        due_date: data.extracted_data?.due_date || '',
        supplier_name: data.extracted_data?.supplier_name || '',
        supplier_nip: data.extracted_data?.supplier_nip || '',
        buyer_name: data.extracted_data?.buyer_name || '',
        buyer_nip: data.extracted_data?.buyer_nip || '',
        net_amount: data.extracted_data?.net_amount || '',
        vat_amount: data.extracted_data?.vat_amount || '',
        total_amount: data.extracted_data?.total_amount || '',
        currency: data.extracted_data?.currency || 'PLN',
        payment_method: data.extracted_data?.payment_method || '',
        description: data.extracted_data?.description || '',
      });
      setFieldConfidence(data.field_confidence || {});
      setError(null);
    } catch (err) {
      console.error('Error fetching OCR result:', err);
      setError('Nie udało się pobrać szczegółów wyniku OCR');
    } finally {
      setLoading(false);
    }
  }, [resultId]);

  useEffect(() => {
    if (resultId) {
      fetchOCRResult();
    }
  }, [fetchOCRResult, resultId]);

  // Handle form field changes
  const handleFieldChange = (field, value) => {
    setFormData(prev => ({ ...prev, [field]: value }));
    // Clear validation error for this field
    if (validationErrors[field]) {
      setValidationErrors(prev => ({ ...prev, [field]: null }));
    }
  };

  // Validate form data
  const validateForm = () => {
    const errors = {};
    
    if (!formData.invoice_number?.trim()) {
      errors.invoice_number = 'Numer faktury jest wymagany';
    }
    
    if (!formData.invoice_date) {
      errors.invoice_date = 'Data wystawienia jest wymagana';
    }
    
    if (!formData.total_amount || parseFloat(formData.total_amount) <= 0) {
      errors.total_amount = 'Kwota brutto musi być większa od 0';
    }
    
    if (!formData.supplier_name?.trim()) {
      errors.supplier_name = 'Nazwa sprzedawcy jest wymagana';
    }

    setValidationErrors(errors);
    return Object.keys(errors).length === 0;
  };

  // Save OCR corrections and create invoice
  const handleSaveAndCreateInvoice = async () => {
    if (!validateForm()) {
      return;
    }

    setSaving(true);
    try {
      const response = await axios.post(`/api/v1/ocr/result/${resultId}/create-invoice/`, {
        extracted_data: formData,
        validation_notes: 'Dane zweryfikowane i poprawione przez użytkownika',
        accuracy_rating: calculateAccuracyRating(),
      });

      if (response.data.success) {
        // Redirect to created invoice
        if (response.data.invoice_id) {
          window.location.href = `/faktury/${response.data.invoice_id}/`;
        } else {
          window.location.href = '/ocr/results/';
        }
      } else {
        throw new Error(response.data.error || 'Nie udało się utworzyć faktury');
      }
    } catch (err) {
      console.error('Error creating invoice:', err);
      setError(err.response?.data?.error || err.message || 'Wystąpił błąd podczas tworzenia faktury');
    } finally {
      setSaving(false);
    }
  };

  // Calculate accuracy rating based on user changes
  const calculateAccuracyRating = () => {
    if (!ocrResult?.extracted_data) return 5;
    
    const originalData = ocrResult.extracted_data;
    let changedFields = 0;
    let totalFields = 0;
    
    Object.keys(formData).forEach(key => {
      if (originalData[key] !== undefined) {
        totalFields++;
        if (originalData[key] !== formData[key]) {
          changedFields++;
        }
      }
    });
    
    if (totalFields === 0) return 5;
    
    const accuracy = 1 - (changedFields / totalFields);
    return Math.max(1, Math.min(10, Math.round(accuracy * 10)));
  };

  // Get confidence badge for field
  const getFieldConfidenceBadge = (fieldName) => {
    const confidence = fieldConfidence[fieldName];
    if (!confidence) return null;
    
    const percentage = Math.round(confidence * 100);
    let variant = 'neutral';
    
    if (percentage >= 90) variant = 'success';
    else if (percentage >= 70) variant = 'warning';
    else variant = 'error';
    
    return <Badge variant={variant} size="xs">{percentage}%</Badge>;
  };

  // Get overall confidence info
  const getOverallConfidence = () => {
    if (!ocrResult?.confidence_score) return { variant: 'neutral', text: 'Nieznana', description: '' };
    
    const score = ocrResult.confidence_score;
    
    if (score >= 95) {
      return {
        variant: 'success',
        text: 'Wysoka pewność',
        description: 'Dane można zaufać, minimalne ryzyko błędów'
      };
    } else if (score >= 80) {
      return {
        variant: 'warning',
        text: 'Średnia pewność',
        description: 'Zalecana weryfikacja kluczowych danych'
      };
    } else {
      return {
        variant: 'error',
        text: 'Niska pewność',
        description: 'Wymagana dokładna weryfikacja wszystkich danych'
      };
    }
  };

  if (loading) {
    return (
      <Container>
        <Card>
          <div className="text-center py-12">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600 mx-auto mb-4"></div>
            <p className="text-neutral-600">Ładowanie szczegółów wyniku OCR...</p>
          </div>
        </Card>
      </Container>
    );
  }

  if (error) {
    return (
      <Container>
        <Card variant="error">
          <div className="text-center py-8">
            <h2 className="text-lg font-semibold text-error-800 mb-2">Błąd ładowania</h2>
            <p className="text-error-600 mb-4">{error}</p>
            <div className="flex gap-2 justify-center">
              <Button variant="primary" onClick={fetchOCRResult}>
                Spróbuj ponownie
              </Button>
              <Button variant="secondary" onClick={() => window.location.href = '/ocr/results/'}>
                Powrót do listy
              </Button>
            </div>
          </div>
        </Card>
      </Container>
    );
  }

  if (!ocrResult) {
    return (
      <Container>
        <Card>
          <div className="text-center py-8">
            <h2 className="text-lg font-semibold text-neutral-800 mb-2">Nie znaleziono wyniku</h2>
            <p className="text-neutral-600 mb-4">Wynik OCR o podanym ID nie istnieje</p>
            <Button variant="primary" onClick={() => window.location.href = '/ocr/results/'}>
              Powrót do listy
            </Button>
          </div>
        </Card>
      </Container>
    );
  }

  const confidence = getOverallConfidence();

  return (
    <Container>
      <Stack gap="lg">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold text-neutral-900">Szczegóły wyniku OCR</h1>
            <p className="text-neutral-600 mt-1">
              Przejrzyj i popraw wyodrębnione dane przed utworzeniem faktury
            </p>
          </div>
          <Button
            variant="secondary"
            onClick={() => window.location.href = '/ocr/results/'}
          >
            Powrót do listy
          </Button>
        </div>

        <Grid cols={{ base: 1, lg: 3 }} gap="lg">
          {/* Document Info */}
          <Card>
            <Card.Header>
              <h3 className="text-lg font-semibold">Informacje o dokumencie</h3>
            </Card.Header>
            <Card.Content>
              <Stack gap="sm">
                <div>
                  <div className="text-sm font-medium text-neutral-700">Nazwa pliku</div>
                  <div className="text-sm text-neutral-900">{ocrResult.document?.original_filename}</div>
                </div>
                <div>
                  <div className="text-sm font-medium text-neutral-700">Rozmiar</div>
                  <div className="text-sm text-neutral-900">
                    {ocrResult.document?.file_size 
                      ? `${(ocrResult.document.file_size / 1024).toFixed(1)} KB`
                      : 'Nieznany'
                    }
                  </div>
                </div>
                <div>
                  <div className="text-sm font-medium text-neutral-700">Przetworzono</div>
                  <div className="text-sm text-neutral-900">
                    {new Date(ocrResult.created_at).toLocaleString('pl-PL')}
                  </div>
                </div>
                <div>
                  <div className="text-sm font-medium text-neutral-700">Czas przetwarzania</div>
                  <div className="text-sm text-neutral-900">
                    {ocrResult.processing_time ? `${ocrResult.processing_time.toFixed(1)}s` : 'Nieznany'}
                  </div>
                </div>
              </Stack>
            </Card.Content>
          </Card>

          {/* Confidence Analysis */}
          <Card>
            <Card.Header>
              <h3 className="text-lg font-semibold">Analiza pewności</h3>
            </Card.Header>
            <Card.Content>
              <Stack gap="md">
                <div className="text-center">
                  <div className="mb-2">
                    <Badge variant={confidence.variant} size="lg">
                      {ocrResult.confidence_score?.toFixed(1)}%
                    </Badge>
                  </div>
                  <div className="font-semibold text-neutral-900">{confidence.text}</div>
                  <div className="text-sm text-neutral-600 mt-1">{confidence.description}</div>
                </div>
                
                <Progress 
                  value={ocrResult.confidence_score || 0} 
                  max={100}
                  variant={confidence.variant}
                  size="md"
                />
                
                <div className="text-xs text-neutral-500">
                  <div>Procesor: {ocrResult.processor_version || 'Nieznany'}</div>
                  <div>Lokalizacja: {ocrResult.processing_location || 'Nieznana'}</div>
                </div>
              </Stack>
            </Card.Content>
          </Card>

          {/* Invoice Status */}
          <Card>
            <Card.Header>
              <h3 className="text-lg font-semibold">Status faktury</h3>
            </Card.Header>
            <Card.Content>
              {ocrResult.faktura ? (
                <Stack gap="md">
                  <div className="text-center">
                    <Badge variant="success" size="lg">Faktura utworzona</Badge>
                  </div>
                  <div>
                    <div className="text-sm font-medium text-neutral-700">Numer faktury</div>
                    <div className="text-sm text-neutral-900">{ocrResult.faktura.numer}</div>
                  </div>
                  <div>
                    <div className="text-sm font-medium text-neutral-700">Data wystawienia</div>
                    <div className="text-sm text-neutral-900">
                      {new Date(ocrResult.faktura.data_wystawienia).toLocaleDateString('pl-PL')}
                    </div>
                  </div>
                  <Button
                    variant="success"
                    size="sm"
                    onClick={() => window.location.href = `/faktury/${ocrResult.faktura.id}/`}
                    className="w-full"
                  >
                    Zobacz fakturę
                  </Button>
                </Stack>
              ) : (
                <Stack gap="md">
                  <div className="text-center">
                    <Badge variant="warning" size="lg">Faktura nie utworzona</Badge>
                  </div>
                  <div className="text-sm text-neutral-600 text-center">
                    Przejrzyj dane i utwórz fakturę na podstawie wyników OCR
                  </div>
                  {ocrResult.confidence_score < 80 && (
                    <div className="bg-warning-50 border border-warning-200 rounded-md p-3">
                      <div className="text-xs text-warning-800">
                        ⚠️ Niska pewność OCR. Zalecana dokładna weryfikacja wszystkich danych.
                      </div>
                    </div>
                  )}
                </Stack>
              )}
            </Card.Content>
          </Card>
        </Grid>

        {/* Editable Form - only show if invoice not created */}
        {!ocrResult.faktura && (
          <Card>
            <Card.Header>
              <h3 className="text-lg font-semibold">Wyodrębnione dane - Edycja</h3>
              <p className="text-sm text-neutral-600">
                Sprawdź i popraw dane przed utworzeniem faktury. Pola z niską pewnością są oznaczone.
              </p>
            </Card.Header>
            <Card.Content>
              <Form onSubmit={(e) => { e.preventDefault(); handleSaveAndCreateInvoice(); }}>
                <Grid cols={{ base: 1, md: 2 }} gap="lg">
                  {/* Basic Invoice Data */}
                  <Stack gap="md">
                    <h4 className="font-semibold text-neutral-900 border-b pb-2">Dane faktury</h4>
                    
                    <div>
                      <div className="flex items-center gap-2 mb-1">
                        <label className="text-sm font-medium text-neutral-700">
                          Numer faktury *
                        </label>
                        {getFieldConfidenceBadge('invoice_number')}
                      </div>
                      <Input
                        value={formData.invoice_number}
                        onChange={(e) => handleFieldChange('invoice_number', e.target.value)}
                        error={validationErrors.invoice_number}
                        placeholder="np. FV/2025/001"
                      />
                    </div>

                    <Grid cols={2} gap="md">
                      <div>
                        <div className="flex items-center gap-2 mb-1">
                          <label className="text-sm font-medium text-neutral-700">
                            Data wystawienia *
                          </label>
                          {getFieldConfidenceBadge('invoice_date')}
                        </div>
                        <DatePicker
                          value={formData.invoice_date}
                          onChange={(value) => handleFieldChange('invoice_date', value)}
                          error={validationErrors.invoice_date}
                        />
                      </div>
                      <div>
                        <div className="flex items-center gap-2 mb-1">
                          <label className="text-sm font-medium text-neutral-700">
                            Termin płatności
                          </label>
                          {getFieldConfidenceBadge('due_date')}
                        </div>
                        <DatePicker
                          value={formData.due_date}
                          onChange={(value) => handleFieldChange('due_date', value)}
                        />
                      </div>
                    </Grid>

                    <Grid cols={{ base: 1, sm: 3 }} gap="md">
                      <div className="sm:col-span-2">
                        <div className="flex items-center gap-2 mb-1">
                          <label className="text-sm font-medium text-neutral-700">
                            Kwota brutto *
                          </label>
                          {getFieldConfidenceBadge('total_amount')}
                        </div>
                        <CurrencyInput
                          value={formData.total_amount}
                          onChange={(value) => handleFieldChange('total_amount', value)}
                          currency={formData.currency}
                          error={validationErrors.total_amount}
                        />
                      </div>
                      <div>
                        <div className="flex items-center gap-2 mb-1">
                          <label className="text-sm font-medium text-neutral-700">
                            Waluta
                          </label>
                        </div>
                        <Select
                          value={formData.currency}
                          onChange={(value) => handleFieldChange('currency', value)}
                          options={[
                            { value: 'PLN', label: 'PLN' },
                            { value: 'EUR', label: 'EUR' },
                            { value: 'USD', label: 'USD' },
                          ]}
                        />
                      </div>
                    </Grid>

                    <Grid cols={2} gap="md">
                      <div>
                        <div className="flex items-center gap-2 mb-1">
                          <label className="text-sm font-medium text-neutral-700">
                            Kwota netto
                          </label>
                          {getFieldConfidenceBadge('net_amount')}
                        </div>
                        <CurrencyInput
                          value={formData.net_amount}
                          onChange={(value) => handleFieldChange('net_amount', value)}
                          currency={formData.currency}
                        />
                      </div>
                      <div>
                        <div className="flex items-center gap-2 mb-1">
                          <label className="text-sm font-medium text-neutral-700">
                            Kwota VAT
                          </label>
                          {getFieldConfidenceBadge('vat_amount')}
                        </div>
                        <CurrencyInput
                          value={formData.vat_amount}
                          onChange={(value) => handleFieldChange('vat_amount', value)}
                          currency={formData.currency}
                        />
                      </div>
                    </Grid>
                  </Stack>

                  {/* Contractor Data */}
                  <Stack gap="md">
                    <h4 className="font-semibold text-neutral-900 border-b pb-2">Kontrahenci</h4>
                    
                    <div>
                      <div className="flex items-center gap-2 mb-1">
                        <label className="text-sm font-medium text-neutral-700">
                          Sprzedawca *
                        </label>
                        {getFieldConfidenceBadge('supplier_name')}
                      </div>
                      <Input
                        value={formData.supplier_name}
                        onChange={(e) => handleFieldChange('supplier_name', e.target.value)}
                        error={validationErrors.supplier_name}
                        placeholder="Nazwa firmy sprzedawcy"
                      />
                    </div>

                    <div>
                      <div className="flex items-center gap-2 mb-1">
                        <label className="text-sm font-medium text-neutral-700">
                          NIP sprzedawcy
                        </label>
                        {getFieldConfidenceBadge('supplier_nip')}
                      </div>
                      <NIPValidator
                        value={formData.supplier_nip}
                        onChange={(value) => handleFieldChange('supplier_nip', value)}
                        placeholder="123-456-78-90"
                      />
                    </div>

                    <div>
                      <div className="flex items-center gap-2 mb-1">
                        <label className="text-sm font-medium text-neutral-700">
                          Nabywca
                        </label>
                        {getFieldConfidenceBadge('buyer_name')}
                      </div>
                      <Input
                        value={formData.buyer_name}
                        onChange={(e) => handleFieldChange('buyer_name', e.target.value)}
                        placeholder="Nazwa firmy nabywcy"
                      />
                    </div>

                    <div>
                      <div className="flex items-center gap-2 mb-1">
                        <label className="text-sm font-medium text-neutral-700">
                          NIP nabywcy
                        </label>
                        {getFieldConfidenceBadge('buyer_nip')}
                      </div>
                      <NIPValidator
                        value={formData.buyer_nip}
                        onChange={(value) => handleFieldChange('buyer_nip', value)}
                        placeholder="123-456-78-90"
                      />
                    </div>

                    <div>
                      <div className="flex items-center gap-2 mb-1">
                        <label className="text-sm font-medium text-neutral-700">
                          Sposób płatności
                        </label>
                      </div>
                      <Select
                        value={formData.payment_method}
                        onChange={(value) => handleFieldChange('payment_method', value)}
                        options={[
                          { value: '', label: 'Wybierz sposób płatności' },
                          { value: 'przelew', label: 'Przelew bankowy' },
                          { value: 'gotowka', label: 'Gotówka' },
                          { value: 'karta', label: 'Karta płatnicza' },
                          { value: 'blik', label: 'BLIK' },
                        ]}
                      />
                    </div>

                    <div>
                      <div className="flex items-center gap-2 mb-1">
                        <label className="text-sm font-medium text-neutral-700">
                          Opis / Uwagi
                        </label>
                      </div>
                      <Textarea
                        value={formData.description}
                        onChange={(e) => handleFieldChange('description', e.target.value)}
                        placeholder="Dodatkowe informacje o fakturze..."
                        rows={3}
                      />
                    </div>
                  </Stack>
                </Grid>

                {/* Action Buttons */}
                <div className="flex justify-between items-center pt-6 border-t">
                  <Button
                    variant="secondary"
                    onClick={() => window.location.href = '/ocr/results/'}
                  >
                    Anuluj
                  </Button>
                  <div className="flex gap-2">
                    <Button
                      variant="outline"
                      onClick={() => window.location.href = '/faktury/dodaj/'}
                    >
                      Utwórz ręcznie
                    </Button>
                    <Button
                      variant="primary"
                      type="submit"
                      loading={saving}
                      disabled={saving}
                    >
                      {saving ? 'Tworzenie faktury...' : 'Utwórz fakturę'}
                    </Button>
                  </div>
                </div>
              </Form>
            </Card.Content>
          </Card>
        )}

        {/* Field Confidence Details */}
        {Object.keys(fieldConfidence).length > 0 && (
          <Card>
            <Card.Header>
              <h3 className="text-lg font-semibold">Szczegółowa pewność pól</h3>
              <p className="text-sm text-neutral-600">
                Pewność OCR dla poszczególnych pól dokumentu
              </p>
            </Card.Header>
            <Card.Content>
              <Grid cols={{ base: 1, sm: 2, lg: 3 }} gap="md">
                {Object.entries(fieldConfidence).map(([field, confidence]) => {
                  const percentage = Math.round(confidence * 100);
                  let variant = 'neutral';
                  
                  if (percentage >= 90) variant = 'success';
                  else if (percentage >= 70) variant = 'warning';
                  else variant = 'error';
                  
                  return (
                    <div key={field} className="flex items-center justify-between p-3 bg-neutral-50 rounded-md">
                      <span className="text-sm font-medium text-neutral-700 capitalize">
                        {field.replace(/_/g, ' ')}
                      </span>
                      <div className="flex items-center gap-2">
                        <Progress 
                          value={percentage} 
                          max={100}
                          variant={variant}
                          size="sm"
                          className="w-16"
                        />
                        <Badge variant={variant} size="xs">
                          {percentage}%
                        </Badge>
                      </div>
                    </div>
                  );
                })}
              </Grid>
            </Card.Content>
          </Card>
        )}

        {/* Raw OCR Text */}
        <Card>
          <Card.Header>
            <h3 className="text-lg font-semibold">Surowy tekst OCR</h3>
            <p className="text-sm text-neutral-600">
              Oryginalny tekst wyodrębniony z dokumentu
            </p>
          </Card.Header>
          <Card.Content>
            <div className="bg-neutral-50 rounded-md p-4 max-h-64 overflow-y-auto">
              <pre className="text-sm text-neutral-800 whitespace-pre-wrap font-mono">
                {ocrResult.raw_text || 'Brak dostępnego tekstu'}
              </pre>
            </div>
          </Card.Content>
        </Card>
      </Stack>
    </Container>
  );
};

export default OCRResultDetailPage;