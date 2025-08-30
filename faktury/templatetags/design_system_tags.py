from django import template
from django.utils.safestring import mark_safe
from django.utils.html import format_html
import json

register = template.Library()

@register.simple_tag
def ds_button(text, variant='primary', size='md', type='button', onclick='', href='', disabled=False, loading=False, **kwargs):
    """
    Render a design system button
    
    Usage:
    {% ds_button "Click me" variant="primary" size="md" %}
    {% ds_button "Link" href="/some-url/" %}
    """
    classes = [
        'ds-button',
        f'ds-button-{variant}',
        f'ds-button-{size}'
    ]
    
    if loading:
        classes.append('ds-button-loading')
    
    if disabled:
        classes.append('ds-button-disabled')
    
    # Add custom classes
    if 'class' in kwargs:
        classes.append(kwargs['class'])
    
    class_str = ' '.join(classes)
    
    # Build attributes
    attrs = []
    if disabled:
        attrs.append('disabled')
    if onclick:
        attrs.append(f'onclick="{onclick}"')
    
    # Add other attributes
    for key, value in kwargs.items():
        if key not in ['class']:
            attrs.append(f'{key}="{value}"')
    
    attr_str = ' '.join(attrs)
    
    if href:
        return format_html(
            '<a href="{}" class="{}" {}>{}</a>',
            href, class_str, attr_str, text
        )
    else:
        return format_html(
            '<button type="{}" class="{}" {}>{}</button>',
            type, class_str, attr_str, text
        )

@register.simple_tag
def ds_badge(text, variant='neutral', size='md', **kwargs):
    """
    Render a design system badge
    
    Usage:
    {% ds_badge "New" variant="success" %}
    {% ds_badge confidence_score|floatformat:1|add:"%" variant="warning" %}
    """
    classes = [
        'ds-badge',
        f'ds-badge-{variant}',
        f'ds-badge-{size}'
    ]
    
    if 'class' in kwargs:
        classes.append(kwargs['class'])
    
    class_str = ' '.join(classes)
    
    return format_html('<span class="{}">{}</span>', class_str, text)

@register.simple_tag
def ds_card(content='', variant='default', **kwargs):
    """
    Render a design system card wrapper
    
    Usage:
    {% ds_card variant="elevated" %}
    """
    classes = [
        'ds-card',
        f'ds-card-{variant}'
    ]
    
    if 'class' in kwargs:
        classes.append(kwargs['class'])
    
    class_str = ' '.join(classes)
    
    return format_html('<div class="{}">{}</div>', class_str, content)

@register.inclusion_tag('design_system/confidence_indicator.html')
def ds_confidence_indicator(confidence, show_progress=False, show_description=False, size='md'):
    """
    Render OCR confidence indicator
    
    Usage:
    {% ds_confidence_indicator result.confidence_score show_description=True %}
    """
    if confidence is None:
        return {
            'confidence': None,
            'variant': 'neutral',
            'text': 'Nieznana',
            'description': 'Brak informacji o pewności',
            'show_progress': show_progress,
            'show_description': show_description,
            'size': size
        }
    
    # Determine confidence level
    if confidence >= 95:
        variant = 'success'
        text = 'Doskonała'
        description = 'Dane bardzo wiarygodne, minimalne ryzyko błędów'
    elif confidence >= 85:
        variant = 'success'
        text = 'Wysoka'
        description = 'Dane wiarygodne, niewielkie ryzyko błędów'
    elif confidence >= 70:
        variant = 'warning'
        text = 'Średnia'
        description = 'Zalecana weryfikacja kluczowych danych'
    elif confidence >= 50:
        variant = 'error'
        text = 'Niska'
        description = 'Wymagana weryfikacja większości danych'
    else:
        variant = 'error'
        text = 'Bardzo niska'
        description = 'Wymagana dokładna weryfikacja wszystkich danych'
    
    return {
        'confidence': round(confidence, 1),
        'variant': variant,
        'text': text,
        'description': description,
        'show_progress': show_progress,
        'show_description': show_description,
        'size': size
    }

