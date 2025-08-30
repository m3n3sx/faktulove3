from django import template
from django.utils.safestring import mark_safe

register = template.Library()

@register.simple_tag
def ds_button(text, variant="primary", onclick="", **kwargs):
    css_class = f"btn btn-{variant}"
    if kwargs.get('class'):
        css_class += f" {kwargs['class']}"
    
    attrs = f'class="{css_class}"'
    if onclick:
        attrs += f' onclick="{onclick}"'
    
    return mark_safe(f'<button {attrs}>{text}</button>')

@register.simple_tag
def ds_theme_toggle():
    return mark_safe('<button class="theme-toggle btn btn-sm" onclick="toggleTheme()"><i class="ri-sun-line"></i></button>')

@register.simple_tag
def ds_accessibility_skip_links():
    return mark_safe('<a href="#main-content" class="skip-link">Przejdź do treści</a>')

@register.simple_tag
def ds_invoice_status_badge(status):
    status_map = {
        'draft': ('Projekt', 'badge-secondary'),
        'sent': ('Wysłana', 'badge-info'),
        'paid': ('Opłacona', 'badge-success'),
        'overdue': ('Przeterminowana', 'badge-danger'),
        'cancelled': ('Anulowana', 'badge-warning')
    }
    label, css_class = status_map.get(status, ('Nieznany', 'badge-secondary'))
    return mark_safe(f'<span class="badge {css_class}">{label}</span>')

@register.simple_tag
def ds_grid(cols=4, gap="md"):
    return mark_safe(f'<div class="grid grid-cols-{cols} gap-{gap}">')

@register.simple_tag
def ds_grid_end():
    return mark_safe('</div>')