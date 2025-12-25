from socket import socket

from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.http import HttpResponse

from .forms import YandexTokenForm
from .models import UserMusicService
from integrations.yandex_music import YandexMusicAPI
from music.services.storage import save_track_and_activity


@login_required
def connect_yandex(request):
    if request.method == "POST":
        form = YandexTokenForm(request.POST)
        if form.is_valid():
            UserMusicService.objects.update_or_create(
                user=request.user,
                service="yandex",
                defaults={"access_token": form.cleaned_data["token"]}
            )
            return redirect("yandex_now_playing")
    else:
        form = YandexTokenForm()

    return render(request, "music/connect_yandex.html", {"form": form})


@login_required
def yandex_now_playing(request):
    try:
        service = UserMusicService.objects.get(
            user=request.user,
            service="yandex"
        )
    except UserMusicService.DoesNotExist:
        return redirect("connect_yandex")

    api = YandexMusicAPI(service.access_token)
    track = api.get_current_track()

    if not track:
        return HttpResponse("No track playing")

    db_track = save_track_and_activity(request.user, track)


    print("Now playing track:", db_track.title)
    return render(
        request,
        "music/now_playing.html",
        {"track": db_track}
    )
