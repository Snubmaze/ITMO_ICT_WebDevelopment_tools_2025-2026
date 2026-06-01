from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from parser import parse_url


app = FastAPI(title="Parser App")


class ParseRequest(BaseModel):
    url: str


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/parse")
async def parse(request: ParseRequest) -> dict:
    try:
        results = await parse_url(request.url)
        return {
            "url": request.url,
            "count": len(results),
            "results": results
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))