@register.inclusion_tag('design_system/table.html')
def ds_table(data, columns, sortable=True, selectable=False, pagination=None, **kwargs):
    """
    Render a design system table
    
    Usage:
    {% ds_table ocr_results table_columns sortable=True %}
    """
    return {
        'data': data,
        'columns': columns,
        'sortable': sortable,
        'selectable': selectable,
        'pagination': pagination,
        'variant': kwargs.get('variant', 'default'),
        'size': kwargs.get('size', 'md'),
        'loading': kwargs.get('loading', False),
        'empty_message': kwargs.get('empty_message', 'Brak danych do wyświetlenia'),
    }

@register.simple_tag
def ocr_stats_high_confidence(results, threshold):
    """Calculate number of high confidence OCR results"""
    if not results or not threshold:
        return 0
    
    count = 0
    for result in results:
        if hasattr(result, 'confidence_score') and result.confidence_score >= threshold:
            count += 1
    
    return count

@register.simple_tag
def ocr_stats_needs_review(results, thresholds):
    """Calculate number of OCR results that need review"""
    if not results or not thresholds:
        return 0
    
    count = 0
    auto_approve = thresholds.get('auto_approve', 95)
    review_required = thresholds.get('review_required', 80)
    
    for result in results:
        if hasattr(result, 'confidence_score'):
            score = result.confidence_score
            if review_required <= score < auto_approve:
                count += 1
    
    return count

@register.simple_tag
def ocr_stats_with_invoice(results):
    """Calculate number of OCR results with created invoices"""
    if not results:
        return 0
    
    count = 0
    for result in results:
        if hasattr(result, 'faktura') and result.faktura:
            count += 1
    
    return count

@register.filter
def confidence_badge_variant(confidence):
    """Get badge variant for confidence score"""
    if confidence is None:
        return 'neutral'
    
    if confidence >= 85:
        return 'success'
    elif confidence >= 70:
        return 'warning'
    else:
        return 'error'

@register.filter
def format_polish_currency(amount, currency='PLN'):
    """Format amount as Polish currency"""
    if amount is None:
        return '-'
    
    try:
        amount = float(amount)
        if currency == 'PLN':
            return f"{amount:,.2f} zł".replace(',', ' ').replace('.', ',')
        else:
            return f"{amount:,.2f} {currency}".replace(',', ' ').replace('.', ',')
    except (ValueError, TypeError):
        return str(amount)

@register.filter
def format_polish_date(date):
    """Format date in Polish format (DD.MM.YYYY)"""
    if not date:
        return '-'
    
    try:
        if hasattr(date, 'strftime'):
            return date.strftime('%d.%m.%Y')
        else:
            # Try to parse string date
            from datetime import datetime
            parsed_date = datetime.fromisoformat(str(date).replace('Z', '+00:00'))
            return parsed_date.strftime('%d.%m.%Y')
    except (ValueError, AttributeError):
        return str(date)

@register.filter
def format_polish_datetime(datetime_obj):
    """Format datetime in Polish format (DD.MM.YYYY HH:MM)"""
    if not datetime_obj:
        return '-'
    
    try:
        if hasattr(datetime_obj, 'strftime'):
            return datetime_obj.strftime('%d.%m.%Y %H:%M')
        else:
            # Try to parse string datetime
            from datetime import datetime
            parsed_datetime = datetime.fromisoformat(str(datetime_obj).replace('Z', '+00:00'))
            return parsed_datetime.strftime('%d.%m.%Y %H:%M')
    except (ValueError, AttributeError):
        return str(datetime_obj)

@register.filter
def file_size_format(bytes_size):
    """Format file size in human readable format"""
    if not bytes_size:
        return '-'
    
    try:
        bytes_size = int(bytes_size)
        if bytes_size < 1024:
            return f"{bytes_size} B"
        elif bytes_size < 1024 * 1024:
            return f"{bytes_size / 1024:.1f} KB"
        elif bytes_size < 1024 * 1024 * 1024:
            return f"{bytes_size / (1024 * 1024):.1f} MB"
        else:
            return f"{bytes_size / (1024 * 1024 * 1024):.1f} GB"
    except (ValueError, TypeError):
        return str(bytes_size)

