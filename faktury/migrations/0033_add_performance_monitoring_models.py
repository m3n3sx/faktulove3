# Generated migration for performance monitoring models

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('faktury', '0032_add_missing_ocr_fields'),
    ]

    operations = [
        migrations.CreateModel(
            name='PerformanceMetric',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('session_id', models.CharField(blank=True, max_length=100, null=True)),
                ('timestamp', models.DateTimeField(default=django.utils.timezone.now)),
                ('url', models.URLField(max_length=500)),
                ('user_agent', models.TextField()),
                ('lcp', models.FloatField(blank=True, help_text='Largest Contentful Paint (ms)', null=True)),
                ('fid', models.FloatField(blank=True, help_text='First Input Delay (ms)', null=True)),
                ('cls', models.FloatField(blank=True, help_text='Cumulative Layout Shift', null=True)),
                ('fcp', models.FloatField(blank=True, help_text='First Contentful Paint (ms)', null=True)),
                ('ttfb', models.FloatField(blank=True, help_text='Time to First Byte (ms)', null=True)),
                ('component_render_time', models.FloatField(blank=True, null=True)),
                ('bundle_size', models.IntegerField(blank=True, null=True)),
                ('css_load_time', models.FloatField(blank=True, null=True)),
                ('theme_load_time', models.FloatField(blank=True, null=True)),
                ('raw_data', models.JSONField(default=dict)),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'performance_metrics',
            },
        ),
        migrations.CreateModel(
            name='ComponentPerformanceMetric',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('component_name', models.CharField(max_length=100)),
                ('render_count', models.IntegerField(default=0)),
                ('total_render_time', models.FloatField(default=0)),
                ('average_render_time', models.FloatField(default=0)),
                ('max_render_time', models.FloatField(default=0)),
                ('min_render_time', models.FloatField(default=0)),
                ('props_changes', models.IntegerField(default=0)),
                ('memory_usage', models.IntegerField(default=0)),
                ('performance_metric', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='components', to='faktury.performancemetric')),
            ],
            options={
                'db_table': 'component_performance_metrics',
            },
        ),
        migrations.CreateModel(
            name='AccessibilityMetric',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('keyboard_navigation_usage', models.IntegerField(default=0)),
                ('keyboard_navigation_errors', models.IntegerField(default=0)),
                ('screen_reader_detected', models.BooleanField(default=False)),
                ('aria_errors', models.IntegerField(default=0)),
                ('missing_labels', models.IntegerField(default=0)),
                ('color_contrast_violations', models.IntegerField(default=0)),
                ('focus_trap_errors', models.IntegerField(default=0)),
                ('lost_focus_count', models.IntegerField(default=0)),
                ('performance_metric', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='accessibility', to='faktury.performancemetric')),
            ],
            options={
                'db_table': 'accessibility_metrics',
            },
        ),
        migrations.AddIndex(
            model_name='performancemetric',
            index=models.Index(fields=['timestamp'], name='performance_timestamp_idx'),
        ),
        migrations.AddIndex(
            model_name='performancemetric',
            index=models.Index(fields=['user', 'timestamp'], name='performance_user_timestamp_idx'),
        ),
        migrations.AddIndex(
            model_name='performancemetric',
            index=models.Index(fields=['url'], name='performance_url_idx'),
        ),
    ]