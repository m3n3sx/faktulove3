import React, { useState, useCallback } from 'react';
import { useQueryClient } from 'react-query';
import { 
  CheckCircle, 
  AlertCircle, 
  Clock,
  FileText,
  TrendingUp
} from 'lucide-react';
import toast from 'react-hot-toast';
import axios from 'axios';
import { 
  Grid, 
  FileUpload, 
  Card, 
  Badge, 
  Button,
  Stack,
  Container
} from '../design-system';

const UploadPage = () => {
  const [uploadedFiles, setUploadedFiles] = useState([]);
  const queryClient = useQueryClient();

  // Handle file upload with enhanced error handling
  const handleFileUpload = useCallback(async (file) => {
    const formData = new FormData();
    formData.append('document', file); // Use 'document' to match backend API
    
    try {
      const response = await axios.post('/api/v1/ocr/upload/', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
        timeout: 30000, // 30 second timeout
      });
      
      toast.success(`${file.name} przesłano pomyślnie!`);
      
      // Start polling for OCR results
      if (response.data.document_id) {
        pollOCRResults(response.data.document_id);
      }
      
      return {
        id: response.data.document_id,
        name: file.name,
        size: file.size,
        type: file.type,
        status: 'uploading',
        uploadTimestamp: new Date().toISOString(),
        ...response.data
      };
    } catch (error) {
      const errorMessage = error.response?.data?.error || 
                          error.response?.data?.message || 
                          error.message || 
                          'Wystąpił nieoczekiwany błąd';
      
      toast.error(`Nie udało się przesłać ${file.name}: ${errorMessage}`);
      throw new Error(errorMessage);
    }
  }, []);



  // Poll for OCR results with enhanced progress tracking
  const pollOCRResults = useCallback((documentId) => {
    let pollCount = 0;
    const maxPolls = 150; // 5 minutes at 2-second intervals
    
    const pollInterval = setInterval(async () => {
      pollCount++;
      
      try {
        const response = await axios.get(`/api/v1/ocr/status/${documentId}/`);
        const { processing_status, ocr_result, error_message } = response.data;
        
        // Update progress based on status
        const progressMap = {
          'uploaded': 10,
          'processing': 50,
          'completed': 100,
          'failed': 100
        };
        
        const progress = progressMap[processing_status] || 0;
        
        setUploadedFiles(prev => 
          prev.map(file => 
            file.id === documentId 
              ? { 
                  ...file, 
                  status: processing_status === 'completed' ? 'completed' : 
                         processing_status === 'failed' ? 'failed' : 'processing',
                  progress: progress,
                  result: ocr_result,
                  error: processing_status === 'failed' ? (error_message || 'Przetwarzanie OCR nie powiodło się') : undefined
                }
              : file
          )
        );
        
        if (processing_status === 'completed' || processing_status === 'failed') {
          clearInterval(pollInterval);
          
          if (processing_status === 'completed') {
            toast.success(`Przetwarzanie OCR zakończone pomyślnie!`);
          } else {
            toast.error(`Przetwarzanie OCR nie powiodło się: ${error_message || 'Nieznany błąd'}`);
          }
          
          queryClient.invalidateQueries(['documents']);
          queryClient.invalidateQueries(['statistics']);
        }
        
        // Stop polling after max attempts
        if (pollCount >= maxPolls) {
          clearInterval(pollInterval);
          setUploadedFiles(prev => 
            prev.map(file => 
              file.id === documentId && file.status === 'processing'
                ? { ...file, status: 'failed', error: 'Przekroczono limit czasu przetwarzania' }
                : file
            )
          );
          toast.error('Przekroczono limit czasu przetwarzania dokumentu');
        }
      } catch (error) {
        console.error('Error polling OCR status:', error);
        
        // On error, retry a few times before giving up
        if (pollCount >= 5) {
          clearInterval(pollInterval);
          setUploadedFiles(prev => 
            prev.map(file => 
              file.id === documentId 
                ? { ...file, status: 'failed', error: 'Błąd podczas sprawdzania statusu' }
                : file
            )
          );
          toast.error('Nie można sprawdzić statusu przetwarzania');
        }
      }
    }, 2000); // Poll every 2 seconds
    
    return pollInterval;
  }, [queryClient]);

  // Convert uploaded files to FileUpload format
  const convertToFileUploadFormat = (files) => {
    return files.map(file => ({
      id: file.id,
      name: file.original_filename || file.name,
      size: file.file_size || file.size,
      type: file.file_type || file.type,
      status: file.status || 'pending',
      uploadTimestamp: file.upload_timestamp || file.uploadTimestamp,
      result: file.ocr_result || file.result,
      error: file.error
    }));
  };

  // View OCR results with enhanced navigation
  const viewResults = useCallback((file) => {
    if (file.result) {
      // Navigate to OCR results detail page
      window.location.href = `/ocr/result/${file.id}/`;
    } else {
      toast.error('Wyniki OCR nie są jeszcze dostępne');
    }
  }, []);

  // Download processed file with proper error handling
  const downloadFile = useCallback(async (file) => {
    try {
      const response = await axios.get(`/api/v1/ocr/download/${file.id}/`, {
        responseType: 'blob',
      });
      
      // Create download link
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', file.name);
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(url);
      
      toast.success('Pobieranie rozpoczęte...');
    } catch (error) {
      console.error('Download error:', error);
      toast.error('Nie udało się pobrać pliku');
    }
  }, []);

  // Remove file with confirmation
  const removeFile = useCallback((fileId) => {
    setUploadedFiles(prev => prev.filter(f => f.id !== fileId));
    toast.success('Plik został usunięty z listy');
  }, []);

  return (
    <Container size="xl" className="py-6">
      <Stack gap="lg">
        {/* Header */}
        <Card variant="flat" padding="lg">
          <Stack gap="sm">
            <div className="flex items-center gap-3">
              <FileText className="h-8 w-8 text-primary-600" />
              <div>
                <h1 className="text-3xl font-bold text-gray-900">Przesyłanie dokumentów OCR</h1>
                <p className="text-lg text-gray-600">
                  Automatyczne przetwarzanie faktur z wykorzystaniem sztucznej inteligencji
                </p>
              </div>
            </div>
            
            <div className="bg-blue-50 border border-blue-200 rounded-md p-4">
              <div className="flex items-start gap-3">
                <AlertCircle className="h-5 w-5 text-blue-600 mt-0.5" />
                <div>
                  <h3 className="text-sm font-medium text-blue-900">Wskazówki dla najlepszych wyników</h3>
                  <ul className="mt-2 text-sm text-blue-800 space-y-1">
                    <li>• Używaj skanów o wysokiej rozdzielczości (min. 300 DPI)</li>
                    <li>• Upewnij się, że tekst jest czytelny i kontrastowy</li>
                    <li>• Obsługiwane formaty: PDF, JPEG, PNG, TIFF (max. 10MB)</li>
                    <li>• Dokumenty są automatycznie usuwane po 30 dniach (zgodnie z GDPR)</li>
                  </ul>
                </div>
              </div>
            </div>
          </Stack>
        </Card>

        {/* File Upload Component */}
        <FileUpload
          files={convertToFileUploadFormat(uploadedFiles)}
          onFilesChange={(files) => setUploadedFiles(files)}
          onFileUpload={handleFileUpload}
          onFileView={viewResults}
          onFileDownload={downloadFile}
          onFileRemove={removeFile}
          uploadAreaLabel="Przeciągnij i upuść dokumenty tutaj"
          uploadAreaSubLabel="lub kliknij, aby wybrać pliki z komputera"
          dragActiveLabel="Upuść dokumenty tutaj..."
          supportedFormats={['PDF', 'JPEG', 'PNG', 'TIFF']}
          maxSizeLabel="10MB"
          maxFiles={10}
          testId="ocr-file-upload"
        />

        {/* Statistics Dashboard */}
        {uploadedFiles.length > 0 && (
          <Card variant="elevated" padding="lg">
            <Stack gap="md">
              <div className="flex items-center gap-2">
                <TrendingUp className="h-5 w-5 text-primary-600" />
                <h2 className="text-lg font-semibold text-gray-900">Statystyki przetwarzania</h2>
              </div>
              
              <Grid cols={4} gap="md">
                <Card variant="outlined" padding="md" className="text-center">
                  <Stack gap="xs" className="items-center">
                    <FileText className="h-8 w-8 text-gray-600" />
                    <div>
                      <p className="text-2xl font-bold text-gray-900">{uploadedFiles.length}</p>
                      <p className="text-sm text-gray-500">Łącznie przesłano</p>
                    </div>
                  </Stack>
                </Card>
                
                <Card variant="outlined" padding="md" className="text-center">
                  <Stack gap="xs" className="items-center">
                    <CheckCircle className="h-8 w-8 text-success-600" />
                    <div>
                      <p className="text-2xl font-bold text-success-700">
                        {uploadedFiles.filter(f => f.status === 'completed').length}
                      </p>
                      <p className="text-sm text-gray-500">Zakończone</p>
                    </div>
                  </Stack>
                </Card>
                
                <Card variant="outlined" padding="md" className="text-center">
                  <Stack gap="xs" className="items-center">
                    <Clock className="h-8 w-8 text-warning-600" />
                    <div>
                      <p className="text-2xl font-bold text-warning-700">
                        {uploadedFiles.filter(f => f.status === 'processing' || f.status === 'uploading').length}
                      </p>
                      <p className="text-sm text-gray-500">Przetwarzane</p>
                    </div>
                  </Stack>
                </Card>
                
                <Card variant="outlined" padding="md" className="text-center">
                  <Stack gap="xs" className="items-center">
                    <AlertCircle className="h-8 w-8 text-error-600" />
                    <div>
                      <p className="text-2xl font-bold text-error-700">
                        {uploadedFiles.filter(f => f.status === 'failed').length}
                      </p>
                      <p className="text-sm text-gray-500">Błędy</p>
                    </div>
                  </Stack>
                </Card>
              </Grid>
              
              {/* Success Rate */}
              {uploadedFiles.length > 0 && (
                <div className="mt-4 p-4 bg-gray-50 rounded-md">
                  <div className="flex items-center justify-between">
                    <span className="text-sm font-medium text-gray-700">Wskaźnik sukcesu</span>
                    <Badge 
                      variant={
                        (uploadedFiles.filter(f => f.status === 'completed').length / uploadedFiles.length) >= 0.8 
                          ? 'success' 
                          : 'warning'
                      }
                    >
                      {Math.round((uploadedFiles.filter(f => f.status === 'completed').length / uploadedFiles.length) * 100)}%
                    </Badge>
                  </div>
                </div>
              )}
            </Stack>
          </Card>
        )}

        {/* Quick Actions */}
        {uploadedFiles.length > 0 && (
          <Card variant="outlined" padding="md">
            <div className="flex items-center justify-between">
              <div>
                <h3 className="text-sm font-medium text-gray-900">Szybkie akcje</h3>
                <p className="text-sm text-gray-500">Zarządzaj przesłanymi dokumentami</p>
              </div>
              <div className="flex gap-2">
                <Button 
                  variant="secondary" 
                  size="sm"
                  onClick={() => window.location.href = '/ocr/results/'}
                >
                  Zobacz wszystkie wyniki
                </Button>
                <Button 
                  variant="primary" 
                  size="sm"
                  onClick={() => window.location.href = '/invoices/create/'}
                >
                  Utwórz fakturę
                </Button>
              </div>
            </div>
          </Card>
        )}
      </Stack>
    </Container>
  );
};

export default UploadPage;
