from math import ceil

MAX_WORKERS = 6
USERS_PER_WORKER = 4
BASE_INTERVAL = 15

SPOTIFY_INTERVAL = 300
USERS_REFRESH_INTERVAL = 60


def calculate_workers(users_count: int) -> int:
    required = ceil(users_count / USERS_PER_WORKER)
    return min(required, MAX_WORKERS)


def calculate_poll_interval(users_count: int, workers_count: int) -> int:
    if workers_count == 0:
        return BASE_INTERVAL

    load_factor = users_count / (workers_count * USERS_PER_WORKER)
    return int(BASE_INTERVAL * max(1, load_factor))
