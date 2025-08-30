import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { FileUpload, FileUploadFile } from '../FileUpload';

// Mock react-dropzone
jest.mock('react-dropzone', () => ({
  useDropzone: jest.fn(() => ({
    getRootProps: () => ({ 'data-testid': 'dropzone' }),
    getInputProps: () => ({ 'data-testid': 'file-input' }),
    isDragActive: false,
  })),
}));

describe('FileUpload', () => {
  const mockFiles: FileUploadFile[] = [
    {
      id: '1',
      name: 'test.pdf',
      size: 1024,
      type: 'application/pdf',
      status: 'completed',
      uploadTimestamp: '2025-01-15T10:00:00Z',
      result: {
        invoice_number: 'FV/001',
        total_amount: '100.00 PLN',
        supplier_name: 'Test Company',
        confidence_score: 95.5,
      },
    },
    {
      id: '2',
      name: 'processing.jpg',
      size: 2048,
      type: 'image/jpeg',
      status: 'processing',
      progress: 50,
    },
  ];

  it('renders upload area correctly', () => {
    render(<FileUpload testId="file-upload" />);
    
    expect(screen.getByTestId('file-upload')).toBeInTheDocument();
    expect(screen.getByText('Przeciągnij i upuść pliki tutaj')).toBeInTheDocument();
    expect(screen.getByText('lub kliknij, aby wybrać pliki')).toBeInTheDocument();
  });

  it('displays files list when files are provided', () => {
    render(
      <FileUpload 
        files={mockFiles}
        testId="file-upload"
      />
    );
    
    expect(screen.getByText('Przesłane dokumenty')).toBeInTheDocument();
    expect(screen.getByText('test.pdf')).toBeInTheDocument();
    expect(screen.getByText('processing.jpg')).toBeInTheDocument();
  });

  it('shows correct status badges', () => {
    render(
      <FileUpload 
        files={mockFiles}
        testId="file-upload"
      />
    );
    
    expect(screen.getByText('Zakończone')).toBeInTheDocument();
    expect(screen.getByText('Przetwarzanie')).toBeInTheDocument();
  });

  it('displays OCR results for completed files', () => {
    render(
      <FileUpload 
        files={mockFiles}
        testId="file-upload"
      />
    );
    
    expect(screen.getByText('FV/001')).toBeInTheDocument();
    expect(screen.getByText('100.00 PLN')).toBeInTheDocument();
    expect(screen.getByText('Test Company')).toBeInTheDocument();
    expect(screen.getByText('95.5%')).toBeInTheDocument();
  });

  it('shows progress bar for processing files', () => {
    render(
      <FileUpload 
        files={mockFiles}
        testId="file-upload"
      />
    );
    
    const progressBar = screen.getByRole('progressbar');
    expect(progressBar).toBeInTheDocument();
    expect(progressBar).toHaveAttribute('aria-valuenow', '50');
  });

  it('calls onFileRemove when remove button is clicked', () => {
    const mockOnFileRemove = jest.fn();
    const mockOnFilesChange = jest.fn();
    
    render(
      <FileUpload 
        files={mockFiles}
        onFileRemove={mockOnFileRemove}
        onFilesChange={mockOnFilesChange}
        testId="file-upload"
      />
    );
    
    const removeButtons = screen.getAllByLabelText('Usuń');
    fireEvent.click(removeButtons[0]);
    
    expect(mockOnFilesChange).toHaveBeenCalledWith([mockFiles[1]]);
  });

  it('calls onFileView when view button is clicked', () => {
    const mockOnFileView = jest.fn();
    
    render(
      <FileUpload 
        files={mockFiles}
        onFileView={mockOnFileView}
        testId="file-upload"
      />
    );
    
    const viewButton = screen.getByLabelText('Wyświetl wyniki');
    fireEvent.click(viewButton);
    
    expect(mockOnFileView).toHaveBeenCalledWith(mockFiles[0]);
  });

  it('calls onFileDownload when download button is clicked', () => {
    const mockOnFileDownload = jest.fn();
    
    render(
      <FileUpload 
        files={mockFiles}
        onFileDownload={mockOnFileDownload}
        testId="file-upload"
      />
    );
    
    const downloadButtons = screen.getAllByLabelText('Pobierz');
    fireEvent.click(downloadButtons[0]);
    
    expect(mockOnFileDownload).toHaveBeenCalledWith(mockFiles[0]);
  });

  it('formats file size correctly', () => {
    const fileWithLargeSize: FileUploadFile = {
      id: '3',
      name: 'large.pdf',
      size: 1048576, // 1MB
      type: 'application/pdf',
      status: 'completed',
    };
    
    render(
      <FileUpload 
        files={[fileWithLargeSize]}
        testId="file-upload"
      />
    );
    
    expect(screen.getByText('1 MB')).toBeInTheDocument();
  });

  it('shows error message for failed files', () => {
    const failedFile: FileUploadFile = {
      id: '4',
      name: 'failed.pdf',
      size: 1024,
      type: 'application/pdf',
      status: 'failed',
      error: 'Upload failed',
    };
    
    render(
      <FileUpload 
        files={[failedFile]}
        testId="file-upload"
      />
    );
    
    expect(screen.getByText('Błąd')).toBeInTheDocument();
    expect(screen.getByText('Upload failed')).toBeInTheDocument();
  });

  it('applies disabled state correctly', () => {
    render(<FileUpload disabled testId="file-upload" />);
    
    const uploadArea = screen.getByTestId('dropzone').parentElement;
    expect(uploadArea).toHaveClass('opacity-50', 'cursor-not-allowed');
  });
});