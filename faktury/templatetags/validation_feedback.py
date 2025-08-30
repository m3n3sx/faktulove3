"""
Template tags for validation and feedback systems
"""

from django import template
from django.utils.safestring import mark_safe
from django.templatetags.static import static

register = template.Library()

@register.inclusion_tag('faktury/partials/validation_scripts.html')
def validation_scripts():
    """Include validation JavaScript files"""
    return {}

@register.inclusion_tag('faktury/partials/feedback_scripts.html')
def feedback_scripts():
    """Include feedback system JavaScript files"""
    return {}

@register.simple_tag
def validation_form_attrs():
    """Return HTML attributes for forms with validation enabled"""
    return mark_safe('data-validate="true" novalidate')

@register.simple_tag
def validation_field_attrs(field_name, **kwargs):
    """Return HTML attributes for validated fields"""
    attrs = []
    
    # Add validation attribute
    attrs.append(f'data-validate-as="{field_name}"')
    
    # Add uniqueness check if specified
    if kwargs.get('check_unique'):
        attrs.append('data-check-uniqueness="true"')
    
    # Add required attribute for accessibility
    if kwargs.get('required'):
        attrs.append('required')
        attrs.append('aria-required="true"')
    
    return mark_safe(' '.join(attrs))

@register.filter
def add_validation_class(field, css_class="form-control"):
    """Add validation CSS class to form field"""
    if hasattr(field, 'as_widget'):
        return field.as_widget(attrs={'class': css_class})
    return field

@register.inclusion_tag('faktury/partials/field_validation_message.html')
def field_validation_message(field):
    """Render validation message container for a field"""
    return {
        'field': field,
        'field_id': getattr(field, 'id_for_label', field.name if hasattr(field, 'name') else '')
    }

@register.simple_tag
def polish_error_messages():
    """Return Polish error messages as JSON for JavaScript"""
    messages = {
        'required': 'To pole jest wymagane',
        'invalid_nip': 'Nieprawidłowy numer NIP',
        'invalid_regon': 'Nieprawidłowy numer REGON',
        'invalid_krs': 'Nieprawidłowy numer KRS',
        'invalid_email': 'Nieprawidłowy adres email',
        'invalid_phone': 'Nieprawidłowy numer telefonu',
        'invalid_postal_code': 'Nieprawidłowy kod pocztowy',
        'invalid_amount': 'Nieprawidłowa kwota',
        'invalid_date': 'Nieprawidłowa data',
        'validation_error': 'Błąd walidacji',
        'network_error': 'Błąd połączenia sieciowego',
        'server_error': 'Błąd serwera'
    }
    
    import json
    return mark_safe(json.dumps(messages))

@register.inclusion_tag('faktury/partials/progress_indicator.html')
def progress_indicator(operation_id, title, steps=None):
    """Render progress indicator for long-running operations"""
    return {
        'operation_id': operation_id,
        'title': title,
        'steps': steps or []
    }