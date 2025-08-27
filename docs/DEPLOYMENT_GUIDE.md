# FaktuLove OCR - Staged Deployment Guide

This guide covers the complete staged deployment and validation process for migrating from Google Cloud Document AI to open-source OCR solution.

## Overview

Task 20 implements a comprehensive staged deployment system with:

1. **Staging Environment Deployment** - Deploy and test in isolated staging environment
2. **Production-like Testing** - Comprehensive testing with realistic data
3. **Feature Flag System** - Gradual rollout with percentage-based user targeting
4. **Performance Monitoring** - Real-time metrics and health monitoring
5. **Final Cutover** - Complete migration from Google Cloud to open-source

## Prerequisites

Before starting the deployment process, ensure:

- [ ] All previous tasks (1-19) are completed
- [ ] OCR infrastructure is set up (`./setup_ocr_infrastructure.sh`)
- [ ] Docker and Docker Compose are installed
- [ ] Python virtual environment is activated
- [ ] Database is accessible and migrations are up to date

## Deployment Process

### Phase 1: Staging Deployment

Deploy the new OCR system to a staging environment for validation:

```bash
# Deploy to staging environment
./deploy_staging.sh

# This will:
# - Create staging environment configuration
# - Set up isolated Docker services
# - Deploy OCR services with staging settings
# - Create test data and validate basic functionality
```

**Expected Output:**
- Staging services running on different ports (OCR: 8001, Redis: 6380, PostgreSQL: 5433)
- Staging database with test data
- Basic functionality validation passed

### Phase 2: Comprehensive Testing

Run comprehensive tests with production-like data:

```bash
# Run comprehensive staging tests
./run_staging_tests.sh

# This will:
# - Test infrastructure health
# - Run unit test suite
# - Test OCR integration pipeline
# - Validate performance metrics
# - Test API compatibility
# - Validate security measures
# - Generate comprehensive test report
```

**Expected Output:**
- All test suites pass
- Performance metrics within acceptable ranges
- Test report generated in `staging_test_results/`

### Phase 3: Feature Flag Implementation

The system includes a sophisticated feature flag system for gradual rollout:

```bash
# Check current deployment status
python manage.py manage_deployment status

# Advance to next rollout stage
python manage.py manage_deployment advance

# Set specific rollout percentage
python manage.py manage_deployment advance --percentage 25

# Check system health
python manage.py manage_deployment health

# Generate deployment report
python manage.py manage_deployment report --hours 24
```

**Rollout Stages:**
- Stage 0: 0% - Google Cloud only
- Stage 1: 5% - Pilot users
- Stage 2: 15% - Early adopters
- Stage 3: 35% - Gradual rollout
- Stage 4: 60% - Majority rollout
- Stage 5: 85% - Near complete
- Stage 6: 100% - Complete rollout

### Phase 4: Performance Monitoring

Monitor the deployment in real-time:

```bash
# Start monitoring dashboard (refreshes every 30 seconds)
./monitor_deployment.sh

# Custom refresh interval and duration
./monitor_deployment.sh 15 7200  # 15s refresh, 2 hours duration

# View specific metrics
python manage.py manage_deployment health --output json
python manage.py manage_deployment report --hours 6 --output json
```

**Monitoring Features:**
- Real-time deployment status
- System health checks
- Performance metrics (processing time, success rate, confidence)
- OCR engine comparison (Google Cloud vs Open Source)
- Service status monitoring
- Alerts and recommendations

### Phase 5: Final Cutover

Execute the final cutover from Google Cloud to open-source:

```bash
# Execute final cutover (includes gradual rollout)
./execute_final_cutover.sh

# This will:
# - Validate pre-cutover conditions
# - Create comprehensive system backup
# - Execute gradual rollout (5% -> 15% -> 35% -> 60% -> 85% -> 100%)
# - Monitor health at each stage
# - Apply final configuration
# - Disable Google Cloud completely
# - Generate rollback script
```

**Expected Output:**
- Gradual rollout completed successfully
- 100% of users using open-source OCR
- Google Cloud OCR disabled
- System health validated
- Rollback script created for emergency use

## Feature Flag System

### Core Features

The feature flag system provides:

- **Gradual Rollout**: Percentage-based user targeting
- **A/B Testing**: Compare Google Cloud vs Open Source performance
- **Emergency Rollback**: Instant rollback to Google Cloud
- **Maintenance Mode**: Disable OCR processing during maintenance
- **Performance Monitoring**: Real-time metrics collection

### Key Feature Flags

