uv run celery -A config worker -l info &
uv run python manage.py runserver