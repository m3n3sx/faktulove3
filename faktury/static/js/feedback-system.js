/**
 * Feedback System for FaktuLove
 * 
 * Provides success feedback, confirmation messages, and progress indicators
 * for long-running operations with Polish language support.
 */

class FeedbackSystem {
    constructor(options = {}) {
        this.options = {
            autoHideDelay: 5000,
            progressUpdateInterval: 500,
            animationDuration: 300,
            position: 'top-right',
            maxNotifications: 5,
            ...options
        };
        
        this.notifications = [];
        this.progressBars = new Map();
        
        this.init();
    }
    
    init() {
        this.createNotificationContainer();
        this.setupStyles();
        this.setupEventListeners();
    }
    
    createNotificationContainer() {
        if (document.getElementById('notification-container')) return;
        
        const container = document.createElement('div');
        container.id = 'notification-container';
        container.className = `notification-container position-${this.options.position}`;
        document.body.appendChild(container);
    }
    
    setupStyles() {
        if (document.getElementById('feedback-system-styles')) return;
        
        const style = document.createElement('style');
        style.id = 'feedback-system-styles';
        style.textContent = `
            .notification-container {
                position: fixed;
                z-index: 9999;
                pointer-events: none;
                max-width: 400px;
            }
            
            .notification-container.position-top-right {
                top: 20px;
                right: 20px;
            }
            
            .notification-container.position-top-left {
                top: 20px;
                left: 20px;
            }
            
            .notification-container.position-bottom-right {
                bottom: 20px;
                right: 20px;
            }
            
            .notification-container.position-bottom-left {
                bottom: 20px;
                left: 20px;
            }
            
            .notification {
                background: white;
                border-radius: 8px;
                box-shadow: 0 4px 20px rgba(0,0,0,0.15);
                margin-bottom: 10px;
                padding: 16px;
                pointer-events: auto;
                position: relative;
                overflow: hidden;
                transform: translateX(100%);
                opacity: 0;
                transition: all 0.3s ease;
                border-left: 4px solid #007bff;
            }
            
            .notification.show {
                transform: translateX(0);
                opacity: 1;
            }
            
            .notification.success {
                border-left-color: #28a745;
            }
            
            .notification.error {
                border-left-color: #dc3545;
            }
            
            .notification.warning {
                border-left-color: #ffc107;
            }
            
            .notification.info {
                border-left-color: #17a2b8;
            }
            
            .notification-header {
                display: flex;
                align-items: center;
                justify-content: space-between;
                margin-bottom: 8px;
            }
            
            .notification-title {
                display: flex;
                align-items: center;
                gap: 8px;
                font-weight: 600;
                color: #343a40;
            }
            
            .notification-icon {
                width: 20px;
                height: 20px;
                flex-shrink: 0;
            }
            
            .notification-close {
                background: none;
                border: none;
                color: #6c757d;
                cursor: pointer;
                font-size: 18px;
                padding: 0;
                width: 24px;
                height: 24px;
                display: flex;
                align-items: center;
                justify-content: center;
                border-radius: 4px;
                transition: all 0.2s ease;
            }
            
            .notification-close:hover {
                background: #f8f9fa;
                color: #495057;
            }
            
            .notification-message {
                color: #6c757d;
                line-height: 1.4;
                margin-bottom: 8px;
            }
            
            .notification-actions {
                display: flex;
                gap: 8px;
                margin-top: 12px;
            }
            
            .notification-action {
                background: #007bff;
                border: none;
                border-radius: 4px;
                color: white;
                cursor: pointer;
                font-size: 12px;
                padding: 6px 12px;
                transition: all 0.2s ease;
            }
            
            .notification-action:hover {
                background: #0056b3;
            }
            
            .notification-action.secondary {
                background: #6c757d;
            }
            
            .notification-action.secondary:hover {
                background: #5a6268;
            }
            
            .notification-progress {
                position: absolute;
                bottom: 0;
                left: 0;
                height: 3px;
                background: rgba(0,123,255,0.3);
                transition: width 0.3s ease;
            }
            
            .progress-indicator {
                background: white;
                border-radius: 8px;
                box-shadow: 0 4px 20px rgba(0,0,0,0.15);
                padding: 20px;
                margin: 20px;
                border-left: 4px solid #007bff;
            }
            
            .progress-header {
                display: flex;
                align-items: center;
                justify-content: space-between;
                margin-bottom: 16px;
            }
            
            .progress-title {
                display: flex;
                align-items: center;
                gap: 12px;
                font-weight: 600;
                color: #343a40;
            }
            
            .progress-spinner {
                width: 20px;
                height: 20px;
                border: 2px solid #e9ecef;
                border-top: 2px solid #007bff;
                border-radius: 50%;
                animation: spin 1s linear infinite;
            }
            
            @keyframes spin {
                0% { transform: rotate(0deg); }
                100% { transform: rotate(360deg); }
            }
            
            .progress-percentage {
                font-weight: 600;
                color: #007bff;
            }
            
            .progress-bar-container {
                background: #e9ecef;
                border-radius: 4px;
                height: 8px;
                overflow: hidden;
                margin-bottom: 12px;
            }
            
            .progress-bar {
                background: linear-gradient(90deg, #007bff, #0056b3);
                height: 100%;
                transition: width 0.3s ease;
                border-radius: 4px;
            }
            
            .progress-details {
                font-size: 14px;
                color: #6c757d;
                line-height: 1.4;
            }
            
            .progress-steps {
                margin-top: 16px;
            }
            
            .progress-step {
                display: flex;
                align-items: center;
                gap: 12px;
                padding: 8px 0;
                border-bottom: 1px solid #f8f9fa;
            }
            
            .progress-step:last-child {
                border-bottom: none;
            }
            
            .progress-step-icon {
                width: 20px;
                height: 20px;
                border-radius: 50%;
                display: flex;
                align-items: center;
                justify-content: center;
                font-size: 12px;
                flex-shrink: 0;
            }
            
            .progress-step.completed .progress-step-icon {
                background: #28a745;
                color: white;
            }
            
            .progress-step.active .progress-step-icon {
                background: #007bff;
                color: white;
            }
            
            .progress-step.pending .progress-step-icon {
                background: #e9ecef;
                color: #6c757d;
            }
            
            .progress-step-text {
                flex: 1;
                font-size: 14px;
            }
            
            .progress-step.completed .progress-step-text {
                color: #28a745;
            }
            
            .progress-step.active .progress-step-text {
                color: #007bff;
                font-weight: 500;
            }
            
            .progress-step.pending .progress-step-text {
                color: #6c757d;
            }
            
            .confirmation-modal {
                position: fixed;
                top: 0;
                left: 0;
                right: 0;
                bottom: 0;
                background: rgba(0,0,0,0.5);
                display: flex;
                align-items: center;
                justify-content: center;
                z-index: 10000;
                opacity: 0;
                visibility: hidden;
                transition: all 0.3s ease;
            }
            
            .confirmation-modal.show {
                opacity: 1;
                visibility: visible;
            }
            
            .confirmation-dialog {
                background: white;
                border-radius: 12px;
                box-shadow: 0 10px 40px rgba(0,0,0,0.3);
                max-width: 500px;
                width: 90%;
                padding: 24px;
                transform: scale(0.9);
                transition: transform 0.3s ease;
            }
            
            .confirmation-modal.show .confirmation-dialog {
                transform: scale(1);
            }
            
            .confirmation-header {
                display: flex;
                align-items: center;
                gap: 16px;
                margin-bottom: 16px;
            }
            
            .confirmation-icon {
                width: 48px;
                height: 48px;
                border-radius: 50%;
                display: flex;
                align-items: center;
                justify-content: center;
                font-size: 24px;
                flex-shrink: 0;
            }
            
            .confirmation-icon.success {
                background: #d4edda;
                color: #28a745;
            }
            
            .confirmation-icon.error {
                background: #f8d7da;
                color: #dc3545;
            }
            
            .confirmation-icon.warning {
                background: #fff3cd;
                color: #ffc107;
            }
            
            .confirmation-title {
                font-size: 18px;
                font-weight: 600;
                color: #343a40;
                margin: 0;
            }
            
            .confirmation-message {
                color: #6c757d;
                line-height: 1.5;
                margin-bottom: 24px;
            }
            
            .confirmation-actions {
                display: flex;
                gap: 12px;
                justify-content: flex-end;
            }
            
            .confirmation-button {
                border: none;
                border-radius: 6px;
                cursor: pointer;
                font-weight: 500;
                padding: 10px 20px;
                transition: all 0.2s ease;
            }
            
            .confirmation-button.primary {
                background: #007bff;
                color: white;
            }
            
            .confirmation-button.primary:hover {
                background: #0056b3;
            }
            
            .confirmation-button.secondary {
                background: #6c757d;
                color: white;
            }
            
            .confirmation-button.secondary:hover {
                background: #5a6268;
            }
            
            .confirmation-button.danger {
                background: #dc3545;
                color: white;
            }
            
            .confirmation-button.danger:hover {
                background: #c82333;
            }
            
            @media (max-width: 768px) {
                .notification-container {
                    left: 10px !important;
                    right: 10px !important;
                    max-width: none;
                }
                
                .notification {
                    margin-bottom: 8px;
                    padding: 12px;
                }
                
                .confirmation-dialog {
                    margin: 20px;
                    padding: 20px;
                }
                
                .confirmation-actions {
                    flex-direction: column;
                }
            }
        `;
        document.head.appendChild(style);
    }
    
