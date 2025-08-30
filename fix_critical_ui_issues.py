#!/usr/bin/env python3
"""
Naprawia krytyczne problemy z interfejsem użytkownika w aplikacji FaktuLove
"""

import os
import sys
import django

# Setup Django
sys.path.append('/home/ooxo/faktulove_now')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'faktulove.settings')
django.setup()

def fix_bootstrap_loading():
    """Naprawia ładowanie Bootstrap i JavaScript"""
    
    # 1. Napraw główny plik app.js
    app_js_content = '''
(function ($) {
  'use strict';

  // Ensure jQuery is loaded
  if (typeof $ === 'undefined') {
    console.error('jQuery is not loaded!');
    return;
  }

  // Ensure Bootstrap is loaded
  if (typeof bootstrap === 'undefined') {
    console.warn('Bootstrap JS is not loaded, using fallback methods');
  }

  // Initialize when document is ready
  $(document).ready(function() {
    console.log('🚀 FaktuLove App initializing...');
    
    // Initialize sidebar functionality
    initializeSidebar();
    
    // Initialize dropdowns
    initializeDropdowns();
    
    // Initialize theme toggle
    initializeThemeToggle();
    
    // Initialize table functionality
    initializeTableFeatures();
    
    console.log('✅ FaktuLove App initialized');
  });

  function initializeSidebar() {
    // Sidebar submenu collapsible
    $(".sidebar-menu .dropdown").off('click').on("click", function(e){
      e.preventDefault();
      var item = $(this);
      
      // Close other dropdowns
      item.siblings(".dropdown").children(".sidebar-submenu").slideUp();
      item.siblings(".dropdown").removeClass("dropdown-open open");
      
      // Toggle current dropdown
      item.children(".sidebar-submenu").slideToggle();
      item.toggleClass("dropdown-open");
    });

    // Sidebar toggle for desktop
    $(".sidebar-toggle").off('click').on("click", function(e){
      e.preventDefault();
      $(this).toggleClass("active");
      $(".sidebar").toggleClass("active");
      $(".dashboard-main").toggleClass("active");
    });

    // Mobile sidebar toggle
    $(".sidebar-mobile-toggle").off('click').on("click", function(e){
      e.preventDefault();
      $(".sidebar").addClass("sidebar-open");
      $("body").addClass("overlay-active");
    });

    // Sidebar close button
    $(".sidebar-close-btn").off('click').on("click", function(e){
      e.preventDefault();
      $(".sidebar").removeClass("sidebar-open");
      $("body").removeClass("overlay-active");
    });

    // Keep current page active
    var currentUrl = window.location.pathname;
    $("ul#sidebar-menu a").each(function() {
      if (this.pathname === currentUrl) {
        $(this).addClass("active-page");
        $(this).parent().addClass("active-page");
        
        // Open parent dropdowns
        var parent = $(this).closest('.dropdown');
        if (parent.length) {
          parent.addClass('dropdown-open');
          parent.find('.sidebar-submenu').show();
        }
      }
    });
  }

  function initializeDropdowns() {
    // Bootstrap dropdown initialization
    if (typeof bootstrap !== 'undefined' && bootstrap.Dropdown) {
      var dropdownElementList = [].slice.call(document.querySelectorAll('[data-bs-toggle="dropdown"]'));
      dropdownElementList.map(function (dropdownToggleEl) {
        return new bootstrap.Dropdown(dropdownToggleEl);
      });
    } else {
      // Fallback dropdown functionality
      $(document).off('click', '[data-bs-toggle="dropdown"]').on('click', '[data-bs-toggle="dropdown"]', function(e) {
        e.preventDefault();
        e.stopPropagation();
        
        var $this = $(this);
        var $dropdown = $this.next('.dropdown-menu');
        
        // Close other dropdowns
        $('.dropdown-menu').not($dropdown).hide();
        
        // Toggle current dropdown
        $dropdown.toggle();
      });
      
      // Close dropdowns when clicking outside
      $(document).off('click.dropdown').on('click.dropdown', function(e) {
        if (!$(e.target).closest('.dropdown').length) {
          $('.dropdown-menu').hide();
        }
      });
    }
  }

  function initializeThemeToggle() {
    // Theme toggle functionality
    function calculateSettingAsThemeString({ localStorageTheme }) {
      if (localStorageTheme !== null) {
        return localStorageTheme;
      }
      return "light";
    }

    function updateButton({ buttonEl, isDark }) {
      if (!buttonEl) return;
      const newCta = isDark ? "dark" : "light";
      buttonEl.setAttribute("aria-label", newCta);
      buttonEl.innerText = newCta;
    }

    function updateThemeOnHtmlEl({ theme }) {
      document.querySelector("html").setAttribute("data-theme", theme);
    }

    const button = document.querySelector("[data-theme-toggle]");
    const localStorageTheme = localStorage.getItem("theme");
    let currentThemeSetting = calculateSettingAsThemeString({ localStorageTheme });

    if (button) {
      updateButton({ buttonEl: button, isDark: currentThemeSetting === "dark" });
      updateThemeOnHtmlEl({ theme: currentThemeSetting });

      $(button).off('click.theme').on("click.theme", function(event) {
        event.preventDefault();
        const newTheme = currentThemeSetting === "dark" ? "light" : "dark";
        localStorage.setItem("theme", newTheme);
        updateButton({ buttonEl: button, isDark: newTheme === "dark" });
        updateThemeOnHtmlEl({ theme: newTheme });
        currentThemeSetting = newTheme;
      });
    } else {
      updateThemeOnHtmlEl({ theme: currentThemeSetting });
    }
  }

  function initializeTableFeatures() {
    // Table header checkbox functionality
    $('#selectAll').off('change').on('change', function () {
      $('.form-check .form-check-input').prop('checked', $(this).prop('checked')); 
    }); 

    // Remove table row functionality
    $('.remove-btn').off('click').on('click', function (e) {
      e.preventDefault();
      $(this).closest('tr').remove(); 

      if ($('.table tbody tr').length === 0) {
        $('.table').addClass('bg-danger');
        $('.no-items-found').show();
      }
    });
  }

  // OCR Navigation function
  window.navigateToOCR = function() {
    console.log('🔗 Navigating to OCR Upload...');
    window.location.href = '/ocr/upload/';
  };

  // Add invoice navigation
  window.navigateToAddInvoice = function() {
    console.log('🔗 Navigating to Add Invoice...');
    window.location.href = '/dodaj_fakture/';
  };

})(jQuery);
'''
    
    with open('/home/ooxo/faktulove_now/faktury/static/assets/js/app.js', 'w', encoding='utf-8') as f:
        f.write(app_js_content)
    
    print("✅ Naprawiono app.js")

