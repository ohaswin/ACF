from django.urls import path
from . import views

app_name = "campaigns"

urlpatterns = [
    path('', views.create_campaign, name='create'),
    path('campaign/<int:campaign_id>/', views.dashboard, name='dashboard'),
    path('campaign/<int:campaign_id>/review/', views.review_campaign, name='review'),
    path('campaign/<int:campaign_id>/download/', views.download_campaign, name='download'),
    path('regenerate/<int:piece_id>/', views.regenerate_piece, name='regenerate'),
]
