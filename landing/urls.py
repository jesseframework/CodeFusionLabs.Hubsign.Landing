from django.urls import path
from . import views

app_name = 'landing'

urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),
    path('pricing/', views.PricingView.as_view(), name='pricing'),
    path('features/', views.FeaturesView.as_view(), name='features'),
]
