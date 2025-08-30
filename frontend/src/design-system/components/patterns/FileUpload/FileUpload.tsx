import React, { useCallback, useState } from 'react';
import { useDropzone } from 'react-dropzone';
import { 
  Upload, 
  FileText, 
  X, 
  Eye, 
  Download,
  AlertCircle
} from 'lucide-react';
import { cn } from '../../../utils/cn';
import { Button } from '../../primitives/Button';
import { Badge } from '../../primitives/Badge';
import { Progress } from '../../primitives/Progress';
import { Grid } from '../../layouts/Grid/Grid';

export interface FileUploadFile {
  id: string;
  name: string;
  size: number;
  type: string;
  status: 'pending' | 'uploading' | 'processing' | 'completed' | 'failed';
  progress?: number;
  uploadTimestamp?: string;
  result?: any;
  error?: string;
}

export interface FileUploadProps {
  accept?: Record<string, string[]>;
  maxSize?: number;
  maxFiles?: number;
  multiple?: boolean;
  disabled?: boolean;
  files?: FileUploadFile[];
  onFilesChange?: (files: FileUploadFile[]) => void;
  onFileUpload?: (file: File) => Promise<any>;
  onFileRemove?: (fileId: string) => void;
  onFileView?: (file: FileUploadFile) => void;
  onFileDownload?: (file: FileUploadFile) => void;
  className?: string;
  testId?: string;
  // Polish business specific props
  supportedFormats?: string[];
  maxSizeLabel?: string;
  uploadAreaLabel?: string;
  uploadAreaSubLabel?: string;
  dragActiveLabel?: string;
}

const DEFAULT_ACCEPT = {
  'application/pdf': ['.pdf'],
  'image/jpeg': ['.jpg', '.jpeg'],
  'image/png': ['.png'],
  'image/tiff': ['.tiff', '.tif']
};

const DEFAULT_MAX_SIZE = 10 * 1024 * 1024; // 10MB

