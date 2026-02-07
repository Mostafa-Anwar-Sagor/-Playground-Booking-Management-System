from django.shortcuts import render
from django.views.generic import TemplateView

# Create your views here.

class EarningsOverviewView(TemplateView):
    template_name = 'earnings/overview.html'

class PayoutRequestView(TemplateView):
    template_name = 'earnings/payout_request.html'

class ImprovementFundView(TemplateView):
    template_name = 'earnings/improvement_fund.html'

class PerformanceMetricsView(TemplateView):
    template_name = 'earnings/performance.html'