    setupEventListeners() {
        // Listen for escape key to close modals
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape') {
                this.closeAllModals();
            }
        });
    }
    
    // Notification methods
    showNotification(type, title, message, options = {}) {
        const notification = this.createNotification(type, title, message, options);
        this.addNotification(notification);
        return notification.id;
    }
    
    showSuccess(title, message, options = {}) {
        return this.showNotification('success', title, message, options);
    }
    
    showError(title, message, options = {}) {
        return this.showNotification('error', title, message, options);
    }
    
    showWarning(title, message, options = {}) {
        return this.showNotification('warning', title, message, options);
    }
    
    showInfo(title, message, options = {}) {
        return this.showNotification('info', title, message, options);
    }
    
    createNotification(type, title, message, options = {}) {
        const id = `notification-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
        
        const notification = document.createElement('div');
        notification.id = id;
        notification.className = `notification ${type}`;
        
        const iconMap = {
            success: 'fas fa-check-circle',
            error: 'fas fa-exclamation-circle',
            warning: 'fas fa-exclamation-triangle',
            info: 'fas fa-info-circle'
        };
        
        notification.innerHTML = `
            <div class="notification-header">
                <div class="notification-title">
                    <i class="${iconMap[type]} notification-icon"></i>
                    <span>${title}</span>
                </div>
                <button class="notification-close" onclick="feedbackSystem.closeNotification('${id}')">
                    <i class="fas fa-times"></i>
                </button>
            </div>
            <div class="notification-message">${message}</div>
            ${options.actions ? this.createNotificationActions(options.actions, id) : ''}
            ${options.autoHide !== false ? '<div class="notification-progress"></div>' : ''}
        `;
        
        return {
            id,
            element: notification,
            type,
            title,
            message,
            options
        };
    }
    
    createNotificationActions(actions, notificationId) {
        const actionsHtml = actions.map(action => `
            <button class="notification-action ${action.type || 'primary'}" 
                    onclick="feedbackSystem.handleNotificationAction('${notificationId}', '${action.id}')">
                ${action.text}
            </button>
        `).join('');
        
        return `<div class="notification-actions">${actionsHtml}</div>`;
    }
    
    addNotification(notification) {
        const container = document.getElementById('notification-container');
        
        // Remove oldest notifications if we exceed the limit
        while (this.notifications.length >= this.options.maxNotifications) {
            const oldest = this.notifications.shift();
            this.closeNotification(oldest.id);
        }
        
        // Add to container
        container.appendChild(notification.element);
        this.notifications.push(notification);
        
        // Trigger animation
        setTimeout(() => {
            notification.element.classList.add('show');
        }, 10);
        
        // Auto-hide if enabled
        if (notification.options.autoHide !== false) {
            this.startAutoHideTimer(notification);
        }
    }
    
    startAutoHideTimer(notification) {
        const progressBar = notification.element.querySelector('.notification-progress');
        if (!progressBar) return;
        
        const duration = notification.options.autoHideDelay || this.options.autoHideDelay;
        let elapsed = 0;
        
        const interval = setInterval(() => {
            elapsed += 100;
            const progress = (elapsed / duration) * 100;
            progressBar.style.width = `${progress}%`;
            
            if (elapsed >= duration) {
                clearInterval(interval);
                this.closeNotification(notification.id);
            }
        }, 100);
        
        notification.autoHideInterval = interval;
    }
    
    closeNotification(id) {
        const notification = this.notifications.find(n => n.id === id);
        if (!notification) return;
        
        // Clear auto-hide timer
        if (notification.autoHideInterval) {
            clearInterval(notification.autoHideInterval);
        }
        
        // Animate out
        notification.element.classList.remove('show');
        
        setTimeout(() => {
            if (notification.element.parentNode) {
                notification.element.parentNode.removeChild(notification.element);
            }
            this.notifications = this.notifications.filter(n => n.id !== id);
        }, this.options.animationDuration);
    }
    
    handleNotificationAction(notificationId, actionId) {
        const notification = this.notifications.find(n => n.id === notificationId);
        if (!notification) return;
        
        const action = notification.options.actions?.find(a => a.id === actionId);
        if (action && action.callback) {
            action.callback();
        }
        
        // Close notification after action
        this.closeNotification(notificationId);
    }
    
    // Progress indicator methods
    createProgressIndicator(id, title, options = {}) {
        const existing = document.getElementById(`progress-${id}`);
        if (existing) {
            existing.remove();
        }
        
        const progress = document.createElement('div');
        progress.id = `progress-${id}`;
        progress.className = 'progress-indicator';
        
        progress.innerHTML = `
            <div class="progress-header">
                <div class="progress-title">
                    <div class="progress-spinner"></div>
                    <span>${title}</span>
                </div>
                <div class="progress-percentage">0%</div>
            </div>
            <div class="progress-bar-container">
                <div class="progress-bar" style="width: 0%"></div>
            </div>
            <div class="progress-details">${options.details || 'Inicjalizacja...'}</div>
            ${options.steps ? this.createProgressSteps(options.steps) : ''}
        `;
        
        // Add to container or body
        const container = options.container || document.body;
        container.appendChild(progress);
        
        this.progressBars.set(id, {
            element: progress,
            percentage: 0,
            steps: options.steps || []
        });
        
        return id;
    }
    
    createProgressSteps(steps) {
        const stepsHtml = steps.map((step, index) => `
            <div class="progress-step pending" data-step="${index}">
                <div class="progress-step-icon">${index + 1}</div>
                <div class="progress-step-text">${step}</div>
            </div>
        `).join('');
        
        return `<div class="progress-steps">${stepsHtml}</div>`;
    }
    
    updateProgress(id, percentage, details, currentStep = null) {
        const progress = this.progressBars.get(id);
        if (!progress) return;
        
        const element = progress.element;
        
        // Update percentage
        progress.percentage = Math.min(100, Math.max(0, percentage));
        element.querySelector('.progress-percentage').textContent = `${Math.round(progress.percentage)}%`;
        element.querySelector('.progress-bar').style.width = `${progress.percentage}%`;
        
        // Update details
        if (details) {
            element.querySelector('.progress-details').textContent = details;
        }
        
        // Update steps
        if (currentStep !== null) {
            const steps = element.querySelectorAll('.progress-step');
            steps.forEach((step, index) => {
                step.classList.remove('completed', 'active', 'pending');
                
                if (index < currentStep) {
                    step.classList.add('completed');
                    step.querySelector('.progress-step-icon').innerHTML = '<i class="fas fa-check"></i>';
                } else if (index === currentStep) {
                    step.classList.add('active');
                } else {
                    step.classList.add('pending');
                }
            });
        }
        
        // Complete progress
        if (progress.percentage >= 100) {
            setTimeout(() => {
                this.completeProgress(id);
            }, 1000);
        }
    }
    
    completeProgress(id, successMessage = 'Operacja zakończona pomyślnie') {
        const progress = this.progressBars.get(id);
        if (!progress) return;
        
        const element = progress.element;
        
        // Update to success state
        element.querySelector('.progress-spinner').style.display = 'none';
        element.querySelector('.progress-title').innerHTML = `
            <i class="fas fa-check-circle" style="color: #28a745;"></i>
            <span>${successMessage}</span>
        `;
        
        // Auto-remove after delay
        setTimeout(() => {
            this.removeProgress(id);
        }, 3000);
    }
    
    removeProgress(id) {
        const progress = this.progressBars.get(id);
        if (!progress) return;
        
        progress.element.style.opacity = '0';
        progress.element.style.transform = 'translateY(-20px)';
        
        setTimeout(() => {
            if (progress.element.parentNode) {
                progress.element.parentNode.removeChild(progress.element);
            }
            this.progressBars.delete(id);
        }, this.options.animationDuration);
    }
    
    // Confirmation modal methods
    showConfirmation(title, message, options = {}) {
        return new Promise((resolve) => {
            const modal = this.createConfirmationModal(title, message, options, resolve);
            document.body.appendChild(modal);
            
            setTimeout(() => {
                modal.classList.add('show');
            }, 10);
        });
    }
    
    createConfirmationModal(title, message, options, resolve) {
        const modal = document.createElement('div');
        modal.className = 'confirmation-modal';
        
        const iconMap = {
            success: 'fas fa-check-circle',
            error: 'fas fa-exclamation-circle',
            warning: 'fas fa-exclamation-triangle',
            question: 'fas fa-question-circle'
        };
        
        const type = options.type || 'question';
        
        modal.innerHTML = `
            <div class="confirmation-dialog">
                <div class="confirmation-header">
                    <div class="confirmation-icon ${type}">
                        <i class="${iconMap[type]}"></i>
                    </div>
                    <h3 class="confirmation-title">${title}</h3>
                </div>
                <div class="confirmation-message">${message}</div>
                <div class="confirmation-actions">
                    ${options.showCancel !== false ? `
                        <button class="confirmation-button secondary" onclick="this.closest('.confirmation-modal').resolve(false)">
                            ${options.cancelText || 'Anuluj'}
                        </button>
                    ` : ''}
                    <button class="confirmation-button ${options.confirmType || 'primary'}" onclick="this.closest('.confirmation-modal').resolve(true)">
                        ${options.confirmText || 'Potwierdź'}
                    </button>
                </div>
            </div>
        `;
        
        modal.resolve = (result) => {
            modal.classList.remove('show');
            setTimeout(() => {
                if (modal.parentNode) {
                    modal.parentNode.removeChild(modal);
                }
                resolve(result);
            }, this.options.animationDuration);
        };
        
        // Close on backdrop click
        modal.addEventListener('click', (e) => {
            if (e.target === modal) {
                modal.resolve(false);
            }
        });
        
        return modal;
    }
    
    closeAllModals() {
        const modals = document.querySelectorAll('.confirmation-modal');
        modals.forEach(modal => {
            if (modal.resolve) {
                modal.resolve(false);
            }
        });
    }
    
    // Utility methods
    clearAllNotifications() {
        this.notifications.forEach(notification => {
            this.closeNotification(notification.id);
        });
    }
    
    clearAllProgress() {
        this.progressBars.forEach((progress, id) => {
            this.removeProgress(id);
        });
    }
}

// Initialize global feedback system
window.feedbackSystem = new FeedbackSystem();

// Export for use in modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = FeedbackSystem;
}