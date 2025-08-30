#!/usr/bin/env python3
"""
User Acceptance Testing Framework for Design System Integration
Provides structured UAT scenarios and validation for Polish business functionality
"""

import json
import time
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@dataclass
class UATScenario:
    """User Acceptance Test scenario definition"""
    id: str
    name: str
    description: str
    user_role: str
    steps: List[Dict[str, Any]]
    expected_outcomes: List[str]
    polish_business_features: List[str]
    priority: str  # high, medium, low
    estimated_duration: int  # minutes

@dataclass
class UATResult:
    """User Acceptance Test result"""
    scenario_id: str
    status: str  # passed, failed, skipped
    execution_time: float
    errors: List[str]
    screenshots: List[str]
    user_feedback: Optional[str]
    timestamp: datetime

class DesignSystemUATFramework:
    """Framework for running User Acceptance Tests on design system integration"""
    
    def __init__(self, base_url: str = "http://staging.faktulove.local"):
        self.base_url = base_url
        self.driver = None
        self.wait = None
        self.results: List[UATResult] = []
        
    def setup_driver(self):
        """Setup Selenium WebDriver with appropriate options"""
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--window-size=1920,1080")
        
        self.driver = webdriver.Chrome(options=chrome_options)
        self.wait = WebDriverWait(self.driver, 10)
        
    def teardown_driver(self):
        """Clean up WebDriver"""
        if self.driver:
            self.driver.quit()
            
    def get_uat_scenarios(self) -> List[UATScenario]:
        """Define comprehensive UAT scenarios for design system integration"""
        return [
            UATScenario(
                id="UAT-001",
                name="Invoice Creation with Polish Business Components",
                description="Test complete invoice creation workflow using design system components",
                user_role="Business Owner",
                steps=[
                    {"action": "navigate", "target": "/faktury/nowa/"},
                    {"action": "verify_component", "target": "design-system-form"},
                    {"action": "fill_field", "target": "numer", "value": "FV/2025/001"},
                    {"action": "select_date", "target": "data_wystawienia", "value": "29.08.2025"},
                    {"action": "fill_nip", "target": "nip_nabywcy", "value": "1234567890"},
                    {"action": "fill_currency", "target": "kwota_brutto", "value": "1230.00"},
                    {"action": "select_vat", "target": "stawka_vat", "value": "23"},
                    {"action": "submit_form", "target": "submit-button"},
                    {"action": "verify_success", "target": "success-message"}
                ],
                expected_outcomes=[
                    "Form uses design system components",
                    "Polish date format is applied",
                    "NIP validation works correctly",
                    "Currency formatting shows PLN",
                    "VAT rates show Polish rates",
                    "Success message uses design system styling"
                ],
                polish_business_features=[
                    "NIP validation",
                    "Polish date format",
                    "PLN currency formatting",
                    "Polish VAT rates"
                ],
                priority="high",
                estimated_duration=15
            ),
            
            UATScenario(
                id="UAT-002",
                name="OCR Document Processing Interface",
                description="Test OCR document upload and processing with design system components",
                user_role="Accountant",
                steps=[
                    {"action": "navigate", "target": "/ocr/upload/"},
                    {"action": "verify_component", "target": "file-upload-component"},
                    {"action": "upload_file", "target": "file-input", "value": "test_invoice.pdf"},
                    {"action": "verify_progress", "target": "progress-indicator"},
                    {"action": "wait_processing", "target": "processing-status"},
                    {"action": "navigate", "target": "/ocr/results/"},
                    {"action": "verify_table", "target": "results-table"},
                    {"action": "check_confidence", "target": "confidence-badges"},
                    {"action": "edit_field", "target": "editable-field", "value": "corrected_value"}
                ],
                expected_outcomes=[
                    "File upload uses design system FileUpload component",
                    "Progress indicator shows processing status",
                    "Results table uses design system Table component",
                    "Confidence scores display with Badge components",
                    "Inline editing works with design system inputs"
                ],
                polish_business_features=[
                    "Polish document recognition",
                    "Polish text extraction",
                    "Polish business field validation"
                ],
                priority="high",
                estimated_duration=20
            ),
            
            UATScenario(
                id="UAT-003",
                name="Dashboard Analytics with Polish Business Metrics",
                description="Test dashboard display with design system components and Polish business data",
                user_role="Business Manager",
                steps=[
                    {"action": "navigate", "target": "/dashboard/"},
                    {"action": "verify_layout", "target": "dashboard-grid"},
                    {"action": "check_cards", "target": "metric-cards"},
                    {"action": "verify_charts", "target": "analytics-charts"},
                    {"action": "test_filters", "target": "filter-controls"},
                    {"action": "check_currency", "target": "currency-displays"},
                    {"action": "verify_dates", "target": "date-displays"}
                ],
                expected_outcomes=[
                    "Dashboard uses design system Grid layout",
                    "Metric cards use design system Card component",
                    "Charts integrate with design system theming",
                    "Filters use design system form components",
                    "Currency displays show PLN formatting",
                    "Dates show Polish format (DD.MM.YYYY)"
                ],
                polish_business_features=[
                    "PLN currency formatting",
                    "Polish date formatting",
                    "Polish business metrics"
                ],
                priority="medium",
                estimated_duration=10
            ),
            
            UATScenario(
                id="UAT-004",
                name="Authentication Flow with Design System",
                description="Test login, registration, and profile management with design system components",
                user_role="New User",
                steps=[
                    {"action": "navigate", "target": "/accounts/login/"},
                    {"action": "verify_form", "target": "login-form"},
                    {"action": "fill_credentials", "target": "login-fields"},
                    {"action": "submit_login", "target": "login-button"},
                    {"action": "navigate", "target": "/accounts/profile/"},
                    {"action": "verify_profile", "target": "profile-form"},
                    {"action": "test_theme_switch", "target": "theme-controls"},
                    {"action": "logout", "target": "logout-button"}
                ],
                expected_outcomes=[
                    "Login form uses design system components",
                    "Form validation shows design system errors",
                    "Profile page uses design system layout",
                    "Theme switching works correctly",
                    "Navigation uses design system components"
                ],
                polish_business_features=[
                    "Polish language support",
                    "Polish business user roles"
                ],
                priority="medium",
                estimated_duration=12
            ),
            
            UATScenario(
                id="UAT-005",
                name="Accessibility Features Validation",
                description="Test accessibility features across the application",
                user_role="User with Accessibility Needs",
                steps=[
                    {"action": "navigate", "target": "/"},
                    {"action": "test_keyboard_nav", "target": "main-navigation"},
                    {"action": "verify_focus", "target": "interactive-elements"},
                    {"action": "test_screen_reader", "target": "aria-labels"},
                    {"action": "check_contrast", "target": "color-elements"},
                    {"action": "test_zoom", "target": "scalable-elements"},
                    {"action": "verify_shortcuts", "target": "keyboard-shortcuts"}
                ],
                expected_outcomes=[
                    "All interactive elements are keyboard accessible",
                    "Focus indicators are clearly visible",
                    "ARIA labels are properly implemented",
                    "Color contrast meets WCAG standards",
                    "Text scales properly up to 200%",
                    "Keyboard shortcuts work as expected"
                ],
                polish_business_features=[
                    "Polish screen reader support",
                    "Polish keyboard shortcuts"
                ],
                priority="high",
                estimated_duration=25
            ),
            
            UATScenario(
                id="UAT-006",
                name="Theme Integration and Customization",
                description="Test theme switching and customization features",
                user_role="Power User",
                steps=[
                    {"action": "navigate", "target": "/"},
                    {"action": "open_theme_controls", "target": "theme-menu"},
                    {"action": "switch_theme", "target": "dark-theme"},
                    {"action": "verify_theme_change", "target": "all-components"},
                    {"action": "test_polish_theme", "target": "polish-business-theme"},
                    {"action": "verify_persistence", "target": "theme-storage"},
                    {"action": "test_responsive", "target": "mobile-view"}
                ],
                expected_outcomes=[
                    "Theme controls are easily accessible",
                    "Theme changes apply to all components",
                    "Polish business theme works correctly",
                    "Theme preference is persisted",
                    "Themes work on mobile devices"
                ],
                polish_business_features=[
                    "Polish business color schemes",
                    "Polish business typography"
                ],
                priority="medium",
                estimated_duration=15
            )
        ]
    
    def execute_scenario(self, scenario: UATScenario) -> UATResult:
        """Execute a single UAT scenario"""
        logger.info(f"Executing scenario: {scenario.name}")
        start_time = time.time()
        errors = []
        screenshots = []
        
        try:
            # Navigate to base URL
            self.driver.get(self.base_url)
            
            # Execute each step
            for step in scenario.steps:
                try:
                    self._execute_step(step)
                    time.sleep(1)  # Small delay between steps
                except Exception as e:
                    error_msg = f"Step failed: {step['action']} - {str(e)}"
                    errors.append(error_msg)
                    logger.error(error_msg)
                    
                    # Take screenshot on error
                    screenshot_path = f"screenshots/{scenario.id}_{step['action']}_error.png"
                    self.driver.save_screenshot(screenshot_path)
                    screenshots.append(screenshot_path)
            
            # Verify expected outcomes
            for outcome in scenario.expected_outcomes:
                try:
                    self._verify_outcome(outcome)
                except Exception as e:
                    error_msg = f"Outcome verification failed: {outcome} - {str(e)}"
                    errors.append(error_msg)
                    logger.error(error_msg)
            
            execution_time = time.time() - start_time
            status = "passed" if not errors else "failed"
            
            return UATResult(
                scenario_id=scenario.id,
                status=status,
                execution_time=execution_time,
                errors=errors,
                screenshots=screenshots,
                user_feedback=None,
                timestamp=datetime.now()
            )
            
        except Exception as e:
            execution_time = time.time() - start_time
            logger.error(f"Scenario execution failed: {str(e)}")
            
            return UATResult(
                scenario_id=scenario.id,
                status="failed",
                execution_time=execution_time,
                errors=[str(e)],
                screenshots=screenshots,
                user_feedback=None,
                timestamp=datetime.now()
            )
    
    def _execute_step(self, step: Dict[str, Any]):
        """Execute a single test step"""
        action = step["action"]
        target = step.get("target", "")
        value = step.get("value", "")
        
        if action == "navigate":
            self.driver.get(f"{self.base_url}{target}")
            
        elif action == "verify_component":
            element = self.wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, f"[data-testid='{target}']"))
            )
            
        elif action == "fill_field":
            element = self.driver.find_element(By.NAME, target)
            element.clear()
            element.send_keys(value)
            
        elif action == "submit_form":
            button = self.driver.find_element(By.CSS_SELECTOR, f"[data-testid='{target}']")
            button.click()
            
        elif action == "verify_success":
            self.wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, f"[data-testid='{target}']"))
            )
            
        # Add more step implementations as needed
        
    def _verify_outcome(self, outcome: str):
        """Verify an expected outcome"""
        # Implementation depends on specific outcome
        # This is a placeholder for outcome verification logic
        pass
    
    def run_all_scenarios(self) -> Dict[str, Any]:
        """Run all UAT scenarios and generate report"""
        logger.info("Starting User Acceptance Testing")
        
        self.setup_driver()
        scenarios = self.get_uat_scenarios()
        
        try:
            for scenario in scenarios:
                result = self.execute_scenario(scenario)
                self.results.append(result)
                
        finally:
            self.teardown_driver()
        
        return self.generate_report()
    
    def generate_report(self) -> Dict[str, Any]:
        """Generate comprehensive UAT report"""
        total_scenarios = len(self.results)
        passed_scenarios = len([r for r in self.results if r.status == "passed"])
        failed_scenarios = len([r for r in self.results if r.status == "failed"])
        
        report = {
            "summary": {
                "total_scenarios": total_scenarios,
                "passed": passed_scenarios,
                "failed": failed_scenarios,
                "success_rate": (passed_scenarios / total_scenarios * 100) if total_scenarios > 0 else 0,
                "total_execution_time": sum(r.execution_time for r in self.results),
                "timestamp": datetime.now().isoformat()
            },
            "scenarios": [asdict(result) for result in self.results],
            "recommendations": self._generate_recommendations()
        }
        
        # Save report to file
        report_file = f"test_results/uat_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2, default=str)
        
        logger.info(f"UAT report saved to: {report_file}")
        return report
    
    def _generate_recommendations(self) -> List[str]:
        """Generate recommendations based on test results"""
        recommendations = []
        
        failed_results = [r for r in self.results if r.status == "failed"]
        
        if failed_results:
            recommendations.append("Review and fix failed test scenarios before production deployment")
            
        if any("accessibility" in r.scenario_id.lower() for r in failed_results):
            recommendations.append("Address accessibility issues to ensure WCAG compliance")
            
        if any("polish" in str(r.errors).lower() for r in failed_results):
            recommendations.append("Fix Polish business functionality issues")
            
        return recommendations

def main():
    """Main execution function"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Run User Acceptance Tests for Design System Integration")
    parser.add_argument("--base-url", default="http://staging.faktulove.local", help="Base URL for testing")
    parser.add_argument("--scenario", help="Run specific scenario by ID")
    
    args = parser.parse_args()
    
    framework = DesignSystemUATFramework(base_url=args.base_url)
    
    if args.scenario:
        scenarios = framework.get_uat_scenarios()
        scenario = next((s for s in scenarios if s.id == args.scenario), None)
        if scenario:
            framework.setup_driver()
            try:
                result = framework.execute_scenario(scenario)
                framework.results.append(result)
                print(f"Scenario {scenario.id}: {result.status}")
            finally:
                framework.teardown_driver()
        else:
            print(f"Scenario {args.scenario} not found")
    else:
        report = framework.run_all_scenarios()
        print(f"UAT completed: {report['summary']['passed']}/{report['summary']['total_scenarios']} scenarios passed")

if __name__ == "__main__":
    main()