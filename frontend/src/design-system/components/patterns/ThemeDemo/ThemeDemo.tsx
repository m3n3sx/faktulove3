import React from 'react';
import { useTheme, useThemeUtils } from '../../providers/ThemeProvider';
import { useUserPreferences, calculateAccessibilityScore, getPolishBusinessAccessibilityRecommendations } from '../../utils/userPreferences';
import { Button } from '../../components/primitives/Button/Button';
import { Card } from '../Card/Card';
import { cn } from '../../utils/cn';
import { Grid } from '../../layouts/Grid/Grid';

export interface ThemeDemoProps {
  className?: string;
  showSystemInfo?: boolean;
  showAccessibilityScore?: boolean;
}

export const ThemeDemo: React.FC<ThemeDemoProps> = ({
  className,
  showSystemInfo = true,
  showAccessibilityScore = true,
}) => {
  const { config, isDark, isHighContrast } = useTheme();
  const { getInvoiceStatusColor, getInvoiceStatusBackground } = useThemeUtils();
  const userPreferences = useUserPreferences();

  const accessibilityScore = showAccessibilityScore 
    ? calculateAccessibilityScore(config, userPreferences)
    : 0;

  const recommendations = showAccessibilityScore
    ? getPolishBusinessAccessibilityRecommendations(config, userPreferences)
    : [];

  return (
    <div className={cn('space-y-6', className)}>
      {/* Theme Status */}
      <Card className="p-6">
        <h3 className="text-lg font-semibold text-text-primary mb-4">
          Status motywu
        </h3>
        
        <div cols={2}>
          <div className="text-center">
            <div className="text-2xl mb-2">{isDark ? '🌙' : '☀️'}</div>
            <div className="text-sm font-medium text-text-primary">
              {isDark ? 'Ciemny' : 'Jasny'}
            </div>
            <div className="text-xs text-text-muted">
              Motyw: {config.mode}
            </div>
          </div>
          
          <div className="text-center">
            <div className="text-2xl mb-2">{isHighContrast ? '🔆' : '🔅'}</div>
            <div className="text-sm font-medium text-text-primary">
              {isHighContrast ? 'Wysoki' : 'Normalny'}
            </div>
            <div className="text-xs text-text-muted">
              Kontrast
            </div>
          </div>
          
          <div className="text-center">
            <div className="text-2xl mb-2">{config.reducedMotion ? '⏸️' : '▶️'}</div>
            <div className="text-sm font-medium text-text-primary">
              {config.reducedMotion ? 'Wyłączone' : 'Włączone'}
            </div>
            <div className="text-xs text-text-muted">
              Animacje
            </div>
          </div>
          
          {showAccessibilityScore && (
            <div className="text-center">
              <div className="text-2xl mb-2">
                {accessibilityScore >= 80 ? '✅' : accessibilityScore >= 60 ? '⚠️' : '❌'}
              </div>
              <div className="text-sm font-medium text-text-primary">
                {accessibilityScore}/100
              </div>
              <div className="text-xs text-text-muted">
                Dostępność
              </div>
            </div>
          )}
        </div>

        {showSystemInfo && (
          <div className="border-t border-border-default pt-4">
            <h4 className="text-sm font-medium text-text-primary mb-2">
              Preferencje systemowe
            </h4>
            <div className="text-xs text-text-muted space-y-1">
              <div>Schemat kolorów: {userPreferences.colorScheme}</div>
              <div>Kontrast: {userPreferences.contrast}</div>
              <div>Ograniczone animacje: {userPreferences.reducedMotion ? 'Tak' : 'Nie'}</div>
            </div>
          </div>
        )}
      </Card>

      {/* Color Palette Demo */}
      <Card className="p-6">
        <h3 className="text-lg font-semibold text-text-primary mb-4">
          Paleta kolorów
        </h3>
        
        <div cols={2}>
          {/* Primary Colors */}
          <div>
            <h4 className="text-sm font-medium text-text-primary mb-2">Główne</h4>
            <div className="space-y-2">
              <div className="h-8 bg-interactive rounded-md flex items-center justify-center text-white text-xs">
                Primary
              </div>
              <div className="h-8 bg-interactive-hover rounded-md flex items-center justify-center text-white text-xs">
                Hover
              </div>
              <div className="h-8 bg-interactive-active rounded-md flex items-center justify-center text-white text-xs">
                Active
              </div>
            </div>
          </div>

          {/* Status Colors */}
          <div>
            <h4 className="text-sm font-medium text-text-primary mb-2">Status</h4>
            <div className="space-y-2">
              <div className="h-8 bg-status-success rounded-md flex items-center justify-center text-white text-xs">
                Sukces
              </div>
              <div className="h-8 bg-status-warning rounded-md flex items-center justify-center text-white text-xs">
                Ostrzeżenie
              </div>
              <div className="h-8 bg-status-error rounded-md flex items-center justify-center text-white text-xs">
                Błąd
              </div>
            </div>
          </div>

          {/* Background Colors */}
          <div>
            <h4 className="text-sm font-medium text-text-primary mb-2">Tła</h4>
            <div className="space-y-2">
              <div className="h-8 bg-background-primary border border-border-default rounded-md flex items-center justify-center text-text-primary text-xs">
                Główne
              </div>
              <div className="h-8 bg-background-secondary border border-border-default rounded-md flex items-center justify-center text-text-primary text-xs">
                Drugorzędne
              </div>
              <div className="h-8 bg-background-muted border border-border-default rounded-md flex items-center justify-center text-text-primary text-xs">
                Wyciszone
              </div>
            </div>
          </div>

          {/* Text Colors */}
          <div>
            <h4 className="text-sm font-medium text-text-primary mb-2">Tekst</h4>
            <div className="space-y-2">
              <div className="h-8 bg-background-secondary rounded-md flex items-center justify-center text-text-primary text-xs">
                Główny
              </div>
              <div className="h-8 bg-background-secondary rounded-md flex items-center justify-center text-text-secondary text-xs">
                Drugorzędny
              </div>
              <div className="h-8 bg-background-secondary rounded-md flex items-center justify-center text-text-muted text-xs">
                Wyciszony
              </div>
            </div>
          </div>
        </div>
      </Card>

      {/* Polish Business Components Demo */}
      <Card className="p-6">
        <h3 className="text-lg font-semibold text-text-primary mb-4">
          Komponenty biznesowe
        </h3>
        
        {/* Invoice Status Examples */}
        <div className="mb-6">
          <h4 className="text-sm font-medium text-text-primary mb-3">
            Statusy faktur
          </h4>
          <div className="flex flex-wrap gap-2">
            {(['draft', 'sent', 'paid', 'overdue', 'cancelled'] as const).map(status => (
              <div
                key={status}
                className="px-3 py-1 rounded-md-full text-sm font-medium"
                style={{
                  color: getInvoiceStatusColor(status),
                  backgroundColor: getInvoiceStatusBackground(status),
                }}
              >
                {status === 'draft' && 'Szkic'}
                {status === 'sent' && 'Wysłana'}
                {status === 'paid' && 'Opłacona'}
                {status === 'overdue' && 'Przeterminowana'}
                {status === 'cancelled' && 'Anulowana'}
              </div>
            ))}
          </div>
        </div>

        {/* Currency Examples */}
        <div className="mb-6">
          <h4 className="text-sm font-medium text-text-primary mb-3">
            Formatowanie walut
          </h4>
          <div className="space-y-2">
            <div className="flex justify-between items-center">
              <span className="text-text-secondary">Kwota dodatnia:</span>
              <span className="font-mono font-semibold text-currency-positive">+1 234,56 zł</span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-text-secondary">Kwota ujemna:</span>
              <span className="font-mono font-semibold text-currency-negative">-567,89 zł</span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-text-secondary">Kwota zerowa:</span>
              <span className="font-mono font-semibold text-currency-neutral">0,00 zł</span>
            </div>
          </div>
        </div>

        {/* VAT Rates */}
        <div className="mb-6">
          <h4 className="text-sm font-medium text-text-primary mb-3">
            Stawki VAT
          </h4>
          <div cols={2}>
            <div className="text-center p-2 bg-background-secondary rounded-md">
              <div className="text-vat-standard font-semibold">23%</div>
              <div className="text-xs text-text-muted">Standardowa</div>
            </div>
            <div className="text-center p-2 bg-background-secondary rounded-md">
              <div className="text-vat-reduced font-semibold">8%</div>
              <div className="text-xs text-text-muted">Obniżona</div>
            </div>
            <div className="text-center p-2 bg-background-secondary rounded-md">
              <div className="text-vat-zero font-semibold">0%</div>
              <div className="text-xs text-text-muted">Zerowa</div>
            </div>
            <div className="text-center p-2 bg-background-secondary rounded-md">
              <div className="text-vat-exempt font-semibold">zw.</div>
              <div className="text-xs text-text-muted">Zwolniona</div>
            </div>
          </div>
        </div>

        {/* Form Validation States */}
        <div>
          <h4 className="text-sm font-medium text-text-primary mb-3">
            Stany walidacji
          </h4>
          <div className="space-y-3">
            <div className="p-3 bg-form-valid-background border border-status-success-border rounded-md">
              <div className="text-form-valid font-medium">✓ Dane poprawne</div>
              <div className="text-xs text-text-muted">NIP został zweryfikowany pomyślnie</div>
            </div>
            <div className="p-3 bg-form-invalid-background border border-status-error-border rounded-md">
              <div className="text-form-invalid font-medium">✗ Błąd walidacji</div>
              <div className="text-xs text-text-muted">Nieprawidłowy format numeru NIP</div>
            </div>
            <div className="p-3 bg-form-pending-background border border-status-warning-border rounded-md">
              <div className="text-form-pending font-medium">⏳ Weryfikacja w toku</div>
              <div className="text-xs text-text-muted">Sprawdzanie danych w bazie GUS...</div>
            </div>
          </div>
        </div>
      </Card>

      {/* Interactive Elements Demo */}
      <Card className="p-6">
        <h3 className="text-lg font-semibold text-text-primary mb-4">
          Elementy interaktywne
        </h3>
        
        <div className="space-y-4">
          <div className="flex flex-wrap gap-2">
            <Button variant="primary">Przycisk główny</Button>
            <Button variant="secondary">Przycisk drugorzędny</Button>
            <Button variant="ghost">Przycisk ghost</Button>
            <Button variant="danger">Przycisk niebezpieczny</Button>
          </div>
          
          <div className="flex flex-wrap gap-2">
            <Button variant="primary" disabled>Wyłączony</Button>
            <Button variant="secondary" disabled>Wyłączony</Button>
            <Button variant="ghost" disabled>Wyłączony</Button>
          </div>
        </div>
      </Card>

      {/* Accessibility Recommendations */}
      {showAccessibilityScore && recommendations.length > 0 && (
        <Card className="p-6">
          <h3 className="text-lg font-semibold text-text-primary mb-4">
            Rekomendacje dostępności
          </h3>
          
          <div className="space-y-2">
            {recommendations.map((recommendation, index) => (
              <div key={index} className="flex items-start gap-2">
                <span className="text-status-info mt-0.5">💡</span>
                <span className="text-sm text-text-secondary">{recommendation}</span>
              </div>
            ))}
          </div>
        </Card>
      )}
    </div>
  );
};

export default ThemeDemo;