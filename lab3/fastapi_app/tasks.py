import httpx
from celery_app import celery_app
from app.config import settings


@celery_app.task(bind=True, name="parse_url_task")
def parse_url_task(self, url: str):
    try:
        with httpx.Client(timeout=30) as client:
            response = client.post(
                f"{settings.PARSER_URL}/parse",
                json={"url": url},
            )
            response.raise_for_status()
            return response.json()
    except Exception as e:
        raise self.retry(exc=e, countdown=5, max_retries=3)