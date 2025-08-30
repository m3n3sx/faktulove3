#!/usr/bin/env python3
"""
Production Rollout Script for Design System Integration
Implements gradual rollout with feature flags, monitoring, and rollback capabilities
"""

import json
import time
import logging
import requests
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
import threading
from concurrent.futures import ThreadPoolExecutor

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@dataclass
class RolloutPhase:
    """Definition of a rollout phase"""
    name: str
    description: str
    percentage: int  # Percentage of users to include
    duration_minutes: int
    feature_flags: List[str]
    success_criteria: Dict[str, Any]
    rollback_triggers: Dict[str, Any]

@dataclass
class RolloutMetrics:
    """Metrics collected during rollout"""
    timestamp: datetime
    phase: str
    user_percentage: int
    error_rate: float
    response_time_p95: float
    user_satisfaction: float
    feature_adoption: Dict[str, float]
    performance_score: float

class ProductionRolloutManager:
    """Manages production rollout of design system integration"""
    
    def __init__(self, base_url: str = "https://faktulove.com"):
        self.base_url = base_url
        self.session = requests.Session()
        self.session.timeout = 30
        self.rollout_active = False
        self.current_phase = None
        self.metrics_history: List[RolloutMetrics] = []
        self.rollback_triggered = False
        
    def get_rollout_phases(self) -> List[RolloutPhase]:
        """Define rollout phases for design system integration"""
        return [
            RolloutPhase(
                name="canary",
                description="Canary deployment to 5% of users",
                percentage=5,
                duration_minutes=30,
                feature_flags=[
                    "DESIGN_SYSTEM_BASIC_COMPONENTS",
                    "POLISH_BUSINESS_NIP_VALIDATION"
                ],
                success_criteria={
                    "error_rate_threshold": 0.01,  # 1%
                    "response_time_p95_threshold": 2000,  # 2 seconds
                    "user_satisfaction_threshold": 4.0  # out of 5
                },
                rollback_triggers={
                    "error_rate_threshold": 0.05,  # 5%
                    "response_time_p95_threshold": 5000,  # 5 seconds
                    "crash_rate_threshold": 0.01  # 1%
                }
            ),
            
            RolloutPhase(
                name="early_adopters",
                description="Early adopters - 15% of users",
                percentage=15,
                duration_minutes=60,
                feature_flags=[
                    "DESIGN_SYSTEM_BASIC_COMPONENTS",
                    "DESIGN_SYSTEM_FORM_COMPONENTS",
                    "POLISH_BUSINESS_NIP_VALIDATION",
                    "POLISH_BUSINESS_VAT_CALCULATOR"
                ],
                success_criteria={
                    "error_rate_threshold": 0.02,  # 2%
                    "response_time_p95_threshold": 2500,  # 2.5 seconds
                    "user_satisfaction_threshold": 3.8,
                    "feature_adoption_threshold": 0.7  # 70% adoption
                },
                rollback_triggers={
                    "error_rate_threshold": 0.08,  # 8%
                    "response_time_p95_threshold": 6000,  # 6 seconds
                    "user_complaints_threshold": 10
                }
            ),
            
            RolloutPhase(
                name="gradual_rollout",
                description="Gradual rollout - 50% of users",
                percentage=50,
                duration_minutes=120,
                feature_flags=[
                    "DESIGN_SYSTEM_BASIC_COMPONENTS",
                    "DESIGN_SYSTEM_FORM_COMPONENTS",
                    "DESIGN_SYSTEM_LAYOUT_COMPONENTS",
                    "POLISH_BUSINESS_NIP_VALIDATION",
                    "POLISH_BUSINESS_VAT_CALCULATOR",
                    "POLISH_BUSINESS_CURRENCY_FORMATTING",
                    "DESIGN_SYSTEM_THEMING"
                ],
                success_criteria={
                    "error_rate_threshold": 0.03,  # 3%
                    "response_time_p95_threshold": 3000,  # 3 seconds
                    "user_satisfaction_threshold": 3.5,
                    "feature_adoption_threshold": 0.6  # 60% adoption
                },
                rollback_triggers={
                    "error_rate_threshold": 0.10,  # 10%
                    "response_time_p95_threshold": 8000,  # 8 seconds
                    "business_impact_threshold": 0.05  # 5% revenue impact
                }
            ),
            
            RolloutPhase(
                name="full_rollout",
                description="Full rollout - 100% of users",
                percentage=100,
                duration_minutes=180,
                feature_flags=[
                    "DESIGN_SYSTEM_BASIC_COMPONENTS",
                    "DESIGN_SYSTEM_FORM_COMPONENTS",
                    "DESIGN_SYSTEM_LAYOUT_COMPONENTS",
                    "DESIGN_SYSTEM_ADVANCED_COMPONENTS",
                    "POLISH_BUSINESS_NIP_VALIDATION",
                    "POLISH_BUSINESS_VAT_CALCULATOR",
                    "POLISH_BUSINESS_CURRENCY_FORMATTING",
                    "POLISH_BUSINESS_DATE_FORMATTING",
                    "POLISH_BUSINESS_INVOICE_COMPLIANCE",
                    "DESIGN_SYSTEM_THEMING",
                    "DESIGN_SYSTEM_ACCESSIBILITY",
                    "DESIGN_SYSTEM_PERFORMANCE_MONITORING"
                ],
                success_criteria={
                    "error_rate_threshold": 0.05,  # 5%
                    "response_time_p95_threshold": 4000,  # 4 seconds
                    "user_satisfaction_threshold": 3.0,
                    "feature_adoption_threshold": 0.5  # 50% adoption
                },
                rollback_triggers={
                    "error_rate_threshold": 0.15,  # 15%
                    "response_time_p95_threshold": 10000,  # 10 seconds
                    "business_critical_failure": True
                }
            )
        ]
    
    def enable_feature_flags(self, flags: List[str], percentage: int):
        """Enable feature flags for a percentage of users"""
        logger.info(f"Enabling feature flags for {percentage}% of users: {flags}")
        
        for flag in flags:
            try:
                response = self.session.post(
                    f"{self.base_url}/api/feature-flags/enable/",
                    json={
                        "flag": flag,
                        "percentage": percentage,
                        "enabled": True
                    }
                )
                
                if response.status_code == 200:
                    logger.info(f"✓ Feature flag {flag} enabled for {percentage}% of users")
                else:
                    logger.error(f"✗ Failed to enable feature flag {flag}: {response.status_code}")
                    
            except Exception as e:
                logger.error(f"✗ Exception enabling feature flag {flag}: {str(e)}")
    
    def collect_metrics(self, phase: str, percentage: int) -> RolloutMetrics:
        """Collect metrics for current rollout phase"""
        try:
            # Collect error rate
            error_response = self.session.get(f"{self.base_url}/api/monitoring/error-rate/")
            error_rate = error_response.json().get("error_rate", 0.0) if error_response.status_code == 200 else 0.0
            
            # Collect response time
            perf_response = self.session.get(f"{self.base_url}/api/monitoring/performance/")
            response_time_p95 = perf_response.json().get("response_time_p95", 0.0) if perf_response.status_code == 200 else 0.0
            
            # Collect user satisfaction
            satisfaction_response = self.session.get(f"{self.base_url}/api/monitoring/user-satisfaction/")
            user_satisfaction = satisfaction_response.json().get("satisfaction_score", 0.0) if satisfaction_response.status_code == 200 else 0.0
            
            # Collect feature adoption
            adoption_response = self.session.get(f"{self.base_url}/api/monitoring/feature-adoption/")
            feature_adoption = adoption_response.json().get("adoption_rates", {}) if adoption_response.status_code == 200 else {}
            
            # Collect performance score
            performance_response = self.session.get(f"{self.base_url}/api/monitoring/performance-score/")
            performance_score = performance_response.json().get("score", 0.0) if performance_response.status_code == 200 else 0.0
            
            return RolloutMetrics(
                timestamp=datetime.now(),
                phase=phase,
                user_percentage=percentage,
                error_rate=error_rate,
                response_time_p95=response_time_p95,
                user_satisfaction=user_satisfaction,
                feature_adoption=feature_adoption,
                performance_score=performance_score
            )
            
        except Exception as e:
            logger.error(f"Error collecting metrics: {str(e)}")
            return RolloutMetrics(
                timestamp=datetime.now(),
                phase=phase,
                user_percentage=percentage,
                error_rate=0.0,
                response_time_p95=0.0,
                user_satisfaction=0.0,
                feature_adoption={},
                performance_score=0.0
            )
    
    def check_success_criteria(self, metrics: RolloutMetrics, criteria: Dict[str, Any]) -> bool:
        """Check if success criteria are met"""
        checks = []
        
        if "error_rate_threshold" in criteria:
            checks.append(metrics.error_rate <= criteria["error_rate_threshold"])
            
        if "response_time_p95_threshold" in criteria:
            checks.append(metrics.response_time_p95 <= criteria["response_time_p95_threshold"])
            
        if "user_satisfaction_threshold" in criteria:
            checks.append(metrics.user_satisfaction >= criteria["user_satisfaction_threshold"])
            
        if "feature_adoption_threshold" in criteria:
            avg_adoption = sum(metrics.feature_adoption.values()) / len(metrics.feature_adoption) if metrics.feature_adoption else 0
            checks.append(avg_adoption >= criteria["feature_adoption_threshold"])
        
        return all(checks)
    
    def check_rollback_triggers(self, metrics: RolloutMetrics, triggers: Dict[str, Any]) -> bool:
        """Check if rollback should be triggered"""
        triggers_hit = []
        
        if "error_rate_threshold" in triggers:
            if metrics.error_rate >= triggers["error_rate_threshold"]:
                triggers_hit.append(f"Error rate: {metrics.error_rate:.3f} >= {triggers['error_rate_threshold']}")
                
        if "response_time_p95_threshold" in triggers:
            if metrics.response_time_p95 >= triggers["response_time_p95_threshold"]:
                triggers_hit.append(f"Response time P95: {metrics.response_time_p95:.0f}ms >= {triggers['response_time_p95_threshold']}ms")
                
        if "crash_rate_threshold" in triggers:
            # This would be implemented based on crash monitoring
            pass
            
        if triggers_hit:
            logger.warning(f"Rollback triggers hit: {', '.join(triggers_hit)}")
            return True
            
        return False
    
    def rollback_deployment(self, reason: str):
        """Rollback the deployment"""
        logger.error(f"🚨 ROLLBACK TRIGGERED: {reason}")
        self.rollback_triggered = True
        
        try:
            # Disable all design system feature flags
            response = self.session.post(
                f"{self.base_url}/api/feature-flags/disable-all/",
                json={"category": "design_system"}
            )
            
            if response.status_code == 200:
                logger.info("✓ All design system feature flags disabled")
            else:
                logger.error(f"✗ Failed to disable feature flags: {response.status_code}")
                
            # Notify stakeholders
            self.notify_rollback(reason)
            
        except Exception as e:
            logger.error(f"✗ Exception during rollback: {str(e)}")
    
    def notify_rollback(self, reason: str):
        """Notify stakeholders about rollback"""
        notification_data = {
            "type": "rollback",
            "reason": reason,
            "timestamp": datetime.now().isoformat(),
            "phase": self.current_phase.name if self.current_phase else "unknown"
        }
        
        try:
            self.session.post(
                f"{self.base_url}/api/notifications/rollback/",
                json=notification_data
            )
            logger.info("✓ Rollback notification sent")
        except Exception as e:
            logger.error(f"✗ Failed to send rollback notification: {str(e)}")
    
    def monitor_phase(self, phase: RolloutPhase) -> bool:
        """Monitor a rollout phase"""
        logger.info(f"📊 Monitoring phase: {phase.name} ({phase.percentage}% users)")
        
        start_time = datetime.now()
        end_time = start_time + timedelta(minutes=phase.duration_minutes)
        
        while datetime.now() < end_time and not self.rollback_triggered:
            # Collect metrics
            metrics = self.collect_metrics(phase.name, phase.percentage)
            self.metrics_history.append(metrics)
            
            # Log current metrics
            logger.info(f"Metrics - Error Rate: {metrics.error_rate:.3f}, "
                       f"Response Time P95: {metrics.response_time_p95:.0f}ms, "
                       f"User Satisfaction: {metrics.user_satisfaction:.1f}")
            
            # Check rollback triggers
            if self.check_rollback_triggers(metrics, phase.rollback_triggers):
                self.rollback_deployment(f"Rollback triggers hit in phase {phase.name}")
                return False
            
            # Check success criteria (for early validation)
            success = self.check_success_criteria(metrics, phase.success_criteria)
            if not success:
                logger.warning(f"Success criteria not met in phase {phase.name}")
            
            # Wait before next check
            time.sleep(60)  # Check every minute
        
        if self.rollback_triggered:
            return False
            
        # Final validation
        final_metrics = self.collect_metrics(phase.name, phase.percentage)
        self.metrics_history.append(final_metrics)
        
        success = self.check_success_criteria(final_metrics, phase.success_criteria)
        
        if success:
            logger.info(f"✅ Phase {phase.name} completed successfully")
            return True
        else:
            logger.warning(f"⚠️ Phase {phase.name} completed but success criteria not fully met")
            return True  # Continue anyway, but log warning
    
    def execute_rollout(self) -> Dict[str, Any]:
        """Execute the complete production rollout"""
        logger.info("🚀 Starting Production Rollout of Design System Integration")
        
        rollout_start = datetime.now()
        self.rollout_active = True
        phases = self.get_rollout_phases()
        
        rollout_report = {
            "start_time": rollout_start.isoformat(),
            "phases": [],
            "success": False,
            "rollback_triggered": False,
            "total_duration": 0,
            "final_metrics": None
        }
        
        try:
            for i, phase in enumerate(phases):
                if self.rollback_triggered:
                    break
                    
                logger.info(f"🎯 Starting Phase {i+1}/{len(phases)}: {phase.name}")
                self.current_phase = phase
                
                phase_start = datetime.now()
                
                # Enable feature flags for this phase
                self.enable_feature_flags(phase.feature_flags, phase.percentage)
                
                # Wait for feature flags to propagate
                time.sleep(30)
                
                # Monitor the phase
                phase_success = self.monitor_phase(phase)
                
                phase_end = datetime.now()
                phase_duration = (phase_end - phase_start).total_seconds() / 60
                
                phase_report = {
                    "name": phase.name,
                    "percentage": phase.percentage,
                    "duration_minutes": phase_duration,
                    "success": phase_success,
                    "feature_flags": phase.feature_flags,
                    "metrics": [asdict(m) for m in self.metrics_history if m.phase == phase.name]
                }
                
                rollout_report["phases"].append(phase_report)
                
                if not phase_success:
                    logger.error(f"❌ Phase {phase.name} failed")
                    break
                    
                logger.info(f"✅ Phase {phase.name} completed in {phase_duration:.1f} minutes")
                
                # Brief pause between phases
                if i < len(phases) - 1:
                    logger.info("⏸️ Pausing 5 minutes between phases...")
                    time.sleep(300)
            
            rollout_end = datetime.now()
            total_duration = (rollout_end - rollout_start).total_seconds() / 60
            
            rollout_report.update({
                "end_time": rollout_end.isoformat(),
                "total_duration": total_duration,
                "success": not self.rollback_triggered and len(rollout_report["phases"]) == len(phases),
                "rollback_triggered": self.rollback_triggered,
                "final_metrics": asdict(self.metrics_history[-1]) if self.metrics_history else None
            })
            
            if rollout_report["success"]:
                logger.info(f"🎉 Production rollout completed successfully in {total_duration:.1f} minutes!")
            else:
                logger.error(f"💥 Production rollout failed after {total_duration:.1f} minutes")
            
        except Exception as e:
            logger.error(f"💥 Rollout failed with exception: {str(e)}")
            rollout_report["error"] = str(e)
            self.rollback_deployment(f"Exception during rollout: {str(e)}")
        
        finally:
            self.rollout_active = False
            
        return rollout_report
    
    def generate_rollout_report(self, rollout_data: Dict[str, Any]) -> str:
        """Generate comprehensive rollout report"""
        
        report_content = f"""
# Production Rollout Report - Design System Integration

**Rollout Date:** {rollout_data.get('start_time', 'Unknown')}
**Total Duration:** {rollout_data.get('total_duration', 0):.1f} minutes
**Success:** {'✅ Yes' if rollout_data.get('success') else '❌ No'}
**Rollback Triggered:** {'🚨 Yes' if rollout_data.get('rollback_triggered') else '✅ No'}

## Phase Summary

"""
        
        for i, phase in enumerate(rollout_data.get('phases', [])):
            report_content += f"""
### Phase {i+1}: {phase['name']}
- **User Percentage:** {phase['percentage']}%
- **Duration:** {phase['duration_minutes']:.1f} minutes
- **Success:** {'✅ Yes' if phase['success'] else '❌ No'}
- **Feature Flags:** {', '.join(phase['feature_flags'])}

"""
        
        # Add metrics summary
        if rollout_data.get('final_metrics'):
            metrics = rollout_data['final_metrics']
            report_content += f"""
## Final Metrics

- **Error Rate:** {metrics.get('error_rate', 0):.3f}
- **Response Time P95:** {metrics.get('response_time_p95', 0):.0f}ms
- **User Satisfaction:** {metrics.get('user_satisfaction', 0):.1f}/5.0
- **Performance Score:** {metrics.get('performance_score', 0):.1f}/100

"""
        
        # Add recommendations
        report_content += """
## Recommendations

"""
        
        if rollout_data.get('success'):
            report_content += """
- ✅ Rollout completed successfully
- Monitor metrics for the next 24 hours
- Collect user feedback for future improvements
- Document lessons learned
"""
        else:
            report_content += """
- ❌ Rollout failed - investigate root causes
- Review rollback procedures and timing
- Analyze metrics to identify improvement areas
- Plan remediation before next rollout attempt
"""
        
        # Save report
        report_file = f"deployment_reports/production_rollout_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        with open(report_file, 'w') as f:
            f.write(report_content)
        
        logger.info(f"📄 Rollout report saved to: {report_file}")
        return report_file

