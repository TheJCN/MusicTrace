from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import render, redirect

from integrations.yandex.api import YandexMusicAPI
from music.forms import YandexTokenForm
from music.models import UserMusicService
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
def dashboard(request):
    yandex_connected = UserMusicService.objects.filter(
        user=request.user,
        service='yandex'
    ).exists()

    spotify_connected = UserMusicService.objects.filter(
        user=request.user,
        service='spotify'
    ).exists()

    return render(
        request,
        'music/dashboard.html',
        {
            'yandex_connected': yandex_connected,
            'spotify_connected': spotify_connected,
        }
    )


@login_required
def yandex_connect(request):
    # Проверяем, подключён ли уже Яндекс
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
def yandex_current(request):
    service = UserMusicService.objects.filter(
        user=request.user,
        service='yandex'
    ).first()

    if not service:
        return redirect('yandex_connect')

    api = YandexMusicAPI(service.access_token)
    yandex_track = api.get_current_track()

    if not yandex_track:
        return render(
            request,
            'music/yandex/current.html',
            {'error': 'Сейчас ничего не воспроизводится'}
        )

    track = save_yandex_current_track(request.user, yandex_track)

    return render(
        request,
        'music/yandex/current.html',
        {'track': track}
    )



@login_required
def spotify_connect(request):
    return render(request, 'music/spotify/connect.html')


@login_required
def spotify_current(request):
    return render(request, 'music/spotify/current.html')