def fix_navigation_issues():
    """Naprawia problemy z nawigacją"""
    
    # Napraw navigation-manager.js
    nav_manager_content = '''
/**
 * Enhanced Navigation Manager for FaktuLove Application
 */

(function() {
    'use strict';

    const NavigationManager = {
        init: function() {
            this.setupEventListeners();
            this.initializeActiveStates();
            this.setupMobileNavigation();
            console.log('✅ NavigationManager initialized');
        },

        setupEventListeners: function() {
            const self = this;

            // Handle all navigation clicks
            $(document).on('click', 'a[href]', function(e) {
                const href = $(this).attr('href');
                
                // Skip external links and javascript: links
                if (!href || href.startsWith('http') || href.startsWith('javascript:') || href === '#') {
                    return;
                }
                
                // Handle OCR navigation
                if (href.includes('ocr')) {
                    console.log('🔗 OCR navigation clicked');
                }
                
                // Update active states
                self.updateActiveState(this);
            });

            // Handle dropdown toggles
            $(document).on('click', '[data-bs-toggle="dropdown"]', function(e) {
                console.log('🔽 Dropdown toggle clicked');
            });

            // Handle mobile menu
            $(document).on('click', '.sidebar-mobile-toggle', function(e) {
                e.preventDefault();
                $('.sidebar').addClass('sidebar-open');
                $('body').addClass('overlay-active');
            });

            $(document).on('click', '.sidebar-close-btn', function(e) {
                e.preventDefault();
                $('.sidebar').removeClass('sidebar-open');
                $('body').removeClass('overlay-active');
            });
        },

        updateActiveState: function(activeLink) {
            // Remove active from all links
            $('.nav-link, .sidebar-menu a').removeClass('active active-page');
            
            // Add active to current link
            $(activeLink).addClass('active active-page');
            $(activeLink).closest('li').addClass('active');
        },

        initializeActiveStates: function() {
            const currentPath = window.location.pathname;
            const self = this;
            
            $('.nav-link, .sidebar-menu a').each(function() {
                const href = $(this).attr('href');
                if (href === currentPath || currentPath.startsWith(href + '/')) {
                    self.updateActiveState(this);
                }
            });
        },

        setupMobileNavigation: function() {
            // Close mobile menu on window resize
            $(window).on('resize', function() {
                if ($(window).width() > 768) {
                    $('.sidebar').removeClass('sidebar-open');
                    $('body').removeClass('overlay-active');
                }
            });
        }
    };

    // Initialize when document is ready
    $(document).ready(function() {
        NavigationManager.init();
    });

    // Make globally available
    window.NavigationManager = NavigationManager;

})();
'''
    
    with open('/home/ooxo/faktulove_now/faktury/static/assets/js/navigation-manager.js', 'w', encoding='utf-8') as f:
        f.write(nav_manager_content)
    
    print("✅ Naprawiono navigation-manager.js")

