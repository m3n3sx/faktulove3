"""
Dashboard and reporting views
"""
import datetime
import json
from decimal import Decimal

from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Q, Sum, F, FloatField
from django.utils import timezone
from dateutil.relativedelta import relativedelta

from ..models import Faktura, Firma, DocumentUpload, OCRResult, OCRValidation


def get_total(queryset, typ_faktury, start_date, end_date):
    """Calculate total for given date range and invoice type - FIXED VAT calculation"""
    from django.db.models import Case, When, DecimalField
    
    total = queryset.filter(
        data_sprzedazy__gte=start_date,
        data_sprzedazy__lt=end_date,
        typ_faktury=typ_faktury
    ).aggregate(
        total=Sum(
            F('pozycjafaktury__ilosc') *
            F('pozycjafaktury__cena_netto') *
            Case(
                # Proper VAT calculation with string values
                When(pozycjafaktury__vat='23', then=Decimal('1.23')),
                When(pozycjafaktury__vat='8', then=Decimal('1.08')),
                When(pozycjafaktury__vat='5', then=Decimal('1.05')),
                When(pozycjafaktury__vat='0', then=Decimal('1.00')),
                When(pozycjafaktury__vat='zw', then=Decimal('1.00')),
                default=Decimal('1.23'),  # Default to 23% VAT
                output_field=DecimalField(max_digits=5, decimal_places=2)
            ),
            output_field=DecimalField(max_digits=15, decimal_places=2)
        )
    )['total'] or Decimal('0.00')
    return float(total)


def get_time_series(queryset, typ_faktury, start_date, end_date, points=10):
    """Generate time series data for charts"""
    total_seconds = (end_date - start_date).total_seconds()
    interval = datetime.timedelta(seconds=total_seconds / points)
    labels = []
    series = []
    for i in range(points):
        interval_start = start_date + interval * i
        interval_end = start_date + interval * (i + 1)
        total = get_total(queryset, typ_faktury, interval_start, interval_end)
        labels.append(interval_start.strftime("%d/%m"))
        series.append(round(total, 2))
    return labels, series


def compare_periods(queryset, typ_faktury, current_start, current_end, previous_start, previous_end):
    """
    Calculate percentage change between current and previous period.
    Returns None when previous period value is zero.
    """
    current_total = get_total(queryset, typ_faktury, current_start, current_end)
    previous_total = get_total(queryset, typ_faktury, previous_start, previous_end)
    if previous_total:
        change = ((current_total - previous_total) / previous_total) * 100
    else:
        change = None
    return change


