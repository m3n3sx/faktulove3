import type { Meta, StoryObj } from '@storybook/react';
import { FileUpload, FileUploadFile } from './FileUpload';
import { useState } from 'react';

const meta: Meta<typeof FileUpload> = {
  title: 'Patterns/FileUpload',
  component: FileUpload,
  parameters: {
    layout: 'padded',
  },
  tags: ['autodocs'],
};

export default meta;
type Story = StoryObj<typeof meta>;

export const Default: Story = {
  render: () => {
    const [files, setFiles] = useState<FileUploadFile[]>([]);
    
    const handleFileUpload = async (file: File): Promise<any> => {
      // Simulate upload delay
      await new Promise(resolve => setTimeout(resolve, 2000));
      
      // Simulate OCR result
      return {
        invoice_number: 'FV/2025/001',
        total_amount: '1,234.56 PLN',
        supplier_name: 'Przykładowa Firma Sp. z o.o.',
        confidence_score: 95.5,
      };
    };

    return (
      <FileUpload
        files={files}
        onFilesChange={setFiles}
        onFileUpload={handleFileUpload}
        onFileView={(file) => console.log('View file:', file)}
        onFileDownload={(file) => console.log('Download file:', file)}
      />
    );
  },
};

export const WithExistingFiles: Story = {
  render: () => {
    const [files, setFiles] = useState<FileUploadFile[]>([
      {
        id: '1',
        name: 'faktura-001.pdf',
        size: 2048576,
        type: 'application/pdf',
        status: 'completed',
        uploadTimestamp: '2025-01-15T10:30:00Z',
        result: {
          invoice_number: 'FV/2025/001',
          total_amount: '1,234.56 PLN',
          supplier_name: 'ABC Sp. z o.o.',
          confidence_score: 98.2,
        },
      },
      {
        id: '2',
        name: 'rachunek-002.jpg',
        size: 1536000,
        type: 'image/jpeg',
        status: 'processing',
        progress: 75,
        uploadTimestamp: '2025-01-15T10:35:00Z',
      },
      {
        id: '3',
        name: 'dokument-003.png',
        size: 3072000,
        type: 'image/png',
        status: 'failed',
        error: 'Nie udało się przetworzyć dokumentu',
        uploadTimestamp: '2025-01-15T10:40:00Z',
      },
    ]);

    return (
      <FileUpload
        files={files}
        onFilesChange={setFiles}
        onFileView={(file) => console.log('View file:', file)}
        onFileDownload={(file) => console.log('Download file:', file)}
      />
    );
  },
};

export const SingleFileUpload: Story = {
  render: () => {
    const [files, setFiles] = useState<FileUploadFile[]>([]);
    
    return (
      <FileUpload
        files={files}
        onFilesChange={setFiles}
        multiple={false}
        maxFiles={1}
        uploadAreaLabel="Przeciągnij fakturę tutaj"
        uploadAreaSubLabel="lub kliknij, aby wybrać plik"
      />
    );
  },
};

export const CustomConfiguration: Story = {
  render: () => {
    const [files, setFiles] = useState<FileUploadFile[]>([]);
    
    return (
      <FileUpload
        files={files}
        onFilesChange={setFiles}
        maxSize={5 * 1024 * 1024} // 5MB
        maxSizeLabel="5MB"
        supportedFormats={['PDF', 'JPEG']}
        accept={{
          'application/pdf': ['.pdf'],
          'image/jpeg': ['.jpg', '.jpeg'],
        }}
        uploadAreaLabel="Prześlij dokumenty księgowe"
        uploadAreaSubLabel="Obsługujemy tylko pliki PDF i JPEG"
      />
    );
  },
};

export const Disabled: Story = {
  render: () => {
    const [files, setFiles] = useState<FileUploadFile[]>([]);
    
    return (
      <FileUpload
        files={files}
        onFilesChange={setFiles}
        disabled={true}
      />
    );
  },
};