@register.inclusion_tag('design_system/form_field.html')
def ds_form_field(field, label='', help_text='', required=False, **kwargs):
    """
    Render a design system form field
    
    Usage:
    {% ds_form_field form.invoice_number label="Numer faktury" required=True %}
    """
    return {
        'field': field,
        'label': label or (field.label if hasattr(field, 'label') else ''),
        'help_text': help_text or (field.help_text if hasattr(field, 'help_text') else ''),
        'required': required or (field.field.required if hasattr(field, 'field') else False),
        'errors': field.errors if hasattr(field, 'errors') else [],
        'size': kwargs.get('size', 'md'),
        'variant': kwargs.get('variant', 'default'),
    }

@register.inclusion_tag('design_system/pagination.html')
def ds_pagination(page_obj, **kwargs):
    """
    Render design system pagination
    
    Usage:
    {% ds_pagination page_obj %}
    """
    if not page_obj:
        return {}
    
    # Calculate page range
    current_page = page_obj.number
    total_pages = page_obj.paginator.num_pages
    
    # Show max 5 pages around current
    start_page = max(1, current_page - 2)
    end_page = min(total_pages, current_page + 2)
    
    # Adjust if we're near the beginning or end
    if end_page - start_page < 4:
        if start_page == 1:
            end_page = min(total_pages, start_page + 4)
        else:
            start_page = max(1, end_page - 4)
    
    page_range = range(start_page, end_page + 1)
    
    return {
        'page_obj': page_obj,
        'page_range': page_range,
        'show_first': start_page > 1,
        'show_last': end_page < total_pages,
        'show_prev_ellipsis': start_page > 2,
        'show_next_ellipsis': end_page < total_pages - 1,
    }

@register.simple_tag
def ds_grid_classes(cols=1, gap='md', **kwargs):
    """
    Generate grid classes for design system
    
    Usage:
    {% ds_grid_classes cols=3 gap="lg" %}
    """
    classes = ['ds-grid', f'ds-gap-{gap}']
    
    if isinstance(cols, dict):
        # Responsive columns
        for breakpoint, col_count in cols.items():
            if breakpoint == 'base':
                classes.append(f'ds-grid-cols-{col_count}')
            else:
                classes.append(f'ds-grid-cols-{breakpoint}-{col_count}')
    else:
        # Single column count
        classes.append(f'ds-grid-cols-{cols}')
    
    return ' '.join(classes)

@register.simple_tag
def ds_stack_classes(gap='md', **kwargs):
    """
    Generate stack classes for design system
    
    Usage:
    {% ds_stack_classes gap="lg" %}
    """
    return f'ds-stack ds-stack-{gap}'

# Polish Business Component Template Tags

@register.simple_tag
def ds_currency_format(amount, currency='PLN', locale='pl-PL'):
    """
    Format currency using Polish business formatting
    
    Usage:
    {% ds_currency_format invoice.total_amount currency="PLN" %}
    """
    if amount is None:
        return '-'
    
    try:
        amount = float(amount)
        if currency == 'PLN':
            return f"{amount:,.2f} zł".replace(',', ' ').replace('.', ',')
        else:
            return f"{amount:,.2f} {currency}".replace(',', ' ').replace('.', ',')
    except (ValueError, TypeError):
        return str(amount)

@register.simple_tag
def ds_date_format(date, locale='pl-PL', format_type='short'):
    """
    Format date using Polish business formatting
    
    Usage:
    {% ds_date_format invoice.issue_date locale="pl-PL" %}
    """
    if not date:
        return '-'
    
    try:
        if hasattr(date, 'strftime'):
            if format_type == 'long':
                return date.strftime('%d %B %Y')
            else:
                return date.strftime('%d.%m.%Y')
        else:
            # Try to parse string date
            from datetime import datetime
            parsed_date = datetime.fromisoformat(str(date).replace('Z', '+00:00'))
            if format_type == 'long':
                return parsed_date.strftime('%d %B %Y')
            else:
                return parsed_date.strftime('%d.%m.%Y')
    except (ValueError, AttributeError):
        return str(date)