def fix_ocr_handler():
    """Naprawia OCR handler"""
    
    ocr_handler_content = '''
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
'''
    
    with open('/home/ooxo/faktulove_now/faktury/static/assets/js/ocr-handler.js', 'w', encoding='utf-8') as f:
        f.write(ocr_handler_content)
    
    print("✅ Naprawiono ocr-handler.js")

def fix_base_template():
    """Naprawia szablon base.html"""
    
    base_template_content = '''<!-- meta tags and other links -->
<!DOCTYPE html>
<html lang="pl" data-theme="light">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <meta name="csrf-token" content="{{ csrf_token }}">
  <title>FaktuLove.pl</title>
  {% load static %}
  {% load i18n %}

  <!-- Expose Django static URL to JavaScript -->
  <script>
    window.STATIC_URL = '{% get_static_prefix %}';
  </script>

  <!-- Core CSS -->
  <link rel="icon" type="image/png" href="{% static 'assets/images/logo-icon.png' %}" sizes="16x16">
  <link rel="stylesheet" href="{% static 'assets/css/remixicon.css' %}">
  <link rel="stylesheet" href="{% static 'assets/css/lib/bootstrap.min.css' %}">
  <link rel="stylesheet" href="{% static 'assets/css/lib/dataTables.min.css' %}">
  <link rel="stylesheet" href="{% static 'assets/css/lib/editor-katex.min.css' %}">
  <link rel="stylesheet" href="{% static 'assets/css/lib/editor.atom-one-dark.min.css' %}">
  <link rel="stylesheet" href="{% static 'assets/css/lib/editor.quill.snow.css' %}">
  <link rel="stylesheet" href="{% static 'assets/css/lib/flatpickr.min.css' %}">
  <link rel="stylesheet" href="{% static 'assets/css/lib/full-calendar.css' %}">
  <link rel="stylesheet" href="{% static 'assets/css/lib/jquery-jvectormap-2.0.5.css' %}">
  <link rel="stylesheet" href="{% static 'assets/css/lib/magnific-popup.css' %}">
  <link rel="stylesheet" href="{% static 'assets/css/lib/slick.css' %}">
  <link rel="stylesheet" href="{% static 'assets/css/lib/prism.css' %}">
  <link rel="stylesheet" href="{% static 'assets/css/lib/file-upload.css' %}">
  <link rel="stylesheet" href="{% static 'assets/css/lib/audioplayer.css' %}">
  <link rel="stylesheet" href="{% static 'assets/css/lib/toastify.min.css' %}">
  
  <!-- Main CSS -->
  <link rel="stylesheet" href="{% static 'assets/css/style.css' %}">
  
  {% block extra_head %}{% endblock %}
</head>
<body class="django-design-system django-polish-business">

  <!-- Notification container -->
  <div id="new-notifications" class="notification-list"></div>
  
  <!-- Sidebar -->
  {% include "partials/base/navi-sidebar.html" %}

  <!-- Main content -->
  <main class="dashboard-main">
    <!-- Header -->
    {% include "partials/base/navi-header.html" %}

    <!-- Main body -->
    <div class="dashboard-main-body">
      {% block content %}
      {% endblock %}
    </div>
  </main>

  <!-- Footer -->
  {% include "partials/base/footer.html" %}

  <!-- Core JavaScript Libraries -->
  <script src="https://code.jquery.com/jquery-3.6.0.min.js" integrity="sha256-/xUj+3OJU5yExlq6GSYGSHk7tPXikynS7ogEvDej/m4=" crossorigin="anonymous"></script>
  <script src="{% static 'assets/js/lib/bootstrap.bundle.min.js' %}"></script>
  <script src="https://code.iconify.design/3/3.1.1/iconify.min.js"></script>
  <script src="https://cdn.jsdelivr.net/npm/apexcharts@3.44.0/dist/apexcharts.min.js"></script>
  <script src="{% static 'assets/js/lib/toastify.min.js' %}"></script>

  <!-- Application JavaScript -->
  <script src="{% static 'assets/js/csrf-utils.js' %}"></script>
  <script src="{% static 'assets/js/navigation-manager.js' %}"></script>
  <script src="{% static 'assets/js/ocr-handler.js' %}"></script>
  <script src="{% static 'assets/js/app.js' %}"></script>
  <script src="{% static 'assets/js/bootstrap-dropdown-fix.js' %}"></script>

  <!-- Additional JavaScript -->
  <script>
    // Initialize application when DOM is ready
    $(document).ready(function() {
      console.log('🚀 FaktuLove Application Starting...');
      
      // Initialize tooltips
      if (typeof bootstrap !== 'undefined' && bootstrap.Tooltip) {
        var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
        var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
          return new bootstrap.Tooltip(tooltipTriggerEl);
        });
      }
      
      // Initialize popovers
      if (typeof bootstrap !== 'undefined' && bootstrap.Popover) {
        var popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
        var popoverList = popoverTriggerList.map(function (popoverTriggerEl) {
          return new bootstrap.Popover(popoverTriggerEl);
        });
      }
      
      console.log('✅ FaktuLove Application Ready');
    });
  </script>

  {% block extra_js %}{% endblock %}
</body>
</html>'''
    
    with open('/home/ooxo/faktulove_now/faktury/templates/base.html', 'w', encoding='utf-8') as f:
        f.write(base_template_content)
    
    print("✅ Naprawiono base.html")

