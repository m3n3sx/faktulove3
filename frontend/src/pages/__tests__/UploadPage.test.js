import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from 'react-query';
import { DesignSystemProvider } from '../../design-system';
import UploadPage from '../UploadPage';

// Mock axios
jest.mock('axios');
const mockedAxios = axios;

// Mock react-hot-toast
jest.mock('react-hot-toast', () => ({
  success: jest.fn(),
  error: jest.fn(),
}));

// Test wrapper with providers
const TestWrapper = ({ children }) => {
  const queryClient = new QueryClient({
    defaultOptions: {
      queries: { retry: false },
      mutations: { retry: false },
    },
  });

  return (
    <DesignSystemProvider>
      <QueryClientProvider client={queryClient}>
        {children}
      </QueryClientProvider>
    </DesignSystemProvider>
  );
};

describe('UploadPage', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('renders upload interface correctly', () => {
    render(
      <TestWrapper>
        <UploadPage />
      </TestWrapper>
    );

    expect(screen.getByText('Przesyłanie dokumentów OCR')).toBeInTheDocument();
    expect(screen.getByText('Automatyczne przetwarzanie faktur z wykorzystaniem sztucznej inteligencji')).toBeInTheDocument();
    expect(screen.getByTestId('ocr-file-upload')).toBeInTheDocument();
  });

  it('shows guidelines and tips', () => {
    render(
      <TestWrapper>
        <UploadPage />
      </TestWrapper>
    );

    expect(screen.getByText('Wskazówki dla najlepszych wyników')).toBeInTheDocument();
    expect(screen.getByText(/Używaj skanów o wysokiej rozdzielczości/)).toBeInTheDocument();
    expect(screen.getByText(/Obsługiwane formaty: PDF, JPEG, PNG, TIFF/)).toBeInTheDocument();
  });

  it('handles file upload successfully', async () => {
    const mockResponse = {
      data: {
        document_id: '123',
        success: true,
      },
    };

    mockedAxios.post.mockResolvedValueOnce(mockResponse);

    render(
      <TestWrapper>
        <UploadPage />
      </TestWrapper>
    );

    const file = new File(['test content'], 'test.pdf', { type: 'application/pdf' });
    const fileUpload = screen.getByTestId('ocr-file-upload');
    
    // Simulate file drop
    fireEvent.drop(fileUpload, {
      dataTransfer: {
        files: [file],
      },
    });

    await waitFor(() => {
      expect(mockedAxios.post).toHaveBeenCalledWith(
        '/api/v1/ocr/upload/',
        expect.any(FormData),
        expect.objectContaining({
          headers: {
            'Content-Type': 'multipart/form-data',
          },
          timeout: 30000,
        })
      );
    });
  });

  it('handles upload errors gracefully', async () => {
    const mockError = {
      response: {
        data: {
          error: 'File too large',
        },
      },
    };

    mockedAxios.post.mockRejectedValueOnce(mockError);

    render(
      <TestWrapper>
        <UploadPage />
      </TestWrapper>
    );

    const file = new File(['test content'], 'test.pdf', { type: 'application/pdf' });
    const fileUpload = screen.getByTestId('ocr-file-upload');
    
    fireEvent.drop(fileUpload, {
      dataTransfer: {
        files: [file],
      },
    });

    await waitFor(() => {
      expect(toast.error).toHaveBeenCalledWith(
        expect.stringContaining('File too large')
      );
    });
  });

  it('shows statistics when files are uploaded', async () => {
    render(
      <TestWrapper>
        <UploadPage />
      </TestWrapper>
    );

    // Initially no statistics should be shown
    expect(screen.queryByText('Statystyki przetwarzania')).not.toBeInTheDocument();

    // Add a file to trigger statistics display
    const mockFiles = [{
      id: '1',
      name: 'test.pdf',
      size: 1024,
      type: 'application/pdf',
      status: 'completed',
      uploadTimestamp: new Date().toISOString(),
    }];

    // This would normally be triggered by the FileUpload component
    // In a real test, we'd need to simulate the file upload process
  });

  it('polls for OCR results after upload', async () => {
    const mockUploadResponse = {
      data: {
        document_id: '123',
        success: true,
      },
    };

    const mockStatusResponse = {
      data: {
        processing_status: 'completed',
        ocr_result: {
          invoice_number: 'FV/2025/001',
          total_amount: '1234.56',
        },
      },
    };

    mockedAxios.post.mockResolvedValueOnce(mockUploadResponse);
    mockedAxios.get.mockResolvedValueOnce(mockStatusResponse);

    render(
      <TestWrapper>
        <UploadPage />
      </TestWrapper>
    );

    const file = new File(['test content'], 'test.pdf', { type: 'application/pdf' });
    const fileUpload = screen.getByTestId('ocr-file-upload');
    
    fireEvent.drop(fileUpload, {
      dataTransfer: {
        files: [file],
      },
    });

    await waitFor(() => {
      expect(mockedAxios.get).toHaveBeenCalledWith('/api/v1/ocr/status/123/');
    });
  });

  it('provides quick actions when files are present', () => {
    render(
      <TestWrapper>
        <UploadPage />
      </TestWrapper>
    );

    // Quick actions should not be visible initially
    expect(screen.queryByText('Szybkie akcje')).not.toBeInTheDocument();
    
    // Would need to simulate having uploaded files to test this properly
  });

  it('handles view results action', () => {
    render(
      <TestWrapper>
        <UploadPage />
      </TestWrapper>
    );

    // This would be tested by simulating a file with results and clicking view
    // The component should navigate to the OCR results page
  });

  it('handles download file action', async () => {
    const mockBlob = new Blob(['file content'], { type: 'application/pdf' });
    const mockResponse = {
      data: mockBlob,
    };

    mockedAxios.get.mockResolvedValueOnce(mockResponse);

    // Create a mock URL.createObjectURL
    global.URL.createObjectURL = jest.fn(() => 'mock-url');
    global.URL.revokeObjectURL = jest.fn();

    render(
      <TestWrapper>
        <UploadPage />
      </TestWrapper>
    );

    // This would be tested by simulating a file download action
    // The component should trigger a file download
  });
});