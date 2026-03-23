"""
Точка входа для Celery worker
Запуск: celery -A app.infra.celery_app worker --loglevel=info
"""

from app.infra.celery_app import celery_app

if __name__ == "__main__":
    celery_app.start()