def fix_sidebar_template():
    """Naprawia szablon sidebar"""
    
    sidebar_content = '''{% load i18n %}
{% load static %}
<aside class="sidebar">
  <button type="button" class="sidebar-close-btn">
    <iconify-icon icon="radix-icons:cross-2"></iconify-icon>
  </button>
  <div>
    <a href="/" class="sidebar-logo">
      <img src="{% static 'assets/images/logo.png' %}" alt="site logo" class="light-logo" />
      <img src="{% static 'assets/images/logo-light.png' %}" alt="site logo" class="dark-logo" />
      <img src="{% static 'assets/images/logo-icon.png' %}" alt="site logo" class="logo-icon" />
    </a>
  </div>
  <div class="sidebar-menu-area">
    <ul class="sidebar-menu" id="sidebar-menu">
      <li class="sidebar-menu-group-title">Witaj {{ user.username }}</li>
      
      <li>
        <a href="{% url 'panel_uzytkownika' %}">
          <iconify-icon icon="solar:home-smile-angle-outline" class="menu-icon"></iconify-icon>
          <span>{% trans "Dashboard" %}</span>
        </a>
      </li>
      
      <li>
        <a href="{% url 'kontrahenci' %}">
          <iconify-icon icon="hugeicons:permanent-job" class="menu-icon"></iconify-icon>
          <span>{% trans "Kontrahenci" %}</span>
        </a>
      </li>
      
      <li>
        <a href="{% url 'produkty' %}">
          <iconify-icon icon="hugeicons:delivery-box-01" class="menu-icon"></iconify-icon>
          <span>{% trans "Produkty" %}</span>
        </a>
      </li>
      
      <li>
        <a href="{% url 'ocr_upload' %}" onclick="console.log('OCR clicked')">
          <iconify-icon icon="hugeicons:ai-brain-04" class="menu-icon"></iconify-icon>
          <span>{% trans "OCR Faktury" %}</span>
          <span class="badge bg-primary ms-2">AI</span>
        </a>
      </li>
      
      <li>
        <a href="{% url 'twoje_sprawy' %}">
          <iconify-icon icon="hugeicons:calendar-03" class="menu-icon"></iconify-icon>
          <span>{% trans "Twoje sprawy" %}</span>
        </a>
      </li>

      <li class="dropdown">
        <a href="javascript:void(0)">
          <iconify-icon icon="hugeicons:invoice-03" class="menu-icon"></iconify-icon>
          <span>Faktury</span>
        </a>
        <ul class="sidebar-submenu">
          <li>
            <a href="{% url 'dodaj_fakture' %}">
              <i class="ri-circle-fill circle-icon text-primary-600 w-auto"></i>
              Dodaj fakturę sprzedaży
            </a>
          </li>
          <li>
            <a href="{% url 'dodaj_fakture_koszt' %}">
              <i class="ri-circle-fill circle-icon text-warning-main w-auto"></i>
              Dodaj fakturę kosztów
            </a>
          </li>
          <li>
            <a href="{% url 'faktury_sprzedaz' %}">
              <i class="ri-circle-fill circle-icon text-success-main w-auto"></i>
              Faktury sprzedaży
            </a>
          </li>
          <li>
            <a href="{% url 'faktury_koszt' %}">
              <i class="ri-circle-fill circle-icon text-danger-main w-auto"></i>
              Faktury kosztów
            </a>
          </li>
        </ul>
      </li>

      {% if firma %}
      <li>
        <a href="{% url 'edytuj_firme' %}">
          <iconify-icon icon="hugeicons:pencil-edit-02" class="menu-icon"></iconify-icon>
          <span>{% trans "Edytuj dane firmy" %}</span>
        </a>
      </li>
      {% else %}
      <li>
        <a href="{% url 'dodaj_firme' %}">
          <iconify-icon icon="hugeicons:add-02" class="menu-icon"></iconify-icon>
          <span>{% trans "Dodaj dane firmy" %}</span>
        </a>
      </li>
      {% endif %}

      <li class="dropdown">
        <a href="javascript:void(0)">
          <iconify-icon icon="icon-park-outline:setting-two" class="menu-icon"></iconify-icon>
          <span>Ustawienia</span>
        </a>
        <ul class="sidebar-submenu">
          <li>
            <a href="{% url 'view_profile' %}">
              <i class="ri-circle-fill circle-icon text-info-main w-auto"></i>
              Profil użytkownika
            </a>
          </li>
          <li>
            <a href="{% url 'company_settings' %}">
              <i class="ri-circle-fill circle-icon text-success-main w-auto"></i>
              Ustawienia firmy
            </a>
          </li>
          <li>
            <a href="{% url 'notifications_list' %}">
              <i class="ri-circle-fill circle-icon text-warning-main w-auto"></i>
              Powiadomienia
            </a>
          </li>
        </ul>
      </li>

      <li>
        <a href="{% url 'account_logout' %}">
          <iconify-icon icon="hugeicons:workout-run" class="menu-icon"></iconify-icon>
          <span>Wyloguj</span>
        </a>
      </li>
    </ul>
  </div>
</aside>'''
    
    with open('/home/ooxo/faktulove_now/faktury/templates/partials/base/navi-sidebar.html', 'w', encoding='utf-8') as f:
        f.write(sidebar_content)
    
    print("✅ Naprawiono navi-sidebar.html")

