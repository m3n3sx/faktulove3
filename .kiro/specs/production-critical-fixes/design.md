# Design Document

## Overview

The FaktuLove application has several critical production issues that prevent basic functionality. The main problems are:

1. **Missing React Bundle Files**: The OCR upload interface expects `upload-app.bundle.js` and React production files that don't exist in the static directory
2. **Disabled JavaScript Components**: Critical JavaScript files are commented out in `base.html` due to previous infinite loop issues
3. **Frontend Build Pipeline**: The React frontend in `/frontend` directory hasn't been built and deployed to static files
4. **Static File Serving Issues**: Icons and CSS files may not be loading correctly due to static file configuration problems
5. **Missing Fallback Mechanisms**: When JavaScript fails to load, there are no proper fallback mechanisms

## Architecture

### Static File Architecture
```
static/
├── assets/
│   ├── css/           # Bootstrap, icons, main styles
│   ├── js/            # Application JavaScript
│   │   ├── lib/       # Third-party libraries
│   │   └── *.js       # Custom application scripts
│   ├── images/        # Static images and icons
│   └── fonts/         # Icon fonts (Remix icons)
├── css/
│   ├── app.css        # React app styles
│   └── design-system.css  # Design system styles
└── js/
    ├── react.production.min.js     # React library
    ├── react-dom.production.min.js # ReactDOM library
    └── upload-app.bundle.js        # OCR upload React app
```

### Frontend Build Pipeline
```
frontend/
├── src/               # React source code
├── build/             # Built React application
├── package.json       # Dependencies and build scripts
└── webpack.config.js  # Build configuration
```

### JavaScript Loading Strategy
```
1. Core Dependencies (jQuery, Bootstrap)
2. CSRF Utilities
3. Application Managers (Navigation, Charts, Tables)
4. Page-specific Scripts (OCR Handler, Invoice Manager)
5. React Applications (Upload App)
```

## Components and Interfaces

### 1. Static File Management Component
**Purpose**: Ensure all static files are properly collected and served

**Interface**:
- Django `collectstatic` command integration
- Static file validation and health checks
- Fallback mechanisms for missing files

**Implementation**:
- Fix `STATICFILES_DIRS` configuration
- Implement static file health check endpoint
- Add missing file detection and logging

### 2. Frontend Build Component
**Purpose**: Build React applications and deploy to static directory

**Interface**:
- Build script execution
- Asset optimization and minification
- Source map generation for debugging

**Implementation**:
- Configure webpack build pipeline
- Create build and deployment scripts
- Integrate with Django static file collection

### 3. JavaScript Loading Manager
**Purpose**: Safely load JavaScript dependencies with error handling

**Interface**:
- Dependency loading with fallbacks
- Error detection and recovery
- Progressive enhancement support

**Implementation**:
- Re-enable critical JavaScript files with proper error handling
- Implement dependency loading order
- Add fallback mechanisms for failed loads

### 4. OCR Upload Interface Component
**Purpose**: Provide functional document upload interface

**Interface**:
- File selection and validation
- Upload progress tracking
- Error handling and user feedback

**Implementation**:
- Build React upload application
- Implement server-side fallback form
- Add proper error boundaries

### 5. Icon and Font Loading Component
**Purpose**: Ensure icons display correctly across the application

**Interface**:
- Font loading with fallbacks
- Icon sprite management
- CSS loading optimization

**Implementation**:
- Verify Remix icon font loading
- Implement icon fallbacks
- Add font loading error detection

## Data Models

### Static File Health Model
```python
class StaticFileHealth:
    file_path: str
    exists: bool
    size: int
    last_modified: datetime
    checksum: str
    load_time: float
```

### Frontend Build Status Model
```python
class FrontendBuildStatus:
    component: str  # 'upload-app', 'dashboard', etc.
    build_time: datetime
    success: bool
    bundle_size: int
    source_map_available: bool
    errors: List[str]
```

### JavaScript Loading Status Model
```python
class JavaScriptLoadingStatus:
    script_name: str
    loaded: bool
    load_time: float
    error_message: str
    fallback_used: bool
```

## Error Handling

### 1. Static File Loading Errors
- **Detection**: Monitor 404 errors for static files
- **Recovery**: Serve fallback files or generate missing files
- **Logging**: Log missing files with request context
- **User Impact**: Graceful degradation with basic functionality

### 2. JavaScript Loading Errors
- **Detection**: Use `onerror` handlers and try/catch blocks
- **Recovery**: Load fallback scripts or disable features gracefully
- **Logging**: Capture script loading failures with stack traces
- **User Impact**: Show user-friendly error messages with retry options

