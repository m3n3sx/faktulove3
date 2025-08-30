import React, { useState, useCallback } from 'react';
import { Button } from '../design-system/components/primitives/Button/Button';
import { Input } from '../design-system/components/primitives/Input/Input';
import { Badge } from '../design-system/components/primitives/Badge/Badge';
import { CurrencyInput } from '../design-system/components/business/CurrencyInput/CurrencyInput';
import { DatePicker } from '../design-system/components/business/DatePicker/DatePicker';
import { NIPValidator } from '../design-system/components/business/NIPValidator/NIPValidator';
import axios from 'axios';

const OCRInlineEditor = ({ 
  ocrResult, 
  onSave, 
  onCancel, 
  onError 
}) => {
  const [formData, setFormData] = useState({
    invoice_number: ocrResult.extracted_data?.invoice_number || '',
    invoice_date: ocrResult.extracted_data?.invoice_date || '',
    supplier_name: ocrResult.extracted_data?.supplier_name || '',
    supplier_nip: ocrResult.extracted_data?.supplier_nip || '',
    buyer_name: ocrResult.extracted_data?.buyer_name || '',
    buyer_nip: ocrResult.extracted_data?.buyer_nip || '',
    total_amount: ocrResult.extracted_data?.total_amount || '',
    net_amount: ocrResult.extracted_data?.net_amount || '',
    currency: ocrResult.extracted_data?.currency || 'PLN',
  });
  const [saving, setSaving] = useState(false);
  const [errors, setErrors] = useState({});

  // Handle field changes
  const handleFieldChange = useCallback((field, value) => {
    setFormData(prev => ({ ...prev, [field]: value }));
    // Clear error for this field
    if (errors[field]) {
      setErrors(prev => ({ ...prev, [field]: null }));
    }
  }, [errors]);

  // Validate form
  const validateForm = useCallback(() => {
    const newErrors = {};
    
    if (!formData.invoice_number?.trim()) {
      newErrors.invoice_number = 'Wymagane';
    }
    
    if (!formData.invoice_date) {
      newErrors.invoice_date = 'Wymagane';
    }
    
    if (!formData.total_amount || parseFloat(formData.total_amount) <= 0) {
      newErrors.total_amount = 'Wymagane > 0';
    }
    
    if (!formData.supplier_name?.trim()) {
      newErrors.supplier_name = 'Wymagane';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  }, [formData]);

  // Save changes
  const handleSave = useCallback(async () => {
    if (!validateForm()) {
      return;
    }

    setSaving(true);
    try {
      const response = await axios.patch(`/api/v1/ocr/result/${ocrResult.id}/`, {
        extracted_data: formData,
      });

      if (response.data.success) {
        onSave?.(response.data.data);
      } else {
        throw new Error(response.data.error || 'Nie udało się zapisać zmian');
      }
    } catch (err) {
      console.error('Error saving OCR data:', err);
      onError?.(err.response?.data?.error || err.message || 'Wystąpił błąd podczas zapisywania');
    } finally {
      setSaving(false);
    }
  }, [formData, ocrResult.id, onSave, onError, validateForm]);

  // Get field confidence badge
  const getConfidenceBadge = useCallback((fieldName) => {
    const confidence = ocrResult.field_confidence?.[fieldName];
    if (!confidence) return null;
    
    const percentage = Math.round(confidence * 100);
    let variant = 'neutral';
    
    if (percentage >= 90) variant = 'success';
    else if (percentage >= 70) variant = 'warning';
    else variant = 'error';
    
    return (
      <Badge variant={variant} size="xs" className="ml-1">
        {percentage}%
      </Badge>
    );
  }, [ocrResult.field_confidence]);

  return (
    <div className="bg-white border border-neutral-200 rounded-md shadow-lg p-4 min-w-[600px]">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold text-neutral-900">
          Edycja danych OCR
        </h3>
        <div className="flex items-center gap-2">
          <Badge 
            variant={ocrResult.confidence_score >= 80 ? 'success' : 'warning'} 
            size="sm"
          >
            Pewność: {ocrResult.confidence_score?.toFixed(1)}%
          </Badge>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
        {/* Invoice Number */}
        <div>
          <div className="flex items-center mb-1">
            <label className="text-sm font-medium text-neutral-700">
              Numer faktury *
            </label>
            {getConfidenceBadge('invoice_number')}
          </div>
          <Input
            value={formData.invoice_number}
            onChange={(e) => handleFieldChange('invoice_number', e.target.value)}
            error={errors.invoice_number}
            size="sm"
            placeholder="np. FV/2025/001"
          />
        </div>

        {/* Invoice Date */}
        <div>
          <div className="flex items-center mb-1">
            <label className="text-sm font-medium text-neutral-700">
              Data wystawienia *
            </label>
            {getConfidenceBadge('invoice_date')}
          </div>
          <DatePicker
            value={formData.invoice_date}
            onChange={(value) => handleFieldChange('invoice_date', value)}
            error={errors.invoice_date}
            size="sm"
          />
        </div>

        {/* Supplier Name */}
        <div>
          <div className="flex items-center mb-1">
            <label className="text-sm font-medium text-neutral-700">
              Sprzedawca *
            </label>
            {getConfidenceBadge('supplier_name')}
          </div>
          <Input
            value={formData.supplier_name}
            onChange={(e) => handleFieldChange('supplier_name', e.target.value)}
            error={errors.supplier_name}
            size="sm"
            placeholder="Nazwa sprzedawcy"
          />
        </div>

        {/* Supplier NIP */}
        <div>
          <div className="flex items-center mb-1">
            <label className="text-sm font-medium text-neutral-700">
              NIP sprzedawcy
            </label>
            {getConfidenceBadge('supplier_nip')}
          </div>
          <NIPValidator
            value={formData.supplier_nip}
            onChange={(value) => handleFieldChange('supplier_nip', value)}
            size="sm"
            placeholder="123-456-78-90"
          />
        </div>

        {/* Buyer Name */}
        <div>
          <div className="flex items-center mb-1">
            <label className="text-sm font-medium text-neutral-700">
              Nabywca
            </label>
            {getConfidenceBadge('buyer_name')}
          </div>
          <Input
            value={formData.buyer_name}
            onChange={(e) => handleFieldChange('buyer_name', e.target.value)}
            size="sm"
            placeholder="Nazwa nabywcy"
          />
        </div>

        {/* Buyer NIP */}
        <div>
          <div className="flex items-center mb-1">
            <label className="text-sm font-medium text-neutral-700">
              NIP nabywcy
            </label>
            {getConfidenceBadge('buyer_nip')}
          </div>
          <NIPValidator
            value={formData.buyer_nip}
            onChange={(value) => handleFieldChange('buyer_nip', value)}
            size="sm"
            placeholder="123-456-78-90"
          />
        </div>

        {/* Total Amount */}
        <div>
          <div className="flex items-center mb-1">
            <label className="text-sm font-medium text-neutral-700">
              Kwota brutto *
            </label>
            {getConfidenceBadge('total_amount')}
          </div>
          <CurrencyInput
            value={formData.total_amount}
            onChange={(value) => handleFieldChange('total_amount', value)}
            currency={formData.currency}
            error={errors.total_amount}
            size="sm"
          />
        </div>

        {/* Net Amount */}
        <div>
          <div className="flex items-center mb-1">
            <label className="text-sm font-medium text-neutral-700">
              Kwota netto
            </label>
            {getConfidenceBadge('net_amount')}
          </div>
          <CurrencyInput
            value={formData.net_amount}
            onChange={(value) => handleFieldChange('net_amount', value)}
            currency={formData.currency}
            size="sm"
          />
        </div>
      </div>

      {/* Action Buttons */}
      <div className="flex justify-end gap-2 pt-4 border-t border-neutral-200">
        <Button
          variant="secondary"
          size="sm"
          onClick={onCancel}
          disabled={saving}
        >
          Anuluj
        </Button>
        <Button
          variant="primary"
          size="sm"
          onClick={handleSave}
          loading={saving}
          disabled={saving}
        >
          {saving ? 'Zapisywanie...' : 'Zapisz zmiany'}
        </Button>
      </div>

      {/* Validation Summary */}
      {Object.keys(errors).length > 0 && (
        <div className="mt-3 p-3 bg-error-50 border border-error-200 rounded-md">
          <div className="text-sm text-error-800">
            <div className="font-medium mb-1">Popraw następujące błędy:</div>
            <ul className="list-disc list-inside space-y-1">
              {Object.entries(errors).map(([field, error]) => (
                <li key={field}>
                  {field.replace(/_/g, ' ')}: {error}
                </li>
              ))}
            </ul>
          </div>
        </div>
      )}
    </div>
  );
};

export default OCRInlineEditor;