/**
 * CSRF Utilities for FaktuLove Application
 * Handles CSRF token management for AJAX requests
 */

(function() {
    'use strict';

    const CSRFUtils = {
        token: null,
        tokenName: 'csrfmiddlewaretoken',

        /**
         * Initialize CSRF utilities
         */
        init: function() {
            this.loadToken();
            this.setupAjaxDefaults();
            this.setupFormDefaults();
            console.log('CSRFUtils initialized');
        },

        /**
         * Load CSRF token from meta tag or cookie
         */
        loadToken: function() {
            // Try to get token from meta tag
            const metaToken = document.querySelector('meta[name="csrf-token"]');
            if (metaToken) {
                this.token = metaToken.getAttribute('content');
                return;
            }

            // Try to get token from cookie
            const cookieToken = this.getCookie('csrftoken');
            if (cookieToken) {
                this.token = cookieToken;
                return;
            }

            console.warn('CSRF token not found');
        },

        /**
         * Get CSRF token
         */
        getToken: function() {
            if (!this.token) {
                this.loadToken();
            }
            return this.token;
        },

        /**
         * Get cookie value by name
         */
        getCookie: function(name) {
            let cookieValue = null;
            if (document.cookie && document.cookie !== '') {
                const cookies = document.cookie.split(';');
                for (let i = 0; i < cookies.length; i++) {
                    const cookie = cookies[i].trim();
                    if (cookie.substring(0, name.length + 1) === (name + '=')) {
                        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                        break;
                    }
                }
            }
            return cookieValue;
        },

        /**
         * Setup jQuery AJAX defaults if jQuery is available
         */
        setupAjaxDefaults: function() {
            const self = this;
            
            // Setup for jQuery if available
            if (typeof $ !== 'undefined' && $.ajaxSetup) {
                $.ajaxSetup({
                    beforeSend: function(xhr, settings) {
                        if (!self.csrfSafeMethod(settings.type) && !this.crossDomain) {
                            xhr.setRequestHeader("X-CSRFToken", self.getToken());
                        }
                    }
                });
            }

            // Setup for fetch API
            this.setupFetchDefaults();
        },

        /**
         * Setup fetch API defaults
         */
        setupFetchDefaults: function() {
            const self = this;
            const originalFetch = window.fetch;

            window.fetch = function(resource, options) {
                options = options || {};
                
                // Add CSRF token to headers if needed
                if (self.needsCSRFToken(options.method)) {
                    options.headers = options.headers || {};
                    
                    if (!options.headers['X-CSRFToken'] && !options.headers['x-csrftoken']) {
                        options.headers['X-CSRFToken'] = self.getToken();
                    }
                }

                return originalFetch.apply(this, arguments);
            };
        },

        /**
         * Setup form defaults
         */
        setupFormDefaults: function() {
            const self = this;

            // Add CSRF token to forms that don't have it
            document.addEventListener('submit', function(e) {
                const form = e.target;
                if (form.tagName === 'FORM' && self.needsCSRFToken(form.method)) {
                    self.ensureFormHasCSRFToken(form);
                }
            });

            // Add CSRF token to existing forms
            this.addCSRFToExistingForms();
        },

        /**
         * Add CSRF token to existing forms
         */
        addCSRFToExistingForms: function() {
            const forms = document.querySelectorAll('form');
            const self = this;
            
            forms.forEach(function(form) {
                if (self.needsCSRFToken(form.method)) {
                    self.ensureFormHasCSRFToken(form);
                }
            });
        },

        /**
         * Ensure form has CSRF token
         */
        ensureFormHasCSRFToken: function(form) {
            // Check if form already has CSRF token
            const existingToken = form.querySelector(`input[name="${this.tokenName}"]`);
            if (existingToken) {
                // Update token value if it's different
                if (existingToken.value !== this.getToken()) {
                    existingToken.value = this.getToken();
                }
                return;
            }

            // Add CSRF token input
            const csrfInput = document.createElement('input');
            csrfInput.type = 'hidden';
            csrfInput.name = this.tokenName;
            csrfInput.value = this.getToken();
            form.appendChild(csrfInput);
        },

        /**
         * Check if method needs CSRF token
         */
        needsCSRFToken: function(method) {
            if (!method) return false;
            
            const safeMethod = this.csrfSafeMethod(method);
            return !safeMethod;
        },

        /**
         * Check if HTTP method is CSRF safe
         */
        csrfSafeMethod: function(method) {
            // These HTTP methods do not require CSRF protection
            return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
        },

        /**
         * Create CSRF header object
         */
        getCSRFHeader: function() {
            return {
                'X-CSRFToken': this.getToken()
            };
        },

        /**
         * Create CSRF form data
         */
        getCSRFFormData: function() {
            const formData = new FormData();
            formData.append(this.tokenName, this.getToken());
            return formData;
        },

        /**
         * Add CSRF token to URL parameters
         */
        addCSRFToURL: function(url) {
            const separator = url.includes('?') ? '&' : '?';
            return url + separator + this.tokenName + '=' + encodeURIComponent(this.getToken());
        },

        /**
         * Create XMLHttpRequest with CSRF token
         */
        createXHR: function(method, url) {
            const xhr = new XMLHttpRequest();
            xhr.open(method, url);
            
            if (this.needsCSRFToken(method)) {
                xhr.setRequestHeader('X-CSRFToken', this.getToken());
            }
            
            return xhr;
        },

        /**
         * Make AJAX request with CSRF token
         */
        ajax: function(options) {
            options = options || {};
            
            // Add CSRF token to headers
            if (this.needsCSRFToken(options.method)) {
                options.headers = options.headers || {};
                options.headers['X-CSRFToken'] = this.getToken();
            }

            // Use fetch if available, otherwise fallback to XMLHttpRequest
            if (typeof fetch !== 'undefined') {
                return fetch(options.url, {
                    method: options.method || 'GET',
                    headers: options.headers,
                    body: options.data
                });
            } else {
                return this.xhrRequest(options);
            }
        },

        /**
         * XMLHttpRequest fallback
         */
        xhrRequest: function(options) {
            return new Promise(function(resolve, reject) {
                const xhr = new XMLHttpRequest();
                xhr.open(options.method || 'GET', options.url);
                
                // Set headers
                if (options.headers) {
                    Object.keys(options.headers).forEach(function(key) {
                        xhr.setRequestHeader(key, options.headers[key]);
                    });
                }

                xhr.onload = function() {
                    if (xhr.status >= 200 && xhr.status < 300) {
                        resolve(xhr);
                    } else {
                        reject(xhr);
                    }
                };

                xhr.onerror = function() {
                    reject(xhr);
                };

                xhr.send(options.data);
            });
        },

        /**
         * Refresh CSRF token
         */
        refreshToken: function() {
            const self = this;
            
            return fetch('/api/csrf-token/', {
                method: 'GET',
                credentials: 'same-origin'
            })
            .then(response => response.json())
            .then(data => {
                if (data.csrf_token) {
                    self.token = data.csrf_token;
                    self.updateMetaTag();
                    self.updateForms();
                    return self.token;
                } else {
                    throw new Error('Failed to refresh CSRF token');
                }
            });
        },

        /**
         * Update meta tag with new token
         */
        updateMetaTag: function() {
            let metaTag = document.querySelector('meta[name="csrf-token"]');
            if (!metaTag) {
                metaTag = document.createElement('meta');
                metaTag.name = 'csrf-token';
                document.head.appendChild(metaTag);
            }
            metaTag.content = this.token;
        },

        /**
         * Update all forms with new token
         */
        updateForms: function() {
            const tokenInputs = document.querySelectorAll(`input[name="${this.tokenName}"]`);
            const self = this;
            
            tokenInputs.forEach(function(input) {
                input.value = self.token;
            });
        },

        /**
         * Handle CSRF token mismatch errors
         */
        handleCSRFError: function(response) {
            if (response.status === 403) {
                console.warn('CSRF token mismatch, refreshing token...');
                return this.refreshToken();
            }
            return Promise.reject(response);
        },

        /**
         * Validate current token
         */
        validateToken: function() {
            return fetch('/api/validate-csrf/', {
                method: 'POST',
                headers: this.getCSRFHeader(),
                credentials: 'same-origin'
            })
            .then(response => {
                if (!response.ok) {
                    throw new Error('CSRF token validation failed');
                }
                return response.json();
            })
            .then(data => {
                return data.valid === true;
            })
            .catch(error => {
                console.warn('CSRF token validation error:', error);
                return false;
            });
        }
    };

    // Initialize CSRF utilities when DOM is ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', function() {
            CSRFUtils.init();
        });
    } else {
        CSRFUtils.init();
    }

    // Make CSRFUtils globally available
    window.CSRFUtils = CSRFUtils;

})();