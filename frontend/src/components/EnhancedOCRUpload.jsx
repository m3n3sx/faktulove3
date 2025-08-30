/**
 * Enhanced OCR Upload Component with drag-and-drop, real-time progress, and queue management
 */

import React, { useState, useEffect, useCallback, useRef } from 'react';
import axios from 'axios';

// Upload status constants
const UPLOAD_STATUS = {
  IDLE: 'idle',
  QUEUED: 'queued',
  VALIDATING: 'validating',
  UPLOADING: 'uploading',
  PROCESSING: 'processing',
  COMPLETED: 'completed',
  FAILED: 'failed',
  CANCELLED: 'cancelled'
};

// File type validation
const SUPPORTED_TYPES = {
  'application/pdf': '.pdf',
  'image/jpeg': '.jpg',
  'image/png': '.png',
  'image/tiff': '.tiff'
};

const MAX_FILE_SIZE = 10 * 1024 * 1024; // 10MB

const EnhancedOCRUpload = ({ 
  apiBaseUrl = '/api/v1',
  csrfToken,
  onUploadComplete,
  onUploadError,
  maxConcurrentUploads = 3
}) => {
  // State management
  const [uploads, setUploads] = useState([]);
  const [dragActive, setDragActive] = useState(false);
  const [queueStatus, setQueueStatus] = useState({});
  const [globalError, setGlobalError] = useState('');
  
  // Refs
  const fileInputRef = useRef(null);
  const progressIntervalRef = useRef(null);
  
  // API client setup
  const apiClient = axios.create({
    baseURL: apiBaseUrl,
    headers: {
      'X-CSRFToken': csrfToken,
      'Content-Type': 'application/json'
    }
  });

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      if (progressIntervalRef.current) {
        clearInterval(progressIntervalRef.current);
      }
    };
  }, []);

  // Start progress polling when uploads are active
  useEffect(() => {
    const activeUploads = uploads.filter(upload => 
      [UPLOAD_STATUS.QUEUED, UPLOAD_STATUS.VALIDATING, UPLOAD_STATUS.UPLOADING, UPLOAD_STATUS.PROCESSING].includes(upload.status)
    );

    if (activeUploads.length > 0 && !progressIntervalRef.current) {
      progressIntervalRef.current = setInterval(updateProgress, 1000);
    } else if (activeUploads.length === 0 && progressIntervalRef.current) {
      clearInterval(progressIntervalRef.current);
      progressIntervalRef.current = null;
    }
  }, [uploads]);

  // File validation
  const validateFile = useCallback((file) => {
    const errors = [];
    
    // Check file type
    if (!SUPPORTED_TYPES[file.type]) {
      errors.push(`Nieobsługiwany typ pliku: ${file.type}`);
    }
    
    // Check file size
    if (file.size > MAX_FILE_SIZE) {
      errors.push(`Plik za duży: ${(file.size / 1024 / 1024).toFixed(2)}MB (max 10MB)`);
    }
    
    // Check file name
    if (file.name.length > 255) {
      errors.push('Nazwa pliku za długa');
    }
    
    // Check for suspicious characters
    const suspiciousChars = /[<>:"|?*\\\/]/;
    if (suspiciousChars.test(file.name)) {
      errors.push('Nazwa pliku zawiera niedozwolone znaki');
    }
    
    return {
      valid: errors.length === 0,
      errors
    };
  }, []);

  // Handle file selection
  const handleFileSelect = useCallback((files) => {
    const fileList = Array.from(files);
    
    fileList.forEach(file => {
      const validation = validateFile(file);
      
      if (!validation.valid) {
        setGlobalError(`Błąd walidacji pliku "${file.name}": ${validation.errors.join(', ')}`);
        return;
      }
      
      // Add to upload queue
      const uploadId = generateUploadId();
      const newUpload = {
        id: uploadId,
        file,
        filename: file.name,
        fileSize: file.size,
        status: UPLOAD_STATUS.QUEUED,
        progress: 0,
        error: null,
        startedAt: new Date(),
        estimatedTime: estimateProcessingTime(file)
      };
      
      setUploads(prev => [...prev, newUpload]);
      
      // Start upload
      startUpload(newUpload);
    });
    
    // Clear file input
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  }, [validateFile]);

  // Start upload process
  const startUpload = async (upload) => {
    try {
      // Update status to validating
      updateUploadStatus(upload.id, UPLOAD_STATUS.VALIDATING);
      
      // Validate with server
      const validationResponse = await apiClient.post('/ocr/validate-upload/', {
        filename: upload.filename,
        fileSize: upload.fileSize,
        contentType: upload.file.type
      });
      
      if (!validationResponse.data.valid) {
        throw new Error(validationResponse.data.error || 'Walidacja pliku nie powiodła się');
      }
      
      // Update status to uploading
      updateUploadStatus(upload.id, UPLOAD_STATUS.UPLOADING);
      
      // Create form data
      const formData = new FormData();
      formData.append('document', upload.file);
      formData.append('upload_id', upload.id);
      
      // Upload with progress tracking
      const uploadResponse = await apiClient.post('/ocr/upload/', formData, {
        headers: {
          'Content-Type': 'multipart/form-data'
        },
        onUploadProgress: (progressEvent) => {
          const progress = Math.round((progressEvent.loaded * 100) / progressEvent.total);
          updateUploadProgress(upload.id, progress);
        }
      });
      
      // Update with server response
      const serverUploadId = uploadResponse.data.document_id;
      updateUploadStatus(upload.id, UPLOAD_STATUS.PROCESSING, { serverUploadId });
      
      // Notify completion
      if (onUploadComplete) {
        onUploadComplete(uploadResponse.data);
      }
      
    } catch (error) {
      console.error('Upload error:', error);
      const errorMessage = error.response?.data?.error || error.message || 'Błąd podczas przesyłania pliku';
      updateUploadStatus(upload.id, UPLOAD_STATUS.FAILED, { error: errorMessage });
      
      if (onUploadError) {
        onUploadError(error, upload);
      }
    }
  };

  // Update upload status
  const updateUploadStatus = (uploadId, status, additionalData = {}) => {
    setUploads(prev => prev.map(upload => 
      upload.id === uploadId 
        ? { 
            ...upload, 
            status, 
            ...additionalData,
            completedAt: [UPLOAD_STATUS.COMPLETED, UPLOAD_STATUS.FAILED, UPLOAD_STATUS.CANCELLED].includes(status) 
              ? new Date() 
              : upload.completedAt
          }
        : upload
    ));
  };

  // Update upload progress
  const updateUploadProgress = (uploadId, progress) => {
    setUploads(prev => prev.map(upload => 
      upload.id === uploadId ? { ...upload, progress } : upload
    ));
  };

  // Update progress from server
  const updateProgress = async () => {
    const activeUploads = uploads.filter(upload => 
      upload.serverUploadId && [UPLOAD_STATUS.PROCESSING].includes(upload.status)
    );

    for (const upload of activeUploads) {
      try {
        const response = await apiClient.get(`/ocr/progress/${upload.serverUploadId}/`);
        const serverProgress = response.data;
        
        // Update upload with server data
        setUploads(prev => prev.map(u => 
          u.id === upload.id 
            ? {
                ...u,
                status: mapServerStatus(serverProgress.status),
                progress: serverProgress.progress_percent || u.progress,
                error: serverProgress.error_message || u.error,
                processingTime: serverProgress.processing_time,
                confidenceScore: serverProgress.confidence_score
              }
            : u
        ));
        
      } catch (error) {
        console.error('Progress update error:', error);
      }
    }
  };

  // Map server status to client status
  const mapServerStatus = (serverStatus) => {
    const mapping = {
      'queued': UPLOAD_STATUS.QUEUED,
      'validating': UPLOAD_STATUS.VALIDATING,
      'uploading': UPLOAD_STATUS.UPLOADING,
      'processing': UPLOAD_STATUS.PROCESSING,
      'completed': UPLOAD_STATUS.COMPLETED,
      'failed': UPLOAD_STATUS.FAILED,
      'cancelled': UPLOAD_STATUS.CANCELLED
    };
    return mapping[serverStatus] || UPLOAD_STATUS.QUEUED;
  };

  // Cancel upload
  const cancelUpload = async (uploadId) => {
    const upload = uploads.find(u => u.id === uploadId);
    if (!upload) return;

    try {
      if (upload.serverUploadId) {
        await apiClient.post(`/ocr/cancel/${upload.serverUploadId}/`);
      }
      updateUploadStatus(uploadId, UPLOAD_STATUS.CANCELLED);
    } catch (error) {
      console.error('Cancel error:', error);
    }
  };

  // Retry upload
  const retryUpload = async (uploadId) => {
    const upload = uploads.find(u => u.id === uploadId);
    if (!upload) return;

    if (upload.serverUploadId) {
      try {
        await apiClient.post(`/ocr/retry/${upload.serverUploadId}/`);
        updateUploadStatus(uploadId, UPLOAD_STATUS.PROCESSING);
      } catch (error) {
        console.error('Retry error:', error);
      }
    } else {
      // Restart local upload
      updateUploadStatus(uploadId, UPLOAD_STATUS.QUEUED, { error: null });
      startUpload(upload);
    }
  };

  // Remove upload from list
  const removeUpload = (uploadId) => {
    setUploads(prev => prev.filter(u => u.id !== uploadId));
  };

  // Drag and drop handlers
  const handleDragEnter = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(true);
  };

  const handleDragLeave = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
  };

  const handleDragOver = (e) => {
    e.preventDefault();
    e.stopPropagation();
  };

  const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    
    const files = e.dataTransfer.files;
    if (files && files.length > 0) {
      handleFileSelect(files);
    }
  };

  // File input change handler
  const handleFileInputChange = (e) => {
    const files = e.target.files;
    if (files && files.length > 0) {
      handleFileSelect(files);
    }
  };

  // Utility functions
  const generateUploadId = () => {
    return `upload_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
  };

  const estimateProcessingTime = (file) => {
    const basetime = 10; // seconds
    const sizeFactor = Math.min(file.size / (5 * 1024 * 1024), 3); // Max 3x for large files
    const typeFactor = file.type === 'application/pdf' ? 1.5 : 1.0;
    return Math.max(Math.round(basetime * sizeFactor * typeFactor), 5);
  };

  const formatFileSize = (bytes) => {
    if (bytes === 0) return '0 B';
    const k = 1024;
    const sizes = ['B', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  const formatTime = (seconds) => {
    if (seconds < 60) return `${seconds}s`;
    const minutes = Math.floor(seconds / 60);
    const remainingSeconds = seconds % 60;
    return `${minutes}m ${remainingSeconds}s`;
  };

  // Status icon component
  const StatusIcon = ({ status }) => {
    const icons = {
      [UPLOAD_STATUS.QUEUED]: '⏳',
      [UPLOAD_STATUS.VALIDATING]: '🔍',
      [UPLOAD_STATUS.UPLOADING]: '⬆️',
      [UPLOAD_STATUS.PROCESSING]: '⚙️',
      [UPLOAD_STATUS.COMPLETED]: '✅',
      [UPLOAD_STATUS.FAILED]: '❌',
      [UPLOAD_STATUS.CANCELLED]: '🚫'
    };
    return <span className="status-icon">{icons[status] || '❓'}</span>;
  };

  // Progress bar component
  const ProgressBar = ({ progress, status }) => {
    const isActive = [UPLOAD_STATUS.UPLOADING, UPLOAD_STATUS.PROCESSING].includes(status);
    
    return (
      <div className="progress-container">
        <div className="progress-bar">
          <div 
            className={`progress-fill ${isActive ? 'active' : ''}`}
            style={{ width: `${progress}%` }}
          />
        </div>
        <span className="progress-text">{Math.round(progress)}%</span>
      </div>
    );
  };

  return (
    <div className="enhanced-ocr-upload">
      {/* Global Error Display */}
      {globalError && (
        <div className="error-banner">
          <span className="error-icon">⚠️</span>
          <span className="error-message">{globalError}</span>
          <button 
            className="error-close"
            onClick={() => setGlobalError('')}
          >
            ×
          </button>
        </div>
      )}

      {/* Upload Area */}
      <div 
        className={`upload-area ${dragActive ? 'drag-active' : ''}`}
        onDragEnter={handleDragEnter}
        onDragLeave={handleDragLeave}
        onDragOver={handleDragOver}
        onDrop={handleDrop}
      >
        <div className="upload-content">
          <div className="upload-icon">📄</div>
          <h3 className="upload-title">Przeciągnij pliki tutaj</h3>
          <p className="upload-subtitle">lub kliknij aby wybrać pliki</p>
          
          <input
            ref={fileInputRef}
            type="file"
            multiple
            accept=".pdf,.jpg,.jpeg,.png,.tiff"
            onChange={handleFileInputChange}
            className="file-input"
          />
          
          <button 
            className="select-files-btn"
            onClick={() => fileInputRef.current?.click()}
          >
            Wybierz pliki
          </button>
          
          <div className="supported-formats">
            <p>Obsługiwane formaty: PDF, JPEG, PNG, TIFF (max 10MB)</p>
          </div>
        </div>
      </div>

      {/* Upload Queue */}
      {uploads.length > 0 && (
        <div className="upload-queue">
          <h4 className="queue-title">Kolejka przesyłania ({uploads.length})</h4>
          
          <div className="upload-list">
            {uploads.map(upload => (
              <div key={upload.id} className={`upload-item ${upload.status}`}>
                <div className="upload-info">
                  <StatusIcon status={upload.status} />
                  <div className="file-details">
                    <div className="filename">{upload.filename}</div>
                    <div className="file-meta">
                      {formatFileSize(upload.fileSize)} • 
                      {upload.estimatedTime && ` ~${formatTime(upload.estimatedTime)}`}
                      {upload.confidenceScore && ` • Pewność: ${Math.round(upload.confidenceScore)}%`}
                    </div>
                  </div>
                </div>
                
                <div className="upload-progress">
                  <ProgressBar progress={upload.progress} status={upload.status} />
                </div>
                
                <div className="upload-actions">
                  {upload.status === UPLOAD_STATUS.FAILED && (
                    <button 
                      className="retry-btn"
                      onClick={() => retryUpload(upload.id)}
                      title="Spróbuj ponownie"
                    >
                      🔄
                    </button>
                  )}
                  
                  {[UPLOAD_STATUS.QUEUED, UPLOAD_STATUS.VALIDATING, UPLOAD_STATUS.UPLOADING].includes(upload.status) && (
                    <button 
                      className="cancel-btn"
                      onClick={() => cancelUpload(upload.id)}
                      title="Anuluj"
                    >
                      ⏹️
                    </button>
                  )}
                  
                  {[UPLOAD_STATUS.COMPLETED, UPLOAD_STATUS.FAILED, UPLOAD_STATUS.CANCELLED].includes(upload.status) && (
                    <button 
                      className="remove-btn"
                      onClick={() => removeUpload(upload.id)}
                      title="Usuń z listy"
                    >
                      🗑️
                    </button>
                  )}
                </div>
                
                {upload.error && (
                  <div className="upload-error">
                    <span className="error-icon">⚠️</span>
                    <span className="error-text">{upload.error}</span>
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Queue Status */}
      {Object.keys(queueStatus).length > 0 && (
        <div className="queue-status">
          <p>Kolejka: {queueStatus.queue_length || 0} • 
             Aktywne: {queueStatus.active_uploads || 0}/{queueStatus.max_concurrent || 3}
             {queueStatus.estimated_wait_time > 0 && ` • Czas oczekiwania: ~${formatTime(queueStatus.estimated_wait_time)}`}
          </p>
        </div>
      )}
    </div>
  );
};

export default EnhancedOCRUpload;