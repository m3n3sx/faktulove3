from django.http import JsonResponse
from django.contrib.admin.views.decorators import staff_member_required
from django.utils.decorators import method_decorator
from django.views import View

@method_decorator(staff_member_required, name='dispatch')
class DashboardStatsView(View):
    def get(self, request):
        return JsonResponse({
            'total_invoices': 0,
            'total_companies': 0,
            'monthly_revenue': 0,
            'pending_invoices': 0
        })

@method_decorator(staff_member_required, name='dispatch')
class SystemHealthView(View):
    def get(self, request):
        return JsonResponse({
            'status': 'healthy',
            'database': 'ok',
            'storage': 'ok',
            'memory_usage': '45%'
        })

@method_decorator(staff_member_required, name='dispatch')
class RecentActivityView(View):
    def get(self, request):
        return JsonResponse({
            'activities': [
                {'action': 'Utworzono fakturę', 'time': '2 min temu'},
                {'action': 'Dodano kontrahenta', 'time': '5 min temu'}
            ]
        })