@register.simple_tag
def ds_nip_format(nip):
    """
    Format NIP number with Polish formatting
    
    Usage:
    {% ds_nip_format contractor.nip %}
    """
    if not nip:
        return '-'
    
    # Remove all non-digit characters
    clean_nip = ''.join(filter(str.isdigit, str(nip)))
    
    if len(clean_nip) == 10:
        return f"{clean_nip[:3]}-{clean_nip[3:6]}-{clean_nip[6:8]}-{clean_nip[8:10]}"
    else:
        return str(nip)

@register.inclusion_tag('design_system/invoice_status_badge.html')
def ds_invoice_status_badge(status, size='md'):
    """
    Render invoice status badge with Polish business styling
    
    Usage:
    {% ds_invoice_status_badge invoice.status size="sm" %}
    """
    # Map Django model status to design system status
    status_mapping = {
        'wystawiona': 'sent',
        'oplacona': 'paid',
        'cz_oplacona': 'viewed',  # Partially paid -> viewed for now
        'anulowana': 'cancelled',
        'szkic': 'draft',
        'przeterminowana': 'overdue',
        'skorygowana': 'corrected',
    }
    
    ds_status = status_mapping.get(status, 'draft')
    
    return {
        'status': ds_status,
        'size': size,
        'original_status': status
    }

@register.inclusion_tag('design_system/compliance_indicator.html')
def ds_compliance_indicator(rules, show_details=False, size='md'):
    """
    Render compliance indicator for Polish business requirements
    
    Usage:
    {% ds_compliance_indicator compliance_rules show_details=True %}
    """
    return {
        'rules': rules,
        'show_details': show_details,
        'size': size
    }

@register.inclusion_tag('design_system/vat_rate_display.html')
def ds_vat_rate_display(vat_rate, amount=None):
    """
    Display VAT rate with Polish formatting
    
    Usage:
    {% ds_vat_rate_display item.vat_rate item.net_amount %}
    """
    if vat_rate == 'zw' or vat_rate == 'zw.':
        return {
            'rate_text': 'zw.',
            'rate_description': 'Zwolnione z VAT',
            'vat_amount': None,
            'is_exempt': True
        }
    elif vat_rate == 'np' or vat_rate == 'np.':
        return {
            'rate_text': 'np.',
            'rate_description': 'Nie podlega VAT',
            'vat_amount': None,
            'is_exempt': True
        }
    else:
        try:
            rate_value = float(vat_rate)
            vat_amount = None
            
            if amount is not None:
                try:
                    net_amount = float(amount)
                    vat_amount = net_amount * (rate_value / 100)
                except (ValueError, TypeError):
                    pass
            
            return {
                'rate_text': f'{rate_value:.0f}%',
                'rate_description': f'Stawka VAT {rate_value:.0f}%',
                'vat_amount': vat_amount,
                'is_exempt': False
            }
        except (ValueError, TypeError):
            return {
                'rate_text': str(vat_rate),
                'rate_description': 'Nieznana stawka VAT',
                'vat_amount': None,
                'is_exempt': False
            }

@register.inclusion_tag('design_system/breadcrumb.html')
def ds_breadcrumb(items):
    """
    Render breadcrumb navigation
    
    Usage:
    {% ds_breadcrumb items="Home,/;Invoices,/invoices/;Invoice Detail,#" %}
    """
    breadcrumb_items = []
    
    if isinstance(items, str):
        # Parse string format: "Label,URL;Label2,URL2"
        for item in items.split(';'):
            if ',' in item:
                label, url = item.split(',', 1)
                breadcrumb_items.append({
                    'label': label.strip(),
                    'url': url.strip() if url.strip() != '#' else None
                })
    elif isinstance(items, list):
        # Direct list format
        breadcrumb_items = items
    
    return {
        'items': breadcrumb_items
    }

