import React from 'react';
import { cn } from '../../../utils/cn';
import { useThemeUtils } from '../../../providers/ThemeProvider';
import { Card } from '../../patterns/Card/Card';
import { Badge } from '../../primitives/Badge/Badge';
import { Typography } from '../../primitives/Typography/Typography';
import { Grid } from '../../layouts/Grid/Grid';
import { Stack } from '../../layouts/Stack/Stack';
import { InvoiceStatusBadge } from '../InvoiceStatusBadge/InvoiceStatusBadge';
import { ComplianceIndicator } from '../ComplianceIndicator/ComplianceIndicator';

export interface PolishBusinessThemeDemoProps {
  className?: string;
  testId?: string;
}

export const PolishBusinessThemeDemo: React.FC<PolishBusinessThemeDemoProps> = ({
  className,
  testId,
}) => {
  const {
    formatCurrency,
    formatDate,
    formatNIP,
    formatVATRate,
    getInvoiceStatusColor,
    getVATRateColor,
    getComplianceColor,
    isDark,
  } = useThemeUtils();

  const sampleInvoiceData = {
    number: 'FV/2025/001',
    amount: 1234.56,
    vatAmount: 284.95,
    netAmount: 949.61,
    issueDate: new Date('2025-01-15'),
    dueDate: new Date('2025-02-14'),
    nip: '1234567890',
    vatRate: 0.23,
  };

  const sampleComplianceRules = [
    {
      id: 'vat-rate',
      name: 'Stawka VAT',
      description: 'Sprawdzenie poprawności stawki VAT',
      status: 'compliant' as const,
    },
    {
      id: 'nip-validation',
      name: 'Walidacja NIP',
      description: 'Sprawdzenie poprawności numeru NIP',
      status: 'compliant' as const,
    },
    {
      id: 'amount-calculation',
      name: 'Kalkulacja kwot',
      description: 'Sprawdzenie poprawności obliczeń',
      status: 'warning' as const,
      details: 'Niewielka rozbieżność w zaokrągleniu',
    },
  ];

  return (
    <div className={cn('space-y-6', className)} data-testid={testId}>
      <div className="text-center">
        <Typography variant="heading-lg" className="mb-2">
          Polskie Motywy Biznesowe
        </Typography>
        <Typography variant="body-medium" color="muted">
          Demonstracja komponentów dostosowanych do polskich standardów biznesowych
        </Typography>
      </div>

      <Grid cols={2} gap="lg">
        {/* Invoice Status Demo */}
        <Card className="p-6">
          <Typography variant="heading-md" className="mb-4">
            Statusy Faktur
          </Typography>
          <Stack gap="sm">
            <InvoiceStatusBadge status="draft" />
            <InvoiceStatusBadge status="sent" />
            <InvoiceStatusBadge status="paid" />
            <InvoiceStatusBadge status="overdue" />
            <InvoiceStatusBadge status="cancelled" />
          </Stack>
        </Card>

        {/* Currency and Formatting Demo */}
        <Card className="p-6">
          <Typography variant="heading-md" className="mb-4">
            Formatowanie Polskie
          </Typography>
          <Stack gap="sm">
            <div className="flex justify-between">
              <span>Kwota netto:</span>
              <span 
                className="font-mono font-semibold"
                style={{ color: 'var(--color-text-primary)' }}
              >
                {formatCurrency(sampleInvoiceData.netAmount)}
              </span>
            </div>
            <div className="flex justify-between">
              <span>VAT ({formatVATRate(sampleInvoiceData.vatRate)}):</span>
              <span 
                className="font-mono font-semibold"
                style={{ color: getVATRateColor(sampleInvoiceData.vatRate) }}
              >
                {formatCurrency(sampleInvoiceData.vatAmount)}
              </span>
            </div>
            <div className="flex justify-between border-t pt-2">
              <span className="font-semibold">Kwota brutto:</span>
              <span 
                className="font-mono font-bold text-lg"
                style={{ color: 'var(--color-primary-600)' }}
              >
                {formatCurrency(sampleInvoiceData.amount)}
              </span>
            </div>
            <div className="flex justify-between text-sm text-text-muted">
              <span>Data wystawienia:</span>
              <span>{formatDate(sampleInvoiceData.issueDate)}</span>
            </div>
            <div className="flex justify-between text-sm text-text-muted">
              <span>NIP:</span>
              <span className="font-mono">{formatNIP(sampleInvoiceData.nip)}</span>
            </div>
          </Stack>
        </Card>

        {/* VAT Rates Demo */}
        <Card className="p-6">
          <Typography variant="heading-md" className="mb-4">
            Stawki VAT
          </Typography>
          <Stack gap="sm">
            {[0.23, 0.08, 0.05, 0, -1].map((rate) => (
              <div key={rate} className="flex items-center justify-between">
                <span>{formatVATRate(rate)}</span>
                <Badge
                  variant="outline"
                  style={{
                    borderColor: getVATRateColor(rate),
                    color: getVATRateColor(rate),
                  }}
                >
                  {rate === 0.23 ? 'Standardowa' : 
                   rate === 0.08 || rate === 0.05 ? 'Obniżona' :
                   rate === 0 ? 'Zerowa' : 'Zwolniona'}
                </Badge>
              </div>
            ))}
          </Stack>
        </Card>

        {/* Compliance Demo */}
        <Card className="p-6">
          <Typography variant="heading-md" className="mb-4">
            Zgodność z Przepisami
          </Typography>
          <ComplianceIndicator
            rules={sampleComplianceRules}
            showDetails
            size="sm"
          />
        </Card>
      </Grid>

      {/* Theme Information */}
      <Card className="p-6 bg-background-secondary">
        <Typography variant="heading-md" className="mb-4">
          Informacje o Motywie
        </Typography>
        <Grid cols={3} gap="md">
          <div className="text-center">
            <div 
              className="w-12 h-12 rounded-full mx-auto mb-2"
              style={{ backgroundColor: 'var(--color-primary-600)' }}
            />
            <Typography variant="body-small" color="muted">
              Kolor główny
            </Typography>
          </div>
          <div className="text-center">
            <div 
              className="w-12 h-12 rounded-full mx-auto mb-2"
              style={{ backgroundColor: 'var(--color-invoice-paid)' }}
            />
            <Typography variant="body-small" color="muted">
              Faktura opłacona
            </Typography>
          </div>
          <div className="text-center">
            <div 
              className="w-12 h-12 rounded-full mx-auto mb-2"
              style={{ backgroundColor: 'var(--color-invoice-overdue)' }}
            />
            <Typography variant="body-small" color="muted">
              Faktura przeterminowana
            </Typography>
          </div>
        </Grid>
        
        <div className="mt-4 p-4 bg-background-primary rounded-lg">
          <Typography variant="body-small" color="muted">
            Aktualny motyw: <strong>{isDark ? 'Ciemny' : 'Jasny'}</strong>
          </Typography>
          <Typography variant="body-small" color="muted" className="mt-1">
            Wszystkie kolory automatycznie dostosowują się do wybranego motywu
          </Typography>
        </div>
      </Card>
    </div>
  );
};

PolishBusinessThemeDemo.displayName = 'PolishBusinessThemeDemo';