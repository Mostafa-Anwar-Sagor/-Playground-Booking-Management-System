from django.urls import path
from . import views

app_name = 'earnings'

urlpatterns = [
    path('', views.EarningsOverviewView.as_view(), name='earnings_overview'),
    path('payout-request/', views.PayoutRequestView.as_view(), name='payout_request'),
    path('improvement-fund/', views.ImprovementFundView.as_view(), name='improvement_fund'),
    path('performance/', views.PerformanceMetricsView.as_view(), name='performance_metrics'),
]