@register.inclusion_tag('design_system/alert.html')
def ds_alert(message='', variant='info', dismissible=False, **kwargs):
    """
    Render alert component
    
    Usage:
    {% ds_alert "Success message" variant="success" dismissible=True %}
    """
    return {
        'message': message,
        'variant': variant,
        'dismissible': dismissible,
        'title': kwargs.get('title', ''),
        'icon': kwargs.get('icon', True),
    }

@register.simple_tag
def ds_currency_input(id='', name='', value='', currency='PLN', locale='pl-PL', **kwargs):
    """
    Render currency input field
    
    Usage:
    {% ds_currency_input id="amount" name="amount" currency="PLN" %}
    """
    attrs = []
    attrs.append(f'id="{id}"' if id else '')
    attrs.append(f'name="{name}"' if name else '')
    attrs.append(f'value="{value}"' if value else '')
    attrs.append(f'data-currency="{currency}"')
    attrs.append(f'data-locale="{locale}"')
    attrs.append('class="ds-currency-input"')
    
    for key, val in kwargs.items():
        if key not in ['class']:
            attrs.append(f'{key}="{val}"')
    
    attr_str = ' '.join(filter(None, attrs))
    
    return format_html('<input type="text" {} />', mark_safe(attr_str))

@register.simple_tag
def ds_date_picker(id='', name='', value='', locale='pl-PL', **kwargs):
    """
    Render date picker field
    
    Usage:
    {% ds_date_picker id="date" name="date" locale="pl-PL" %}
    """
    attrs = []
    attrs.append(f'id="{id}"' if id else '')
    attrs.append(f'name="{name}"' if name else '')
    attrs.append(f'value="{value}"' if value else '')
    attrs.append(f'data-locale="{locale}"')
    attrs.append('class="ds-date-picker"')
    
    for key, val in kwargs.items():
        if key not in ['class']:
            attrs.append(f'{key}="{val}"')
    
    attr_str = ' '.join(filter(None, attrs))
    
    return format_html('<input type="text" {} />', mark_safe(attr_str))

@register.simple_tag
def ds_nip_validator(id='', name='', value='', **kwargs):
    """
    Render NIP validator field
    
    Usage:
    {% ds_nip_validator id="nip" name="nip" %}
    """
    attrs = []
    attrs.append(f'id="{id}"' if id else '')
    attrs.append(f'name="{name}"' if name else '')
    attrs.append(f'value="{value}"' if value else '')
    attrs.append('class="ds-nip-validator"')
    attrs.append('data-real-time-validation="true"')
    attrs.append('data-show-validation-icon="true"')
    
    for key, val in kwargs.items():
        if key not in ['class']:
            attrs.append(f'{key}="{val}"')
    
    attr_str = ' '.join(filter(None, attrs))
    
    return format_html('<input type="text" {} />', mark_safe(attr_str))

@register.simple_tag
def ds_vat_rate_selector(id='', name='', value='', **kwargs):
    """
    Render VAT rate selector
    
    Usage:
    {% ds_vat_rate_selector id="vat" name="vat" %}
    """
    attrs = []
    attrs.append(f'id="{id}"' if id else '')
    attrs.append(f'name="{name}"' if name else '')
    attrs.append(f'value="{value}"' if value else '')
    attrs.append('class="ds-vat-rate-selector"')
    attrs.append('data-include-exempt="true"')
    
    for key, val in kwargs.items():
        if key not in ['class']:
            attrs.append(f'{key}="{val}"')
    
    attr_str = ' '.join(filter(None, attrs))
    
    return format_html('<select {}></select>', mark_safe(attr_str))

