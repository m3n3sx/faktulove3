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

  const handleSave = async () => {
    setIsSaving(true);
    // Simulate API call
    await new Promise(resolve => setTimeout(resolve, 1000));
    setIsSaving(false);
    // In a real app, this would save to backend
    console.log('Settings saved:', settings);
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
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`
                  py-2 px-1 border-b-2 font-medium text-sm flex items-center space-x-2
                  ${activeTab === tab.id
                    ? 'border-primary-500 text-primary-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                  }
                `}
              >
                <Icon className="h-4 w-4" />
                <span>{tab.name}</span>
              </button>
            );
          })}
        </nav>
      </div>

      {/* Settings Content */}
      <div className="bg-white rounded-lg shadow">
        {/* OCR Settings */}
        {activeTab === 'ocr' && (
          <div className="p-6 space-y-6">
            <div>
              <h3 className="text-lg font-medium text-gray-900 mb-4">OCR Processing Settings</h3>
              
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Confidence Threshold (%)
                  </label>
                  <input
                    type="range"
                    min="50"
                    max="100"
                    value={settings.ocr.confidence_threshold}
                    onChange={(e) => handleSettingChange('ocr', 'confidence_threshold', parseInt(e.target.value))}
                    className="w-full"
                  />
                  <div className="flex justify-between text-xs text-gray-500 mt-1">
                    <span>50%</span>
                    <span className="font-medium">{settings.ocr.confidence_threshold}%</span>
                    <span>100%</span>
                  </div>
                  <p className="text-xs text-gray-500 mt-1">
                    Documents below this confidence will require manual review
                  </p>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Manual Review Threshold (%)
                  </label>
                  <input
                    type="range"
                    min="70"
                    max="100"
                    value={settings.ocr.manual_review_threshold}
                    onChange={(e) => handleSettingChange('ocr', 'manual_review_threshold', parseInt(e.target.value))}
                    className="w-full"
                  />
                  <div className="flex justify-between text-xs text-gray-500 mt-1">
                    <span>70%</span>
                    <span className="font-medium">{settings.ocr.manual_review_threshold}%</span>
                    <span>100%</span>
                  </div>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Processing Timeout (seconds)
                  </label>
                  <input
                    type="number"
                    min="10"
                    max="120"
                    value={settings.ocr.processing_timeout}
                    onChange={(e) => handleSettingChange('ocr', 'processing_timeout', parseInt(e.target.value))}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-primary-500 focus:border-primary-500"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Maximum File Size (MB)
                  </label>
                  <input
                    type="number"
                    min="1"
                    max="50"
                    value={settings.ocr.max_file_size}
                    onChange={(e) => handleSettingChange('ocr', 'max_file_size', parseInt(e.target.value))}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-primary-500 focus:border-primary-500"
                  />
                </div>
              </div>

              <div className="mt-6">
                <label className="flex items-center">
                  <input
                    type="checkbox"
                    checked={settings.ocr.auto_create_invoices}
                    onChange={(e) => handleSettingChange('ocr', 'auto_create_invoices', e.target.checked)}
                    className="h-4 w-4 text-primary-600 focus:ring-primary-500 border-gray-300 rounded"
                  />
                  <span className="ml-2 text-sm text-gray-700">
                    Automatically create invoices from high-confidence OCR results
                  </span>
                </label>
              </div>
            </div>
          </div>
        )}

        {/* System Settings */}
        {activeTab === 'system' && (
          <div className="p-6 space-y-6">
            <div>
              <h3 className="text-lg font-medium text-gray-900 mb-4">System Configuration</h3>
              
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Auto Cleanup (days)
                  </label>
                  <input
                    type="number"
                    min="30"
                    max="365"
                    value={settings.system.auto_cleanup_days}
                    onChange={(e) => handleSettingChange('system', 'auto_cleanup_days', parseInt(e.target.value))}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-primary-500 focus:border-primary-500"
                  />
                  <p className="text-xs text-gray-500 mt-1">
                    Automatically delete old documents after this many days
                  </p>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Backup Frequency
                  </label>
                  <select
                    value={settings.system.backup_frequency}
                    onChange={(e) => handleSettingChange('system', 'backup_frequency', e.target.value)}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-primary-500 focus:border-primary-500"
                  >
                    <option value="daily">Daily</option>
                    <option value="weekly">Weekly</option>
                    <option value="monthly">Monthly</option>
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Log Level
                  </label>
                  <select
                    value={settings.system.log_level}
                    onChange={(e) => handleSettingChange('system', 'log_level', e.target.value)}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-primary-500 focus:border-primary-500"
                  >
                    <option value="debug">Debug</option>
                    <option value="info">Info</option>
                    <option value="warning">Warning</option>
                    <option value="error">Error</option>
                  </select>
                </div>
              </div>

              <div className="mt-6 space-y-4">
                <label className="flex items-center">
                  <input
                    type="checkbox"
                    checked={settings.system.backup_enabled}
                    onChange={(e) => handleSettingChange('system', 'backup_enabled', e.target.checked)}
                    className="h-4 w-4 text-primary-600 focus:ring-primary-500 border-gray-300 rounded"
                  />
                  <span className="ml-2 text-sm text-gray-700">Enable automatic backups</span>
                </label>

                <label className="flex items-center">
                  <input
                    type="checkbox"
                    checked={settings.system.debug_mode}
                    onChange={(e) => handleSettingChange('system', 'debug_mode', e.target.checked)}
                    className="h-4 w-4 text-primary-600 focus:ring-primary-500 border-gray-300 rounded"
                  />
                  <span className="ml-2 text-sm text-gray-700">Enable debug mode</span>
                </label>
              </div>
            </div>
          </div>
        )}

        {/* Notification Settings */}
        {activeTab === 'notifications' && (
          <div className="p-6 space-y-6">
            <div>
              <h3 className="text-lg font-medium text-gray-900 mb-4">Notification Preferences</h3>
              
              <div className="space-y-4">
                <label className="flex items-center">
                  <input
                    type="checkbox"
                    checked={settings.notifications.email_notifications}
                    onChange={(e) => handleSettingChange('notifications', 'email_notifications', e.target.checked)}
                    className="h-4 w-4 text-primary-600 focus:ring-primary-500 border-gray-300 rounded"
                  />
                  <span className="ml-2 text-sm text-gray-700">Enable email notifications</span>
                </label>

                <label className="flex items-center">
                  <input
                    type="checkbox"
                    checked={settings.notifications.processing_complete}
                    onChange={(e) => handleSettingChange('notifications', 'processing_complete', e.target.checked)}
                    className="h-4 w-4 text-primary-600 focus:ring-primary-500 border-gray-300 rounded"
                  />
                  <span className="ml-2 text-sm text-gray-700">Notify when processing completes</span>
                </label>

                <label className="flex items-center">
                  <input
                    type="checkbox"
                    checked={settings.notifications.processing_failed}
                    onChange={(e) => handleSettingChange('notifications', 'processing_failed', e.target.checked)}
                    className="h-4 w-4 text-primary-600 focus:ring-primary-500 border-gray-300 rounded"
                  />
                  <span className="ml-2 text-sm text-gray-700">Notify when processing fails</span>
                </label>

                <label className="flex items-center">
                  <input
                    type="checkbox"
                    checked={settings.notifications.low_confidence_alert}
                    onChange={(e) => handleSettingChange('notifications', 'low_confidence_alert', e.target.checked)}
                    className="h-4 w-4 text-primary-600 focus:ring-primary-500 border-gray-300 rounded"
                  />
                  <span className="ml-2 text-sm text-gray-700">Alert for low confidence results</span>
                </label>

                <label className="flex items-center">
                  <input
                    type="checkbox"
                    checked={settings.notifications.daily_summary}
                    onChange={(e) => handleSettingChange('notifications', 'daily_summary', e.target.checked)}
                    className="h-4 w-4 text-primary-600 focus:ring-primary-500 border-gray-300 rounded"
                  />
                  <span className="ml-2 text-sm text-gray-700">Send daily summary reports</span>
                </label>
              </div>
            </div>
          </div>
        )}

        {/* Security Settings */}
        {activeTab === 'security' && (
          <div className="p-6 space-y-6">
            <div>
              <h3 className="text-lg font-medium text-gray-900 mb-4">Security Configuration</h3>
              
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Session Timeout (minutes)
                  </label>
                  <input
                    type="number"
                    min="15"
                    max="480"
                    value={settings.security.session_timeout}
                    onChange={(e) => handleSettingChange('security', 'session_timeout', parseInt(e.target.value))}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-primary-500 focus:border-primary-500"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    IP Whitelist
                  </label>
                  <textarea
                    value={settings.security.ip_whitelist}
                    onChange={(e) => handleSettingChange('security', 'ip_whitelist', e.target.value)}
                    placeholder="Enter IP addresses (one per line)"
                    rows={3}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-primary-500 focus:border-primary-500"
                  />
                  <p className="text-xs text-gray-500 mt-1">
                    Leave empty to allow all IPs
                  </p>
                </div>
              </div>

              <div className="mt-6 space-y-4">
                <label className="flex items-center">
                  <input
                    type="checkbox"
                    checked={settings.security.require_2fa}
                    onChange={(e) => handleSettingChange('security', 'require_2fa', e.target.checked)}
                    className="h-4 w-4 text-primary-600 focus:ring-primary-500 border-gray-300 rounded"
                  />
                  <span className="ml-2 text-sm text-gray-700">Require two-factor authentication</span>
                </label>

                <label className="flex items-center">
                  <input
                    type="checkbox"
                    checked={settings.security.audit_logging}
                    onChange={(e) => handleSettingChange('security', 'audit_logging', e.target.checked)}
                    className="h-4 w-4 text-primary-600 focus:ring-primary-500 border-gray-300 rounded"
                  />
                  <span className="ml-2 text-sm text-gray-700">Enable audit logging</span>
                </label>
              </div>
            </div>
          </div>
        )}

        {/* Action Buttons */}
        <div className="px-6 py-4 bg-gray-50 border-t border-gray-200 flex justify-between">
          <button
            onClick={handleReset}
            className="flex items-center px-4 py-2 border border-gray-300 rounded-md text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500"
          >
            <RefreshCw className="h-4 w-4 mr-2" />
            Reset to Defaults
          </button>
          
          <button
            onClick={handleSave}
            disabled={isSaving}
            className="flex items-center px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-primary-600 hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500 disabled:opacity-50"
          >
            {isSaving ? (
              <>
                <RefreshCw className="h-4 w-4 mr-2 animate-spin" />
                Saving...
              </>
            ) : (
              <>
                <Save className="h-4 w-4 mr-2" />
                Save Settings
              </>
            )}
          </button>
        </div>
      </div>
    </div>
  );
};

export default SettingsPage;
