# Comprehensive Testing Framework Guide

## Overview

This document describes the comprehensive testing framework implemented for the FaktuLove system improvements. The framework includes multiple types of tests to ensure system quality, performance, and accessibility.

## Test Types

### 1. Unit Tests (`test_comprehensive_unit_tests.py`)
- **Purpose**: Test individual components and services in isolation
- **Coverage**: All new services and components from system improvements
- **Location**: `faktury/tests/test_comprehensive_unit_tests.py`
- **Run Command**: `pytest faktury/tests/test_comprehensive_unit_tests.py -v`

**Components Tested**:
- NavigationManager
- AdminAssetManager
- AdminEnhancementService
- EnhancedOCRUploadManager
- OCRFeedbackSystem
- UIConsistencyManager
- UserExperienceOptimizer
- CompanyManagementService
- PartnershipManager
- PerformanceMonitor
- AssetOptimizer
- ErrorManager
- ValidationService
- SearchService
- DataExportImportService
- SecurityService
- HealthCheckService
- MaintenanceService

### 2. Integration Tests (`test_comprehensive_integration_tests.py`)
- **Purpose**: Test component interactions and workflows
- **Coverage**: Cross-component functionality and data flow
- **Location**: `faktury/tests/test_comprehensive_integration_tests.py`
- **Run Command**: `pytest faktury/tests/test_comprehensive_integration_tests.py -v`

**Test Areas**:
- OCR workflow integration
- Multi-company workflow integration
- Performance monitoring integration
- Validation service integration
- API integration
- Database integration
- Security integration

### 3. End-to-End Tests (`test_comprehensive_e2e_tests.py`)
- **Purpose**: Test complete user scenarios from start to finish
- **Coverage**: Full user workflows and business processes
- **Location**: `faktury/tests/test_comprehensive_e2e_tests.py`
- **Run Command**: `pytest faktury/tests/test_comprehensive_e2e_tests.py -v`

**Scenarios Tested**:
- User registration and login workflow
- Invoice creation workflow
- OCR upload and processing workflow
- Multi-company setup workflow
- Browser-based workflows (with Selenium)
- Error handling workflows

### 4. Performance Tests (`test_comprehensive_performance_tests.py`)
- **Purpose**: Validate response time requirements and system performance
- **Coverage**: Page load times, database performance, concurrent processing
- **Location**: `faktury/tests/test_comprehensive_performance_tests.py`
- **Run Command**: `pytest faktury/tests/test_comprehensive_performance_tests.py -v`

**Performance Criteria**:
- Page load times < 3 seconds
- API response times < 1 second
- Database queries < 1 second
- OCR processing < 5 seconds per document
- Memory usage monitoring
- Concurrent user handling

### 5. Accessibility Tests (`test_accessibility_compliance.py`)
- **Purpose**: Ensure WCAG 2.1 compliance
- **Coverage**: Web accessibility standards and screen reader compatibility
- **Location**: `faktury/tests/test_accessibility_compliance.py`
- **Run Command**: `pytest faktury/tests/test_accessibility_compliance.py -v`

**WCAG Guidelines Tested**:
- 1.1.1: Images have alt text
- 1.3.1: Form labels and heading hierarchy
- 1.4.3: Color contrast indicators
- 2.4.1: Skip navigation links
- 2.4.7: Focus indicators
- 3.1.1: Language declaration
- 3.3.1: Form error messages
- Keyboard navigation support
- Screen reader compatibility

### 6. Cross-Browser Tests (`test_cross_browser_compatibility.py`)
- **Purpose**: Ensure compatibility across different browsers
- **Coverage**: Chrome, Firefox, Edge browser testing
- **Location**: `faktury/tests/test_cross_browser_compatibility.py`
- **Run Command**: `pytest faktury/tests/test_cross_browser_compatibility.py -v`

**Browser Features Tested**:
- Basic page loading
- JavaScript functionality
- CSS rendering
- Form submission
- Responsive design
- Browser-specific features

### 7. Mobile Device Tests (`test_mobile_device_compatibility.py`)
- **Purpose**: Test responsive design and mobile functionality
- **Coverage**: Various mobile devices and touch interfaces
- **Location**: `faktury/tests/test_mobile_device_compatibility.py`
- **Run Command**: `pytest faktury/tests/test_mobile_device_compatibility.py -v`

**Mobile Devices Tested**:
- iPhone 12 (390x844)
- iPhone SE (375x667)
- Samsung Galaxy S21 (360x800)
- iPad (768x1024)
- iPad Pro (1024x1366)

**Mobile Features Tested**:
- Touch interface elements (44px minimum)
- Mobile navigation
- Form interaction
- Table responsiveness
- Performance on mobile

### 8. Visual Regression Tests (`test_visual_regression.py`)
- **Purpose**: Detect unintended UI changes
- **Coverage**: Visual consistency across pages and screen sizes
- **Location**: `faktury/tests/test_visual_regression.py`
- **Run Command**: `pytest faktury/tests/test_visual_regression.py -v`

**Visual Elements Tested**:
- Homepage consistency
- Admin panel consistency
- Form layouts
- Navigation elements
- Responsive layouts
- Color scheme consistency

## Test Configuration

### pytest.ini
Main pytest configuration file with:
- Test discovery patterns
- Coverage settings
- Test markers
- Warning filters
- Performance thresholds