```python
# Core flags
'use_opensource_ocr': True/False          # Enable open-source OCR
'disable_google_cloud': True/False        # Disable Google Cloud completely
'gradual_rollout_enabled': True/False     # Enable percentage-based rollout
'rollout_percentage': 0-100               # Current rollout percentage

# Monitoring flags
'enable_performance_monitoring': True/False
'enable_accuracy_comparison': True/False
'collect_ocr_metrics': True/False

# Emergency flags
'maintenance_mode': True/False            # Emergency maintenance mode
'force_opensource_for_testing': True/False
```

### Usage Examples

```bash
# Enable open-source OCR for all users
python manage.py manage_deployment enable

# Disable open-source OCR (rollback to Google Cloud)
python manage.py manage_deployment disable

# Enable maintenance mode
python manage.py manage_deployment maintenance-on --reason "Emergency maintenance"

# Disable maintenance mode
python manage.py manage_deployment maintenance-off

# Rollback to previous stage
python manage.py manage_deployment rollback
```

## Monitoring and Metrics

### Health Checks

The system monitors:

- **Processing Time**: Average, max, min processing times
- **Success Rate**: Percentage of successful OCR operations
- **Error Rate**: Percentage of failed operations
- **Confidence Scores**: OCR accuracy metrics
- **Service Health**: OCR processor, Redis, database connectivity

### Performance Thresholds

```python
PERFORMANCE_THRESHOLDS = {
    'max_processing_time': 30.0,    # seconds
    'min_success_rate': 0.95,       # 95%
    'min_confidence': 0.80,         # 80%
    'max_error_rate': 0.05,         # 5%
}

ALERT_THRESHOLDS = {
    'critical_error_rate': 0.10,    # 10%
    'critical_processing_time': 60.0, # 60 seconds
    'critical_success_rate': 0.90,  # 90%
}
```

### Comparison Metrics

The system compares Google Cloud vs Open Source performance:

- Processing time differences
- Confidence score differences
- Success rate differences
- Volume distribution

## Emergency Procedures

### Rollback to Google Cloud

If issues are detected during deployment:

```bash
# Automatic rollback script (created during cutover)
./rollback_cutover.sh

# Manual rollback
python manage.py manage_deployment disable
python manage.py manage_deployment maintenance-off
```

### Emergency Maintenance

```bash
# Enable maintenance mode (disables all OCR processing)
python manage.py manage_deployment maintenance-on --reason "Critical issue detected"

# Check system status
python manage.py manage_deployment health

# Disable maintenance mode when resolved
python manage.py manage_deployment maintenance-off
```

### Troubleshooting

Common issues and solutions:

1. **OCR Service Not Responding**
   ```bash
   # Check service status
   curl -f http://localhost:8001/health
   
   # Restart OCR services
   docker-compose -f docker-compose.staging.yml restart ocr-processor-staging
   ```

2. **High Error Rate**
   ```bash
   # Check recent errors
   python manage.py manage_deployment health
   
   # Rollback if critical
   python manage.py manage_deployment rollback
   ```

3. **Performance Degradation**
   ```bash
   # Check performance metrics
   python manage.py manage_deployment report --hours 1
   
   # Monitor in real-time
   ./monitor_deployment.sh
   ```

## Validation

Validate the implementation before deployment:

```bash
# Run validation script
python validate_deployment_implementation.py

# Expected output: All validations passed
```

## File Structure

The deployment implementation includes:

```
├── deploy_staging.sh                     # Staging deployment script
├── run_staging_tests.sh                  # Comprehensive testing script
├── execute_final_cutover.sh              # Final cutover script
├── monitor_deployment.sh                 # Real-time monitoring dashboard
├── validate_deployment_implementation.py # Implementation validation
├── faktury/services/
│   ├── feature_flag_service.py          # Feature flag management
│   └── deployment_monitoring_service.py  # Metrics and monitoring
└── faktury/management/commands/
    └── manage_deployment.py              # Deployment management CLI
```

## Success Criteria

The deployment is considered successful when:

- [ ] All staging tests pass
- [ ] Performance metrics meet thresholds
- [ ] 100% rollout completed without critical issues
- [ ] Google Cloud OCR completely disabled
- [ ] System health status is "healthy"
- [ ] No critical alerts for 24 hours post-deployment

## Post-Deployment

After successful deployment:

1. **Monitor for 24-48 hours** using the monitoring dashboard
2. **Review performance metrics** and optimize if needed
3. **Collect user feedback** and address any issues
4. **Schedule Google Cloud resource cleanup**
5. **Update documentation** and runbooks
6. **Plan performance optimization** based on production data

## Support

For issues during deployment:

1. Check the monitoring dashboard: `./monitor_deployment.sh`
2. Review deployment logs in the generated log files
3. Use management commands for quick status checks
4. Execute emergency rollback if critical issues occur

---

**Note**: This deployment process is designed to be safe and reversible. Each stage includes validation and health checks to ensure system stability throughout the migration process.