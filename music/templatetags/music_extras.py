from django import template

register = template.Library()


@register.filter
def ms_to_time(ms):
    try:
        seconds = int(ms) // 1000
        minutes = seconds // 60
        seconds = seconds % 60
        return f"{minutes}:{seconds:02d}"
    except (TypeError, ValueError):
        return "0:00"
