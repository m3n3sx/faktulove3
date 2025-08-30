import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from 'react-query';
import { Toaster } from 'react-hot-toast';

// Design System
import { ThemeProvider, DesignSystemProvider } from './design-system';
import { DesignSystemContextProvider } from './design-system/context/DesignSystemContext';

// Components
import Layout from './components/Layout';
import Dashboard from './pages/Dashboard';
import UploadPage from './pages/UploadPage';
import DocumentsPage from './pages/DocumentsPage';
import StatisticsPage from './pages/StatisticsPage';
import SettingsPage from './pages/SettingsPage';

// Create a client
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: 1,
      refetchOnWindowFocus: false,
      staleTime: 5 * 60 * 1000, // 5 minutes
    },
  },
});

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <ThemeProvider defaultMode="auto" defaultContrast="normal">
        <DesignSystemContextProvider>
          <DesignSystemProvider>
            <Router>
              <div className="min-h-screen bg-background-primary text-text-primary polish-business-app design-system-app">
                <Layout>
                  <Routes>
                    <Route path="/" element={<Dashboard />} />
                    <Route path="/upload" element={<UploadPage />} />
                    <Route path="/documents" element={<DocumentsPage />} />
                    <Route path="/statistics" element={<StatisticsPage />} />
                    <Route path="/settings" element={<SettingsPage />} />
                  </Routes>
                </Layout>
                
                {/* Toast notifications */}
                <Toaster
                  position="top-right"
                  toastOptions={{
                    duration: 4000,
                    style: {
                      background: 'var(--color-background-inverse)',
                      color: 'var(--color-text-inverse)',
                      fontFamily: 'var(--font-family-sans)',
                      fontSize: 'var(--font-size-sm)',
                      borderRadius: 'var(--border-radius-md)',
                      boxShadow: 'var(--shadow-lg)',
                    },
                    success: {
                      duration: 3000,
                      iconTheme: {
                        primary: 'var(--color-status-success)',
                        secondary: 'var(--color-text-inverse)',
                      },
                    },
                    error: {
                      duration: 5000,
                      iconTheme: {
                        primary: 'var(--color-status-error)',
                        secondary: 'var(--color-text-inverse)',
                      },
                    },
                  }}
                />
              </div>
            </Router>
          </DesignSystemProvider>
        </DesignSystemContextProvider>
      </ThemeProvider>
    </QueryClientProvider>
  );
}

export default App;
