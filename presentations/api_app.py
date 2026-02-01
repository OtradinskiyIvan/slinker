from fastapi import FastAPI, HTTPException, Response, status, Request
from pydantic import BaseModel
from requests import RequestException
from typing import List

from infrastructure.database import db_dependency
from infrastructure.models import Usage

from services.link_service import LinkService
import time
import requests
from loguru import logger


# TODO:
def create_app() -> FastAPI:
    app = FastAPI()

    class PutLink(BaseModel):
        link: str

    class LinkResponse(BaseModel):
        link: str

    class UsageOut(BaseModel):
        user_ip: str
        user_agent: str
        count: int

        class Config:
            from_attributes = True

    class PaginatedUsage(BaseModel):
        page: int
        size: int
        total: int
        items: List[UsageOut]


    def _service_link_to_real(short_link: str) -> str:
        return f"http://localhost:8000/{short_link}"

    @app.post("/link")
    def create_link(
            put_link_request: PutLink,
            db : db_dependency, request: Request
    ) -> LinkResponse:
        short_link_service = LinkService(db)

        inp_link = put_link_request.link
        url = inp_link if inp_link.startswith(('https://', 'http://')) else 'https://' + inp_link

        try:
            test_get = requests.get(url)
            is_valid = True if test_get.status_code < 400 else False

            if is_valid:
                short_link = short_link_service.create_link(real_link=url)
                return LinkResponse(link=_service_link_to_real(short_link))
            else:
                raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_CONTENT)
        except RequestException as e:
            logger.exception("connection via {} url failed. Error: {}", inp_link, e)
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_CONTENT)


    @app.middleware("http")
    async def add_process_time_header(request: Request, call_next) -> Response:
        t0 = time.time()

        response = await call_next(request)

        elapsed_ms = round((time.time() - t0) * 1000, 2)
        response.headers["X-Process-Time"] = str(elapsed_ms)
        logger.debug("{} {} done in {}ms", request.method, request.url, elapsed_ms)

        return response


    @app.get("/{link}")
    def get_link(link: str, request: Request, db: db_dependency) -> Response:
        short_link_service = LinkService(db)
        real_link = short_link_service.get_real_link(link)

        if real_link is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Short link not found:(")

        link_obj = short_link_service.get_link_by_short(link)
        if link_obj:
            user_ip = request.client.host if request.client else "unknown"
            user_agent = request.headers.get('user-agent', '')

            usage_count = short_link_service.get_link_usage_count(link_obj.id)
            short_link_service.log_usage(
                link_id=link_obj.id,
                user_ip=user_ip,
                user_agent=user_agent,
                usage_count=(usage_count + 1)
            )
            logger.info(f"Redirect: {link} -> {real_link} | IP: {user_ip}")

        return Response(status_code=status.HTTP_301_MOVED_PERMANENTLY, headers={"Location": real_link})

    from fastapi import Query

    @app.get("/{link}/statistics", response_model=PaginatedUsage)
    def get_stats(
            link: str,
            db: db_dependency,
            page: int = Query(1, ge=1),
            size: int = Query(20, ge=1, le=100)
    ):
        service = LinkService(db)

        link_obj = service.get_link_by_short(link)
        if not link_obj:
            raise HTTPException(status_code=404, detail="Link not found")

        offset = (page - 1) * size

        items = service.get_link_usage_paginated(
            link_id=link_obj.id,
            offset=offset,
            limit=size
        )

        total = service.get_link_usage_count(link_obj.id)

        return {
            "page": page,
            "size": size,
            "total": total,
            "items": items
        }

    return app
