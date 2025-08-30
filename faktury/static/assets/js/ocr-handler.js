
/**
 * Enhanced OCR Handler for FaktuLove Application
 */

(function() {
    'use strict';

    const OCRHandler = {
        config: {
            maxFileSize: 10 * 1024 * 1024, // 10MB
            allowedTypes: ['application/pdf', 'image/jpeg', 'image/png', 'image/tiff'],
            uploadEndpoint: '/ocr/api/upload/',
            statusEndpoint: '/ocr/api/status/',
            pollInterval: 2000
        },

        init: function() {
            this.setupEventListeners();
            this.setupDropZones();
            console.log('✅ OCRHandler initialized');
        },

        setupEventListeners: function() {
            const self = this;

            // File upload events
            $(document).on('change', 'input[type="file"][data-ocr-upload]', function() {
                self.handleFileSelection(this.files, this);
            });

            // Upload button clicks
            $(document).on('click', '[data-ocr-upload-btn]', function(e) {
                e.preventDefault();
                const fileInput = $($(this).data('ocr-upload-btn'));
                if (fileInput.length) {
                    fileInput.click();
                }
            });

            // OCR navigation
            $(document).on('click', 'a[href*="ocr"]', function(e) {
                console.log('🔗 OCR link clicked:', $(this).attr('href'));
            });
        },

        setupDropZones: function() {
            const dropZones = $('[data-ocr-dropzone]');
            const self = this;

            dropZones.on('dragover', function(e) {
                e.preventDefault();
                $(this).addClass('drag-over');
            });

            dropZones.on('dragleave', function(e) {
                e.preventDefault();
                $(this).removeClass('drag-over');
            });

            dropZones.on('drop', function(e) {
                e.preventDefault();
                $(this).removeClass('drag-over');
                self.handleFileSelection(e.originalEvent.dataTransfer.files, this);
            });
        },

        handleFileSelection: function(files, sourceElement) {
            const fileArray = Array.from(files);
            const self = this;

            fileArray.forEach(function(file) {
                if (self.validateFile(file)) {
                    self.uploadFile(file, sourceElement);
                } else {
                    self.showError(`Invalid file: ${file.name}`, sourceElement);
                }
            });
        },

        validateFile: function(file) {
            if (file.size > this.config.maxFileSize) {
                this.showError(`File too large: ${file.name}`);
                return false;
            }

            if (!this.config.allowedTypes.includes(file.type)) {
                this.showError(`Unsupported file type: ${file.name}`);
                return false;
            }

            return true;
        },

        uploadFile: function(file, sourceElement) {
            const formData = new FormData();
            formData.append('file', file);
            
            if (window.CSRFUtils) {
                formData.append('csrfmiddlewaretoken', window.CSRFUtils.getToken());
            }

            const self = this;
            
            $.ajax({
                url: this.config.uploadEndpoint,
                type: 'POST',
                data: formData,
                processData: false,
                contentType: false,
                success: function(response) {
                    self.handleUploadSuccess(response, sourceElement);
                },
                error: function(xhr, status, error) {
                    self.handleUploadError(error, sourceElement);
                }
            });

            this.showUploadStarted(file, sourceElement);
        },

        handleUploadSuccess: function(response, sourceElement) {
            this.showUploadComplete(response, sourceElement);
            
            if (response.task_id) {
                this.startPolling(response.task_id, sourceElement);
            }
        },

        handleUploadError: function(error, sourceElement) {
            this.showUploadError(error, sourceElement);
        },

        startPolling: function(taskId, sourceElement) {
            const self = this;
            
            const poll = function() {
                $.get(self.config.statusEndpoint + taskId + '/')
                    .done(function(data) {
                        self.handleStatusUpdate(taskId, data, sourceElement);
                        
                        if (data.status === 'processing' || data.status === 'pending') {
                            setTimeout(poll, self.config.pollInterval);
                        }
                    })
                    .fail(function() {
                        self.showError('Failed to check OCR status');
                    });
            };
            
            poll();
        },

        handleStatusUpdate: function(taskId, data, sourceElement) {
            switch (data.status) {
                case 'pending':
                    this.showProcessingPending(taskId, sourceElement);
                    break;
                case 'processing':
                    this.showProcessingInProgress(taskId, data.progress || 0, sourceElement);
                    break;
                case 'completed':
                    this.showProcessingComplete(taskId, data.results, sourceElement);
                    break;
                case 'failed':
                    this.showProcessingFailed(taskId, data.error, sourceElement);
                    break;
            }
        },

        // UI Methods
        showUploadStarted: function(file, sourceElement) {
            this.showMessage(`Uploading ${file.name}...`, 'info');
        },

        showUploadComplete: function(response, sourceElement) {
            this.showMessage('Upload complete, processing...', 'success');
        },

        showUploadError: function(error, sourceElement) {
            this.showMessage(`Upload failed: ${error}`, 'error');
        },

        showProcessingPending: function(taskId, sourceElement) {
            this.showMessage('OCR processing pending...', 'info');
        },

        showProcessingInProgress: function(taskId, progress, sourceElement) {
            this.showMessage(`OCR processing... ${progress}%`, 'info');
        },

        showProcessingComplete: function(taskId, results, sourceElement) {
            this.showMessage('OCR processing complete!', 'success');
        },

        showProcessingFailed: function(taskId, error, sourceElement) {
            this.showMessage(`OCR processing failed: ${error}`, 'error');
        },

        showMessage: function(message, type) {
            if (typeof Toastify !== 'undefined') {
                const backgroundColor = type === 'success' ? '#28a745' : 
                                     type === 'error' ? '#dc3545' : 
                                     type === 'warning' ? '#ffc107' : '#17a2b8';
                
                Toastify({
                    text: message,
                    duration: 5000,
                    gravity: 'top',
                    position: 'right',
                    backgroundColor: backgroundColor
                }).showToast();
            } else {
                console.log(`${type.toUpperCase()}: ${message}`);
            }
        },

        showError: function(message, sourceElement) {
            this.showMessage(message, 'error');
        }
    };

    // Initialize when document is ready
    $(document).ready(function() {
        OCRHandler.init();
    });

    // Make globally available
    window.OCRHandler = OCRHandler;

})();
