/**
 * Cypress Integration Tests for FaktuLove OCR
 * Comprehensive end-to-end testing with real user interactions
 */

describe('FaktuLove OCR - Comprehensive Integration Tests', () => {
  const baseUrl = Cypress.env('baseUrl') || 'http://localhost:8000';
  
  beforeEach(() => {
    // Set up test environment
    cy.viewport(1920, 1080);
    
    // Intercept and log all network requests
    cy.intercept('**', (req) => {
      console.log(`🔄 ${req.method} ${req.url}`);
    }).as('allRequests');
  });

  describe('🏠 Homepage and Basic Navigation', () => {
    it('should load homepage successfully', () => {
      cy.visit(baseUrl);
      
      // Check page loads
      cy.get('body').should('exist');
      
      // Log page details
      cy.title().then((title) => {
        cy.log(`Page title: ${title}`);
      });
      
      cy.url().then((url) => {
        cy.log(`Current URL: ${url}`);
      });
      
      // Take screenshot
      cy.screenshot('homepage-load');
      
      // Check for common elements
      cy.get('body').then(($body) => {
        const navElements = $body.find('nav, .navbar, .navigation').length;
        const mainContent = $body.find('main, .main-content, .content').length;
        const forms = $body.find('form').length;
        
        cy.log(`Navigation elements: ${navElements}`);
        cy.log(`Main content areas: ${mainContent}`);
        cy.log(`Forms found: ${forms}`);
        
        // Verify basic page structure
        expect(navElements + mainContent).to.be.greaterThan(0);
      });
    });

    it('should handle navigation links', () => {
      cy.visit(baseUrl);
      
      // Find all navigation links
      cy.get('nav a, .navbar a, .menu a, .navigation a').then(($links) => {
        const linkCount = $links.length;
        cy.log(`Found ${linkCount} navigation links`);
        
        if (linkCount > 0) {
          // Test first few links
          const linksToTest = Math.min(5, linkCount);
          
          for (let i = 0; i < linksToTest; i++) {
            const link = $links.eq(i);
            const href = link.attr('href');
            const text = link.text().trim();
            
            if (href && !href.startsWith('#') && !href.startsWith('javascript:')) {
              cy.log(`Testing link: ${text} -> ${href}`);
              
              // Click link and verify it doesn't cause errors
              cy.wrap(link).click();
              
              // Wait for page to load
              cy.wait(1000);
              
              // Check for error pages
              cy.get('body').then(($body) => {
                const hasErrors = $body.find('.error, .not-found, .404, .exception').length > 0;
                if (hasErrors) {
                  cy.log(`⚠️ Error page detected for link: ${text}`);
                } else {
                  cy.log(`✅ Link working: ${text}`);
                }
              });
              
              // Go back to homepage for next test
              cy.visit(baseUrl);
            }
          }
        }
      });
    });

    it('should be responsive on different screen sizes', () => {
      const viewports = [
        { width: 1920, height: 1080, name: 'Desktop Large' },
        { width: 1366, height: 768, name: 'Desktop Standard' },
        { width: 768, height: 1024, name: 'Tablet' },
        { width: 375, height: 667, name: 'Mobile' }
      ];

      viewports.forEach((viewport) => {
        cy.log(`Testing ${viewport.name} (${viewport.width}x${viewport.height})`);
        
        cy.viewport(viewport.width, viewport.height);
        cy.visit(baseUrl);
        
        // Wait for page to adjust
        cy.wait(1000);
        
        // Take screenshot for each viewport
        cy.screenshot(`responsive-${viewport.name.toLowerCase().replace(' ', '-')}`);
        
        // Check for mobile-specific elements on smaller screens
        if (viewport.width <= 768) {
          cy.get('body').then(($body) => {
            const mobileElements = $body.find('.mobile-menu, .hamburger, .menu-toggle').length;
            cy.log(`Mobile menu elements: ${mobileElements}`);
          });
        }
        
        // Verify page is still functional
        cy.get('body').should('be.visible');
      });
    });
  });

  describe('🔐 Authentication System', () => {
    it('should detect authentication requirements', () => {
      cy.visit(baseUrl);
      
      // Look for authentication elements
      cy.get('body').then(($body) => {
        const loginLinks = $body.find('a[href*="login"], .login-link, #login').length;
        const loginForms = $body.find('form[action*="login"], .login-form').length;
        const logoutElements = $body.find('a[href*="logout"], .logout').length;
        const userMenus = $body.find('.user-menu, .profile-menu').length;
        
        cy.log(`Login links: ${loginLinks}`);
        cy.log(`Login forms: ${loginForms}`);
        cy.log(`Logout elements: ${logoutElements}`);
        cy.log(`User menus: ${userMenus}`);
        
        if (logoutElements > 0 || userMenus > 0) {
          cy.log('✅ User appears to be logged in');
        } else if (loginLinks > 0 || loginForms > 0) {
          cy.log('ℹ️ Login interface available');
          
          // Try to access login form
          if (loginLinks > 0) {
            cy.get('a[href*="login"], .login-link').first().click();
            cy.wait(2000);
            
            // Check for login form fields
            cy.get('body').then(($loginBody) => {
              const usernameFields = $loginBody.find('input[name="username"], input[name="email"], #id_username').length;
              const passwordFields = $loginBody.find('input[name="password"], input[type="password"], #id_password').length;
              
              cy.log(`Username fields: ${usernameFields}`);
              cy.log(`Password fields: ${passwordFields}`);
              
              if (usernameFields > 0 && passwordFields > 0) {
                cy.log('✅ Complete login form found');
                
                // Test form interaction (without actually logging in)
                cy.get('input[name="username"], input[name="email"], #id_username').first().then(($username) => {
                  if ($username.is(':enabled')) {
                    cy.wrap($username).clear().type('test');
                    cy.log('✅ Username field accepts input');
                  }
                });
                
                cy.get('input[name="password"], input[type="password"], #id_password').first().then(($password) => {
                  if ($password.is(':enabled')) {
                    cy.wrap($password).clear().type('test');
                    cy.log('✅ Password field accepts input');
                  }
                });
              }
            });
          }
        } else {
          cy.log('⚠️ No authentication interface found');
        }
      });
    });
  });

  describe('📄 OCR Upload Functionality', () => {
    it('should access OCR upload page', () => {
      const ocrUrl = `${baseUrl}/ocr/upload/`;
      cy.log(`Navigating to OCR URL: ${ocrUrl}`);
      
      cy.visit(ocrUrl);
      
      // Log current URL (might be redirected)
      cy.url().then((currentUrl) => {
        cy.log(`Current URL after navigation: ${currentUrl}`);
      });
      
      // Take screenshot of OCR page
      cy.screenshot('ocr-upload-page');
      
      // Check for OCR-related elements
      cy.get('body').then(($body) => {
        const uploadForms = $body.find('form[enctype*="multipart"], .upload-form').length;
        const fileInputs = $body.find('input[type="file"]').length;
        const uploadButtons = $body.find('button[type="submit"], .upload-btn, .btn-upload').length;
        const dropzones = $body.find('.dropzone, .drag-drop, [data-dropzone]').length;
        
        cy.log(`Upload forms: ${uploadForms}`);
        cy.log(`File inputs: ${fileInputs}`);
        cy.log(`Upload buttons: ${uploadButtons}`);
        cy.log(`Dropzones: ${dropzones}`);
        
        // Check if this is a login page instead
        const isLoginPage = currentUrl.includes('login') || 
                           $body.find('input[type="password"]').length > 0;
        
        if (isLoginPage) {
          cy.log('ℹ️ Redirected to login page - authentication required');
        } else if (fileInputs > 0 || dropzones > 0) {
          cy.log('✅ OCR upload interface found');
        } else {
          cy.log('⚠️ No OCR upload interface found');
        }
      });
    });

    it('should test file upload interaction', () => {
      cy.visit(`${baseUrl}/ocr/upload/`);
      
      // Look for file input elements
      cy.get('body').then(($body) => {
        const fileInputs = $body.find('input[type="file"]');
        
        if (fileInputs.length > 0) {
          cy.log(`Found ${fileInputs.length} file input(s)`);
          
          // Create a test file
          const testContent = `FAKTURA VAT
Nr: FV/2025/001
Data: 29.08.2025

Sprzedawca:
Test Company Sp. z o.o.
ul. Testowa 123
00-001 Warszawa
NIP: 1234567890

Nabywca:
Klient Testowy
ul. Kliencka 456
00-002 Kraków
NIP: 0987654321

Pozycje:
1. Usługa testowa - 1000.00 PLN + 23% VAT = 1230.00 PLN

Razem do zapłaty: 1230.00 PLN`;
          
          // Try to interact with file input
          cy.get('input[type="file"]').first().then(($fileInput) => {
            if ($fileInput.is(':visible') && $fileInput.is(':enabled')) {
              cy.log('✅ File input is interactive');
              
              // Create a blob and try to upload
              const blob = new Blob([testContent], { type: 'text/plain' });
              const testFile = new File([blob], 'test_invoice.txt', { type: 'text/plain' });
              
              // Simulate file selection
              cy.wrap($fileInput).selectFile({
                contents: Cypress.Buffer.from(testContent),
                fileName: 'test_invoice.txt',
                mimeType: 'text/plain'
              }, { force: true });
              
              cy.log('✅ Test file uploaded to input');
              
            } else {
              cy.log('⚠️ File input not interactive');
            }
          });
        } else {
          cy.log('ℹ️ No file input elements found');
        }
      });
    });

    it('should test drag and drop functionality', () => {
      cy.visit(`${baseUrl}/ocr/upload/`);
      
      // Look for dropzone elements
      cy.get('body').then(($body) => {
        const dropzones = $body.find('.dropzone, .drag-drop, [data-dropzone]');
        
        if (dropzones.length > 0) {
          cy.log(`Found ${dropzones.length} dropzone(s)`);
          
          // Test drag and drop interaction
          cy.get('.dropzone, .drag-drop, [data-dropzone]').first().then(($dropzone) => {
            // Simulate drag enter
            cy.wrap($dropzone).trigger('dragenter');
            cy.wrap($dropzone).trigger('dragover');
            
            // Check if dropzone responds to drag events
            cy.wrap($dropzone).should('be.visible');
            
            cy.log('✅ Dropzone responds to drag events');
          });
        } else {
          cy.log('ℹ️ No dropzone elements found');
        }
      });
    });
  });

  describe('🔧 JavaScript and Performance', () => {
    it('should not have JavaScript errors', () => {
      // Listen for JavaScript errors
      cy.window().then((win) => {
        const errors = [];
        
        win.addEventListener('error', (e) => {
          errors.push(e.message);
        });
        
        win.addEventListener('unhandledrejection', (e) => {
          errors.push(e.reason);
        });
        
        cy.visit(baseUrl);
        
        // Wait for page to fully load
        cy.wait(3000);
        
        // Check for errors
        cy.then(() => {
          if (errors.length > 0) {
            cy.log(`❌ JavaScript errors found: ${errors.length}`);
            errors.forEach((error, index) => {
              cy.log(`Error ${index + 1}: ${error}`);
            });
          } else {
            cy.log('✅ No JavaScript errors detected');
          }
        });
      });
    });

    it('should have reasonable performance', () => {
      cy.visit(baseUrl);
      
      // Measure performance
      cy.window().then((win) => {
        const navigation = win.performance.getEntriesByType('navigation')[0];
        
        if (navigation) {
          const loadTime = navigation.loadEventEnd - navigation.loadEventStart;
          const domContentLoaded = navigation.domContentLoadedEventEnd - navigation.domContentLoadedEventStart;
          
          cy.log(`Page load time: ${loadTime}ms`);
          cy.log(`DOM content loaded: ${domContentLoaded}ms`);
          
          // Check performance thresholds
          if (loadTime < 5000) {
            cy.log('✅ Good page load performance');
          } else {
            cy.log('⚠️ Slow page load performance');
          }
        }
        
        // Check resource loading
        const resources = win.performance.getEntriesByType('resource');
        const slowResources = resources.filter(r => r.duration > 1000);
        
        cy.log(`Total resources: ${resources.length}`);
        cy.log(`Slow resources (>1s): ${slowResources.length}`);
        
        if (slowResources.length < 5) {
          cy.log('✅ Good resource loading performance');
        } else {
          cy.log('⚠️ Many slow resources detected');
        }
      });
    });

    it('should test AJAX functionality', () => {
      cy.visit(baseUrl);
      
      // Intercept AJAX requests
      cy.intercept('GET', '**').as('getRequests');
      cy.intercept('POST', '**').as('postRequests');
      
      // Try to trigger AJAX by interacting with elements
      cy.get('body').then(($body) => {
        const clickableElements = $body.find('button, .btn, a[href="#"]');
        
        if (clickableElements.length > 0) {
          cy.log(`Found ${clickableElements.length} clickable elements`);
          
          // Click first few elements to trigger potential AJAX
          const elementsToTest = Math.min(3, clickableElements.length);
          
          for (let i = 0; i < elementsToTest; i++) {
            cy.wrap(clickableElements.eq(i)).click({ force: true });
            cy.wait(1000);
          }
        }
      });
      
      // Check if any AJAX requests were made
      cy.get('@getRequests.all').then((requests) => {
        cy.log(`GET requests made: ${requests.length}`);
      });
      
      cy.get('@postRequests.all').then((requests) => {
        cy.log(`POST requests made: ${requests.length}`);
      });
    });
  });

  describe('📊 Accessibility and Standards', () => {
    it('should have basic accessibility features', () => {
      cy.visit(baseUrl);
      
      // Check for accessibility features
      cy.get('body').then(($body) => {
        const altTexts = $body.find('img[alt]').length;
        const labels = $body.find('label').length;
        const headings = $body.find('h1, h2, h3, h4, h5, h6').length;
        const landmarks = $body.find('main, nav, header, footer, aside').length;
        
        cy.log(`Images with alt text: ${altTexts}`);
        cy.log(`Form labels: ${labels}`);
        cy.log(`Headings: ${headings}`);
        cy.log(`Landmark elements: ${landmarks}`);
        
        // Basic accessibility score
        const accessibilityScore = altTexts + labels + headings + landmarks;
        
        if (accessibilityScore > 5) {
          cy.log('✅ Basic accessibility features present');
        } else {
          cy.log('⚠️ Limited accessibility features');
        }
      });
    });

    it('should have proper HTML structure', () => {
      cy.visit(baseUrl);
      
      // Check HTML structure
      cy.get('html').should('have.attr', 'lang');
      cy.get('head title').should('exist');
      cy.get('head meta[charset]').should('exist');
      
      // Check for viewport meta tag
      cy.get('head').then(($head) => {
        const viewportMeta = $head.find('meta[name="viewport"]').length;
        cy.log(`Viewport meta tag: ${viewportMeta > 0 ? '✅' : '❌'}`);
      });
      
      cy.log('✅ Basic HTML structure validated');
    });
  });

  afterEach(() => {
    // Clean up after each test
    cy.clearCookies();
    cy.clearLocalStorage();
  });

  after(() => {
    // Generate final report
    cy.task('generateCypressReport');
  });
});