@register.simple_tag
def ds_input(id='', name='', value='', type='text', **kwargs):
    """
    Render basic input field
    
    Usage:
    {% ds_input id="name" name="name" type="text" %}
    """
    attrs = []
    attrs.append(f'id="{id}"' if id else '')
    attrs.append(f'name="{name}"' if name else '')
    attrs.append(f'value="{value}"' if value else '')
    attrs.append(f'type="{type}"')
    attrs.append('class="ds-input"')
    
    for key, val in kwargs.items():
        if key not in ['class']:
            attrs.append(f'{key}="{val}"')
    
    attr_str = ' '.join(filter(None, attrs))
    
    return format_html('<input {} />', mark_safe(attr_str))

@register.simple_tag
def ds_select(id='', name='', value='', options='', **kwargs):
    """
    Render select field
    
    Usage:
    {% ds_select id="status" name="status" %}
    """
    attrs = []
    attrs.append(f'id="{id}"' if id else '')
    attrs.append(f'name="{name}"' if name else '')
    attrs.append('class="ds-select"')
    
    for key, val in kwargs.items():
        if key not in ['class']:
            attrs.append(f'{key}="{val}"')
    
    attr_str = ' '.join(filter(None, attrs))
    
    return format_html('<select {}>{}</select>', mark_safe(attr_str), options)

@register.simple_tag
def ds_textarea(id='', name='', value='', **kwargs):
    """
    Render textarea field
    
    Usage:
    {% ds_textarea id="notes" name="notes" %}
    """
    attrs = []
    attrs.append(f'id="{id}"' if id else '')
    attrs.append(f'name="{name}"' if name else '')
    attrs.append('class="ds-textarea"')
    
    for key, val in kwargs.items():
        if key not in ['class']:
            attrs.append(f'{key}="{val}"')
    
    attr_str = ' '.join(filter(None, attrs))
    
    return format_html('<textarea {}>{}</textarea>', mark_safe(attr_str), value)

# Block template tags for complex components

@register.simple_tag
def ds_table():
    """Start a design system table"""
    return mark_safe('<table class="ds-table">')

@register.simple_tag
def end_ds_table():
    """End a design system table"""
    return mark_safe('</table>')

@register.simple_tag
def ds_card(variant='default'):
    """Start a design system card"""
    return mark_safe(f'<div class="ds-card ds-card-{variant}">')

@register.simple_tag
def end_ds_card():
    """End a design system card"""
    return mark_safe('</div>')

@register.simple_tag
def ds_button(variant='primary', size='md', type='button', **kwargs):
    """Start a design system button"""
    classes = f'ds-button ds-button-{variant} ds-button-{size}'
    
    attrs = []
    attrs.append(f'type="{type}"')
    attrs.append(f'class="{classes}"')
    
    for key, val in kwargs.items():
        attrs.append(f'{key}="{val}"')
    
    attr_str = ' '.join(attrs)
    
    return mark_safe(f'<button {attr_str}>')

@register.simple_tag
def end_ds_button():
    """End a design system button"""
    return mark_safe('</button>')

# Authentication Form Components

@register.inclusion_tag('design_system/input_field.html')
def ds_input(name='', type='text', label='', placeholder='', required=False, 
             icon='', icon_position='start', size='md', value='', error='', 
             helper_text='', show_password_toggle=False, **kwargs):
    """
    Render design system input field for authentication forms
    
    Usage:
    {% ds_input name="email" type="email" label="Email" required=True icon="mage:email" %}
    """
    return {
        'name': name,
        'type': type,
        'label': label,
        'placeholder': placeholder,
        'required': required,
        'icon': icon,
        'icon_position': icon_position,
        'size': size,
        'value': value,
        'error': error,
        'helper_text': helper_text,
        'show_password_toggle': show_password_toggle,
        'id': kwargs.get('id', f'id_{name}'),
        'class': kwargs.get('class', ''),
        'autocomplete': kwargs.get('autocomplete', ''),
        'pattern': kwargs.get('pattern', ''),
        'minlength': kwargs.get('minlength', ''),
        'maxlength': kwargs.get('maxlength', ''),
    }

