#!/usr/bin/env python3
"""
Polish Business Functionality Validation Framework
Validates all Polish business-specific features in the design system integration
"""

import json
import logging
from datetime import datetime, date
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
import re
import requests
from decimal import Decimal

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@dataclass
class ValidationResult:
    """Result of a Polish business functionality validation"""
    test_name: str
    status: str  # passed, failed, warning
    message: str
    details: Optional[Dict[str, Any]] = None
    timestamp: datetime = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()

class PolishBusinessValidator:
    """Validator for Polish business functionality in design system integration"""
    
    def __init__(self, base_url: str = "http://staging.faktulove.local"):
        self.base_url = base_url
        self.results: List[ValidationResult] = []
        
    def validate_nip_functionality(self) -> List[ValidationResult]:
        """Validate NIP (Tax Identification Number) functionality"""
        logger.info("Validating NIP functionality...")
        results = []
        
        # Test cases for NIP validation
        test_cases = [
            ("1234567890", True, "Valid NIP format"),
            ("123-456-78-90", True, "Valid NIP with dashes"),
            ("123 456 78 90", True, "Valid NIP with spaces"),
            ("1234567891", False, "Invalid NIP checksum"),
            ("12345678", False, "Too short NIP"),
            ("12345678901", False, "Too long NIP"),
            ("abcdefghij", False, "Non-numeric NIP"),
            ("", False, "Empty NIP")
        ]
        
        for nip, expected_valid, description in test_cases:
            try:
                # Test API endpoint
                response = requests.post(
                    f"{self.base_url}/api/polish-business/validate-nip/",
                    json={"nip": nip},
                    timeout=10
                )
                
                if response.status_code == 200:
                    data = response.json()
                    is_valid = data.get("valid", False)
                    
                    if is_valid == expected_valid:
                        results.append(ValidationResult(
                            test_name=f"NIP Validation: {description}",
                            status="passed",
                            message=f"NIP '{nip}' validation result correct: {is_valid}",
                            details={"nip": nip, "expected": expected_valid, "actual": is_valid}
                        ))
                    else:
                        results.append(ValidationResult(
                            test_name=f"NIP Validation: {description}",
                            status="failed",
                            message=f"NIP '{nip}' validation incorrect. Expected: {expected_valid}, Got: {is_valid}",
                            details={"nip": nip, "expected": expected_valid, "actual": is_valid}
                        ))
                else:
                    results.append(ValidationResult(
                        test_name=f"NIP Validation: {description}",
                        status="failed",
                        message=f"API request failed with status {response.status_code}",
                        details={"nip": nip, "status_code": response.status_code}
                    ))
                    
            except Exception as e:
                results.append(ValidationResult(
                    test_name=f"NIP Validation: {description}",
                    status="failed",
                    message=f"Exception during NIP validation: {str(e)}",
                    details={"nip": nip, "error": str(e)}
                ))
        
        return results
    
    def validate_vat_calculations(self) -> List[ValidationResult]:
        """Validate Polish VAT rate calculations"""
        logger.info("Validating VAT calculations...")
        results = []
        
        # Polish VAT rates and test cases
        vat_test_cases = [
            (100.00, 23, 123.00, "Standard VAT rate 23%"),
            (100.00, 8, 108.00, "Reduced VAT rate 8%"),
            (100.00, 5, 105.00, "Reduced VAT rate 5%"),
            (100.00, 0, 100.00, "Zero VAT rate 0%"),
            (1000.00, 23, 1230.00, "Higher amount with 23% VAT"),
            (50.50, 23, 62.12, "Decimal amount with VAT")
        ]
        
        for net_amount, vat_rate, expected_gross, description in vat_test_cases:
            try:
                response = requests.post(
                    f"{self.base_url}/api/polish-business/calculate-vat/",
                    json={
                        "net_amount": net_amount,
                        "vat_rate": vat_rate
                    },
                    timeout=10
                )
                
                if response.status_code == 200:
                    data = response.json()
                    gross_amount = data.get("gross_amount", 0)
                    
                    # Allow small floating point differences
                    if abs(gross_amount - expected_gross) < 0.01:
                        results.append(ValidationResult(
                            test_name=f"VAT Calculation: {description}",
                            status="passed",
                            message=f"VAT calculation correct: {net_amount} + {vat_rate}% = {gross_amount}",
                            details={
                                "net_amount": net_amount,
                                "vat_rate": vat_rate,
                                "expected_gross": expected_gross,
                                "actual_gross": gross_amount
                            }
                        ))
                    else:
                        results.append(ValidationResult(
                            test_name=f"VAT Calculation: {description}",
                            status="failed",
                            message=f"VAT calculation incorrect. Expected: {expected_gross}, Got: {gross_amount}",
                            details={
                                "net_amount": net_amount,
                                "vat_rate": vat_rate,
                                "expected_gross": expected_gross,
                                "actual_gross": gross_amount
                            }
                        ))
                else:
                    results.append(ValidationResult(
                        test_name=f"VAT Calculation: {description}",
                        status="failed",
                        message=f"API request failed with status {response.status_code}",
                        details={"status_code": response.status_code}
                    ))
                    
            except Exception as e:
                results.append(ValidationResult(
                    test_name=f"VAT Calculation: {description}",
                    status="failed",
                    message=f"Exception during VAT calculation: {str(e)}",
                    details={"error": str(e)}
                ))
        
        return results
    
    def validate_currency_formatting(self) -> List[ValidationResult]:
        """Validate Polish currency formatting (PLN)"""
        logger.info("Validating currency formatting...")
        results = []
        
        currency_test_cases = [
            (1234.56, "1 234,56 zł", "Standard currency formatting"),
            (1000.00, "1 000,00 zł", "Round amount formatting"),
            (0.50, "0,50 zł", "Small amount formatting"),
            (1000000.99, "1 000 000,99 zł", "Large amount formatting"),
            (0, "0,00 zł", "Zero amount formatting")
        ]
        
        for amount, expected_format, description in currency_test_cases:
            try:
                response = requests.post(
                    f"{self.base_url}/api/polish-business/format-currency/",
                    json={"amount": amount, "currency": "PLN"},
                    timeout=10
                )
                
                if response.status_code == 200:
                    data = response.json()
                    formatted = data.get("formatted", "")
                    
                    if formatted == expected_format:
                        results.append(ValidationResult(
                            test_name=f"Currency Formatting: {description}",
                            status="passed",
                            message=f"Currency formatting correct: {amount} -> {formatted}",
                            details={"amount": amount, "expected": expected_format, "actual": formatted}
                        ))
                    else:
                        results.append(ValidationResult(
                            test_name=f"Currency Formatting: {description}",
                            status="failed",
                            message=f"Currency formatting incorrect. Expected: {expected_format}, Got: {formatted}",
                            details={"amount": amount, "expected": expected_format, "actual": formatted}
                        ))
                else:
                    results.append(ValidationResult(
                        test_name=f"Currency Formatting: {description}",
                        status="failed",
                        message=f"API request failed with status {response.status_code}",
                        details={"status_code": response.status_code}
                    ))
                    
            except Exception as e:
                results.append(ValidationResult(
                    test_name=f"Currency Formatting: {description}",
                    status="failed",
                    message=f"Exception during currency formatting: {str(e)}",
                    details={"error": str(e)}
                ))
        
        return results
    
    def validate_date_formatting(self) -> List[ValidationResult]:
        """Validate Polish date formatting"""
        logger.info("Validating date formatting...")
        results = []
        
        date_test_cases = [
            (date(2025, 8, 29), "29.08.2025", "Standard date formatting"),
            (date(2025, 1, 1), "01.01.2025", "New Year date formatting"),
            (date(2025, 12, 31), "31.12.2025", "Year end date formatting"),
            (date(2025, 2, 5), "05.02.2025", "Single digit day/month formatting")
        ]
        
        for test_date, expected_format, description in date_test_cases:
            try:
                response = requests.post(
                    f"{self.base_url}/api/polish-business/format-date/",
                    json={"date": test_date.isoformat()},
                    timeout=10
                )
                
                if response.status_code == 200:
                    data = response.json()
                    formatted = data.get("formatted", "")
                    
                    if formatted == expected_format:
                        results.append(ValidationResult(
                            test_name=f"Date Formatting: {description}",
                            status="passed",
                            message=f"Date formatting correct: {test_date} -> {formatted}",
                            details={"date": str(test_date), "expected": expected_format, "actual": formatted}
                        ))
                    else:
                        results.append(ValidationResult(
                            test_name=f"Date Formatting: {description}",
                            status="failed",
                            message=f"Date formatting incorrect. Expected: {expected_format}, Got: {formatted}",
                            details={"date": str(test_date), "expected": expected_format, "actual": formatted}
                        ))
                else:
                    results.append(ValidationResult(
                        test_name=f"Date Formatting: {description}",
                        status="failed",
                        message=f"API request failed with status {response.status_code}",
                        details={"status_code": response.status_code}
                    ))
                    
            except Exception as e:
                results.append(ValidationResult(
                    test_name=f"Date Formatting: {description}",
                    status="failed",
                    message=f"Exception during date formatting: {str(e)}",
                    details={"error": str(e)}
                ))
        
        return results
    
    def validate_invoice_compliance(self) -> List[ValidationResult]:
        """Validate Polish invoice compliance features"""
        logger.info("Validating invoice compliance...")
        results = []
        
        # Test invoice compliance validation
        compliance_test_cases = [
            {
                "invoice_data": {
                    "numer": "FV/2025/001",
                    "data_wystawienia": "2025-08-29",
                    "sprzedawca_nip": "1234567890",
                    "nabywca_nip": "0987654321",
                    "pozycje": [
                        {
                            "nazwa": "Usługa konsultingowa",
                            "ilosc": 1,
                            "cena_netto": 1000.00,
                            "stawka_vat": 23
                        }
                    ]
                },
                "expected_valid": True,
                "description": "Valid Polish invoice"
            },
            {
                "invoice_data": {
                    "numer": "",
                    "data_wystawienia": "2025-08-29",
                    "sprzedawca_nip": "1234567890",
                    "nabywca_nip": "0987654321"
                },
                "expected_valid": False,
                "description": "Invoice without number"
            }
        ]
        
        for test_case in compliance_test_cases:
            try:
                response = requests.post(
                    f"{self.base_url}/api/polish-business/validate-invoice-compliance/",
                    json=test_case["invoice_data"],
                    timeout=10
                )
                
                if response.status_code == 200:
                    data = response.json()
                    is_compliant = data.get("compliant", False)
                    
                    if is_compliant == test_case["expected_valid"]:
                        results.append(ValidationResult(
                            test_name=f"Invoice Compliance: {test_case['description']}",
                            status="passed",
                            message=f"Invoice compliance validation correct: {is_compliant}",
                            details={
                                "expected": test_case["expected_valid"],
                                "actual": is_compliant,
                                "validation_details": data.get("details", {})
                            }
                        ))
                    else:
                        results.append(ValidationResult(
                            test_name=f"Invoice Compliance: {test_case['description']}",
                            status="failed",
                            message=f"Invoice compliance validation incorrect. Expected: {test_case['expected_valid']}, Got: {is_compliant}",
                            details={
                                "expected": test_case["expected_valid"],
                                "actual": is_compliant,
                                "validation_details": data.get("details", {})
                            }
                        ))
                else:
                    results.append(ValidationResult(
                        test_name=f"Invoice Compliance: {test_case['description']}",
                        status="failed",
                        message=f"API request failed with status {response.status_code}",
                        details={"status_code": response.status_code}
                    ))
                    
            except Exception as e:
                results.append(ValidationResult(
                    test_name=f"Invoice Compliance: {test_case['description']}",
                    status="failed",
                    message=f"Exception during compliance validation: {str(e)}",
                    details={"error": str(e)}
                ))
        
        return results
    
    def validate_design_system_integration(self) -> List[ValidationResult]:
        """Validate design system integration with Polish business components"""
        logger.info("Validating design system integration...")
        results = []
        
        # Test design system component endpoints
        component_tests = [
            ("/api/design-system/components/nip-validator/", "NIP Validator Component"),
            ("/api/design-system/components/currency-input/", "Currency Input Component"),
            ("/api/design-system/components/vat-rate-selector/", "VAT Rate Selector Component"),
            ("/api/design-system/components/date-picker/", "Date Picker Component"),
            ("/api/design-system/components/invoice-status-badge/", "Invoice Status Badge Component"),
            ("/api/design-system/components/compliance-indicator/", "Compliance Indicator Component")
        ]
        
        for endpoint, component_name in component_tests:
            try:
                response = requests.get(f"{self.base_url}{endpoint}", timeout=10)
                
                if response.status_code == 200:
                    data = response.json()
                    
                    # Check if component has required Polish business properties
                    required_props = data.get("required_props", [])
                    polish_features = data.get("polish_business_features", [])
                    
                    if polish_features:
                        results.append(ValidationResult(
                            test_name=f"Design System Integration: {component_name}",
                            status="passed",
                            message=f"{component_name} has Polish business features: {', '.join(polish_features)}",
                            details={
                                "component": component_name,
                                "polish_features": polish_features,
                                "required_props": required_props
                            }
                        ))
                    else:
                        results.append(ValidationResult(
                            test_name=f"Design System Integration: {component_name}",
                            status="warning",
                            message=f"{component_name} missing Polish business features",
                            details={
                                "component": component_name,
                                "required_props": required_props
                            }
                        ))
                else:
                    results.append(ValidationResult(
                        test_name=f"Design System Integration: {component_name}",
                        status="failed",
                        message=f"Component endpoint not accessible: {response.status_code}",
                        details={"endpoint": endpoint, "status_code": response.status_code}
                    ))
                    
            except Exception as e:
                results.append(ValidationResult(
                    test_name=f"Design System Integration: {component_name}",
                    status="failed",
                    message=f"Exception accessing component: {str(e)}",
                    details={"endpoint": endpoint, "error": str(e)}
                ))
        
        return results
    
    def run_all_validations(self) -> Dict[str, Any]:
        """Run all Polish business functionality validations"""
        logger.info("Starting Polish business functionality validation...")
        
        all_results = []
        
        # Run all validation categories
        validation_methods = [
            self.validate_nip_functionality,
            self.validate_vat_calculations,
            self.validate_currency_formatting,
            self.validate_date_formatting,
            self.validate_invoice_compliance,
            self.validate_design_system_integration
        ]
        
        for validation_method in validation_methods:
            try:
                results = validation_method()
                all_results.extend(results)
            except Exception as e:
                logger.error(f"Validation method {validation_method.__name__} failed: {str(e)}")
                all_results.append(ValidationResult(
                    test_name=f"Validation Method: {validation_method.__name__}",
                    status="failed",
                    message=f"Validation method failed: {str(e)}",
                    details={"error": str(e)}
                ))
        
        self.results = all_results
        return self.generate_report()
    
    def generate_report(self) -> Dict[str, Any]:
        """Generate comprehensive validation report"""
        total_tests = len(self.results)
        passed_tests = len([r for r in self.results if r.status == "passed"])
        failed_tests = len([r for r in self.results if r.status == "failed"])
        warning_tests = len([r for r in self.results if r.status == "warning"])
        
        report = {
            "summary": {
                "total_tests": total_tests,
                "passed": passed_tests,
                "failed": failed_tests,
                "warnings": warning_tests,
                "success_rate": (passed_tests / total_tests * 100) if total_tests > 0 else 0,
                "timestamp": datetime.now().isoformat()
            },
            "results": [asdict(result) for result in self.results],
            "categories": {
                "nip_validation": [r for r in self.results if "NIP" in r.test_name],
                "vat_calculations": [r for r in self.results if "VAT" in r.test_name],
                "currency_formatting": [r for r in self.results if "Currency" in r.test_name],
                "date_formatting": [r for r in self.results if "Date" in r.test_name],
                "invoice_compliance": [r for r in self.results if "Invoice Compliance" in r.test_name],
                "design_system_integration": [r for r in self.results if "Design System" in r.test_name]
            },
            "recommendations": self._generate_recommendations()
        }
        
        # Save report to file
        report_file = f"test_results/polish_business_validation_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2, default=str)
        
        logger.info(f"Polish business validation report saved to: {report_file}")
        return report
    
    def _generate_recommendations(self) -> List[str]:
        """Generate recommendations based on validation results"""
        recommendations = []
        
        failed_results = [r for r in self.results if r.status == "failed"]
        warning_results = [r for r in self.results if r.status == "warning"]
        
        if failed_results:
            recommendations.append("Fix failed Polish business functionality tests before production deployment")
            
        if any("NIP" in r.test_name for r in failed_results):
            recommendations.append("Address NIP validation issues - critical for Polish business compliance")
            
        if any("VAT" in r.test_name for r in failed_results):
            recommendations.append("Fix VAT calculation issues - required for accurate invoicing")
            
        if any("Currency" in r.test_name for r in failed_results):
            recommendations.append("Correct currency formatting issues for proper PLN display")
            
        if any("Date" in r.test_name for r in failed_results):
            recommendations.append("Fix date formatting to use proper Polish format (DD.MM.YYYY)")
            
        if warning_results:
            recommendations.append("Review warning items to ensure complete Polish business feature coverage")
            
        return recommendations

def main():
    """Main execution function"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Validate Polish Business Functionality in Design System Integration")
    parser.add_argument("--base-url", default="http://staging.faktulove.local", help="Base URL for validation")
    parser.add_argument("--category", help="Run specific validation category")
    
    args = parser.parse_args()
    
    validator = PolishBusinessValidator(base_url=args.base_url)
    
    if args.category:
        method_name = f"validate_{args.category}"
        if hasattr(validator, method_name):
            method = getattr(validator, method_name)
            results = method()
            validator.results = results
            report = validator.generate_report()
            print(f"Category validation completed: {len([r for r in results if r.status == 'passed'])}/{len(results)} tests passed")
        else:
            print(f"Category {args.category} not found")
    else:
        report = validator.run_all_validations()
        print(f"Polish business validation completed: {report['summary']['passed']}/{report['summary']['total_tests']} tests passed")
        if report['summary']['failed'] > 0:
            print(f"⚠️  {report['summary']['failed']} tests failed - review before production deployment")

if __name__ == "__main__":
    main()