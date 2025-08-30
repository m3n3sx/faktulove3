"""
Custom Django admin widgets with design system integration
"""

from django import forms
from django.utils.safestring import mark_safe
from django.utils.html import format_html
from decimal import Decimal
import re


class DesignSystemWidget(forms.Widget):
    """Base widget with design system styling"""
    
    def __init__(self, attrs=None, **kwargs):
        default_attrs = {
            'class': 'django-design-system-widget'
        }
        if attrs:
            default_attrs.update(attrs)
        super().__init__(default_attrs, **kwargs)


class NIPWidget(DesignSystemWidget, forms.TextInput):
    """Widget for Polish NIP number input with validation"""
    
    def __init__(self, attrs=None):
        default_attrs = {
            'class': 'nip-input django-polish-business',
            'placeholder': '123-456-78-90',
            'pattern': r'\d{3}-\d{3}-\d{2}-\d{2}',
            'maxlength': '13'
        }
        if attrs:
            default_attrs.update(attrs)
        super().__init__(default_attrs)
    
    def render(self, name, value, attrs=None, renderer=None):
        if value:
            # Format NIP with dashes
            clean_nip = re.sub(r'\D', '', str(value))
            if len(clean_nip) == 10:
                value = f"{clean_nip[:3]}-{clean_nip[3:6]}-{clean_nip[6:8]}-{clean_nip[8:10]}"
        
        html = super().render(name, value, attrs, renderer)
        
        # Add validation script
        validation_script = format_html('''
            <script>
                document.addEventListener('DOMContentLoaded', function() {{
                    const nipInput = document.getElementById('id_{name}');
                    if (nipInput) {{
                        function validateNIP(nip) {{
                            const cleanNip = nip.replace(/\\D/g, '');
                            if (cleanNip.length !== 10) return false;
                            
                            const weights = [6, 5, 7, 2, 3, 4, 5, 6, 7];
                            let sum = 0;
                            for (let i = 0; i < 9; i++) {{
                                sum += parseInt(cleanNip[i]) * weights[i];
                            }}
                            const checksum = sum % 11;
                            return checksum === parseInt(cleanNip[9]);
                        }}
                        
                        function formatNIP(nip) {{
                            const cleanNip = nip.replace(/\\D/g, '');
                            if (cleanNip.length === 10) {{
                                return cleanNip.slice(0, 3) + '-' + cleanNip.slice(3, 6) + '-' + 
                                       cleanNip.slice(6, 8) + '-' + cleanNip.slice(8, 10);
                            }}
                            return nip;
                        }}
                        
                        nipInput.addEventListener('blur', function() {{
                            const value = this.value.trim();
                            if (value) {{
                                const isValid = validateNIP(value);
                                this.style.borderColor = isValid ? 'var(--color-status-success)' : 'var(--color-status-error)';
                                this.value = formatNIP(value);
                            }}
                        }});
                        
                        nipInput.addEventListener('input', function() {{
                            this.style.borderColor = 'var(--color-border-default)';
                        }});
                    }}
                }});
            </script>
        ''', name=name)
        
        return mark_safe(html + validation_script)


class CurrencyWidget(DesignSystemWidget, forms.NumberInput):
    """Widget for Polish currency input"""
    
    def __init__(self, currency='PLN', attrs=None):
        self.currency = currency
        default_attrs = {
            'class': 'currency-input django-polish-business',
            'step': '0.01',
            'min': '0'
        }
        if attrs:
            default_attrs.update(attrs)
        super().__init__(default_attrs)
    
    def render(self, name, value, attrs=None, renderer=None):
        input_html = super().render(name, value, attrs, renderer)
        
        wrapper_html = format_html('''
            <div class="currency-input-wrapper">
                {input}
                <span class="currency-symbol">{currency}</span>
            </div>
            <style>
                .currency-input-wrapper {{
                    display: flex;
                    align-items: stretch;
                }}
                .currency-input-wrapper .currency-input {{
                    border-top-right-radius: 0 !important;
                    border-bottom-right-radius: 0 !important;
                    border-right: none !important;
                    text-align: right !important;
                    font-family: var(--typography-currency-family) !important;
                    font-size: var(--typography-currency-size) !important;
                    font-weight: var(--typography-currency-weight) !important;
                }}
                .currency-input-wrapper .currency-symbol {{
                    background: var(--color-background-secondary);
                    border: 1px solid var(--color-border-default);
                    border-left: none;
                    border-top-left-radius: 0;
                    border-bottom-left-radius: 0;
                    border-top-right-radius: var(--border-radius-md);
                    border-bottom-right-radius: var(--border-radius-md);
                    padding: var(--spacing-2) var(--spacing-3);
                    color: var(--color-text-secondary);
                    font-size: var(--font-size-base);
                    display: flex;
                    align-items: center;
                }}
                .currency-input-wrapper .currency-input:focus + .currency-symbol {{
                    border-color: var(--color-interactive);
                }}
            </style>
        ''', input=input_html, currency=self.currency)
        
        return mark_safe(wrapper_html)