@login_required
def panel_uzytkownika(request):
    """Main dashboard view"""
    # Get user invoices with optimized queries using custom manager
    faktury = Faktura.objects.for_user(request.user).with_related()

    # Sorting
    sort_by = request.GET.get('sort', '-data_wystawienia')
    valid_sort_fields = [
        'typ_dokumentu', 'numer', 'data_sprzedazy', 'data_wystawienia',
        'termin_platnosci', 'nabywca__nazwa', 'suma_netto', 'suma_brutto',
        'status', 'typ_faktury'
    ]
    if sort_by.replace('-', '') in valid_sort_fields:
        faktury = faktury.order_by(sort_by)
    elif sort_by.replace('-', '') == 'produkt_usluga':
        faktury = faktury.annotate(first_product_name=F('pozycjafaktury__nazwa'))
        faktury = faktury.order_by(('-' if sort_by.startswith('-') else '') + 'first_product_name')
    else:
        faktury = faktury.order_by('-data_wystawienia')

    try:
        firma = Firma.objects.get(user=request.user)
    except Firma.DoesNotExist:
        firma = None

    # Date ranges
    today = timezone.now().date()
    
    # Week: Monday to Sunday
    week_start = today - datetime.timedelta(days=today.weekday())
    week_end = week_start + datetime.timedelta(days=7)
    
    # Month: first day of current month to first day of next month
    month_start = today.replace(day=1)
    month_end = (month_start + datetime.timedelta(days=32)).replace(day=1)
    
    # Quarter
    quarter = (today.month - 1) // 3 + 1
    quarter_start = datetime.date(today.year, 3 * quarter - 2, 1)
    quarter_end = quarter_start + datetime.timedelta(days=92)
    
    # Year
    year_start = today.replace(month=1, day=1)
    year_end = today.replace(year=today.year + 1, month=1, day=1)
    
    # Total period
    total_start = datetime.date(1970, 1, 1)
    total_end = today + datetime.timedelta(days=1)

    # Calculate totals for current periods
    # Sales
    sprzedaz_tygodniowa = round(get_total(faktury, 'sprzedaz', week_start, week_end), 2)
    sprzedaz_miesieczna = round(get_total(faktury, 'sprzedaz', month_start, month_end), 2)
    sprzedaz_kwartalna = round(get_total(faktury, 'sprzedaz', quarter_start, quarter_end), 2)
    sprzedaz_roczna = round(get_total(faktury, 'sprzedaz', year_start, year_end), 2)
    sprzedaz_calkowita = round(get_total(faktury, 'sprzedaz', total_start, total_end), 2)

    # Costs
    koszt_tygodniowy = round(get_total(faktury, 'koszt', week_start, week_end), 2)
    koszt_miesieczny = round(get_total(faktury, 'koszt', month_start, month_end), 2)
    koszt_kwartalny = round(get_total(faktury, 'koszt', quarter_start, quarter_end), 2)
    koszt_roczny = round(get_total(faktury, 'koszt', year_start, year_end), 2)
    koszty_calkowite = round(get_total(faktury, 'koszt', total_start, total_end), 2)

    # Period comparisons for sales
    sprzedaz_weekly_change = compare_periods(
        faktury, 'sprzedaz',
        week_start, week_end,
        week_start - datetime.timedelta(days=7), week_start
    )
    sprzedaz_monthly_change = compare_periods(
        faktury, 'sprzedaz',
        month_start, month_end,
        month_start - relativedelta(months=1), month_start
    )
    sprzedaz_quarterly_change = compare_periods(
        faktury, 'sprzedaz',
        quarter_start, quarter_end,
        quarter_start - relativedelta(months=3), quarter_start
    )
    sprzedaz_yearly_change = compare_periods(
        faktury, 'sprzedaz',
        year_start, year_end,
        year_start - relativedelta(years=1), year_start
    )
    
    # Period comparisons for costs
    koszty_weekly_change = compare_periods(
        faktury, 'koszt',
        week_start, week_end,
        week_start - datetime.timedelta(days=7), week_start
    )
    koszty_monthly_change = compare_periods(
        faktury, 'koszt',
        month_start, month_end,
        month_start - relativedelta(months=1), month_start
    )
    koszty_quarterly_change = compare_periods(
        faktury, 'koszt',
        quarter_start, quarter_end,
        quarter_start - relativedelta(months=3), quarter_start
    )
    koszty_yearly_change = compare_periods(
        faktury, 'koszt',
        year_start, year_end,
        year_start - relativedelta(years=1), year_start
    )

    # Generate time series data for charts
    sales_weekly_labels, sales_weekly_series = get_time_series(faktury, 'sprzedaz', week_start, week_end)
    sales_monthly_labels, sales_monthly_series = get_time_series(faktury, 'sprzedaz', month_start, month_end)
    sales_quarterly_labels, sales_quarterly_series = get_time_series(faktury, 'sprzedaz', quarter_start, quarter_end)
    sales_yearly_labels, sales_yearly_series = get_time_series(faktury, 'sprzedaz', year_start, year_end)
    sales_total_labels, sales_total_series = get_time_series(faktury, 'sprzedaz', total_start, total_end)
    
    costs_weekly_labels, costs_weekly_series = get_time_series(faktury, 'koszt', week_start, week_end)
    costs_monthly_labels, costs_monthly_series = get_time_series(faktury, 'koszt', month_start, month_end)
    costs_quarterly_labels, costs_quarterly_series = get_time_series(faktury, 'koszt', quarter_start, quarter_end)
    costs_yearly_labels, costs_yearly_series = get_time_series(faktury, 'koszt', year_start, year_end)
    costs_total_labels, costs_total_series = get_time_series(faktury, 'koszt', total_start, total_end)

    context = {
        'faktury': faktury,
        'firma': firma,
        'sort_by': sort_by,
        'sprzedaz': {
            'Tygodniowa': sprzedaz_tygodniowa,
            'Miesięczna': sprzedaz_miesieczna,
            'Kwartalna': sprzedaz_kwartalna,
            'Roczna': sprzedaz_roczna,
            'Całkowita': sprzedaz_calkowita,
        },
        'koszty': {
            'Tygodniowy': koszt_tygodniowy,
            'Miesięczny': koszt_miesieczny,
            'Kwartalny': koszt_kwartalny,
            'Roczny': koszt_roczny,
            'Całkowity': koszty_calkowite,
        },
        'comparisons': {
            'sprzedaz': {
                'Tygodniowa': sprzedaz_weekly_change,
                'Miesięczna': sprzedaz_monthly_change,
                'Kwartalna': sprzedaz_quarterly_change,
                'Roczna': sprzedaz_yearly_change,
            },
            'koszty': {
                'Tygodniowy': koszty_weekly_change,
                'Miesięczny': koszty_monthly_change,
                'Kwartalny': koszty_quarterly_change,
                'Roczny': koszty_yearly_change,
            }
        },
        # Chart data - converted to JSON
        'sales_weekly_labels': json.dumps(sales_weekly_labels),
        'sales_weekly_series': json.dumps(sales_weekly_series),
        'sales_monthly_labels': json.dumps(sales_monthly_labels),
        'sales_monthly_series': json.dumps(sales_monthly_series),
        'sales_quarterly_labels': json.dumps(sales_quarterly_labels),
        'sales_quarterly_series': json.dumps(sales_quarterly_series),
        'sales_yearly_labels': json.dumps(sales_yearly_labels),
        'sales_yearly_series': json.dumps(sales_yearly_series),
        'sales_total_labels': json.dumps(sales_total_labels),
        'sales_total_series': json.dumps(sales_total_series),

        'costs_weekly_labels': json.dumps(costs_weekly_labels),
        'costs_weekly_series': json.dumps(costs_weekly_series),
        'costs_monthly_labels': json.dumps(costs_monthly_labels),
        'costs_monthly_series': json.dumps(costs_monthly_series),
        'costs_quarterly_labels': json.dumps(costs_quarterly_labels),
        'costs_quarterly_series': json.dumps(costs_quarterly_series),
        'costs_yearly_labels': json.dumps(costs_yearly_labels),
        'costs_yearly_series': json.dumps(costs_yearly_series),
        'costs_total_labels': json.dumps(costs_total_labels),
        'costs_total_series': json.dumps(costs_total_series),
    }
    
    # Add OCR statistics to context
    ocr_context = get_ocr_dashboard_context(request.user)
    context.update(ocr_context)
    return render(request, 'faktury/panel_uzytkownika.html', context)


