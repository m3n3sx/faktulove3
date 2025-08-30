"""
Template tags for UI consistency and design system components.
"""

from django import template
from django.utils.safestring import mark_safe
from django.template.loader import render_to_string

register = template.Library()


@register.inclusion_tag('components/button.html')
def ds_button(text='', variant='primary', type='button', icon=None, loading=False, 
              disabled=False, extra_classes='', onclick=None, id=None):
    """
    Render a design system button component.
    
    Usage:
        {% ds_button text="Save" variant="primary" icon="save" %}
        {% ds_button text="Cancel" variant="secondary" %}
    """
    return {
        'text': text,
        'variant': variant,
        'type': type,
        'icon': icon,
        'loading': loading,
        'disabled': disabled,
        'extra_classes': extra_classes,
        'onclick': onclick,
        'id': id
    }


@register.inclusion_tag('components/form_input.html')
def ds_form_input(field_id, name, label='', input_type='text', value='', 
                  placeholder='', required=False, disabled=False, error='', 
                  help_text=''):
    """
    Render a design system form input component.
    
    Usage:
        {% ds_form_input field_id="email" name="email" label="Email Address" required=True %}
    """
    return {
        'field_id': field_id,
        'name': name,
        'label': label,
        'input_type': input_type,
        'value': value,
        'placeholder': placeholder,
        'required': required,
        'disabled': disabled,
        'error': error,
        'help_text': help_text
    }


@register.inclusion_tag('components/skeleton.html')
def ds_skeleton(width='100%', height='1rem', radius='0.25rem'):
    """
    Render a loading skeleton component.
    
    Usage:
        {% ds_skeleton width="200px" height="2rem" %}
    """
    return {
        'width': width,
        'height': height,
        'radius': radius
    }


@register.simple_tag
def ds_loading_button(text, form_id=None, loading_text='Zapisywanie...'):
    """
    Create a button that shows loading state on form submission.
    
    Usage:
        {% ds_loading_button "Save Invoice" form_id="invoice-form" %}
    """
    button_html = f'''
    <button type="submit" class="ds-btn ds-btn-primary" 
            onclick="loadingManager.showLoading(this, {{text: '{loading_text}'}})">
        {text}
    </button>
    '''
    
    return mark_safe(button_html)


@register.simple_tag
def ds_mobile_menu_toggle():
    """
    Create a mobile menu toggle button.
    
    Usage:
        {% ds_mobile_menu_toggle %}
    """
    toggle_html = '''
    <button type="button" class="ds-btn ds-btn-secondary ds-mobile-only" 
            onclick="toggleMobileMenu()" aria-label="Toggle navigation menu">
        <iconify-icon icon="heroicons:bars-3"></iconify-icon>
    </button>
    '''
    
    return mark_safe(toggle_html)


@register.filter
def add_ds_classes(field, css_classes=''):
    """
    Add design system classes to form fields.
    
    Usage:
        {{ form.email|add_ds_classes:"ds-form-input" }}
    """
    existing_classes = field.field.widget.attrs.get('class', '')
    new_classes = f"{existing_classes} {css_classes}".strip()
    field.field.widget.attrs['class'] = new_classes
    return field


@register.simple_tag
def ds_breadcrumb(items):
    """
    Create a breadcrumb navigation.
    
    Usage:
        {% ds_breadcrumb "Home,Invoices,Create,#" %}
    """
    if not items:
        return ''
    
    parts = items.split(',')
    breadcrumb_html = '<nav aria-label="Breadcrumb"><ol class="ds-breadcrumb">'
    
    for i, part in enumerate(parts):
        if i == len(parts) - 1:  # Last item (current page)
            breadcrumb_html += f'<li class="ds-breadcrumb-item active">{part}</li>'
        else:
            breadcrumb_html += f'<li class="ds-breadcrumb-item"><a href="#">{part}</a></li>'
    
    breadcrumb_html += '</ol></nav>'
    
    return mark_safe(breadcrumb_html)


@register.simple_tag
def ds_alert(message, type='info', dismissible=True):
    """
    Create an alert component.
    
    Usage:
        {% ds_alert "Success message" type="success" %}
    """
    dismiss_button = ''
    if dismissible:
        dismiss_button = '''
        <button type="button" class="ds-alert-close" onclick="this.parentElement.remove()">
            <iconify-icon icon="heroicons:x-mark"></iconify-icon>
        </button>
        '''
    
    alert_html = f'''
    <div class="ds-alert ds-alert-{type}" role="alert">
        {message}
        {dismiss_button}
    </div>
    '''
    
    return mark_safe(alert_html)


@register.simple_tag
def ds_card(title='', content='', footer='', extra_classes=''):
    """
    Create a card component.
    
    Usage:
        {% ds_card title="Invoice Details" content="..." %}
    """
    card_html = f'<div class="ds-card {extra_classes}">'
    
    if title:
        card_html += f'<div class="ds-card-header"><h3 class="ds-card-title">{title}</h3></div>'
    
    if content:
        card_html += f'<div class="ds-card-body">{content}</div>'
    
    if footer:
        card_html += f'<div class="ds-card-footer">{footer}</div>'
    
    card_html += '</div>'
    
    return mark_safe(card_html)


@register.simple_tag
def ds_progress_bar(value, max_value=100, label='', show_percentage=True):
    """
    Create a progress bar component.
    
    Usage:
        {% ds_progress_bar 75 label="Upload Progress" %}
    """
    percentage = (value / max_value) * 100 if max_value > 0 else 0
    
    progress_html = f'''
    <div class="ds-progress" role="progressbar" aria-valuenow="{value}" 
         aria-valuemin="0" aria-valuemax="{max_value}">
        {f'<div class="ds-progress-label">{label}</div>' if label else ''}
        <div class="ds-progress-bar">
            <div class="ds-progress-fill" style="width: {percentage}%"></div>
        </div>
        {f'<div class="ds-progress-text">{percentage:.0f}%</div>' if show_percentage else ''}
    </div>
    '''
    
    return mark_safe(progress_html)


@register.simple_tag
def ds_tooltip(content, text, position='top'):
    """
    Create a tooltip component.
    
    Usage:
        {% ds_tooltip "This is helpful information" "Hover me" %}
    """
    tooltip_html = f'''
    <span class="ds-tooltip ds-tooltip-{position}" data-tooltip="{content}">
        {text}
    </span>
    '''
    
    return mark_safe(tooltip_html)


@register.simple_tag(takes_context=True)
def ds_form_errors(context, form):
    """
    Display form errors in a consistent way.
    
    Usage:
        {% ds_form_errors form %}
    """
    if not form.errors:
        return ''
    
    errors_html = '<div class="ds-form-errors">'
    
    for field, errors in form.errors.items():
        field_label = form.fields.get(field, {}).get('label', field) if field != '__all__' else 'Form'
        
        for error in errors:
            errors_html += f'''
            <div class="ds-alert ds-alert-danger">
                <strong>{field_label}:</strong> {error}
            </div>
            '''
    
    errors_html += '</div>'
    
    return mark_safe(errors_html)


@register.simple_tag
def ds_loading_overlay(target_id, message='Ładowanie...'):
    """
    Create a loading overlay for specific elements.
    
    Usage:
        {% ds_loading_overlay "invoice-form" "Zapisywanie faktury..." %}
    """
    overlay_html = f'''
    <div id="{target_id}-loading" class="ds-loading-overlay" style="display: none;">
        <div class="ds-loading-spinner"></div>
        <div class="ds-loading-message">{message}</div>
    </div>
    '''
    
    return mark_safe(overlay_html)