### conftest.py
Global test fixtures and configuration:
- Database setup
- User fixtures
- Company and invoice fixtures
- File upload fixtures
- OCR service mocks
- Performance timers
- Browser drivers
- Mobile emulation

## Running Tests

### Individual Test Suites
```bash
# Unit tests
pytest faktury/tests/test_comprehensive_unit_tests.py -v

# Integration tests
pytest faktury/tests/test_comprehensive_integration_tests.py -v

# End-to-end tests
pytest faktury/tests/test_comprehensive_e2e_tests.py -v

# Performance tests
pytest faktury/tests/test_comprehensive_performance_tests.py -v

# Accessibility tests
pytest faktury/tests/test_accessibility_compliance.py -v

# Browser tests
pytest faktury/tests/test_cross_browser_compatibility.py -v

# Mobile tests
pytest faktury/tests/test_mobile_device_compatibility.py -v

# Visual regression tests
pytest faktury/tests/test_visual_regression.py -v
```

### Comprehensive Test Runner
```bash
# Run all tests
python run_comprehensive_tests.py

# Run specific test suites
python run_comprehensive_tests.py --suites unit integration performance

# List available test suites
python run_comprehensive_tests.py --list-suites
```

### Test Markers
Use pytest markers to run specific test categories:
```bash
# Run only unit tests
pytest -m unit

# Run only performance tests
pytest -m performance

# Run only accessibility tests
pytest -m accessibility

# Run only browser tests
pytest -m browser

# Run only mobile tests
pytest -m mobile

# Run only visual tests
pytest -m visual
```

## Test Requirements

### System Requirements
- Python 3.11+
- Django 4.2+
- PostgreSQL/SQLite
- Chrome/Chromium browser (for Selenium tests)
- Firefox browser (optional, for cross-browser tests)
- Edge browser (optional, for cross-browser tests)

### Python Dependencies
Install test requirements:
```bash
pip install -r test_requirements.txt
```

### Browser Drivers
For browser testing, install WebDriver binaries:
```bash
# Chrome driver (automatic with webdriver-manager)
# Firefox driver (automatic with webdriver-manager)
# Edge driver (automatic with webdriver-manager)
```

## Test Data Management

### Fixtures
- Test users with different roles
- Test companies with Polish business data
- Test contractors and invoices
- Sample file uploads (PDF, images)
- Mock OCR responses

### Database
- Tests use isolated database transactions
- SQLite in-memory database for speed
- Automatic cleanup after each test
- Realistic Polish business data

## Performance Benchmarks

### Response Time Requirements
- Homepage: < 3 seconds
- Invoice list: < 3 seconds
- Invoice detail: < 2 seconds
- Admin panel: < 3 seconds
- API endpoints: < 1 second
- Database queries: < 1 second
- OCR processing: < 5 seconds per document

### Resource Usage
- Memory usage: < 200MB for 20 documents
- Concurrent users: 50+ simultaneous
- Database connections: Efficient pooling
- Cache hit ratio: > 90%

## Accessibility Standards

### WCAG 2.1 Compliance
- Level AA compliance target
- Keyboard navigation support
- Screen reader compatibility
- Color contrast requirements
- Touch target sizing (44px minimum)
- Focus indicators
- Alternative text for images
- Proper heading hierarchy
- Form labels and error messages

## Browser Support

### Desktop Browsers
- Chrome 90+ ✅
- Firefox 88+ ✅
- Edge 90+ ✅
- Safari 14+ (manual testing recommended)

### Mobile Browsers
- Chrome Mobile ✅
- Safari Mobile ✅
- Samsung Internet ✅
- Firefox Mobile ✅

## Continuous Integration

### CI/CD Integration
The test framework is designed for CI/CD pipelines:
- Headless browser support
- Parallel test execution
- JUnit XML output
- Coverage reporting
- Performance metrics
- Visual regression baselines

### GitHub Actions Example
```yaml
name: Comprehensive Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install -r test_requirements.txt
      - name: Run comprehensive tests
        run: python run_comprehensive_tests.py
```

## Troubleshooting

### Common Issues

#### Selenium WebDriver Issues
```bash
# Update Chrome driver
pip install --upgrade webdriver-manager

# Check Chrome version
google-chrome --version
```

#### Database Issues
```bash
# Reset test database
python manage.py migrate --run-syncdb
python manage.py flush --noinput
```

#### Performance Test Failures
- Check system resources
- Ensure no other heavy processes running
- Verify database optimization
- Check network connectivity

#### Visual Regression Failures
- Review screenshot differences in `test_results/visual_regression/`
- Update baselines if changes are intentional
- Check for font rendering differences across systems

### Debug Mode
Run tests with verbose output and debugging:
```bash
pytest -v -s --tb=long --capture=no
```

## Reporting

### Test Reports
- HTML coverage reports in `htmlcov/`
- JSON test results in `test_results/`
- Visual regression screenshots in `test_results/visual_regression/`
- Performance metrics in test output

### Quality Metrics
- Test coverage percentage
- Performance benchmarks
- Accessibility compliance score
- Browser compatibility matrix
- Visual regression status

## Maintenance

### Regular Tasks
- Update browser drivers monthly
- Review and update performance benchmarks
- Refresh visual regression baselines
- Update accessibility standards
- Monitor test execution times
- Clean up old test results

### Test Data Refresh
- Update Polish business test data
- Refresh sample documents
- Update mock API responses
- Review test scenarios for completeness