@login_required
def faktury_sprzedaz(request):
    """Sales invoices view"""
    faktury = Faktura.objects.for_user(request.user).sprzedaz().with_related()
    context = {'faktury': faktury}
    return render(request, 'faktury/faktury_sprzedaz.html', context)


@login_required
def faktury_koszt(request):
    """Cost invoices view"""
    faktury = Faktura.objects.for_user(request.user).koszt().with_related()
    context = {'faktury': faktury}
    return render(request, 'faktury/faktury_koszt.html', context)


# ============================================================================
# OCR DASHBOARD FUNCTIONS
# ============================================================================

def get_ocr_statistics(user, days=30):
    """Get OCR statistics for dashboard"""
    from django.db.models import Count, Avg
    from django.conf import settings
    
    # Calculate date range
    end_date = timezone.now()
    start_date = end_date - datetime.timedelta(days=days)
    
    # Base querysets for user
    documents = DocumentUpload.objects.filter(
        user=user,
        upload_timestamp__gte=start_date
    )
    
    ocr_results = OCRResult.objects.filter(
        document__user=user,
        created_at__gte=start_date
    )
    
    # Document statistics
    total_documents = documents.count()
    completed_docs = documents.filter(processing_status='completed').count()
    failed_docs = documents.filter(processing_status='failed').count()
    processing_docs = documents.filter(processing_status='processing').count()
    
    # OCR accuracy statistics
    if ocr_results.exists():
        confidence_stats = ocr_results.aggregate(
            avg_confidence=Avg('confidence_score'),
            high_confidence=Count('id', filter=Q(confidence_score__gte=95)),
            medium_confidence=Count('id', filter=Q(confidence_score__gte=80, confidence_score__lt=95)),
            low_confidence=Count('id', filter=Q(confidence_score__lt=80)),
            auto_created=Count('id', filter=Q(faktura__isnull=False)),
        )
        
        processing_stats = ocr_results.aggregate(
            avg_processing_time=Avg('processing_time')
        )
    else:
        confidence_stats = {
            'avg_confidence': 0,
            'high_confidence': 0,
            'medium_confidence': 0,
            'low_confidence': 0,
            'auto_created': 0,
        }
        processing_stats = {'avg_processing_time': 0}
    
    # Calculate success rate
    success_rate = (completed_docs / total_documents * 100) if total_documents > 0 else 0
    
    # Calculate auto-creation rate
    auto_creation_rate = (confidence_stats['auto_created'] / ocr_results.count() * 100) if ocr_results.count() > 0 else 0
    
    return {
        'total_documents': total_documents,
        'completed_documents': completed_docs,
        'failed_documents': failed_docs,
        'processing_documents': processing_docs,
        'success_rate': round(success_rate, 1),
        'avg_confidence': round(confidence_stats['avg_confidence'] or 0, 1),
        'high_confidence_count': confidence_stats['high_confidence'],
        'medium_confidence_count': confidence_stats['medium_confidence'],
        'low_confidence_count': confidence_stats['low_confidence'],
        'auto_created_invoices': confidence_stats['auto_created'],
        'auto_creation_rate': round(auto_creation_rate, 1),
        'avg_processing_time': round(processing_stats['avg_processing_time'] or 0, 1),
        'total_ocr_results': ocr_results.count(),
    }