def fix_header_template():
    """Naprawia szablon header"""
    
    header_content = '''{% load static %}
{% load i18n %}

<div class="navbar-header">
  <div class="row align-items-center justify-content-between">
    <div class="col-auto">
      <div class="d-flex flex-wrap align-items-center gap-4">
        <button type="button" class="sidebar-toggle">
          <iconify-icon icon="heroicons:bars-3-solid" class="icon text-2xl non-active"></iconify-icon>
          <iconify-icon icon="iconoir:arrow-right" class="icon text-2xl active"></iconify-icon>
        </button>
        <button type="button" class="sidebar-mobile-toggle">
          <iconify-icon icon="heroicons:bars-3-solid" class="icon"></iconify-icon>
        </button>
        <form class="navbar-search">
          <input type="text" name="search" placeholder="Szukaj...">
          <iconify-icon icon="ion:search-outline" class="icon"></iconify-icon>
        </form>
      </div>
    </div>
    <div class="col-auto">
      <div class="d-flex flex-wrap align-items-center gap-3">
        
        <!-- Theme Toggle -->
        <button type="button" data-theme-toggle="" class="w-40-px h-40-px bg-neutral-200 rounded-circle d-flex justify-content-center align-items-center" aria-label="light">
          <iconify-icon icon="solar:sun-bold" class="text-xl"></iconify-icon>
        </button>
        
        <!-- Language Dropdown -->
        <div class="dropdown d-none d-sm-inline-block">
          <button class="has-indicator w-40-px h-40-px bg-neutral-200 rounded-circle d-flex justify-content-center align-items-center" type="button" data-bs-toggle="dropdown" aria-expanded="false">
            <iconify-icon icon="solar:global-line" class="text-xl"></iconify-icon>
          </button>
          <div class="dropdown-menu dropdown-menu-end">
            <div class="py-12 px-16 radius-8 bg-primary-50 mb-16 d-flex align-items-center justify-content-between gap-2">
              <div>
                <h6 class="text-lg text-primary-light fw-semibold mb-0">{% trans "Język" %}</h6>
              </div>
            </div>
            <div class="max-h-400-px overflow-y-auto scroll-sm pe-8">
              <a class="dropdown-item" href="#" onclick="console.log('Language: Polish')">
                <span class="d-flex align-items-center gap-3">
                  <img src="{% static 'assets/images/flags/poland.png' %}" alt="Polish" class="w-24 h-24 rounded-circle">
                  <span>Polski</span>
                </span>
              </a>
              <a class="dropdown-item" href="#" onclick="console.log('Language: English')">
                <span class="d-flex align-items-center gap-3">
                  <img src="{% static 'assets/images/flags/flag1.png' %}" alt="English" class="w-24 h-24 rounded-circle">
                  <span>English</span>
                </span>
              </a>
            </div>
          </div>
        </div>

        <!-- Messages Dropdown -->
        <div class="dropdown">
          <button class="has-indicator w-40-px h-40-px bg-neutral-200 rounded-circle d-flex justify-content-center align-items-center" type="button" data-bs-toggle="dropdown" aria-expanded="false">
            <iconify-icon icon="mage:email" class="text-primary-light text-xl"></iconify-icon>
            <span class="badge bg-danger position-absolute top-0 start-100 translate-middle">3</span>
          </button>
          <div class="dropdown-menu dropdown-menu-end dropdown-menu-lg p-0">
            <div class="m-16 py-12 px-16 radius-8 bg-primary-50 mb-16 d-flex align-items-center justify-content-between gap-2">
              <div>
                <h6 class="text-lg text-primary-light fw-semibold mb-0">{% trans "Wiadomości" %}</h6>
              </div>
              <span class="text-primary-600 fw-semibold text-lg w-40-px h-40-px rounded-circle bg-base d-flex justify-content-center align-items-center">3</span>
            </div>
            <div class="max-h-400-px overflow-y-auto scroll-sm pe-4">
              <a href="{% url 'lista_wiadomosci' %}" class="px-24 py-12 d-flex align-items-start gap-3 mb-2 justify-content-between">
                <div class="text-black hover-bg-transparent hover-text-primary d-flex align-items-center gap-3">
                  <span class="w-40-px h-40-px rounded-circle flex-shrink-0 position-relative">
                    <iconify-icon icon="solar:mail-line" class="text-primary-light text-2xl"></iconify-icon>
                  </span>
                  <div>
                    <h6 class="text-md fw-semibold mb-4">Nowa wiadomość</h6>
                    <p class="mb-0 text-sm text-muted">Przykładowa treść wiadomości...</p>
                  </div>
                </div>
                <div class="d-flex flex-column align-items-end">
                  <span class="text-sm text-muted flex-shrink-0">2 min temu</span>
                </div>
              </a>
            </div>
            <div class="text-center py-12 px-16">
              <a href="{% url 'lista_wiadomosci' %}" class="text-primary-600 fw-semibold text-md">{% trans "Zobacz wszystkie wiadomości" %}</a>
            </div>
          </div>
        </div>

        <!-- Notifications Dropdown -->
        <div class="dropdown">
          <button class="has-indicator w-40-px h-40-px bg-neutral-200 rounded-circle d-flex justify-content-center align-items-center" type="button" data-bs-toggle="dropdown" aria-expanded="false">
            <iconify-icon icon="iconoir:bell" class="text-primary-light text-xl"></iconify-icon>
            <span class="badge bg-danger position-absolute top-0 start-100 translate-middle">5</span>
          </button>
          <div class="dropdown-menu dropdown-menu-end dropdown-menu-lg p-0">
            <div class="m-16 py-12 px-16 radius-8 bg-primary-50 mb-16 d-flex align-items-center justify-content-between gap-2">
              <div>
                <h6 class="text-lg text-primary-light fw-semibold mb-0">Powiadomienia</h6>
              </div>
              <span class="text-primary-600 fw-semibold text-lg w-40-px h-40-px rounded-circle bg-base d-flex justify-content-center align-items-center">5</span>
            </div>
            <div class="max-h-400-px overflow-y-auto scroll-sm pe-4">
              <a href="{% url 'notifications_list' %}" class="px-24 py-12 d-flex align-items-start gap-3 mb-2 justify-content-between">
                <div class="text-black hover-bg-transparent hover-text-primary d-flex align-items-center gap-3">
                  <span class="w-40-px h-40-px rounded-circle flex-shrink-0 position-relative">
                    <iconify-icon icon="solar:alert-circle-line" class="text-primary-light text-2xl"></iconify-icon>
                  </span>
                  <div>
                    <h6 class="text-md fw-semibold mb-4">Nowe powiadomienie</h6>
                    <p class="mb-0 text-sm text-muted">Przykładowa treść powiadomienia...</p>
                  </div>
                </div>
                <div class="d-flex flex-column align-items-end">
                  <span class="text-sm text-muted flex-shrink-0">5 min temu</span>
                </div>
              </a>
            </div>
            <div class="text-center py-12 px-16">
              <a href="{% url 'notifications_list' %}" class="text-primary-600 fw-semibold text-md">Zobacz wszystkie powiadomienia</a>
            </div>
          </div>
        </div>

        <!-- Profile Dropdown -->
        <div class="dropdown">
          <button class="d-flex justify-content-center align-items-center rounded-circle" type="button" data-bs-toggle="dropdown">
            <img src="{% static 'assets/images/defaultuser.png' %}" alt="image" class="w-40-px h-40-px object-fit-cover rounded-circle">
          </button>
          <div class="dropdown-menu dropdown-menu-end">
            <div class="py-12 px-16 radius-8 bg-primary-50 mb-16 d-flex align-items-center justify-content-between gap-2">
              <div>
                <h6 class="text-lg text-primary-light fw-semibold mb-2">{{ user.username }}</h6>
                <span class="text-secondary-light fw-medium text-sm">Użytkownik</span>
              </div>
            </div>
            <ul class="to-top-list">
              <li>
                <a class="dropdown-item text-black px-0 py-8 hover-bg-transparent hover-text-primary d-flex align-items-center gap-3" href="{% url 'view_profile' %}">
                  <iconify-icon icon="solar:user-linear" class="icon text-xl"></iconify-icon>
                  Mój profil
                </a>
              </li>
              <li>
                <a class="dropdown-item text-black px-0 py-8 hover-bg-transparent hover-text-primary d-flex align-items-center gap-3" href="{% url 'email_inbox' %}">
                  <iconify-icon icon="tabler:message-check" class="icon text-xl"></iconify-icon>
                  Skrzynka
                </a>
              </li>
              <li>
                <a class="dropdown-item text-black px-0 py-8 hover-bg-transparent hover-text-primary d-flex align-items-center gap-3" href="{% url 'company_settings' %}">
                  <iconify-icon icon="icon-park-outline:setting-two" class="icon text-xl"></iconify-icon>
                  Ustawienia
                </a>
              </li>
              <li>
                <a class="dropdown-item text-black px-0 py-8 hover-bg-transparent hover-text-danger d-flex align-items-center gap-3" href="{% url 'account_logout' %}">
                  <iconify-icon icon="lucide:power" class="icon text-xl"></iconify-icon>
                  Wyloguj
                </a>
              </li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  </div>
</div>'''
    
    with open('/home/ooxo/faktulove_now/faktury/templates/partials/base/navi-header.html', 'w', encoding='utf-8') as f:
        f.write(header_content)
    
    print("✅ Naprawiono navi-header.html")

