"""
Backup of the modular views structure - all functions imported from original file for compatibility
"""

# Import everything from original views for now to ensure compatibility
from .views_original import *

# Also import from new modular structure
try:
    from .views.import_export_views import *
    from .views.partnership_views import *
    from .views.recurring_views import *
    from .views.calendar_views import *
    from .views.notification_views import *
except ImportError as e:
    # If modular imports fail, continue with original views
    pass