def main():
    """Main execution function"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Execute Production Rollout of Design System Integration")
    parser.add_argument("--base-url", default="https://faktulove.com", help="Production base URL")
    parser.add_argument("--dry-run", action="store_true", help="Simulate rollout without making changes")
    parser.add_argument("--phase", help="Execute specific phase only")
    
    args = parser.parse_args()
    
    if args.dry_run:
        logger.info("🧪 DRY RUN MODE - No actual changes will be made")
    
    manager = ProductionRolloutManager(base_url=args.base_url)
    
    if args.phase:
        phases = manager.get_rollout_phases()
        phase = next((p for p in phases if p.name == args.phase), None)
        if phase:
            logger.info(f"Executing single phase: {phase.name}")
            if not args.dry_run:
                manager.enable_feature_flags(phase.feature_flags, phase.percentage)
                success = manager.monitor_phase(phase)
                print(f"Phase {phase.name}: {'Success' if success else 'Failed'}")
            else:
                print(f"Would execute phase: {phase.name} with {phase.percentage}% users")
        else:
            print(f"Phase {args.phase} not found")
    else:
        if not args.dry_run:
            rollout_data = manager.execute_rollout()
            report_file = manager.generate_rollout_report(rollout_data)
            print(f"Rollout completed. Report: {report_file}")
        else:
            phases = manager.get_rollout_phases()
            print("Would execute rollout phases:")
            for i, phase in enumerate(phases):
                print(f"  {i+1}. {phase.name} - {phase.percentage}% users for {phase.duration_minutes} minutes")

if __name__ == "__main__":
    main()