export const FileUpload: React.FC<FileUploadProps> = ({
  accept = DEFAULT_ACCEPT,
  maxSize = DEFAULT_MAX_SIZE,
  maxFiles,
  multiple = true,
  disabled = false,
  files = [],
  onFilesChange,
  onFileUpload,
  onFileRemove,
  onFileView,
  onFileDownload,
  className,
  testId,
  supportedFormats = ['PDF', 'JPEG', 'PNG', 'TIFF'],
  maxSizeLabel = '10MB',
  uploadAreaLabel = 'Przeciągnij i upuść pliki tutaj',
  uploadAreaSubLabel = 'lub kliknij, aby wybrać pliki',
  dragActiveLabel = 'Upuść pliki tutaj...',
}) => {
  const [uploadingFiles, setUploadingFiles] = useState<Set<string>>(new Set());

  const onDrop = useCallback(async (acceptedFiles: File[]) => {
    if (disabled) return;

    for (const file of acceptedFiles) {
      // Validate file type
      const allowedTypes = Object.keys(accept);
      if (!allowedTypes.includes(file.type)) {
        // Handle error - could emit an error event or show toast
        console.error(`${file.name} nie jest obsługiwanym typem pliku.`);
        continue;
      }
      
      // Validate file size
      if (file.size > maxSize) {
        console.error(`${file.name} jest za duży. Maksymalny rozmiar to ${maxSizeLabel}.`);
        continue;
      }

      // Check max files limit
      if (maxFiles && files.length >= maxFiles) {
        console.error(`Można przesłać maksymalnie ${maxFiles} plików.`);
        break;
      }

      const fileId = `${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
      const newFile: FileUploadFile = {
        id: fileId,
        name: file.name,
        size: file.size,
        type: file.type,
        status: 'uploading',
        progress: 0,
        uploadTimestamp: new Date().toISOString(),
      };

      // Add file to list
      const updatedFiles = [...files, newFile];
      onFilesChange?.(updatedFiles);
      setUploadingFiles(prev => {
        const newSet = new Set(prev);
        newSet.add(fileId);
        return newSet;
      });

      // Start upload
      if (onFileUpload) {
        try {
          const result = await onFileUpload(file);
          
          // Update file status
          const finalFiles = updatedFiles.map(f => 
            f.id === fileId 
              ? { ...f, status: 'completed' as const, progress: 100, result }
              : f
          );
          onFilesChange?.(finalFiles);
        } catch (error) {
          // Update file status to failed
          const finalFiles = updatedFiles.map(f => 
            f.id === fileId 
              ? { ...f, status: 'failed' as const, error: error instanceof Error ? error.message : 'Upload failed' }
              : f
          );
          onFilesChange?.(finalFiles);
        } finally {
          setUploadingFiles(prev => {
            const newSet = new Set(prev);
            newSet.delete(fileId);
            return newSet;
          });
        }
      }
    }
  }, [accept, maxSize, maxFiles, files, onFilesChange, onFileUpload, disabled, maxSizeLabel]);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept,
    multiple,
    disabled,
  });

  const removeFile = (fileId: string) => {
    const updatedFiles = files.filter(f => f.id !== fileId);
    onFilesChange?.(updatedFiles);
    onFileRemove?.(fileId);
  };

  const formatFileSize = (bytes: number) => {
    if (bytes === 0) return '0 B';
    const k = 1024;
    const sizes = ['B', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  const getStatusBadge = (file: FileUploadFile) => {
    switch (file.status) {
      case 'pending':
        return <Badge variant="default">Oczekuje</Badge>;
      case 'uploading':
        return <Badge variant="info">Przesyłanie</Badge>;
      case 'processing':
        return <Badge variant="warning">Przetwarzanie</Badge>;
      case 'completed':
        return <Badge variant="success">Zakończone</Badge>;
      case 'failed':
        return <Badge variant="error">Błąd</Badge>;
      default:
        return <Badge variant="default">Nieznany</Badge>;
    }
  };

  return (
    <div className={cn('space-y-6', className)} data-testid={testId}>
      {/* Upload Area */}
      <div
        {...getRootProps()}
        className={cn(
          'border-2 border-dashed rounded-md-lg p-8 text-center cursor-pointer transition-colors duration-200',
          isDragActive 
            ? 'border-primary-400 bg-primary-50' 
            : 'border-gray-300 hover:border-primary-400 hover:bg-gray-50',
          disabled && 'opacity-50 cursor-not-allowed'
        )}
      >
        <input {...getInputProps()} />
        <Upload className="mx-auto h-12 w-12 text-gray-400" />
        <div className="mt-4">
          <p className="text-lg font-medium text-gray-900">
            {isDragActive ? dragActiveLabel : uploadAreaLabel}
          </p>
          <p className="mt-2 text-sm text-gray-500">
            {uploadAreaSubLabel}
          </p>
        </div>
        <div className="mt-4 text-xs text-gray-400">
          Maksymalny rozmiar pliku: {maxSizeLabel} • Obsługiwane formaty: {supportedFormats.join(', ')}
        </div>
      </div>

      {/* Files List */}
      {files.length > 0 && (
        <div className="bg-white shadow-sm rounded-md-lg">
          <div className="px-6 py-4 border-b border-gray-200">
            <h3 className="text-lg font-medium text-gray-900">Przesłane dokumenty</h3>
          </div>
          <div className="divide-y divide-gray-200">
            {files.map((file) => (
              <div key={file.id} className="px-6 py-4">
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-4 flex-1">
                    <FileText className="h-8 w-8 text-gray-400 flex-shrink-0" />
                    <div className="flex-1 min-w-0">
                      <p className="text-sm font-medium text-gray-900 truncate">{file.name}</p>
                      <p className="text-xs text-gray-500">
                        {formatFileSize(file.size)}
                        {file.uploadTimestamp && (
                          <> • Przesłano {new Date(file.uploadTimestamp).toLocaleString('pl-PL')}</>
                        )}
                      </p>
                      
                      {/* Progress bar for uploading files */}
                      {(file.status === 'uploading' || file.status === 'processing') && file.progress !== undefined && (
                        <div className="mt-2">
                          <Progress 
                            value={file.progress} 
                            size="sm" 
                            variant={file.status === 'processing' ? 'warning' : 'default'}
                          />
                        </div>
                      )}
                      
                      {/* Error message */}
                      {file.status === 'failed' && file.error && (
                        <div className="mt-2 flex items-center text-error-600">
                          <AlertCircle className="h-4 w-4 mr-1" />
                          <span className="text-xs">{file.error}</span>
                        </div>
                      )}
                    </div>
                  </div>
                  
                  <div className="flex items-center space-x-3 ml-4">
                    {/* Status badge */}
                    {getStatusBadge(file)}
                    
                    {/* Actions */}
                    <div className="flex items-center space-x-1">
                      {file.result && onFileView && (
                        <Button
                          variant="ghost"
                          size="xs"
                          onClick={() => onFileView(file)}
                          aria-label="Wyświetl wyniki"
                        >
                          <Eye className="h-4 w-4" />
                        </Button>
                      )}
                      
                      {onFileDownload && (
                        <Button
                          variant="ghost"
                          size="xs"
                          onClick={() => onFileDownload(file)}
                          aria-label="Pobierz"
                        >
                          <Download className="h-4 w-4" />
                        </Button>
                      )}
                      
                      <Button
                        variant="ghost"
                        size="xs"
                        onClick={() => removeFile(file.id)}
                        aria-label="Usuń"
                      >
                        <X className="h-4 w-4" />
                      </Button>
                    </div>
                  </div>
                </div>
                
                {/* Results Preview */}
                {file.result && (
                  <div className="mt-3 pl-12">
                    <div className="bg-gray-50 rounded-md-lg p-3">
                      <Grid cols={2} gap="md">
                        <div>
                          <span className="text-xs text-gray-500">Numer faktury:</span>
                          <p className="text-sm font-medium">{file.result.invoice_number || 'Brak'}</p>
                        </div>
                        <div>
                          <span className="text-xs text-gray-500">Kwota:</span>
                          <p className="text-sm font-medium">{file.result.total_amount || 'Brak'}</p>
                        </div>
                        <div>
                          <span className="text-xs text-gray-500">Dostawca:</span>
                          <p className="text-sm font-medium truncate">{file.result.supplier_name || 'Brak'}</p>
                        </div>
                        <div>
                          <span className="text-xs text-gray-500">Pewność:</span>
                          <p className="text-sm font-medium">
                            {file.result.confidence_score ? `${file.result.confidence_score.toFixed(1)}%` : 'Brak'}
                          </p>
                        </div>
                      </Grid>
                    </div>
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

FileUpload.displayName = 'FileUpload';