from datetime import timedelta

from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.db.models import Count
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from spotipy import SpotifyOAuth, SpotifyException

from MusicTrace import settings
from integrations.spotify.api import SpotifyMusicAPI
from integrations.spotify.utils import get_valid_spotify_token
from integrations.yandex.api import YandexMusicAPI
from music.forms import YandexTokenForm
from music.models import UserMusicService, Track, UserTrackActivity
from music.services.lyrics_service import LyricsService
from music.services.spotify_service import save_spotify_current_track
from music.services.yandex_service import save_yandex_current_track


def landing(request):
    if request.user.is_authenticated:
        return redirect("dashboard")
    return render(request, "music/landing.html")


def register(request):
    if request.user.is_authenticated:
        return redirect("dashboard")

    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("login")
    else:
        form = UserCreationForm()

    return render(request, "registration/register.html", {"form": form})


@login_required
def dashboard(request):
    return render(request, "music/dashboard.html")


@login_required
def yandex_connect(request):
    service = UserMusicService.objects.filter(
        user=request.user, service="yandex"
    ).first()

    if request.method == "POST":
        form = YandexTokenForm(request.POST)
        if form.is_valid():
            UserMusicService.objects.update_or_create(
                user=request.user,
                service="yandex",
                defaults={"access_token": form.cleaned_data["token"]},
            )
            return redirect("dashboard")
    else:
        form = YandexTokenForm(
            initial={"token": service.access_token} if service else None
        )

    return render(
        request,
        "music/yandex/connect.html",
        {"form": form, "connected": bool(service)},
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
    return redirect(oauth.get_authorize_url())


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
            "expires_at": timezone.now()
            + timezone.timedelta(seconds=token_info["expires_in"]),
        },
    )

    return redirect("dashboard")


@login_required
def api_user_services(request):
    services = list(
        UserMusicService.objects
        .filter(user=request.user)
        .values_list("service", flat=True)
    )

    default = None
    if "yandex" in services:
        default = "yandex"
    elif "spotify" in services:
        default = "spotify"

    return JsonResponse({
        "services": services,
        "default": default,
    })


@login_required
def api_now_playing(request):
    source = request.GET.get("source")

    if source not in ("yandex", "spotify"):
        return JsonResponse({"status": "error", "message": "Invalid source"})

    service = UserMusicService.objects.filter(
        user=request.user,
        service=source
    ).first()

    if not service:
        return JsonResponse({
            "status": "not_connected",
            "source": source
        })

    if source == "yandex":
        api = YandexMusicAPI(service.access_token)
        data = api.get_current_track()

        if not data:
            return JsonResponse({
                "status": "loading",
                "source": "yandex"
            })

        track = save_yandex_current_track(request.user, data)

        return JsonResponse({
            "status": "ok",
            "source": "yandex",
            "track": {
                "id": track.id,
                "title": track.title,
                "artist": track.artist,
                "cover": track.cover_url,
            },
        })

    if source == "spotify":
        try:
            access_token = get_valid_spotify_token(service)
            api = SpotifyMusicAPI(access_token)
            data = api.get_current_track()
        except SpotifyException:
            return JsonResponse({
                "status": "auth_error",
                "source": "spotify"
            })

        if data is None:
            return JsonResponse({
                "status": "empty",
                "source": "spotify"
            })

        if not data.get("is_playing"):
            return JsonResponse({
                "status": "paused",
                "source": "spotify"
            })

        track = save_spotify_current_track(request.user, data)

        return JsonResponse({
            "status": "ok",
            "source": "spotify",
            "track": {
                "id": track.id,
                "title": track.title,
                "artist": track.artist,
                "cover": track.cover_url,
            }
        })


@login_required
def api_stats_summary(request):
    source = request.GET.get("source")

    qs = UserTrackActivity.objects.filter(
        user=request.user,
        track__service=source
    )

    top_genre = (
        qs.exclude(track__genre="")
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

    total = qs.values("track_id").distinct().count() or 1

    return JsonResponse({
        "top_genre": {
            "name": top_genre["track__genre"] if top_genre else "—",
            "percent": int(top_genre["c"] / total * 100) if top_genre else 0,
        },
        "top_artist": {
            "name": top_artist["track__artist"] if top_artist else "—",
            "percent": int(top_artist["c"] / total * 100) if top_artist else 0,
        }
    })


@login_required
def api_stats_recent(request):
    source = request.GET.get("source")

    qs = (
        UserTrackActivity.objects
        .filter(user=request.user, track__service=source)
        .select_related("track")
        .order_by("-played_at")[:20]
    )

    return JsonResponse({
        "tracks": [{
            "title": a.track.title,
            "artist": a.track.artist,
            "cover": a.track.cover_url,
        } for a in qs]
    })


@login_required
def api_stats_activity(request):
    source = request.GET.get("source")
    period = request.GET.get("period", "day")
    now = timezone.localtime()

    if period == "day":
        data = [0] * 24
        start = now - timedelta(hours=24)

        qs = UserTrackActivity.objects.filter(
            user=request.user,
            track__service=source,
            played_at__gte=start
        )

        for a in qs:
            data[timezone.localtime(a.played_at).hour] += 1

        return JsonResponse({"data": data})

    if period == "week":
        data = [0] * 7
        start = now - timedelta(days=7)

        qs = UserTrackActivity.objects.filter(
            user=request.user,
            track__service=source,
            played_at__gte=start
        )

        for a in qs:
            data[timezone.localtime(a.played_at).weekday()] += 1

        return JsonResponse({"data": data})

    if period == "month":
        data = [0] * 12
        start = now - timedelta(days=365)

        qs = UserTrackActivity.objects.filter(
            user=request.user,
            track__service=source,
            played_at__gte=start
        )

        for a in qs:
            data[timezone.localtime(a.played_at).month - 1] += 1

        return JsonResponse({"data": data})


@login_required
def track_lyrics(request, track_id):
    track = get_object_or_404(Track, id=track_id)
    lyrics = LyricsService().get_lyrics(track)

    if not lyrics:
        return render(request, "music/lyrics.html", {"error": "Текст не найден"})

    return render(
        request,
        "music/lyrics.html",
        {"lyrics": lyrics, "track": track},
    )
