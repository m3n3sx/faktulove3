# Phased Deployment Guide

This guide covers the complete phased deployment and validation process for the FaktuLove system improvements.

## Overview

The phased deployment process validates and deploys system improvements in two main phases:

1. **Phase 1**: Core fixes validation (navigation, admin panel, OCR, UI/UX)
2. **Phase 2**: Complete system validation (multi-company, performance, security, compliance)

## Prerequisites

Before starting the deployment:

1. **Environment Setup**
   ```bash
   # Activate virtual environment
   source venv/bin/activate
   
   # Ensure all dependencies are installed
   pip install -r requirements.txt
   ```

2. **Database Backup**
   ```bash
   # Create database backup
   python manage.py dumpdata > backup_$(date +%Y%m%d_%H%M%S).json
   ```

3. **Service Status Check**
   ```bash
   # Check Redis
   redis-cli ping
   
   # Check database connectivity
   python manage.py check --database default
   ```

## Deployment Methods

### Method 1: Automated Phased Deployment (Recommended)

Run the complete automated deployment process:

```bash
./scripts/run_phased_deployment.sh
```

This script will:
- Check prerequisites
- Create system backup
- Run database migrations
- Collect static files
- Execute Phase 1 validation
- Execute Phase 2 validation
- Run comprehensive tests
- Restart services
- Generate deployment report

### Method 2: Manual Phase Execution

#### Phase 1: Core Fixes Validation

```bash
python scripts/deploy_and_validate_core_fixes.py
```

Validates:
- Navigation system fixes
- Admin panel improvements
- OCR functionality enhancements
- UI/UX consistency improvements

#### Phase 2: Complete System Validation

```bash
python scripts/complete_system_validation.py
```

Validates:
- Multi-company features
- Partnership management
- Performance monitoring
- Security enhancements
- Data management tools
- Compliance features
- System health monitoring

## Validation Criteria

### Phase 1 Success Criteria

- ✅ All navigation routes accessible (>90% success rate)
- ✅ Admin panel static assets available
- ✅ OCR upload interface working without loading issues
- ✅ UI consistency across pages
- ✅ Mobile responsiveness functional

### Phase 2 Success Criteria

- ✅ Multi-company context switching working
- ✅ Partnership management functional
- ✅ Performance monitoring active
- ✅ Security framework operational
- ✅ Data export/import working
- ✅ Polish compliance validated
- ✅ System health monitoring active

## Monitoring and Rollback

### Post-Deployment Monitoring

1. **Performance Metrics**
   ```bash
   # Check system health
   python manage.py monitor_system_health
   
   # View performance dashboard
   # Navigate to /admin/system-health/
   ```

2. **Error Monitoring**
   ```bash
   # Check error logs
   tail -f logs/django_errors.log
   tail -f logs/api_errors.log
   ```

3. **User Experience Validation**
   - Test key user workflows
   - Verify OCR processing
   - Check invoice creation/management
   - Validate multi-company switching

### Rollback Procedures

If issues are detected after deployment:

1. **Database Rollback**
   ```bash
   # Restore from backup
   python manage.py loaddata backup_YYYYMMDD_HHMMSS.json
   ```

2. **Code Rollback**
   ```bash
   # Revert to previous commit
   git revert HEAD
   
   # Restart services
   ./scripts/restart_gunicorn.sh
   ```

3. **Service Restart**
   ```bash
   # Restart all services
   ./scripts/stop_dev.sh
   ./scripts/start_dev.sh
   ```

## Deployment Reports

All deployment activities generate detailed reports in `deployment_reports/`:

- `core_fixes_validation_YYYYMMDD_HHMMSS.json` - Phase 1 validation results
- `complete_system_validation_YYYYMMDD_HHMMSS.json` - Phase 2 validation results
- `phased_deployment_YYYYMMDD_HHMMSS.json` - Overall deployment report

### Report Structure

```json
{
  "validation_timestamp": "2025-01-XX...",
  "validation_duration": "0:05:23",
  "overall_status": "PASSED|FAILED|PARTIAL",
  "success_rate": 95.5,
  "results": {
    "navigation_fixes": {...},
    "admin_panel_fixes": {...},
    "ocr_improvements": {...},
    "ui_ux_enhancements": {...},
    "performance_metrics": {...}
  },
  "recommendations": [...]
}
```

## Troubleshooting

### Common Issues

1. **Database Migration Failures**
   ```bash
   # Check migration status
   python manage.py showmigrations
   
   # Fake problematic migration
   python manage.py migrate --fake app_name migration_name
   ```

2. **Static Files Issues**
   ```bash
   # Clear and recollect static files
   rm -rf staticfiles/
   python manage.py collectstatic --noinput
   ```

3. **OCR Service Issues**
   ```bash
   # Check OCR service status
   python manage.py test_ocr_setup
   
   # Restart OCR containers
   docker-compose -f docker-compose.ocr.yml restart
   ```

4. **Performance Issues**
   ```bash
   # Run performance optimization
   python manage.py optimize_database_performance
   python manage.py optimize_assets
   ```

### Getting Help

If deployment issues persist:

1. Check deployment reports for specific error messages
2. Review system logs in `logs/` directory
3. Verify all prerequisites are met
4. Consider running individual validation scripts for debugging

## Production Deployment Checklist

Before deploying to production:

- [ ] All validation phases pass successfully
- [ ] Performance metrics meet requirements (< 3s page load)
- [ ] Security audit completed
- [ ] Backup procedures tested
- [ ] Rollback procedures verified
- [ ] Monitoring systems active
- [ ] User acceptance testing completed
- [ ] Documentation updated

## Post-Deployment Tasks

After successful deployment:

1. **User Communication**
   - Notify users of new features
   - Provide training materials
   - Update user documentation

2. **Monitoring Setup**
   - Configure performance alerts
   - Set up error notifications
   - Schedule regular health checks

3. **Maintenance Planning**
   - Schedule regular backups
   - Plan maintenance windows
   - Update deployment procedures

## Support and Maintenance

For ongoing support:

- Monitor system health dashboard
- Review performance metrics regularly
- Keep deployment documentation updated
- Maintain backup and rollback procedures