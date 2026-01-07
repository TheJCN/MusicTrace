from datetime import timedelta

from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.db.models import Count
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from spotipy import SpotifyOAuth

from MusicTrace import settings
from integrations.yandex.api import YandexMusicAPI
from music.forms import YandexTokenForm
from music.models import UserMusicService, Track, UserTrackActivity
from music.services.lyrics_service import LyricsService
from music.services.yandex_service import save_yandex_current_track


def landing(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    return render(request, 'music/landing.html')


def register(request):
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')
    else:
        form = UserCreationForm()

    return render(
        request,
        'registration/register.html',
        {'form': form}
    )


@login_required
def yandex_connect(request):
    service = UserMusicService.objects.filter(
        user=request.user,
        service='yandex'
    ).first()

    if request.method == 'POST':
        form = YandexTokenForm(request.POST)
        if form.is_valid():
            UserMusicService.objects.update_or_create(
                user=request.user,
                service='yandex',
                defaults={
                    'access_token': form.cleaned_data['token']
                }
            )
            return redirect('dashboard')
    else:
        form = YandexTokenForm(
            initial={'token': service.access_token} if service else None
        )

    return render(
        request,
        'music/yandex/connect.html',
        {
            'form': form,
            'connected': bool(service),
        }
    )


@login_required
def spotify_connect(request):
    oauth = SpotifyOAuth(
        client_id=settings.SPOTIFY_CLIENT_ID,
        client_secret=settings.SPOTIFY_CLIENT_SECRET,
        redirect_uri=settings.SPOTIFY_REDIRECT_URI,
        scope="user-read-currently-playing user-read-playback-state",
        show_dialog=True,
    )

    auth_url = oauth.get_authorize_url()
    return redirect(auth_url)


@login_required
def spotify_callback(request):
    code = request.GET.get("code")
    if not code:
        return redirect("dashboard")

    oauth = SpotifyOAuth(
        client_id=settings.SPOTIFY_CLIENT_ID,
        client_secret=settings.SPOTIFY_CLIENT_SECRET,
        redirect_uri=settings.SPOTIFY_REDIRECT_URI,
        scope="user-read-currently-playing user-read-playback-state",
    )

    token_info = oauth.get_access_token(code)

    UserMusicService.objects.update_or_create(
        user=request.user,
        service="spotify",
        defaults={
            "access_token": token_info["access_token"],
            "refresh_token": token_info.get("refresh_token"),
            "expires_at": timezone.now() + timezone.timedelta(
                seconds=token_info["expires_in"]
            ),
        }
    )

    return redirect("dashboard")


@login_required
def track_lyrics(request, track_id):
    track = get_object_or_404(Track, id=track_id)

    service = LyricsService()
    lyrics = service.get_lyrics(track)

    if not lyrics:
        return render(
            request,
            "music/lyrics.html",
            {"error": "Текст не найден"}
        )

    return render(
        request,
        "music/lyrics.html",
        {"lyrics": lyrics}
    )


@login_required
def dashboard(request):
    yandex_connected = UserMusicService.objects.filter(user=request.user, service="yandex").exists()
    spotify_connected = UserMusicService.objects.filter(user=request.user, service="spotify").exists()

    return render(
        request,
        "music/dashboard.html",
        {
            "yandex_connected": yandex_connected,
            "spotify_connected": spotify_connected,
            "source": request.GET.get("source", "yandex" if yandex_connected else "spotify"),
        }
    )


@login_required
def api_now_playing(request):
    service = UserMusicService.objects.filter(user=request.user, service="yandex").first()
    if not service:
        return JsonResponse({"status": "error"})

    api = YandexMusicAPI(service.access_token)
    data = api.get_current_track()
    if not data:
        return JsonResponse({"status": "empty"})

    track = save_yandex_current_track(request.user, data)

    return JsonResponse({
        "status": "ok",
        "track": {
            "id": track.id,
            "title": track.title,
            "artist": track.artist,
            "cover": track.cover_url,
        }
    })


@login_required
def api_stats_summary(request):
    qs = UserTrackActivity.objects.filter(user=request.user)

    top_genre = (
        qs.exclude(track__genre__isnull=True)
          .exclude(track__genre="")
          .values("track__genre")
          .annotate(c=Count("track_id", distinct=True))
          .order_by("-c")
          .first()
    )

    top_artist = (
        qs.values("track__artist")
          .annotate(c=Count("track_id", distinct=True))
          .order_by("-c")
          .first()
    )

    total_tracks = qs.values("track_id").distinct().count() or 1

    return JsonResponse({
        "top_genre": {
            "name": top_genre["track__genre"] if top_genre else "—",
            "percent": int(top_genre["c"] / total_tracks * 100) if top_genre else 0,
        },
        "top_artist": {
            "name": top_artist["track__artist"] if top_artist else "—",
            "percent": int(top_artist["c"] / total_tracks * 100) if top_artist else 0,
        }
    })


@login_required
def api_stats_recent(request):
    qs = (
        UserTrackActivity.objects
        .filter(user=request.user)
        .select_related("track")
        .order_by("-played_at")[:20]
    )

    return JsonResponse({
        "tracks": [
            {
                "title": a.track.title,
                "artist": a.track.artist,
                "cover": a.track.cover_url,
            } for a in qs
        ]
    })


@login_required
def api_stats_activity(request):
    period = request.GET.get("period", "day")
    now = timezone.now()

    if period == "day":
        start = now - timedelta(hours=24)
        buckets = 24
        key = "hour"
    elif period == "week":
        start = now - timedelta(days=7)
        buckets = 7
        key = "day"
    else:  # month
        start = now - timedelta(days=30)
        buckets = 30
        key = "day"

    qs = (
        UserTrackActivity.objects
        .filter(user=request.user, played_at__gte=start)
        .values("track_id", "played_at")
    )

    data = [0] * buckets
    seen = [set() for _ in range(buckets)]

    for row in qs:
        dt = row["played_at"]
        idx = (
            dt.hour if key == "hour"
            else (now.date() - dt.date()).days
        )

        if 0 <= idx < buckets:
            seen[idx].add(row["track_id"])

    for i in range(buckets):
        data[i] = len(seen[i])

    return JsonResponse({
        "period": period,
        "data": data[::-1]
    })