def get_ocr_chart_data(user, days=30):
    """Get OCR data for charts"""
    end_date = timezone.now()
    start_date = end_date - datetime.timedelta(days=days)
    
    # Daily upload trend
    daily_uploads = DocumentUpload.objects.filter(
        user=user,
        upload_timestamp__gte=start_date
    ).extra(
        select={'day': 'date(upload_timestamp)'}
    ).values('day').annotate(
        uploads=Count('id'),
        completed=Count('id', filter=Q(processing_status='completed')),
        failed=Count('id', filter=Q(processing_status='failed'))
    ).order_by('day')
    
    # Confidence distribution
    ocr_results = OCRResult.objects.filter(
        document__user=user,
        created_at__gte=start_date
    )
    
    confidence_ranges = [
        ('95-100%', ocr_results.filter(confidence_score__gte=95).count()),
        ('80-94%', ocr_results.filter(confidence_score__gte=80, confidence_score__lt=95).count()),
        ('60-79%', ocr_results.filter(confidence_score__gte=60, confidence_score__lt=80).count()),
        ('<60%', ocr_results.filter(confidence_score__lt=60).count()),
    ]
    
    return {
        'daily_uploads': list(daily_uploads),
        'confidence_distribution': confidence_ranges,
    }


def get_recent_ocr_activity(user, limit=5):
    """Get recent OCR activity for dashboard"""
    recent_documents = DocumentUpload.objects.filter(
        user=user
    ).select_related('user').prefetch_related('ocrresult_set').order_by('-upload_timestamp')[:limit]
    
    activities = []
    for doc in recent_documents:
        activity = {
            'filename': doc.original_filename,
            'upload_time': doc.upload_timestamp,
            'status': doc.processing_status,
            'has_result': hasattr(doc, 'ocrresult'),
        }
        
        # Add OCR result info if available
        try:
            ocr_result = doc.ocrresult
            activity.update({
                'confidence': ocr_result.confidence_score,
                'processing_time': ocr_result.processing_time,
                'has_invoice': bool(ocr_result.faktura),
                'invoice_number': ocr_result.faktura.numer if ocr_result.faktura else None,
                'ocr_result_id': ocr_result.id,
            })
        except OCRResult.DoesNotExist:
            activity.update({
                'confidence': None,
                'processing_time': None,
                'has_invoice': False,
                'invoice_number': None,
                'ocr_result_id': None,
            })
        
        activities.append(activity)
    
    return activities


def get_ocr_dashboard_context(user):
    """Get complete OCR context for dashboard"""
    stats = get_ocr_statistics(user)
    charts = get_ocr_chart_data(user)
    recent = get_recent_ocr_activity(user)
    
    return {
        'ocr_stats': stats,
        'ocr_charts': charts,
        'recent_ocr_activity': recent,
        'has_ocr_activity': stats['total_documents'] > 0,
    }
