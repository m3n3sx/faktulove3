import React, { useState } from 'react';

// Simple Upload App without external dependencies
const SimpleUploadApp = ({ 
  apiBaseUrl = '/api/v1',
  csrfToken,
  maxFileSize = 10,
  supportedTypes = {},
  recentUploads = []
}) => {
  const [selectedFile, setSelectedFile] = useState(null);
  const [uploading, setUploading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [message, setMessage] = useState('');
  const [messageType, setMessageType] = useState('');

  const handleFileSelect = (event) => {
    const file = event.target.files[0];
    if (file) {
      // Validate file size
      if (file.size > maxFileSize * 1024 * 1024) {
        setMessage(`Plik jest za duży. Maksymalny rozmiar to ${maxFileSize}MB.`);
        setMessageType('error');
        return;
      }
      
      // Validate file type
      const allowedTypes = ['application/pdf', 'image/jpeg', 'image/png', 'image/tiff'];
      if (!allowedTypes.includes(file.type)) {
        setMessage('Nieobsługiwany typ pliku. Dozwolone: PDF, JPEG, PNG, TIFF.');
        setMessageType('error');
        return;
      }
      
      setSelectedFile(file);
      setMessage('');
      setMessageType('');
    }
  };

  const handleUpload = async () => {
    if (!selectedFile) {
      setMessage('Proszę wybrać plik do przesłania.');
      setMessageType('error');
      return;
    }

    setUploading(true);
    setUploadProgress(0);
    setMessage('Przesyłanie pliku...');
    setMessageType('info');

    const formData = new FormData();
    formData.append('document', selectedFile);

    try {
      const xhr = new XMLHttpRequest();
      
      xhr.upload.addEventListener('progress', (event) => {
        if (event.lengthComputable) {
          const progress = Math.round((event.loaded / event.total) * 100);
          setUploadProgress(progress);
        }
      });

      xhr.onload = function() {
        if (xhr.status === 200 || xhr.status === 302) {
          setMessage('Plik został pomyślnie przesłany!');
          setMessageType('success');
          setSelectedFile(null);
          setUploadProgress(0);
          
          // Redirect to results page after successful upload
          setTimeout(() => {
            window.location.href = '/ocr/results/';
          }, 2000);
        } else {
          setMessage('Błąd podczas przesyłania pliku. Spróbuj ponownie.');
          setMessageType('error');
        }
        setUploading(false);
      };

      xhr.onerror = function() {
        setMessage('Błąd połączenia. Sprawdź połączenie internetowe.');
        setMessageType('error');
        setUploading(false);
      };

      xhr.open('POST', '/ocr/upload/');
      xhr.setRequestHeader('X-CSRFToken', csrfToken);
      xhr.setRequestHeader('X-Requested-With', 'XMLHttpRequest');
      xhr.send(formData);

    } catch (error) {
      console.error('Upload error:', error);
      setMessage('Wystąpił błąd podczas przesyłania pliku.');
      setMessageType('error');
      setUploading(false);
    }
  };

  const handleDragOver = (event) => {
    event.preventDefault();
    event.currentTarget.classList.add('drag-over');
  };

  const handleDragLeave = (event) => {
    event.preventDefault();
    event.currentTarget.classList.remove('drag-over');
  };

  const handleDrop = (event) => {
    event.preventDefault();
    event.currentTarget.classList.remove('drag-over');
    
    const files = event.dataTransfer.files;
    if (files.length > 0) {
      const file = files[0];
      setSelectedFile(file);
    }
  };

  return React.createElement('div', { className: 'upload-app' },
    React.createElement('div', { className: 'upload-container' },
      React.createElement('h2', { className: 'upload-title' }, 'Przesyłanie dokumentu OCR'),
      
      // Upload area
      React.createElement('div', {
        className: `upload-area ${selectedFile ? 'has-file' : ''}`,
        onDragOver: handleDragOver,
        onDragLeave: handleDragLeave,
        onDrop: handleDrop
      },
        React.createElement('div', { className: 'upload-icon' }, '📄'),
        React.createElement('p', { className: 'upload-text' },
          selectedFile 
            ? `Wybrany plik: ${selectedFile.name}`
            : 'Przeciągnij plik tutaj lub kliknij aby wybrać'
        ),
        React.createElement('input', {
          type: 'file',
          id: 'file-input',
          className: 'file-input',
          accept: '.pdf,.jpg,.jpeg,.png,.tiff',
          onChange: handleFileSelect,
          disabled: uploading
        }),
        React.createElement('label', {
          htmlFor: 'file-input',
          className: 'file-input-label'
        }, 'Wybierz plik')
      ),

      // File info
      selectedFile && React.createElement('div', { className: 'file-info' },
        React.createElement('p', null, `Nazwa: ${selectedFile.name}`),
        React.createElement('p', null, `Rozmiar: ${(selectedFile.size / 1024 / 1024).toFixed(2)} MB`),
        React.createElement('p', null, `Typ: ${selectedFile.type}`)
      ),

      // Progress bar
      uploading && React.createElement('div', { className: 'progress-container' },
        React.createElement('div', { className: 'progress' },
          React.createElement('div', {
            className: 'progress-bar',
            style: { width: `${uploadProgress}%` }
          })
        ),
        React.createElement('p', { className: 'progress-text' }, `${uploadProgress}%`)
      ),

      // Message
      message && React.createElement('div', {
        className: `status-message ${messageType}`
      }, message),

      // Upload button
      React.createElement('button', {
        className: 'upload-button',
        onClick: handleUpload,
        disabled: !selectedFile || uploading
      }, uploading ? 'Przesyłanie...' : 'Prześlij dokument'),

      // Supported formats info
      React.createElement('div', { className: 'supported-formats' },
        React.createElement('h3', null, 'Obsługiwane formaty:'),
        React.createElement('ul', null,
          React.createElement('li', null, `PDF (max ${maxFileSize}MB)`),
          React.createElement('li', null, `JPEG, PNG (max ${maxFileSize}MB)`),
          React.createElement('li', null, `TIFF (max ${maxFileSize}MB)`)
        )
      )
    )
  );
};

// Export for global access
if (typeof window !== 'undefined') {
  window.UploadApp = SimpleUploadApp;
}

export default SimpleUploadApp;