class VATRateWidget(DesignSystemWidget, forms.Select):
    """Widget for Polish VAT rate selection"""
    
    def __init__(self, attrs=None):
        default_attrs = {
            'class': 'vat-rate-select django-polish-business'
        }
        if attrs:
            default_attrs.update(attrs)
        super().__init__(default_attrs)
        
        # Set default choices for Polish VAT rates
        self.choices = [
            ('', '---------'),
            (0, '0%'),
            (0.05, '5%'),
            (0.08, '8%'),
            (0.23, '23%'),
            (-1, 'zw. (zwolniony)'),
        ]
    
    def render(self, name, value, attrs=None, renderer=None):
        html = super().render(name, value, attrs, renderer)
        
        # Add styling
        style = '''
            <style>
                .vat-rate-select {
                    background-image: url("data:image/svg+xml,%3csvg xmlns='http://www.w3.org/2000/svg' fill='none' viewBox='0 0 20 20'%3e%3cpath stroke='%236b7280' stroke-linecap='round' stroke-linejoin='round' stroke-width='1.5' d='m6 8 4 4 4-4'/%3e%3c/svg%3e");
                    background-position: right var(--spacing-2) center;
                    background-repeat: no-repeat;
                    background-size: 1.5em 1.5em;
                    padding-right: var(--spacing-8) !important;
                }
            </style>
        '''
        
        return mark_safe(html + style)


class PolishDateWidget(DesignSystemWidget, forms.DateInput):
    """Widget for Polish date input"""
    
    def __init__(self, attrs=None):
        default_attrs = {
            'class': 'date-input django-polish-business',
            'placeholder': 'DD.MM.YYYY'
        }
        if attrs:
            default_attrs.update(attrs)
        super().__init__(default_attrs, format='%d.%m.%Y')
    
    def render(self, name, value, attrs=None, renderer=None):
        html = super().render(name, value, attrs, renderer)
        
        # Add date formatting script
        script = format_html('''
            <script>
                document.addEventListener('DOMContentLoaded', function() {{
                    const dateInput = document.getElementById('id_{name}');
                    if (dateInput) {{
                        dateInput.addEventListener('blur', function() {{
                            const value = this.value.trim();
                            if (value) {{
                                const dateRegex = /^(\\d{{1,2}})[.\\-\\/](\\d{{1,2}})[.\\-\\/](\\d{{4}})$/;
                                const match = value.match(dateRegex);
                                
                                if (match) {{
                                    const day = match[1].padStart(2, '0');
                                    const month = match[2].padStart(2, '0');
                                    const year = match[3];
                                    
                                    const date = new Date(year, month - 1, day);
                                    if (date.getFullYear() == year && 
                                        date.getMonth() == month - 1 && 
                                        date.getDate() == day) {{
                                        this.value = day + '.' + month + '.' + year;
                                        this.style.borderColor = 'var(--color-status-success)';
                                    }} else {{
                                        this.style.borderColor = 'var(--color-status-error)';
                                    }}
                                }}
                            }}
                        }});
                        
                        dateInput.addEventListener('input', function() {{
                            this.style.borderColor = 'var(--color-border-default)';
                        }});
                    }}
                }});
            </script>
            <style>
                .date-input {{
                    font-family: var(--typography-date-family) !important;
                    font-size: var(--typography-date-size) !important;
                }}
            </style>
        ''', name=name)
        
        return mark_safe(html + script)


class InvoiceStatusWidget(DesignSystemWidget, forms.Select):
    """Widget for invoice status selection with visual indicators"""
    
    def __init__(self, attrs=None):
        default_attrs = {
            'class': 'invoice-status-select django-polish-business'
        }
        if attrs:
            default_attrs.update(attrs)
        super().__init__(default_attrs)
        
        # Set default choices for invoice statuses
        self.choices = [
            ('', '---------'),
            ('draft', 'Szkic'),
            ('sent', 'Wysłana'),
            ('paid', 'Opłacona'),
            ('overdue', 'Przeterminowana'),
            ('cancelled', 'Anulowana'),
        ]
    
    def render(self, name, value, attrs=None, renderer=None):
        html = super().render(name, value, attrs, renderer)
        
        # Add status-specific styling
        script = format_html('''
            <script>
                document.addEventListener('DOMContentLoaded', function() {{
                    const statusSelect = document.getElementById('id_{name}');
                    if (statusSelect) {{
                        function updateStatusColor() {{
                            const value = statusSelect.value;
                            statusSelect.className = statusSelect.className.replace(/status-\\w+/g, '');
                            if (value) {{
                                statusSelect.classList.add('status-' + value);
                            }}
                        }}
                        
                        statusSelect.addEventListener('change', updateStatusColor);
                        updateStatusColor(); // Initial call
                    }}
                }});
            </script>
            <style>
                .invoice-status-select.status-draft {{
                    border-left: 4px solid var(--color-invoice-draft);
                }}
                .invoice-status-select.status-sent {{
                    border-left: 4px solid var(--color-invoice-sent);
                }}
                .invoice-status-select.status-paid {{
                    border-left: 4px solid var(--color-invoice-paid);
                }}
                .invoice-status-select.status-overdue {{
                    border-left: 4px solid var(--color-invoice-overdue);
                }}
                .invoice-status-select.status-cancelled {{
                    border-left: 4px solid var(--color-invoice-cancelled);
                }}
            </style>
        ''', name=name)
        
        return mark_safe(html + script)


class CompanySelectWidget(DesignSystemWidget, forms.Select):
    """Widget for company selection with enhanced display"""
    
    def __init__(self, attrs=None, **kwargs):
        default_attrs = {
            'class': 'django-design-system-widget'
        }
        if attrs:
            default_attrs.update(attrs)
        super().__init__(default_attrs, **kwargs)
    
    def render(self, name, value, attrs=None, renderer=None):
        html = super().render(name, value, attrs, renderer)
        
        style = '''
            <style>
                .company-select {
                    font-family: var(--typography-company-name-family) !important;
                    font-size: var(--typography-company-name-size) !important;
                    font-weight: var(--typography-company-name-weight) !important;
                }
            </style>
        '''
        
        return mark_safe(html + style)