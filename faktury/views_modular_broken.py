"""
Main views module for faktury application

This file imports all views from modular structure to maintain 
backward compatibility with existing URL configurations.

The views are organized in the following modules:
- auth_views.py - Authentication and user management
- dashboard_views.py - Dashboard and reporting
- company_views.py - Company management
- contractor_views.py - Contractor management
- product_views.py - Product management
- invoice_views.py - Invoice management
- team_views.py - Team and task management
- notification_views.py - Notifications
- api_views.py - API endpoints
"""

# Import all views from modular structure
from faktury.views.auth_views import *
from faktury.views.dashboard_views import *
from faktury.views.company_views import *
from faktury.views.contractor_views import *
from faktury.views.api_views import *

# Import remaining modules as they are created
from faktury.views.product_views import *
from faktury.views.invoice_views import *
from faktury.views.team_views import *
from faktury.views.notification_views import *
from faktury.views.partnership_views import *
from faktury.views.recurring_views import *
from faktury.views.calendar_views import *

# Import remaining modules
from faktury.views.import_export_views import *

# Temporarily import remaining views from original file
# from faktury.views_original import (
#     # These are now handled by import_export_views
# )
