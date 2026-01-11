import time
import psycopg
from django.conf import settings

while True:
    try:
        with psycopg.connect(settings.DATABASES["default"]["NAME"],
                              user=settings.DATABASES["default"]["USER"],
                              password=settings.DATABASES["default"]["PASSWORD"],
                              host=settings.DATABASES["default"]["HOST"],
                              port=settings.DATABASES["default"]["PORT"]) as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT 1 FROM auth_user LIMIT 1;")
        break
    except Exception:
        print("Waiting for migrations...")
        time.sleep(2)
