# Complete views module - original functions + new features
from .views_original import *

# Add new functionality - these will extend existing functions
try:
    from .views.import_export_views import *
    from .views.partnership_views import *
    from .views.recurring_views import *
    from .views.calendar_views import *
except ImportError:
    pass  # Continue if modular views not available
