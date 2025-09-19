from .import views 
from django.urls import path
from .views import export_transactions
from django.views.generic.base import RedirectView

from finance.views import RegisterView,TransactionListView,TransactionCreateView,DashboardView,GoalCreateView
urlpatterns = [
    path('register/',RegisterView.as_view(),name='register'),
    path('',DashboardView.as_view(),name='dashboard'),
    path('transaction/add/',TransactionCreateView.as_view(),name='transaction_add'),
    path('transactions/',TransactionListView.as_view(),name='transaction_list'),
    path('goal/add/',GoalCreateView.as_view(),name='goal_add'),
path('generate-report/', export_transactions, name='export_transactions'),

   
]