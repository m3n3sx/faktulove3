
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