@register.inclusion_tag('design_system/checkbox_field.html')
def ds_checkbox(name='', label='', label_html='', checked=False, required=False, **kwargs):
    """
    Render design system checkbox field
    
    Usage:
    {% ds_checkbox name="remember" label="Remember me" %}
    {% ds_checkbox name="terms" label_html='I accept <a href="#">Terms</a>' required=True %}
    """
    return {
        'name': name,
        'label': label,
        'label_html': label_html,
        'checked': checked,
        'required': required,
        'id': kwargs.get('id', f'id_{name}'),
        'class': kwargs.get('class', ''),
    }

@register.inclusion_tag('design_system/button_field.html')
def ds_button(type='button', variant='primary', size='md', full_width=False, 
              loading_text='', disabled=False, **kwargs):
    """
    Render design system button
    
    Usage:
    {% ds_button type="submit" variant="primary" size="lg" full_width=True %}Submit{% end_ds_button %}
    """
    return {
        'type': type,
        'variant': variant,
        'size': size,
        'full_width': full_width,
        'loading_text': loading_text,
        'disabled': disabled,
        'id': kwargs.get('id', ''),
        'class': kwargs.get('class', ''),
        'onclick': kwargs.get('onclick', ''),
    }

@register.inclusion_tag('design_system/typography.html')
def ds_typography(variant='body-md', element='p', **kwargs):
    """
    Render design system typography
    
    Usage:
    {% ds_typography variant="heading-lg" element="h1" %}Title{% end_ds_typography %}
    """
    return {
        'variant': variant,
        'element': element,
        'class': kwargs.get('class', ''),
        'id': kwargs.get('id', ''),
    }

@register.inclusion_tag('design_system/theme_controls.html')
def ds_theme_controls(compact=False, show_advanced=False, **kwargs):
    """
    Render theme controls component
    
    Usage:
    {% ds_theme_controls compact=True %}
    """
    return {
        'compact': compact,
        'show_advanced': show_advanced,
        'class': kwargs.get('class', ''),
    }

# Block template tags for complex components with content

@register.simple_tag
def ds_typography_start(variant='body-md', element='p', **kwargs):
    """Start a design system typography element"""
    classes = f'ds-typography ds-typography-{variant}'
    if 'class' in kwargs:
        classes += f' {kwargs["class"]}'
    
    attrs = []
    attrs.append(f'class="{classes}"')
    
    for key, val in kwargs.items():
        if key not in ['class']:
            attrs.append(f'{key}="{val}"')
    
    attr_str = ' '.join(attrs)
    
    return mark_safe(f'<{element} {attr_str}>')

@register.simple_tag
def end_ds_typography(element='p'):
    """End a design system typography element"""
    return mark_safe(f'</{element}>')

@register.simple_tag
def ds_card_start(variant='default', **kwargs):
    """Start a design system card"""
    classes = f'ds-card ds-card-{variant}'
    if 'class' in kwargs:
        classes += f' {kwargs["class"]}'
    
    attrs = []
    attrs.append(f'class="{classes}"')
    
    for key, val in kwargs.items():
        if key not in ['class']:
            attrs.append(f'{key}="{val}"')
    
    attr_str = ' '.join(attrs)
    
    return mark_safe(f'<div {attr_str}>')

@register.simple_tag
def end_ds_card():
    """End a design system card"""
    return mark_safe('</div>')

@register.simple_tag
def ds_button_start(type='button', variant='primary', size='md', full_width=False, **kwargs):
    """Start a design system button"""
    classes = f'ds-button ds-button-{variant} ds-button-{size}'
    if full_width:
        classes += ' ds-button-full-width'
    if 'class' in kwargs:
        classes += f' {kwargs["class"]}'
    
    attrs = []
    attrs.append(f'type="{type}"')
    attrs.append(f'class="{classes}"')
    
    for key, val in kwargs.items():
        if key not in ['class']:
            attrs.append(f'{key}="{val}"')
    
    attr_str = ' '.join(attrs)
    
    return mark_safe(f'<button {attr_str}>')

@register.simple_tag
def end_ds_button():
    """End a design system button"""
    return mark_safe('</button>')