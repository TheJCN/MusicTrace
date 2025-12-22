from django.db.models import Count
from django.shortcuts import render
from .models import Track, UserTrackActivity


def track_list(request):
    tracks = Track.objects.all()
    return render(request, 'music/track_list.html', {
        'tracks': tracks
    })

def top_tracks(request):
    stats = (
        UserTrackActivity.objects
        .values('track__title')
        .annotate(total=Count('id'))
        .order_by('-total')
    )

    return render(request, 'music/top_tracks.html', {
        'stats': stats
    })