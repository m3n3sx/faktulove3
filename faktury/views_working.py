"""
Working views module - combines original views with new modular components
"""

# Import everything from original views first to ensure all functions are available
from .views_original import *

# Then add new modular components (these will override any existing functions)
try:
    # Import/Export views
    from .views.import_export_views import *
    
    # Partnership views  
    from .views.partnership_views import *
    
    # Recurring invoice views
    from .views.recurring_views import *
    
    # Calendar views
    from .views.calendar_views import *
    
    # Enhanced notification views (may override some from original)
    from .views.notification_views import *
    
except ImportError as e:
    # If any modular imports fail, continue with original views
    import logging
    logging.warning(f"Could not import modular views: {e}")
    pass
