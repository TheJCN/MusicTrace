from django.urls import path
from .views import track_list, top_tracks

urlpatterns = [
    path('tracks/', track_list, name='track_list'),
    path('stats/top-tracks/', top_tracks),
]
