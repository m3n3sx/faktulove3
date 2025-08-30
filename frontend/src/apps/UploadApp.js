import React from 'react';
import { QueryClient, QueryClientProvider } from 'react-query';
import { Toaster } from 'react-hot-toast';
import UploadPage from '../pages/UploadPage';
import { DesignSystemProvider } from '../design-system';

// Create a query client for React Query
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: 3,
      staleTime: 5 * 60 * 1000, // 5 minutes
    },
  },
});

// Main Upload App component that wraps UploadPage with providers
const UploadApp = ({ 
  apiBaseUrl = '/api/v1',
  csrfToken,
  maxFileSize = 10,
  supportedTypes = {},
  recentUploads = []
}) => {
  // Set up axios defaults
  React.useEffect(() => {
    if (window.axios) {
      window.axios.defaults.baseURL = apiBaseUrl;
      window.axios.defaults.headers.common['X-CSRFToken'] = csrfToken;
      window.axios.defaults.headers.common['X-Requested-With'] = 'XMLHttpRequest';
    }
  }, [apiBaseUrl, csrfToken]);

  return (
    <DesignSystemProvider>
      <QueryClientProvider client={queryClient}>
        <div className="min-h-screen bg-gray-50">
          <UploadPage 
            maxFileSize={maxFileSize}
            supportedTypes={supportedTypes}
            recentUploads={recentUploads}
          />
          <Toaster 
            position="top-right"
            toastOptions={{
              duration: 4000,
              style: {
                background: '#363636',
                color: '#fff',
              },
              success: {
                style: {
                  background: '#10b981',
                },
              },
              error: {
                style: {
                  background: '#ef4444',
                },
              },
            }}
          />
        </div>
      </QueryClientProvider>
    </DesignSystemProvider>
  );
};

// Export for global access
if (typeof window !== 'undefined') {
  window.UploadApp = UploadApp;
}

export default UploadApp;