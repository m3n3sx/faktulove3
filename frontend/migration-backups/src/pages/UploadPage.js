import React, { useState, useCallback } from 'react';
import { useDropzone } from 'react-dropzone';
import { useMutation, useQueryClient } from 'react-query';
import { 
  Upload, 
  FileText, 
  CheckCircle, 
  AlertCircle, 
  Clock, 
  X,
  Eye,
  Download
} from 'lucide-react';
import toast from 'react-hot-toast';
import axios from 'axios';

const UploadPage = () => {
  const [uploadedFiles, setUploadedFiles] = useState([]);
  const [processingFiles, setProcessingFiles] = useState(new Set());
  const queryClient = useQueryClient();

  // Upload mutation
  const uploadMutation = useMutation(
    async (file) => {
      const formData = new FormData();
      formData.append('file', file);
      
      const response = await axios.post('/api/ocr/upload/', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });
      
      return response.data;
    },
    {
      onSuccess: (data, file) => {
        toast.success(`${file.name} uploaded successfully!`);
        setUploadedFiles(prev => [...prev, { ...data, file }]);
        setProcessingFiles(prev => new Set([...prev, data.id]));
        
        // Start polling for OCR results
        pollOCRResults(data.id);
      },
      onError: (error, file) => {
        toast.error(`Failed to upload ${file.name}: ${error.response?.data?.message || error.message}`);
      },
    }
  );

  // OCR processing mutation
  const processMutation = useMutation(
    async (documentId) => {
      const response = await axios.post(`/api/ocr/process/${documentId}/`);
      return response.data;
    },
    {
      onSuccess: (data, documentId) => {
        toast.success(`OCR processing completed for document ${documentId}!`);
        setProcessingFiles(prev => {
          const newSet = new Set(prev);
          newSet.delete(documentId);
          return newSet;
        });
        
        // Update the uploaded files list
        setUploadedFiles(prev => 
          prev.map(file => 
            file.id === documentId 
              ? { ...file, ocr_result: data, status: 'completed' }
              : file
          )
        );
        
        // Invalidate queries to refresh data
        queryClient.invalidateQueries(['documents']);
        queryClient.invalidateQueries(['statistics']);
      },
      onError: (error, documentId) => {
        toast.error(`OCR processing failed for document ${documentId}: ${error.response?.data?.message || error.message}`);
        setProcessingFiles(prev => {
          const newSet = new Set(prev);
          newSet.delete(documentId);
          return newSet;
        });
      },
    }
  );

  // Poll for OCR results
  const pollOCRResults = useCallback((documentId) => {
    const pollInterval = setInterval(async () => {
      try {
        const response = await axios.get(`/api/ocr/status/${documentId}/`);
        const { status, ocr_result } = response.data;
        
        if (status === 'completed' || status === 'failed') {
          clearInterval(pollInterval);
          
          if (status === 'completed') {
            setUploadedFiles(prev => 
              prev.map(file => 
                file.id === documentId 
                  ? { ...file, ocr_result, status: 'completed' }
                  : file
              )
            );
            toast.success(`OCR processing completed for document ${documentId}!`);
          } else {
            toast.error(`OCR processing failed for document ${documentId}`);
          }
          
          setProcessingFiles(prev => {
            const newSet = new Set(prev);
            newSet.delete(documentId);
            return newSet;
          });
          
          queryClient.invalidateQueries(['documents']);
          queryClient.invalidateQueries(['statistics']);
        }
      } catch (error) {
        console.error('Error polling OCR status:', error);
      }
    }, 2000); // Poll every 2 seconds
    
    // Cleanup after 5 minutes
    setTimeout(() => {
      clearInterval(pollInterval);
      setProcessingFiles(prev => {
        const newSet = new Set(prev);
        newSet.delete(documentId);
        return newSet;
      });
    }, 5 * 60 * 1000);
  }, [queryClient]);

  // Dropzone configuration
  const onDrop = useCallback((acceptedFiles) => {
    acceptedFiles.forEach(file => {
      // Validate file type
      const allowedTypes = ['application/pdf', 'image/jpeg', 'image/png', 'image/tiff'];
      if (!allowedTypes.includes(file.type)) {
        toast.error(`${file.name} is not a supported file type. Please upload PDF, JPEG, PNG, or TIFF files.`);
        return;
      }
      
      // Validate file size (10MB limit)
      if (file.size > 10 * 1024 * 1024) {
        toast.error(`${file.name} is too large. Maximum file size is 10MB.`);
        return;
      }
      
      uploadMutation.mutate(file);
    });
  }, [uploadMutation]);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'application/pdf': ['.pdf'],
      'image/jpeg': ['.jpg', '.jpeg'],
      'image/png': ['.png'],
      'image/tiff': ['.tiff', '.tif']
    },
    multiple: true
  });

  // Remove file from list
  const removeFile = (fileId) => {
    setUploadedFiles(prev => prev.filter(file => file.id !== fileId));
  };

  // View OCR results
  const viewResults = (file) => {
    if (file.ocr_result) {
      // In a real app, this would open a modal or navigate to results page
      console.log('OCR Results:', file.ocr_result);
      toast.success('Viewing OCR results...');
    }
  };

  // Download processed file
  const downloadFile = (file) => {
    // In a real app, this would trigger a download
    console.log('Downloading file:', file);
    toast.success('Download started...');
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Upload Documents</h1>
        <p className="mt-2 text-gray-600">
          Upload invoice documents for AI-powered OCR processing. Supported formats: PDF, JPEG, PNG, TIFF.
        </p>
      </div>

      {/* Upload Area */}
      <div
        {...getRootProps()}
        className={`
          border-2 border-dashed rounded-lg p-8 text-center cursor-pointer transition-colors duration-200
          ${isDragActive 
            ? 'border-primary-400 bg-primary-50' 
            : 'border-gray-300 hover:border-primary-400 hover:bg-gray-50'
          }
        `}
      >
        <input {...getInputProps()} />
        <Upload className="mx-auto h-12 w-12 text-gray-400" />
        <div className="mt-4">
          <p className="text-lg font-medium text-gray-900">
            {isDragActive ? 'Drop files here...' : 'Drag & drop files here'}
          </p>
          <p className="mt-2 text-sm text-gray-500">
            or click to select files
          </p>
        </div>
        <div className="mt-4 text-xs text-gray-400">
          Maximum file size: 10MB • Supported formats: PDF, JPEG, PNG, TIFF
        </div>
      </div>

      {/* Upload Progress */}
      {uploadMutation.isLoading && (
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
          <div className="flex items-center">
            <Clock className="h-5 w-5 text-blue-500 animate-spin" />
            <span className="ml-2 text-blue-700">Uploading files...</span>
          </div>
        </div>
      )}

      {/* Processing Status */}
      {processingFiles.size > 0 && (
        <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
          <div className="flex items-center">
            <Clock className="h-5 w-5 text-yellow-500 animate-spin" />
            <span className="ml-2 text-yellow-700">
              Processing {processingFiles.size} document{processingFiles.size > 1 ? 's' : ''}...
            </span>
          </div>
        </div>
      )}

      {/* Uploaded Files List */}
      {uploadedFiles.length > 0 && (
        <div className="bg-white shadow rounded-lg">
          <div className="px-6 py-4 border-b border-gray-200">
            <h3 className="text-lg font-medium text-gray-900">Uploaded Documents</h3>
          </div>
          <div className="divide-y divide-gray-200">
            {uploadedFiles.map((file) => (
              <div key={file.id} className="px-6 py-4">
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-4">
                    <FileText className="h-8 w-8 text-gray-400" />
                    <div>
                      <p className="text-sm font-medium text-gray-900">{file.original_filename}</p>
                      <p className="text-xs text-gray-500">
                        {(file.file_size / 1024 / 1024).toFixed(2)} MB • Uploaded {new Date(file.upload_timestamp).toLocaleString()}
                      </p>
                    </div>
                  </div>
                  
                  <div className="flex items-center space-x-2">
                    {/* Status indicator */}
                    {processingFiles.has(file.id) ? (
                      <div className="flex items-center text-yellow-600">
                        <Clock className="h-4 w-4 animate-spin" />
                        <span className="ml-1 text-sm">Processing...</span>
                      </div>
                    ) : file.status === 'completed' ? (
                      <div className="flex items-center text-green-600">
                        <CheckCircle className="h-4 w-4" />
                        <span className="ml-1 text-sm">Completed</span>
                      </div>
                    ) : file.status === 'failed' ? (
                      <div className="flex items-center text-red-600">
                        <AlertCircle className="h-4 w-4" />
                        <span className="ml-1 text-sm">Failed</span>
                      </div>
                    ) : (
                      <div className="flex items-center text-gray-600">
                        <Clock className="h-4 w-4" />
                        <span className="ml-1 text-sm">Pending</span>
                      </div>
                    )}
                    
                    {/* Actions */}
                    <div className="flex items-center space-x-1">
                      {file.ocr_result && (
                        <button
                          onClick={() => viewResults(file)}
                          className="p-1 text-gray-400 hover:text-gray-600 transition-colors"
                          title="View results"
                        >
                          <Eye className="h-4 w-4" />
                        </button>
                      )}
                      
                      <button
                        onClick={() => downloadFile(file)}
                        className="p-1 text-gray-400 hover:text-gray-600 transition-colors"
                        title="Download"
                      >
                        <Download className="h-4 w-4" />
                      </button>
                      
                      <button
                        onClick={() => removeFile(file.id)}
                        className="p-1 text-gray-400 hover:text-red-600 transition-colors"
                        title="Remove"
                      >
                        <X className="h-4 w-4" />
                      </button>
                    </div>
                  </div>
                </div>
                
                {/* OCR Results Preview */}
                {file.ocr_result && (
                  <div className="mt-3 pl-12">
                    <div className="bg-gray-50 rounded-lg p-3">
                      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                        <div>
                          <span className="text-gray-500">Invoice #:</span>
                          <p className="font-medium">{file.ocr_result.invoice_number || 'N/A'}</p>
                        </div>
                        <div>
                          <span className="text-gray-500">Amount:</span>
                          <p className="font-medium">{file.ocr_result.total_amount || 'N/A'}</p>
                        </div>
                        <div>
                          <span className="text-gray-500">Supplier:</span>
                          <p className="font-medium truncate">{file.ocr_result.supplier_name || 'N/A'}</p>
                        </div>
                        <div>
                          <span className="text-gray-500">Confidence:</span>
                          <p className="font-medium">{file.ocr_result.confidence_score?.toFixed(1)}%</p>
                        </div>
                      </div>
                    </div>
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Statistics */}
      {uploadedFiles.length > 0 && (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="bg-white p-4 rounded-lg shadow">
            <div className="flex items-center">
              <FileText className="h-8 w-8 text-primary-600" />
              <div className="ml-3">
                <p className="text-sm font-medium text-gray-500">Total Uploaded</p>
                <p className="text-2xl font-bold text-gray-900">{uploadedFiles.length}</p>
              </div>
            </div>
          </div>
          
          <div className="bg-white p-4 rounded-lg shadow">
            <div className="flex items-center">
              <CheckCircle className="h-8 w-8 text-green-600" />
              <div className="ml-3">
                <p className="text-sm font-medium text-gray-500">Completed</p>
                <p className="text-2xl font-bold text-gray-900">
                  {uploadedFiles.filter(f => f.status === 'completed').length}
                </p>
              </div>
            </div>
          </div>
          
          <div className="bg-white p-4 rounded-lg shadow">
            <div className="flex items-center">
              <Clock className="h-8 w-8 text-yellow-600" />
              <div className="ml-3">
                <p className="text-sm font-medium text-gray-500">Processing</p>
                <p className="text-2xl font-bold text-gray-900">{processingFiles.size}</p>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default UploadPage;
