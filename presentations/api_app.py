from fastapi import FastAPI, Path, Response, HTTPException, status, Request, Header
from fastapi.responses import RedirectResponse
from pydantic import BaseModel
from utils.strings import rand_str
from services.link_service import LinkService
import time
from typing import Callable, Awaitable
from loguru import logger
import requests



class LinkRequest(BaseModel):
    l_link: str


class LinkResponse(BaseModel):
    s_link: str

def create_app() -> FastAPI:
    app = FastAPI()

    links: dict[str, str] = {}

    @app.middleware("http")
    async def add_process_time_header(request: Request, call_next) -> Response:
        t0 = time.time()

        response = await call_next(request)
        elapsed_ms = round((time.time() - t0) * 1000, 2)
        response.headers["X-Process-Time"] = str(elapsed_ms)
        logger.debug("{} {} done in {}ms", request.method, request.url, elapsed_ms)

        return response

    link_service = LinkService()

    @app.post("/link")
    def create_link(payload: LinkRequest) -> LinkResponse:
        short_link = link_service.create_link(payload.l_link) # ??
        return LinkResponse(s_link=f'http://localhost:8000/{short_link}')

    @app.get("/{link}")
    def create_link(link: str) -> Response:
        l_link = link_service.get_link(link)

        if l_link is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="link not found")

        return Response(status_code=status.HTTP_301_MOVED_PERMANENTLY,
                        headers={"Location": l_link},)

    return app