### 3. React Application Errors
- **Detection**: Error boundaries in React components
- **Recovery**: Fallback to server-rendered forms
- **Logging**: Capture React errors with component stack
- **User Impact**: Provide alternative interfaces when React fails

### 4. Build Pipeline Errors
- **Detection**: Monitor build script exit codes
- **Recovery**: Use previous successful builds as fallback
- **Logging**: Capture build errors with full output
- **User Impact**: Prevent deployment of broken builds

## Testing Strategy

### 1. Static File Testing
```bash
# Test static file collection
python manage.py collectstatic --dry-run

# Test static file serving
curl -I http://localhost:8000/static/assets/css/style.css

# Test icon font loading
curl -I http://localhost:8000/static/assets/css/remixicon.css
```

### 2. Frontend Build Testing
```bash
# Test React build process
cd frontend && npm run build

# Test bundle generation
ls -la frontend/build/static/js/

# Test bundle integration
python manage.py test faktury.tests.test_frontend_integration
```

### 3. JavaScript Loading Testing
```javascript
// Test dependency loading
window.addEventListener('load', function() {
    console.log('jQuery loaded:', typeof $ !== 'undefined');
    console.log('Bootstrap loaded:', typeof bootstrap !== 'undefined');
    console.log('React loaded:', typeof React !== 'undefined');
});

// Test error handling
window.addEventListener('error', function(e) {
    console.error('Script loading error:', e.filename, e.message);
});
```

### 4. OCR Upload Testing
```python
# Test upload interface rendering
def test_ocr_upload_page_renders(self):
    response = self.client.get('/ocr/upload/')
    self.assertEqual(response.status_code, 200)
    self.assertContains(response, 'ocr-upload-app')

# Test fallback form functionality
def test_ocr_upload_fallback_works(self):
    with self.settings(DEBUG=False):
        response = self.client.post('/ocr/upload/', {
            'document': SimpleUploadedFile('test.pdf', b'content')
        })
        self.assertEqual(response.status_code, 302)
```

### 5. Integration Testing
```python
# Test complete user workflow
def test_invoice_creation_workflow(self):
    # Login
    self.client.login(username='testuser', password='testpass')
    
    # Navigate to invoice creation
    response = self.client.get('/faktury/dodaj/')
    self.assertEqual(response.status_code, 200)
    
    # Submit invoice form
    response = self.client.post('/faktury/dodaj/', invoice_data)
    self.assertEqual(response.status_code, 302)
    
    # Verify invoice was created
    self.assertTrue(Faktura.objects.filter(numer='TEST-001').exists())
```

### 6. Performance Testing
```python
# Test static file loading performance
def test_static_file_performance(self):
    start_time = time.time()
    response = self.client.get('/static/assets/css/style.css')
    load_time = time.time() - start_time
    
    self.assertEqual(response.status_code, 200)
    self.assertLess(load_time, 1.0)  # Should load within 1 second

# Test JavaScript execution performance
def test_javascript_execution_performance(self):
    # Use Selenium to test actual browser performance
    driver.get('http://localhost:8000/')
    
    # Wait for JavaScript to load
    WebDriverWait(driver, 10).until(
        lambda d: d.execute_script('return typeof $ !== "undefined"')
    )
    
    # Measure page load time
    navigation_start = driver.execute_script(
        'return window.performance.timing.navigationStart'
    )
    load_complete = driver.execute_script(
        'return window.performance.timing.loadEventEnd'
    )
    
    load_time = (load_complete - navigation_start) / 1000
    self.assertLess(load_time, 5.0)  # Should load within 5 seconds
```

## Implementation Phases

### Phase 1: Static File Infrastructure (Critical)
1. Fix Django static file configuration
2. Implement static file health checks
3. Add missing file detection and logging
4. Test static file serving

### Phase 2: Frontend Build Pipeline (Critical)
1. Configure React build process
2. Create deployment scripts
3. Build and deploy React applications
4. Test bundle integration

### Phase 3: JavaScript Loading (High Priority)
1. Re-enable critical JavaScript files with error handling
2. Implement dependency loading manager
3. Add fallback mechanisms
4. Test JavaScript functionality

### Phase 4: OCR Upload Interface (High Priority)
1. Deploy React upload application
2. Implement server-side fallback
3. Add error boundaries and recovery
4. Test upload functionality

### Phase 5: Icon and Font Loading (Medium Priority)
1. Fix icon font loading issues
2. Implement icon fallbacks
3. Optimize font loading performance
4. Test cross-browser compatibility

### Phase 6: Monitoring and Optimization (Low Priority)
1. Implement performance monitoring
2. Add error tracking and alerting
3. Optimize loading performance
4. Create maintenance procedures