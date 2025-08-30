# Generated migration for rollout monitoring models

from django.db import migrations, models
import django.db.models.deletion
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('faktury', '0033_add_performance_monitoring_models'),
    ]

    operations = [
        migrations.CreateModel(
            name='FeatureFlag',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, unique=True, verbose_name='Flag Name')),
                ('description', models.TextField(blank=True, verbose_name='Description')),
                ('enabled', models.BooleanField(default=False, verbose_name='Enabled')),
                ('rollout_percentage', models.IntegerField(default=0, help_text='Percentage of users to include (0-100)', verbose_name='Rollout Percentage')),
                ('start_date', models.DateTimeField(blank=True, null=True, verbose_name='Start Date')),
                ('end_date', models.DateTimeField(blank=True, null=True, verbose_name='End Date')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Created At')),
                ('updated_at', models.DateTimeField(auto_now=True, verbose_name='Updated At')),
            ],
            options={
                'verbose_name': 'Feature Flag',
                'verbose_name_plural': 'Feature Flags',
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='UserFeedback',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('rating', models.IntegerField(choices=[(1, '1 - Very Poor'), (2, '2 - Poor'), (3, '3 - Average'), (4, '4 - Good'), (5, '5 - Excellent')], verbose_name='Rating')),
                ('category', models.CharField(choices=[('design_system', 'Design System'), ('polish_business', 'Polish Business Features'), ('performance', 'Performance'), ('usability', 'Usability'), ('bug_report', 'Bug Report'), ('feature_request', 'Feature Request'), ('other', 'Other')], max_length=50, verbose_name='Category')),
                ('comment', models.TextField(blank=True, verbose_name='Comment')),
                ('page_url', models.URLField(blank=True, verbose_name='Page URL')),
                ('user_agent', models.TextField(blank=True, verbose_name='User Agent')),
                ('feature_flags_active', models.JSONField(blank=True, default=dict, verbose_name='Active Feature Flags')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Created At')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='User')),
            ],
            options={
                'verbose_name': 'User Feedback',
                'verbose_name_plural': 'User Feedback',
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='FeatureUsageLog',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('feature_name', models.CharField(max_length=100, verbose_name='Feature Name')),
                ('session_id', models.CharField(blank=True, max_length=100, verbose_name='Session ID')),
                ('page_url', models.URLField(blank=True, verbose_name='Page URL')),
                ('user_agent', models.TextField(blank=True, verbose_name='User Agent')),
                ('timestamp', models.DateTimeField(auto_now_add=True, verbose_name='Timestamp')),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL, verbose_name='User')),
            ],
            options={
                'verbose_name': 'Feature Usage Log',
                'verbose_name_plural': 'Feature Usage Logs',
                'ordering': ['-timestamp'],
            },
        ),
        migrations.CreateModel(
            name='RolloutEvent',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('event_type', models.CharField(choices=[('feature_flag_enabled', 'Feature Flag Enabled'), ('feature_flag_disabled', 'Feature Flag Disabled'), ('user_feedback_submitted', 'User Feedback Submitted'), ('emergency_rollback', 'Emergency Rollback'), ('phase_started', 'Phase Started'), ('phase_completed', 'Phase Completed'), ('anomaly_detected', 'Anomaly Detected')], max_length=50, verbose_name='Event Type')),
                ('details', models.JSONField(blank=True, default=dict, verbose_name='Event Details')),
                ('timestamp', models.DateTimeField(auto_now_add=True, verbose_name='Timestamp')),
            ],
            options={
                'verbose_name': 'Rollout Event',
                'verbose_name_plural': 'Rollout Events',
                'ordering': ['-timestamp'],
            },
        ),
        migrations.CreateModel(
            name='ErrorLog',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('level', models.CharField(choices=[('DEBUG', 'Debug'), ('INFO', 'Info'), ('WARNING', 'Warning'), ('ERROR', 'Error'), ('CRITICAL', 'Critical')], max_length=20, verbose_name='Level')),
                ('message', models.TextField(verbose_name='Message')),
                ('exception_type', models.CharField(blank=True, max_length=100, verbose_name='Exception Type')),
                ('stack_trace', models.TextField(blank=True, verbose_name='Stack Trace')),
                ('request_path', models.CharField(blank=True, max_length=500, verbose_name='Request Path')),
                ('user_agent', models.TextField(blank=True, verbose_name='User Agent')),
                ('timestamp', models.DateTimeField(auto_now_add=True, verbose_name='Timestamp')),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL, verbose_name='User')),
            ],
            options={
                'verbose_name': 'Error Log',
                'verbose_name_plural': 'Error Logs',
                'ordering': ['-timestamp'],
            },
        ),
        migrations.CreateModel(
            name='RequestLog',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('method', models.CharField(max_length=10, verbose_name='HTTP Method')),
                ('path', models.CharField(max_length=500, verbose_name='Request Path')),
                ('status_code', models.IntegerField(verbose_name='Status Code')),
                ('response_time_ms', models.FloatField(verbose_name='Response Time (ms)')),
                ('user_agent', models.TextField(blank=True, verbose_name='User Agent')),
                ('ip_address', models.GenericIPAddressField(blank=True, null=True, verbose_name='IP Address')),
                ('timestamp', models.DateTimeField(auto_now_add=True, verbose_name='Timestamp')),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL, verbose_name='User')),
            ],
            options={
                'verbose_name': 'Request Log',
                'verbose_name_plural': 'Request Logs',
                'ordering': ['-timestamp'],
            },
        ),
        migrations.CreateModel(
            name='UserSession',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('session_key', models.CharField(max_length=100, verbose_name='Session Key')),
                ('ip_address', models.GenericIPAddressField(blank=True, null=True, verbose_name='IP Address')),
                ('user_agent', models.TextField(blank=True, verbose_name='User Agent')),
                ('started_at', models.DateTimeField(auto_now_add=True, verbose_name='Started At')),
                ('last_activity', models.DateTimeField(auto_now=True, verbose_name='Last Activity')),
                ('page_views', models.IntegerField(default=0, verbose_name='Page Views')),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL, verbose_name='User')),
            ],
            options={
                'verbose_name': 'User Session',
                'verbose_name_plural': 'User Sessions',
                'ordering': ['-last_activity'],
            },
        ),
        
        # Add indexes for performance
        migrations.RunSQL(
            "CREATE INDEX IF NOT EXISTS faktury_featureflag_name_enabled_idx ON faktury_featureflag (name, enabled);",
            reverse_sql="DROP INDEX IF EXISTS faktury_featureflag_name_enabled_idx;"
        ),
        migrations.RunSQL(
            "CREATE INDEX IF NOT EXISTS faktury_userfeedback_created_at_idx ON faktury_userfeedback (created_at);",
            reverse_sql="DROP INDEX IF EXISTS faktury_userfeedback_created_at_idx;"
        ),
        migrations.RunSQL(
            "CREATE INDEX IF NOT EXISTS faktury_featureusagelog_timestamp_idx ON faktury_featureusagelog (timestamp);",
            reverse_sql="DROP INDEX IF EXISTS faktury_featureusagelog_timestamp_idx;"
        ),
        migrations.RunSQL(
            "CREATE INDEX IF NOT EXISTS faktury_errorlog_timestamp_level_idx ON faktury_errorlog (timestamp, level);",
            reverse_sql="DROP INDEX IF EXISTS faktury_errorlog_timestamp_level_idx;"
        ),
        migrations.RunSQL(
            "CREATE INDEX IF NOT EXISTS faktury_requestlog_timestamp_idx ON faktury_requestlog (timestamp);",
            reverse_sql="DROP INDEX IF EXISTS faktury_requestlog_timestamp_idx;"
        ),
    ]