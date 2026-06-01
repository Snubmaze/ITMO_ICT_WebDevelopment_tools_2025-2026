import httpx
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.config import settings
from tasks import parse_url_task


router = APIRouter(prefix="/parse", tags=["parser"])


class ParseRequest(BaseModel):
    url: str


@router.post("")
async def parse_sync(request: ParseRequest):
    """Подзадача 2: синхронный вызов parser-сервиса."""
    try:
        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.post(
                f"{settings.PARSER_URL}/parse",
                json={"url": request.url},
            )
            response.raise_for_status()
            return response.json()
    except httpx.RequestError as e:
        raise HTTPException(status_code=502, detail=f"Parser service unavailable: {e}")
    except httpx.HTTPStatusError as e:
        raise HTTPException(status_code=e.response.status_code, detail=e.response.text)


@router.post("/async")
def parse_async(request: ParseRequest):
    task = parse_url_task.delay(request.url)
    return {"task_id": task.id, "status": "queued"}


@router.get("/status/{task_id}")
def parse_status(task_id: str):
    task = parse_url_task.AsyncResult(task_id)
    if task.state == "PENDING":
        return {"task_id": task_id, "status": "pending"}
    if task.state == "FAILURE":
        return {"task_id": task_id, "status": "failure", "error": str(task.result)}
    return {"task_id": task_id, "status": task.state.lower(), "result": task.result}