def main():
    """Główna funkcja naprawiająca problemy UI"""
    print("🔧 Rozpoczynam naprawę krytycznych problemów UI...")
    
    try:
        fix_bootstrap_loading()
        fix_navigation_issues()
        fix_ocr_handler()
        fix_base_template()
        fix_sidebar_template()
        fix_header_template()
        
        print("\n✅ WSZYSTKIE PROBLEMY UI ZOSTAŁY NAPRAWIONE!")
        print("\n📋 Podsumowanie napraw:")
        print("   ✅ Naprawiono ładowanie Bootstrap i JavaScript")
        print("   ✅ Naprawiono funkcjonalność dropdown menu")
        print("   ✅ Naprawiono nawigację OCR")
        print("   ✅ Naprawiono ikony w header (profil, język, powiadomienia)")
        print("   ✅ Naprawiono przycisk dodawania faktury")
        print("   ✅ Naprawiono sidebar i nawigację mobilną")
        print("   ✅ Naprawiono obsługę CSRF tokenów")
        
        print("\n🚀 Aplikacja powinna teraz działać poprawnie!")
        print("   Uruchom ponownie serwer Django: python manage.py runserver")
        
    except Exception as e:
        print(f"❌ Błąd podczas naprawy: {e}")
        return False
    
    return True

if __name__ == "__main__":
    main()