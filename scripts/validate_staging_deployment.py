#!/usr/bin/env python3
"""
Staging Deployment Validation Script
Validates that the design system integration is working correctly in staging
"""

import requests
import json
import time
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@dataclass
class ValidationCheck:
    """Individual validation check result"""
    name: str
    status: str  # passed, failed, warning
    message: str
    response_time: Optional[float] = None
    details: Optional[Dict[str, Any]] = None
    timestamp: datetime = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()

class StagingDeploymentValidator:
    """Validates staging deployment of design system integration"""
    
    def __init__(self, base_url: str = "http://staging.faktulove.local"):
        self.base_url = base_url
        self.session = requests.Session()
        self.session.timeout = 30
        self.results: List[ValidationCheck] = []
        
    def validate_health_endpoints(self) -> List[ValidationCheck]:
        """Validate basic health endpoints"""
        logger.info("Validating health endpoints...")
        results = []
        
        health_endpoints = [
            ("/health/", "Application Health Check"),
            ("/api/health/", "API Health Check"),
            ("/api/design-system/health/", "Design System Health Check"),
            ("/api/polish-business/health/", "Polish Business Health Check")
        ]
        
        for endpoint, description in health_endpoints:
            start_time = time.time()
            try:
                response = self.session.get(f"{self.base_url}{endpoint}")
                response_time = time.time() - start_time
                
                if response.status_code == 200:
                    data = response.json() if response.headers.get('content-type', '').startswith('application/json') else {}
                    results.append(ValidationCheck(
                        name=description,
                        status="passed",
                        message=f"Health check passed ({response.status_code})",
                        response_time=response_time,
                        details={"status_code": response.status_code, "data": data}
                    ))
                else:
                    results.append(ValidationCheck(
                        name=description,
                        status="failed",
                        message=f"Health check failed ({response.status_code})",
                        response_time=response_time,
                        details={"status_code": response.status_code}
                    ))
                    
            except Exception as e:
                response_time = time.time() - start_time
                results.append(ValidationCheck(
                    name=description,
                    status="failed",
                    message=f"Health check exception: {str(e)}",
                    response_time=response_time,
                    details={"error": str(e)}
                ))
        
        return results
    
    def validate_design_system_components(self) -> List[ValidationCheck]:
        """Validate design system component endpoints"""
        logger.info("Validating design system components...")
        results = []
        
        component_endpoints = [
            ("/api/design-system/components/", "Component Registry"),
            ("/api/design-system/themes/", "Theme Registry"),
            ("/api/design-system/tokens/", "Design Tokens"),
            ("/api/design-system/components/button/", "Button Component"),
            ("/api/design-system/components/input/", "Input Component"),
            ("/api/design-system/components/form/", "Form Component"),
            ("/api/design-system/components/table/", "Table Component"),
            ("/api/design-system/components/card/", "Card Component")
        ]
        
        for endpoint, description in component_endpoints:
            start_time = time.time()
            try:
                response = self.session.get(f"{self.base_url}{endpoint}")
                response_time = time.time() - start_time
                
                if response.status_code == 200:
                    data = response.json()
                    results.append(ValidationCheck(
                        name=f"Design System: {description}",
                        status="passed",
                        message=f"Component endpoint accessible",
                        response_time=response_time,
                        details={"component_count": len(data) if isinstance(data, list) else 1}
                    ))
                else:
                    results.append(ValidationCheck(
                        name=f"Design System: {description}",
                        status="failed",
                        message=f"Component endpoint failed ({response.status_code})",
                        response_time=response_time,
                        details={"status_code": response.status_code}
                    ))
                    
            except Exception as e:
                response_time = time.time() - start_time
                results.append(ValidationCheck(
                    name=f"Design System: {description}",
                    status="failed",
                    message=f"Component endpoint exception: {str(e)}",
                    response_time=response_time,
                    details={"error": str(e)}
                ))
        
        return results
    
    def validate_polish_business_components(self) -> List[ValidationCheck]:
        """Validate Polish business component endpoints"""
        logger.info("Validating Polish business components...")
        results = []
        
        polish_endpoints = [
            ("/api/polish-business/components/nip-validator/", "NIP Validator"),
            ("/api/polish-business/components/currency-input/", "Currency Input"),
            ("/api/polish-business/components/vat-rate-selector/", "VAT Rate Selector"),
            ("/api/polish-business/components/date-picker/", "Date Picker"),
            ("/api/polish-business/components/invoice-status-badge/", "Invoice Status Badge"),
            ("/api/polish-business/components/compliance-indicator/", "Compliance Indicator")
        ]
        
        for endpoint, description in polish_endpoints:
            start_time = time.time()
            try:
                response = self.session.get(f"{self.base_url}{endpoint}")
                response_time = time.time() - start_time
                
                if response.status_code == 200:
                    data = response.json()
                    polish_features = data.get("polish_business_features", [])
                    
                    if polish_features:
                        results.append(ValidationCheck(
                            name=f"Polish Business: {description}",
                            status="passed",
                            message=f"Component has Polish features: {', '.join(polish_features)}",
                            response_time=response_time,
                            details={"polish_features": polish_features}
                        ))
                    else:
                        results.append(ValidationCheck(
                            name=f"Polish Business: {description}",
                            status="warning",
                            message=f"Component missing Polish business features",
                            response_time=response_time,
                            details={"data": data}
                        ))
                else:
                    results.append(ValidationCheck(
                        name=f"Polish Business: {description}",
                        status="failed",
                        message=f"Component endpoint failed ({response.status_code})",
                        response_time=response_time,
                        details={"status_code": response.status_code}
                    ))
                    
            except Exception as e:
                response_time = time.time() - start_time
                results.append(ValidationCheck(
                    name=f"Polish Business: {description}",
                    status="failed",
                    message=f"Component endpoint exception: {str(e)}",
                    response_time=response_time,
                    details={"error": str(e)}
                ))
        
        return results
    
    def validate_frontend_assets(self) -> List[ValidationCheck]:
        """Validate frontend assets and static files"""
        logger.info("Validating frontend assets...")
        results = []
        
        asset_endpoints = [
            ("/static/css/design-system.css", "Design System CSS"),
            ("/static/js/design-system.js", "Design System JavaScript"),
            ("/static/js/polish-business.js", "Polish Business JavaScript"),
            ("/static/assets/fonts/", "Font Assets"),
            ("/static/assets/icons/", "Icon Assets")
        ]
        
        for endpoint, description in asset_endpoints:
            start_time = time.time()
            try:
                response = self.session.get(f"{self.base_url}{endpoint}")
                response_time = time.time() - start_time
                
                if response.status_code == 200:
                    content_length = len(response.content)
                    results.append(ValidationCheck(
                        name=f"Frontend Assets: {description}",
                        status="passed",
                        message=f"Asset loaded successfully ({content_length} bytes)",
                        response_time=response_time,
                        details={"content_length": content_length}
                    ))
                else:
                    results.append(ValidationCheck(
                        name=f"Frontend Assets: {description}",
                        status="failed" if response.status_code == 404 else "warning",
                        message=f"Asset request failed ({response.status_code})",
                        response_time=response_time,
                        details={"status_code": response.status_code}
                    ))
                    
            except Exception as e:
                response_time = time.time() - start_time
                results.append(ValidationCheck(
                    name=f"Frontend Assets: {description}",
                    status="failed",
                    message=f"Asset request exception: {str(e)}",
                    response_time=response_time,
                    details={"error": str(e)}
                ))
        
        return results
    
    def validate_page_rendering(self) -> List[ValidationCheck]:
        """Validate that key pages render correctly"""
        logger.info("Validating page rendering...")
        results = []
        
        pages = [
            ("/", "Home Page"),
            ("/accounts/login/", "Login Page"),
            ("/dashboard/", "Dashboard"),
            ("/faktury/", "Invoice List"),
            ("/faktury/nowa/", "New Invoice Form"),
            ("/ocr/upload/", "OCR Upload Page"),
            ("/admin/", "Admin Panel")
        ]
        
        for endpoint, description in pages:
            start_time = time.time()
            try:
                response = self.session.get(f"{self.base_url}{endpoint}")
                response_time = time.time() - start_time
                
                if response.status_code == 200:
                    content = response.text
                    
                    # Check for design system indicators
                    has_design_system = any(indicator in content for indicator in [
                        'data-design-system',
                        'ds-component',
                        'design-system-theme',
                        'polish-business-component'
                    ])
                    
                    if has_design_system:
                        results.append(ValidationCheck(
                            name=f"Page Rendering: {description}",
                            status="passed",
                            message=f"Page renders with design system components",
                            response_time=response_time,
                            details={"has_design_system": True, "content_length": len(content)}
                        ))
                    else:
                        results.append(ValidationCheck(
                            name=f"Page Rendering: {description}",
                            status="warning",
                            message=f"Page renders but may not use design system",
                            response_time=response_time,
                            details={"has_design_system": False, "content_length": len(content)}
                        ))
                        
                elif response.status_code in [301, 302]:
                    results.append(ValidationCheck(
                        name=f"Page Rendering: {description}",
                        status="passed",
                        message=f"Page redirects correctly ({response.status_code})",
                        response_time=response_time,
                        details={"status_code": response.status_code, "location": response.headers.get('Location')}
                    ))
                else:
                    results.append(ValidationCheck(
                        name=f"Page Rendering: {description}",
                        status="failed",
                        message=f"Page failed to render ({response.status_code})",
                        response_time=response_time,
                        details={"status_code": response.status_code}
                    ))
                    
            except Exception as e:
                response_time = time.time() - start_time
                results.append(ValidationCheck(
                    name=f"Page Rendering: {description}",
                    status="failed",
                    message=f"Page rendering exception: {str(e)}",
                    response_time=response_time,
                    details={"error": str(e)}
                ))
        
        return results
    
    def validate_performance_metrics(self) -> List[ValidationCheck]:
        """Validate performance metrics"""
        logger.info("Validating performance metrics...")
        results = []
        
        # Test response times for key endpoints
        performance_endpoints = [
            ("/", "Home Page Load Time"),
            ("/api/design-system/components/", "Component API Response Time"),
            ("/static/css/design-system.css", "CSS Load Time"),
            ("/static/js/design-system.js", "JavaScript Load Time")
        ]
        
        for endpoint, description in performance_endpoints:
            start_time = time.time()
            try:
                response = self.session.get(f"{self.base_url}{endpoint}")
                response_time = time.time() - start_time
                
                # Performance thresholds
                if response_time < 1.0:
                    status = "passed"
                    message = f"Good performance: {response_time:.2f}s"
                elif response_time < 3.0:
                    status = "warning"
                    message = f"Acceptable performance: {response_time:.2f}s"
                else:
                    status = "failed"
                    message = f"Poor performance: {response_time:.2f}s"
                
                results.append(ValidationCheck(
                    name=f"Performance: {description}",
                    status=status,
                    message=message,
                    response_time=response_time,
                    details={"threshold_passed": response_time < 1.0}
                ))
                
            except Exception as e:
                response_time = time.time() - start_time
                results.append(ValidationCheck(
                    name=f"Performance: {description}",
                    status="failed",
                    message=f"Performance test exception: {str(e)}",
                    response_time=response_time,
                    details={"error": str(e)}
                ))
        
        return results
    
    def validate_database_connectivity(self) -> List[ValidationCheck]:
        """Validate database connectivity and migrations"""
        logger.info("Validating database connectivity...")
        results = []
        
        try:
            # Test database connectivity through API
            start_time = time.time()
            response = self.session.get(f"{self.base_url}/api/health/database/")
            response_time = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                if data.get("database_connected", False):
                    results.append(ValidationCheck(
                        name="Database Connectivity",
                        status="passed",
                        message="Database connection successful",
                        response_time=response_time,
                        details=data
                    ))
                else:
                    results.append(ValidationCheck(
                        name="Database Connectivity",
                        status="failed",
                        message="Database connection failed",
                        response_time=response_time,
                        details=data
                    ))
            else:
                results.append(ValidationCheck(
                    name="Database Connectivity",
                    status="failed",
                    message=f"Database health check failed ({response.status_code})",
                    response_time=response_time,
                    details={"status_code": response.status_code}
                ))
                
        except Exception as e:
            results.append(ValidationCheck(
                name="Database Connectivity",
                status="failed",
                message=f"Database connectivity exception: {str(e)}",
                details={"error": str(e)}
            ))
        
        return results
    
    def run_all_validations(self) -> Dict[str, Any]:
        """Run all staging deployment validations"""
        logger.info("Starting staging deployment validation...")
        
        all_results = []
        
        # Run all validation categories
        validation_methods = [
            self.validate_health_endpoints,
            self.validate_design_system_components,
            self.validate_polish_business_components,
            self.validate_frontend_assets,
            self.validate_page_rendering,
            self.validate_performance_metrics,
            self.validate_database_connectivity
        ]
        
        for validation_method in validation_methods:
            try:
                results = validation_method()
                all_results.extend(results)
            except Exception as e:
                logger.error(f"Validation method {validation_method.__name__} failed: {str(e)}")
                all_results.append(ValidationCheck(
                    name=f"Validation Method: {validation_method.__name__}",
                    status="failed",
                    message=f"Validation method failed: {str(e)}",
                    details={"error": str(e)}
                ))
        
        self.results = all_results
        return self.generate_report()
    
    def generate_report(self) -> Dict[str, Any]:
        """Generate comprehensive validation report"""
        total_checks = len(self.results)
        passed_checks = len([r for r in self.results if r.status == "passed"])
        failed_checks = len([r for r in self.results if r.status == "failed"])
        warning_checks = len([r for r in self.results if r.status == "warning"])
        
        avg_response_time = sum(r.response_time for r in self.results if r.response_time) / len([r for r in self.results if r.response_time]) if self.results else 0
        
        report = {
            "summary": {
                "total_checks": total_checks,
                "passed": passed_checks,
                "failed": failed_checks,
                "warnings": warning_checks,
                "success_rate": (passed_checks / total_checks * 100) if total_checks > 0 else 0,
                "average_response_time": avg_response_time,
                "timestamp": datetime.now().isoformat(),
                "staging_url": self.base_url
            },
            "results": [asdict(result) for result in self.results],
            "categories": {
                "health_checks": [r for r in self.results if "Health Check" in r.name],
                "design_system": [r for r in self.results if "Design System" in r.name],
                "polish_business": [r for r in self.results if "Polish Business" in r.name],
                "frontend_assets": [r for r in self.results if "Frontend Assets" in r.name],
                "page_rendering": [r for r in self.results if "Page Rendering" in r.name],
                "performance": [r for r in self.results if "Performance" in r.name],
                "database": [r for r in self.results if "Database" in r.name]
            },
            "recommendations": self._generate_recommendations()
        }
        
        # Save report to file
        report_file = f"test_results/staging_validation_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2, default=str)
        
        logger.info(f"Staging validation report saved to: {report_file}")
        return report
    
    def _generate_recommendations(self) -> List[str]:
        """Generate recommendations based on validation results"""
        recommendations = []
        
        failed_results = [r for r in self.results if r.status == "failed"]
        warning_results = [r for r in self.results if r.status == "warning"]
        
        if failed_results:
            recommendations.append("Fix failed validation checks before proceeding to production")
            
        if any("Health Check" in r.name for r in failed_results):
            recommendations.append("Critical: Fix health check failures - application may not be running correctly")
            
        if any("Design System" in r.name for r in failed_results):
            recommendations.append("Fix design system component issues - core functionality affected")
            
        if any("Polish Business" in r.name for r in failed_results):
            recommendations.append("Address Polish business component issues - business functionality affected")
            
        if any("Performance" in r.name for r in failed_results):
            recommendations.append("Optimize performance issues - user experience may be impacted")
            
        if any("Database" in r.name for r in failed_results):
            recommendations.append("Critical: Fix database connectivity issues")
            
        if warning_results:
            recommendations.append("Review warning items to ensure optimal functionality")
            
        # Performance recommendations
        slow_responses = [r for r in self.results if r.response_time and r.response_time > 2.0]
        if slow_responses:
            recommendations.append("Optimize slow response times for better user experience")
            
        return recommendations

def main():
    """Main execution function"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Validate Staging Deployment of Design System Integration")
    parser.add_argument("--base-url", default="http://staging.faktulove.local", help="Base URL for validation")
    parser.add_argument("--category", help="Run specific validation category")
    
    args = parser.parse_args()
    
    validator = StagingDeploymentValidator(base_url=args.base_url)
    
    if args.category:
        method_name = f"validate_{args.category}"
        if hasattr(validator, method_name):
            method = getattr(validator, method_name)
            results = method()
            validator.results = results
            report = validator.generate_report()
            print(f"Category validation completed: {len([r for r in results if r.status == 'passed'])}/{len(results)} checks passed")
        else:
            print(f"Category {args.category} not found")
    else:
        report = validator.run_all_validations()
        print(f"Staging validation completed: {report['summary']['passed']}/{report['summary']['total_checks']} checks passed")
        if report['summary']['failed'] > 0:
            print(f"⚠️  {report['summary']['failed']} checks failed - review before production deployment")
        print(f"Average response time: {report['summary']['average_response_time']:.2f}s")

if __name__ == "__main__":
    main()