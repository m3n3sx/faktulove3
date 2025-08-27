/**
 * OCR Handler for FaktuLove Application
 * Handles OCR file uploads, processing, and result management
 */

(function() {
    'use strict';

    const OCRHandler = {
        config: {
            maxFileSize: 10 * 1024 * 1024, // 10MB
            allowedTypes: ['application/pdf', 'image/jpeg', 'image/png', 'image/tiff'],
            uploadEndpoint: '/api/ocr/upload/',
            statusEndpoint: '/api/ocr/status/',
            resultsEndpoint: '/api/ocr/results/',
            pollInterval: 2000,
            maxPollTime: 300000 // 5 minutes
        },

        activeUploads: {},
        processingTasks: {},
        uploadQueue: [],

        /**
         * Initialize OCR handler
         */
        init: function() {
            this.setupEventListeners();
            this.setupDropZones();
            this.setupFileInputs();
            this.initializeExistingTasks();
            console.log('OCRHandler initialized');
        },

        /**
         * Setup event listeners
         */
        setupEventListeners: function() {
            const self = this;

            // File upload events
            document.addEventListener('change', function(e) {
                if (e.target.matches('input[type="file"][data-ocr-upload]')) {
                    self.handleFileSelection(e.target.files, e.target);
                }
            });

            // Upload button clicks
            document.addEventListener('click', function(e) {
                if (e.target.matches('[data-ocr-upload-btn]')) {
                    e.preventDefault();
                    const fileInput = document.querySelector(e.target.dataset.ocrUploadBtn);
                    if (fileInput) {
                        fileInput.click();
                    }
                }

                // Cancel upload
                if (e.target.matches('[data-cancel-upload]')) {
                    e.preventDefault();
                    const uploadId = e.target.dataset.cancelUpload;
                    self.cancelUpload(uploadId);
                }

                // Retry upload
                if (e.target.matches('[data-retry-upload]')) {
                    e.preventDefault();
                    const uploadId = e.target.dataset.retryUpload;
                    self.retryUpload(uploadId);
                }

                // View OCR results
                if (e.target.matches('[data-view-ocr-results]')) {
                    e.preventDefault();
                    const taskId = e.target.dataset.viewOcrResults;
                    self.viewOCRResults(taskId);
                }
            });

            // Form submissions with OCR data
            document.addEventListener('submit', function(e) {
                if (e.target.matches('form[data-ocr-form]')) {
                    self.handleOCRFormSubmission(e);
                }
            });
        },

        /**
         * Setup drag and drop zones
         */
        setupDropZones: function() {
            const dropZones = document.querySelectorAll('[data-ocr-dropzone]');
            const self = this;

            dropZones.forEach(function(dropZone) {
                dropZone.addEventListener('dragover', function(e) {
                    e.preventDefault();
                    this.classList.add('drag-over');
                });

                dropZone.addEventListener('dragleave', function(e) {
                    e.preventDefault();
                    this.classList.remove('drag-over');
                });

                dropZone.addEventListener('drop', function(e) {
                    e.preventDefault();
                    this.classList.remove('drag-over');
                    self.handleFileSelection(e.dataTransfer.files, this);
                });
            });
        },

        /**
         * Setup file inputs
         */
        setupFileInputs: function() {
            const fileInputs = document.querySelectorAll('input[type="file"][data-ocr-upload]');
            
            fileInputs.forEach(function(input) {
                // Set accept attribute
                input.accept = '.pdf,.jpg,.jpeg,.png,.tiff';
                
                // Allow multiple files if specified
                if (input.hasAttribute('data-multiple')) {
                    input.multiple = true;
                }
            });
        },

        /**
         * Initialize existing OCR tasks
         */
        initializeExistingTasks: function() {
            // Check for existing processing tasks on page load
            const existingTasks = document.querySelectorAll('[data-ocr-task-id]');
            const self = this;

            existingTasks.forEach(function(element) {
                const taskId = element.dataset.ocrTaskId;
                const status = element.dataset.ocrStatus;
                
                if (status === 'processing' || status === 'pending') {
                    self.startPolling(taskId, element);
                }
            });
        },

        /**
         * Handle file selection
         */
        handleFileSelection: function(files, sourceElement) {
            const fileArray = Array.from(files);
            const self = this;

            fileArray.forEach(function(file) {
                if (self.validateFile(file)) {
                    self.queueUpload(file, sourceElement);
                } else {
                    self.showError(`Invalid file: ${file.name}`, sourceElement);
                }
            });

            this.processUploadQueue();
        },

        /**
         * Validate file
         */
        validateFile: function(file) {
            // Check file size
            if (file.size > this.config.maxFileSize) {
                this.showError(`File too large: ${file.name} (max ${this.config.maxFileSize / 1024 / 1024}MB)`);
                return false;
            }

            // Check file type
            if (!this.config.allowedTypes.includes(file.type)) {
                this.showError(`Unsupported file type: ${file.name}`);
                return false;
            }

            return true;
        },

        /**
         * Queue file for upload
         */
        queueUpload: function(file, sourceElement) {
            const uploadId = this.generateUploadId();
            
            this.uploadQueue.push({
                id: uploadId,
                file: file,
                sourceElement: sourceElement,
                status: 'queued',
                progress: 0
            });

            this.showUploadQueued(uploadId, file, sourceElement);
        },

        /**
         * Process upload queue
         */
        processUploadQueue: function() {
            const queuedUploads = this.uploadQueue.filter(upload => upload.status === 'queued');
            const self = this;

            queuedUploads.forEach(function(upload) {
                self.startUpload(upload);
            });
        },

        /**
         * Start file upload
         */
        startUpload: function(upload) {
            upload.status = 'uploading';
            this.activeUploads[upload.id] = upload;

            const formData = new FormData();
            formData.append('file', upload.file);
            formData.append('upload_id', upload.id);

            // Add CSRF token
            if (window.CSRFUtils) {
                formData.append('csrfmiddlewaretoken', window.CSRFUtils.getToken());
            }

            const xhr = new XMLHttpRequest();
            const self = this;

            // Upload progress
            xhr.upload.addEventListener('progress', function(e) {
                if (e.lengthComputable) {
                    const progress = (e.loaded / e.total) * 100;
                    self.updateUploadProgress(upload.id, progress);
                }
            });

            // Upload complete
            xhr.addEventListener('load', function() {
                if (xhr.status === 200) {
                    try {
                        const response = JSON.parse(xhr.responseText);
                        self.handleUploadSuccess(upload.id, response);
                    } catch (e) {
                        self.handleUploadError(upload.id, 'Invalid response from server');
                    }
                } else {
                    self.handleUploadError(upload.id, `Upload failed: ${xhr.status} ${xhr.statusText}`);
                }
            });

            // Upload error
            xhr.addEventListener('error', function() {
                self.handleUploadError(upload.id, 'Network error during upload');
            });

            // Upload timeout
            xhr.addEventListener('timeout', function() {
                self.handleUploadError(upload.id, 'Upload timeout');
            });

            xhr.open('POST', this.config.uploadEndpoint);
            xhr.timeout = 60000; // 1 minute timeout
            xhr.send(formData);

            this.showUploadStarted(upload.id, upload.file, upload.sourceElement);
        },

        /**
         * Handle upload success
         */
        handleUploadSuccess: function(uploadId, response) {
            const upload = this.activeUploads[uploadId];
            if (!upload) return;

            upload.status = 'uploaded';
            upload.taskId = response.task_id;

            this.showUploadComplete(uploadId, response);

            // Start polling for OCR results
            if (response.task_id) {
                this.startPolling(response.task_id, upload.sourceElement);
            }

            // Clean up
            delete this.activeUploads[uploadId];
        },

        /**
         * Handle upload error
         */
        handleUploadError: function(uploadId, error) {
            const upload = this.activeUploads[uploadId];
            if (!upload) return;

            upload.status = 'error';
            upload.error = error;

            this.showUploadError(uploadId, error);

            // Clean up
            delete this.activeUploads[uploadId];
        },

        /**
         * Start polling for OCR results
         */
        startPolling: function(taskId, sourceElement) {
            if (this.processingTasks[taskId]) {
                return; // Already polling this task
            }

            const self = this;
            const startTime = Date.now();

            const poll = function() {
                fetch(`${self.config.statusEndpoint}${taskId}/`, {
                    headers: window.CSRFUtils ? window.CSRFUtils.getCSRFHeader() : {}
                })
                .then(response => response.json())
                .then(data => {
                    self.handleStatusUpdate(taskId, data, sourceElement);

                    // Continue polling if still processing
                    if (data.status === 'processing' || data.status === 'pending') {
                        const elapsed = Date.now() - startTime;
                        if (elapsed < self.config.maxPollTime) {
                            setTimeout(poll, self.config.pollInterval);
                        } else {
                            self.handlePollingTimeout(taskId);
                        }
                    } else {
                        // Polling complete
                        delete self.processingTasks[taskId];
                    }
                })
                .catch(error => {
                    console.error('OCR status polling error:', error);
                    self.handlePollingError(taskId, error);
                });
            };

            this.processingTasks[taskId] = { startTime: startTime, sourceElement: sourceElement };
            this.showProcessingStarted(taskId, sourceElement);
            poll();
        },

        /**
         * Handle status update
         */
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

        /**
         * Handle polling timeout
         */
        handlePollingTimeout: function(taskId) {
            this.showProcessingTimeout(taskId);
            delete this.processingTasks[taskId];
        },

        /**
         * Handle polling error
         */
        handlePollingError: function(taskId, error) {
            this.showProcessingError(taskId, error);
            delete this.processingTasks[taskId];
        },

        /**
         * Cancel upload
         */
        cancelUpload: function(uploadId) {
            const upload = this.activeUploads[uploadId];
            if (upload && upload.xhr) {
                upload.xhr.abort();
                upload.status = 'cancelled';
                this.showUploadCancelled(uploadId);
                delete this.activeUploads[uploadId];
            }
        },

        /**
         * Retry upload
         */
        retryUpload: function(uploadId) {
            const upload = this.uploadQueue.find(u => u.id === uploadId);
            if (upload) {
                upload.status = 'queued';
                upload.progress = 0;
                this.startUpload(upload);
            }
        },

        /**
         * View OCR results
         */
        viewOCRResults: function(taskId) {
            fetch(`${this.config.resultsEndpoint}${taskId}/`, {
                headers: window.CSRFUtils ? window.CSRFUtils.getCSRFHeader() : {}
            })
            .then(response => response.json())
            .then(data => {
                this.displayOCRResults(data);
            })
            .catch(error => {
                console.error('Failed to load OCR results:', error);
                this.showError('Failed to load OCR results');
            });
        },

        /**
         * Display OCR results
         */
        displayOCRResults: function(results) {
            // Create modal or popup to show results
            const modal = this.createResultsModal(results);
            document.body.appendChild(modal);
            modal.style.display = 'block';
        },

        /**
         * Create results modal
         */
        createResultsModal: function(results) {
            const modal = document.createElement('div');
            modal.className = 'ocr-results-modal';
            modal.style.cssText = `
                position: fixed;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                background: rgba(0, 0, 0, 0.8);
                z-index: 10000;
                display: flex;
                align-items: center;
                justify-content: center;
            `;

            const content = document.createElement('div');
            content.className = 'modal-content';
            content.style.cssText = `
                background: white;
                padding: 20px;
                border-radius: 8px;
                max-width: 80%;
                max-height: 80%;
                overflow-y: auto;
            `;

            content.innerHTML = `
                <div class="modal-header" style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px;">
                    <h3>OCR Results</h3>
                    <button class="close-btn" style="background: none; border: none; font-size: 24px; cursor: pointer;">&times;</button>
                </div>
                <div class="modal-body">
                    <div class="ocr-confidence" style="margin-bottom: 15px;">
                        <strong>Confidence: ${results.confidence || 'N/A'}%</strong>
                    </div>
                    <div class="ocr-text" style="background: #f5f5f5; padding: 15px; border-radius: 4px; white-space: pre-wrap;">
                        ${results.text || 'No text extracted'}
                    </div>
                    ${results.fields ? this.formatExtractedFields(results.fields) : ''}
                </div>
                <div class="modal-footer" style="margin-top: 20px; text-align: right;">
                    <button class="btn btn-primary use-results-btn">Use Results</button>
                    <button class="btn btn-secondary close-btn" style="margin-left: 10px;">Close</button>
                </div>
            `;

            modal.appendChild(content);

            // Event listeners
            const closeButtons = content.querySelectorAll('.close-btn');
            closeButtons.forEach(btn => {
                btn.addEventListener('click', () => {
                    modal.remove();
                });
            });

            const useResultsBtn = content.querySelector('.use-results-btn');
            if (useResultsBtn) {
                useResultsBtn.addEventListener('click', () => {
                    this.useOCRResults(results);
                    modal.remove();
                });
            }

            // Close on outside click
            modal.addEventListener('click', (e) => {
                if (e.target === modal) {
                    modal.remove();
                }
            });

            return modal;
        },

        /**
         * Format extracted fields
         */
        formatExtractedFields: function(fields) {
            let html = '<div class="extracted-fields" style="margin-top: 20px;"><h4>Extracted Fields:</h4>';
            
            Object.entries(fields).forEach(([key, value]) => {
                html += `
                    <div class="field-row" style="margin-bottom: 10px; display: flex;">
                        <label style="width: 150px; font-weight: bold;">${key}:</label>
                        <span>${value}</span>
                    </div>
                `;
            });
            
            html += '</div>';
            return html;
        },

        /**
         * Use OCR results to fill form
         */
        useOCRResults: function(results) {
            if (results.fields) {
                Object.entries(results.fields).forEach(([fieldName, value]) => {
                    const field = document.querySelector(`[name="${fieldName}"], #${fieldName}`);
                    if (field) {
                        field.value = value;
                        // Trigger change event
                        field.dispatchEvent(new Event('change', { bubbles: true }));
                    }
                });
            }

            this.showMessage('OCR results applied to form', 'success');
        },

        /**
         * Handle OCR form submission
         */
        handleOCRFormSubmission: function(event) {
            // Check if there are pending OCR tasks
            const pendingTasks = Object.keys(this.processingTasks);
            
            if (pendingTasks.length > 0) {
                event.preventDefault();
                this.showMessage('Please wait for OCR processing to complete', 'warning');
                return false;
            }

            return true;
        },

        /**
         * UI update methods
         */
        showUploadQueued: function(uploadId, file, sourceElement) {
            this.updateUploadStatus(uploadId, 'Queued for upload...', 'info', sourceElement);
        },

        showUploadStarted: function(uploadId, file, sourceElement) {
            this.updateUploadStatus(uploadId, 'Uploading...', 'info', sourceElement);
        },

        showUploadComplete: function(uploadId, response) {
            this.updateUploadStatus(uploadId, 'Upload complete, processing...', 'success');
        },

        showUploadError: function(uploadId, error) {
            this.updateUploadStatus(uploadId, `Upload failed: ${error}`, 'error');
        },

        showUploadCancelled: function(uploadId) {
            this.updateUploadStatus(uploadId, 'Upload cancelled', 'warning');
        },

        showProcessingStarted: function(taskId, sourceElement) {
            this.updateProcessingStatus(taskId, 'OCR processing started...', 'info', sourceElement);
        },

        showProcessingPending: function(taskId, sourceElement) {
            this.updateProcessingStatus(taskId, 'OCR processing pending...', 'info', sourceElement);
        },

        showProcessingInProgress: function(taskId, progress, sourceElement) {
            this.updateProcessingStatus(taskId, `OCR processing... ${progress}%`, 'info', sourceElement);
        },

        showProcessingComplete: function(taskId, results, sourceElement) {
            this.updateProcessingStatus(taskId, 'OCR processing complete!', 'success', sourceElement);
            this.showResultsButton(taskId, sourceElement);
        },

        showProcessingFailed: function(taskId, error, sourceElement) {
            this.updateProcessingStatus(taskId, `OCR processing failed: ${error}`, 'error', sourceElement);
        },

        showProcessingTimeout: function(taskId) {
            this.updateProcessingStatus(taskId, 'OCR processing timeout', 'warning');
        },

        showProcessingError: function(taskId, error) {
            this.updateProcessingStatus(taskId, `OCR processing error: ${error}`, 'error');
        },

        /**
         * Update upload status display
         */
        updateUploadStatus: function(uploadId, message, type, sourceElement) {
            // Find or create status element
            let statusElement = document.getElementById(`upload-status-${uploadId}`);
            
            if (!statusElement) {
                statusElement = document.createElement('div');
                statusElement.id = `upload-status-${uploadId}`;
                statusElement.className = 'upload-status';
                
                if (sourceElement) {
                    sourceElement.parentNode.appendChild(statusElement);
                } else {
                    document.body.appendChild(statusElement);
                }
            }

            statusElement.className = `upload-status status-${type}`;
            statusElement.textContent = message;
        },

        /**
         * Update upload progress
         */
        updateUploadProgress: function(uploadId, progress) {
            const statusElement = document.getElementById(`upload-status-${uploadId}`);
            if (statusElement) {
                statusElement.textContent = `Uploading... ${Math.round(progress)}%`;
            }
        },

        /**
         * Update processing status display
         */
        updateProcessingStatus: function(taskId, message, type, sourceElement) {
            // Find or create status element
            let statusElement = document.getElementById(`processing-status-${taskId}`);
            
            if (!statusElement) {
                statusElement = document.createElement('div');
                statusElement.id = `processing-status-${taskId}`;
                statusElement.className = 'processing-status';
                
                if (sourceElement) {
                    sourceElement.parentNode.appendChild(statusElement);
                } else {
                    document.body.appendChild(statusElement);
                }
            }

            statusElement.className = `processing-status status-${type}`;
            statusElement.textContent = message;
        },

        /**
         * Show results button
         */
        showResultsButton: function(taskId, sourceElement) {
            const button = document.createElement('button');
            button.textContent = 'View Results';
            button.className = 'btn btn-primary';
            button.dataset.viewOcrResults = taskId;
            
            const statusElement = document.getElementById(`processing-status-${taskId}`);
            if (statusElement) {
                statusElement.appendChild(button);
            }
        },

        /**
         * Utility methods
         */
        generateUploadId: function() {
            return 'upload-' + Date.now() + '-' + Math.random().toString(36).substr(2, 9);
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
            
            if (sourceElement) {
                const errorElement = document.createElement('div');
                errorElement.className = 'ocr-error';
                errorElement.textContent = message;
                errorElement.style.color = '#dc3545';
                sourceElement.parentNode.appendChild(errorElement);
                
                setTimeout(() => {
                    errorElement.remove();
                }, 5000);
            }
        }
    };

    // Initialize OCR handler when DOM is ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', function() {
            OCRHandler.init();
        });
    } else {
        OCRHandler.init();
    }

    // Make OCRHandler globally available
    window.OCRHandler = OCRHandler;

})();