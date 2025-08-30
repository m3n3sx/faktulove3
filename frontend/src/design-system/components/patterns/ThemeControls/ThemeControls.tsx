import React from 'react';
import { useTheme } from '../../../providers/ThemeProvider';
import { Button } from '../../primitives/Button/Button';
import { Select } from '../../primitives/Select/Select';
import { Switch } from '../../primitives/Switch/Switch';
import { Card } from '../Card/Card';
import { cn } from '../../../utils/cn';

export interface ThemeControlsProps {
  className?: string;
  showAdvanced?: boolean;
  compact?: boolean;
}

export const ThemeControls: React.FC<ThemeControlsProps> = ({
  className,
  showAdvanced = false,
  compact = false,
}) => {
  const {
    config,
    setMode,
    setContrast,
    setReducedMotion,
    toggleMode,
    toggleContrast,
    isDark,
    isHighContrast,
  } = useTheme();

  const modeOptions = [
    { value: 'light', label: 'Jasny' },
    { value: 'dark', label: 'Ciemny' },
    { value: 'auto', label: 'Automatyczny' },
  ];

  const contrastOptions = [
    { value: 'normal', label: 'Normalny' },
    { value: 'high', label: 'Wysoki kontrast' },
  ];

  if (compact) {
    return (
      <div className={cn('flex items-center gap-2', className)}>
        <Button
          variant="ghost"
          size="sm"
          onClick={toggleMode}
          aria-label={`Przełącz motyw (obecnie: ${isDark ? 'ciemny' : 'jasny'})`}
          className="p-2"
        >
          {isDark ? '🌙' : '☀️'}
        </Button>
        
        {showAdvanced && (
          <Button
            variant="ghost"
            size="sm"
            onClick={toggleContrast}
            aria-label={`Przełącz kontrast (obecnie: ${isHighContrast ? 'wysoki' : 'normalny'})`}
            className="p-2"
          >
            {isHighContrast ? '🔆' : '🔅'}
          </Button>
        )}
      </div>
    );
  }

  return (
    <Card className={cn('p-6', className)}>
      <div className="space-y-6">
        <div>
          <h3 className="text-lg font-semibold text-text-primary mb-4">
            Ustawienia motywu
          </h3>
          <p className="text-sm text-text-secondary mb-6">
            Dostosuj wygląd aplikacji do swoich preferencji
          </p>
        </div>

        <div className="space-y-4">
          {/* Theme Mode */}
          <div className="space-y-2">
            <label className="block text-sm font-medium text-text-primary">
              Motyw kolorystyczny
            </label>
            <Select
              value={config.mode}
              onValueChange={(value) => setMode(value as any)}
              options={modeOptions}
              placeholder="Wybierz motyw"
            />
            <p className="text-xs text-text-muted">
              {config.mode === 'auto' 
                ? 'Automatycznie dostosowuje się do ustawień systemu'
                : config.mode === 'dark'
                ? 'Ciemny motyw dla lepszej pracy w słabym oświetleniu'
                : 'Jasny motyw dla lepszej czytelności w dzień'
              }
            </p>
          </div>

          {/* Contrast Mode */}
          <div className="space-y-2">
            <label className="block text-sm font-medium text-text-primary">
              Kontrast
            </label>
            <Select
              value={config.contrast}
              onValueChange={(value) => setContrast(value as any)}
              options={contrastOptions}
              placeholder="Wybierz kontrast"
            />
            <p className="text-xs text-text-muted">
              {config.contrast === 'high'
                ? 'Zwiększony kontrast dla lepszej dostępności'
                : 'Standardowy kontrast dla komfortowego użytkowania'
              }
            </p>
          </div>

          {/* Reduced Motion */}
          <div className="flex items-center justify-between">
            <div className="space-y-1">
              <label className="block text-sm font-medium text-text-primary">
                Ograniczone animacje
              </label>
              <p className="text-xs text-text-muted">
                Wyłącza animacje dla lepszej dostępności
              </p>
            </div>
            <Switch
              checked={config.reducedMotion}
              onCheckedChange={setReducedMotion}
              aria-label="Przełącz ograniczone animacje"
            />
          </div>

          {showAdvanced && (
            <>
              <hr className="border-border-default" />
              
              {/* Quick Actions */}
              <div className="space-y-3">
                <h4 className="text-sm font-medium text-text-primary">
                  Szybkie akcje
                </h4>
                
                <div className="flex flex-wrap gap-2">
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={toggleMode}
                  >
                    {isDark ? 'Przełącz na jasny' : 'Przełącz na ciemny'}
                  </Button>
                  
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={toggleContrast}
                  >
                    {isHighContrast ? 'Normalny kontrast' : 'Wysoki kontrast'}
                  </Button>
                  
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => setReducedMotion(!config.reducedMotion)}
                  >
                    {config.reducedMotion ? 'Włącz animacje' : 'Wyłącz animacje'}
                  </Button>
                </div>
              </div>

              {/* Theme Status */}
              <div className="space-y-2">
                <h4 className="text-sm font-medium text-text-primary">
                  Status motywu
                </h4>
                <div className="text-xs text-text-muted space-y-1">
                  <div>Aktualny motyw: {isDark ? 'Ciemny' : 'Jasny'}</div>
                  <div>Kontrast: {isHighContrast ? 'Wysoki' : 'Normalny'}</div>
                  <div>Animacje: {config.reducedMotion ? 'Wyłączone' : 'Włączone'}</div>
                </div>
              </div>
            </>
          )}
        </div>
      </div>
    </Card>
  );
};

export default ThemeControls;