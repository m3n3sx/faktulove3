import React, { useState } from 'react';
import { 
  Settings, 
  Save, 
  RefreshCw, 
  Zap, 
  Shield, 
  Database,
  Cloud,
  Bell,
  User,
  Key
} from 'lucide-react';
import { Button, Grid, Stack, Select, Input, Textarea, Checkbox, Form, FormField } from '../design-system';

const SettingsPage = () => {
  const [settings, setSettings] = useState({
    // OCR Settings
    ocr: {
      confidence_threshold: 85,
      auto_create_invoices: true,
      manual_review_threshold: 90,
      processing_timeout: 30,
      max_file_size: 10,
      supported_formats: ['pdf', 'jpg', 'jpeg', 'png', 'tiff', 'tif']
    },
    // System Settings
    system: {
      auto_cleanup_days: 90,
      backup_enabled: true,
      backup_frequency: 'daily',
      log_level: 'info',
      debug_mode: false
    },
    // Notification Settings
    notifications: {
      email_notifications: true,
      processing_complete: true,
      processing_failed: true,
      low_confidence_alert: true,
      daily_summary: false
    },
    // Security Settings
    security: {
      session_timeout: 60,
      require_2fa: false,
      ip_whitelist: '',
      audit_logging: true
    }
  });

  const [isSaving, setIsSaving] = useState(false);
  const [activeTab, setActiveTab] = useState('ocr');

  const handleSettingChange = (category, key, value) => {
    setSettings(prev => ({
      ...prev,
      [category]: {
        ...prev[category],
        [key]: value
      }
    }));
  };

  const handleSave = async (formData) => {
    setIsSaving(true);
    try {
      // Simulate API call
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      // Update settings with form data
      setSettings(formData);
      
      // In a real app, this would save to backend
      console.log('Settings saved:', formData);
    } catch (error) {
      console.error('Failed to save settings:', error);
    } finally {
      setIsSaving(false);
    }
  };

  const handleReset = () => {
    // Reset to default settings
    setSettings({
      ocr: {
        confidence_threshold: 85,
        auto_create_invoices: true,
        manual_review_threshold: 90,
        processing_timeout: 30,
        max_file_size: 10,
        supported_formats: ['pdf', 'jpg', 'jpeg', 'png', 'tiff', 'tif']
      },
      system: {
        auto_cleanup_days: 90,
        backup_enabled: true,
        backup_frequency: 'daily',
        log_level: 'info',
        debug_mode: false
      },
      notifications: {
        email_notifications: true,
        processing_complete: true,
        processing_failed: true,
        low_confidence_alert: true,
        daily_summary: false
      },
      security: {
        session_timeout: 60,
        require_2fa: false,
        ip_whitelist: '',
        audit_logging: true
      }
    });
  };

  const tabs = [
    { id: 'ocr', name: 'OCR Settings', icon: Zap },
    { id: 'system', name: 'System', icon: Settings },
    { id: 'notifications', name: 'Notifications', icon: Bell },
    { id: 'security', name: 'Security', icon: Shield }
  ];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Settings</h1>
        <p className="mt-2 text-gray-600">
          Configure OCR processing, system preferences, and security settings.
        </p>
      </div>

      {/* Tabs */}
      <div className="border-b border-gray-200">
        <nav className="-mb-px flex space-x-8">
          {tabs.map((tab) => {
            const Icon = tab.icon;
            return (
              <Button
                key={tab.id}
                variant={activeTab === tab.id ? 'primary' : 'ghost'}
                size="sm"
                onClick={() => setActiveTab(tab.id)}
                startIcon={<Icon className="h-4 w-4" />}
                className={`
                  py-2 px-1 border-b-2 font-medium text-sm
                  ${activeTab === tab.id
                    ? 'border-primary-500 text-primary-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                  }
                `}
              >
                {tab.name}
              </Button>
            );
          })}
        </nav>
      </div>

      {/* Settings Content */}
      <div className="bg-white rounded-md-lg shadow-sm">
        {/* OCR Settings */}
        {activeTab === 'ocr' && (
          <div className="p-6 space-y-6">
            <div>
              <h3 className="text-lg font-medium text-gray-900 mb-4">OCR Processing Settings</h3>
              
              <Stack gap="lg">
                <Grid cols={2} gap="md">
                  <div>
                    <Input
                      type="range"
                      label="Confidence Threshold (%)"
                      min="50"
                      max="100"
                      value={settings.ocr.confidence_threshold}
                      onChange={(e) => handleSettingChange('ocr', 'confidence_threshold', parseInt(e.target.value))}
                      helperText={`Current: ${settings.ocr.confidence_threshold}% - Documents below this confidence will require manual review`}
                      error={settings.ocr.confidence_threshold < 50 || settings.ocr.confidence_threshold > 100}
                      errorMessage={settings.ocr.confidence_threshold < 50 || settings.ocr.confidence_threshold > 100 ? 'Wartość musi być między 50 a 100' : undefined}
                    />
                  </div>

                  <div>
                    <Input
                      type="range"
                      label="Manual Review Threshold (%)"
                      min="70"
                      max="100"
                      value={settings.ocr.manual_review_threshold}
                      onChange={(e) => handleSettingChange('ocr', 'manual_review_threshold', parseInt(e.target.value))}
                      helperText={`Current: ${settings.ocr.manual_review_threshold}%`}
                      error={settings.ocr.manual_review_threshold < 70 || settings.ocr.manual_review_threshold > 100}
                      errorMessage={settings.ocr.manual_review_threshold < 70 || settings.ocr.manual_review_threshold > 100 ? 'Wartość musi być między 70 a 100' : undefined}
                    />
                  </div>

                  <div>
                    <Input
                      type="number"
                      label="Processing Timeout (seconds)"
                      min="10"
                      max="120"
                      value={settings.ocr.processing_timeout}
                      onChange={(e) => handleSettingChange('ocr', 'processing_timeout', parseInt(e.target.value))}
                      error={settings.ocr.processing_timeout < 10 || settings.ocr.processing_timeout > 120}
                      errorMessage={settings.ocr.processing_timeout < 10 || settings.ocr.processing_timeout > 120 ? 'Wartość musi być między 10 a 120 sekund' : undefined}
                    />
                  </div>

                  <div>
                    <Input
                      type="number"
                      label="Maximum File Size (MB)"
                      min="1"
                      max="50"
                      value={settings.ocr.max_file_size}
                      onChange={(e) => handleSettingChange('ocr', 'max_file_size', parseInt(e.target.value))}
                      error={settings.ocr.max_file_size < 1 || settings.ocr.max_file_size > 50}
                      errorMessage={settings.ocr.max_file_size < 1 || settings.ocr.max_file_size > 50 ? 'Wartość musi być między 1 a 50 MB' : undefined}
                    />
                  </div>
                </Grid>

                <Checkbox
                  checked={settings.ocr.auto_create_invoices}
                  onChange={(checked) => handleSettingChange('ocr', 'auto_create_invoices', checked)}
                  label="Automatically create invoices from high-confidence OCR results"
                />
              </Stack>
            </div>
          </div>
        )}

        {/* System Settings */}
        {activeTab === 'system' && (
          <div className="p-6 space-y-6">
            <div>
              <h3 className="text-lg font-medium text-gray-900 mb-4">System Configuration</h3>
              
              <Stack gap="lg">
                <Grid cols={2} gap="md">
                  <div>
                    <Input
                      type="number"
                      label="Auto Cleanup (days)"
                      min="30"
                      max="365"
                      value={settings.system.auto_cleanup_days}
                      onChange={(e) => handleSettingChange('system', 'auto_cleanup_days', parseInt(e.target.value))}
                      helperText="Automatically delete old documents after this many days"
                      error={settings.system.auto_cleanup_days < 30 || settings.system.auto_cleanup_days > 365}
                      errorMessage={settings.system.auto_cleanup_days < 30 || settings.system.auto_cleanup_days > 365 ? 'Wartość musi być między 30 a 365 dni' : undefined}
                    />
                  </div>

                  <div>
                    <Select
                      label="Backup Frequency"
                      value={settings.system.backup_frequency}
                      onChange={(value) => handleSettingChange('system', 'backup_frequency', value)}
                      options={[
                        { value: 'daily', label: 'Codziennie' },
                        { value: 'weekly', label: 'Tygodniowo' },
                        { value: 'monthly', label: 'Miesięcznie' }
                      ]}
                    />
                  </div>

                  <div>
                    <Select
                      label="Log Level"
                      value={settings.system.log_level}
                      onChange={(value) => handleSettingChange('system', 'log_level', value)}
                      options={[
                        { value: 'debug', label: 'Debug' },
                        { value: 'info', label: 'Info' },
                        { value: 'warning', label: 'Ostrzeżenia' },
                        { value: 'error', label: 'Błędy' }
                      ]}
                    />
                  </div>
                </Grid>

                <Stack gap="md">
                  <Checkbox
                    checked={settings.system.backup_enabled}
                    onChange={(checked) => handleSettingChange('system', 'backup_enabled', checked)}
                    label="Włącz automatyczne kopie zapasowe"
                  />

                  <Checkbox
                    checked={settings.system.debug_mode}
                    onChange={(checked) => handleSettingChange('system', 'debug_mode', checked)}
                    label="Włącz tryb debugowania"
                  />
                </Stack>
              </Stack>
            </div>
          </div>
        )}

        {/* Notification Settings */}
        {activeTab === 'notifications' && (
          <div className="p-6 space-y-6">
            <div>
              <h3 className="text-lg font-medium text-gray-900 mb-4">Preferencje powiadomień</h3>
              
              <Stack gap="md">
                <Checkbox
                  checked={settings.notifications.email_notifications}
                  onChange={(checked) => handleSettingChange('notifications', 'email_notifications', checked)}
                  label="Włącz powiadomienia e-mail"
                />

                <Checkbox
                  checked={settings.notifications.processing_complete}
                  onChange={(checked) => handleSettingChange('notifications', 'processing_complete', checked)}
                  label="Powiadom o zakończeniu przetwarzania"
                />

                <Checkbox
                  checked={settings.notifications.processing_failed}
                  onChange={(checked) => handleSettingChange('notifications', 'processing_failed', checked)}
                  label="Powiadom o błędach przetwarzania"
                />

                <Checkbox
                  checked={settings.notifications.low_confidence_alert}
                  onChange={(checked) => handleSettingChange('notifications', 'low_confidence_alert', checked)}
                  label="Ostrzeż o niskiej pewności wyników"
                />

                <Checkbox
                  checked={settings.notifications.daily_summary}
                  onChange={(checked) => handleSettingChange('notifications', 'daily_summary', checked)}
                  label="Wysyłaj dzienne raporty podsumowujące"
                />
              </Stack>
            </div>
          </div>
        )}

        {/* Security Settings */}
        {activeTab === 'security' && (
          <div className="p-6 space-y-6">
            <div>
              <h3 className="text-lg font-medium text-gray-900 mb-4">Konfiguracja bezpieczeństwa</h3>
              
              <Stack gap="lg">
                <Grid cols={2} gap="md">
                  <div>
                    <Input
                      type="number"
                      label="Timeout sesji (minuty)"
                      min="15"
                      max="480"
                      value={settings.security.session_timeout}
                      onChange={(e) => handleSettingChange('security', 'session_timeout', parseInt(e.target.value))}
                      error={settings.security.session_timeout < 15 || settings.security.session_timeout > 480}
                      errorMessage={settings.security.session_timeout < 15 || settings.security.session_timeout > 480 ? 'Wartość musi być między 15 a 480 minut' : undefined}
                    />
                  </div>

                  <div>
                    <Textarea
                      label="Lista dozwolonych IP"
                      value={settings.security.ip_whitelist}
                      onChange={(e) => handleSettingChange('security', 'ip_whitelist', e.target.value)}
                      placeholder="Wprowadź adresy IP (jeden na linię)"
                      rows={3}
                      helperText="Pozostaw puste aby zezwolić na wszystkie IP"
                    />
                  </div>
                </Grid>

                <Stack gap="md">
                  <Checkbox
                    checked={settings.security.require_2fa}
                    onChange={(checked) => handleSettingChange('security', 'require_2fa', checked)}
                    label="Wymagaj uwierzytelniania dwuskładnikowego"
                  />

                  <Checkbox
                    checked={settings.security.audit_logging}
                    onChange={(checked) => handleSettingChange('security', 'audit_logging', checked)}
                    label="Włącz logowanie audytu"
                  />
                </Stack>
              </Stack>
            </div>
          </div>
        )}

        {/* Action Buttons */}
        <div className="px-6 py-4 bg-gray-50 border-t border-gray-200 flex justify-between items-center">
          <Button
            onClick={handleReset}
            variant="secondary"
            startIcon={<RefreshCw className="h-4 w-4" />}
          >
            Przywróć domyślne
          </Button>
          
          <Button
            onClick={() => handleSave(settings)}
            disabled={isSaving}
            variant="primary"
            loading={isSaving}
            startIcon={isSaving ? undefined : <Save className="h-4 w-4" />}
          >
            {isSaving ? 'Zapisywanie...' : 'Zapisz ustawienia'}
          </Button>
        </div>
      </div>
    </div>
  );
};

export default SettingsPage;
