from math import ceil


MAX_WORKERS = 6
USERS_PER_WORKER = 4
BASE_INTERVAL = 15  # секунд


def calculate_workers(users_count: int) -> int:
    """
    Сколько воркеров нужно для данного числа пользователей
    """
    required = ceil(users_count / USERS_PER_WORKER)
    return min(required, MAX_WORKERS)


def calculate_poll_interval(users_count: int, workers_count: int) -> int:
    """
    Чем больше нагрузка — тем реже опрос
    """
    if workers_count == 0:
        return BASE_INTERVAL

    load_factor = users_count / (workers_count * USERS_PER_WORKER)
    return int(BASE_INTERVAL * max(1, load_factor))