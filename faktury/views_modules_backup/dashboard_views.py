"""
Dashboard and reporting views
"""
import datetime
import json
from decimal import Decimal

from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Q, Sum, F, FloatField, DecimalField, Case, When
from django.utils import timezone
from dateutil.relativedelta import relativedelta

from ..models import Faktura, Firma


def get_total(queryset, typ_faktury, start_date, end_date):
    """Calculate total for given date range and invoice type - FIXED VAT calculation"""
    from decimal import Decimal
    
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
    return float(total)  # Convert to float for compatibility with existing code


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
