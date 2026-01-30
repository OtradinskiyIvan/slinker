from idlelib.autocomplete import TRY_A

from fastapi import FastAPI, HTTPException, Response, status, Request
from pydantic import BaseModel
from requests import RequestException
from urllib3.exceptions import RequestError

from services.link_service import LinkService
import time
import requests
from loguru import logger


# TODO: link-str -> link-HttpUrl, IsValid(422 Exception)

def create_app() -> FastAPI:
    app = FastAPI()
    short_link_service = LinkService()

    class PutLink(BaseModel):
        link: str

    def _service_link_to_real(short_link: str) -> str:
        return f"http://localhost:8000/{short_link}"

    @app.post("/link")
    def create_link(put_link_request: PutLink) -> PutLink:
        inp_link = put_link_request.link
        url = inp_link if inp_link.startswith(('https://', 'http://')) else 'https://' + inp_link

        try:
            test_get = requests.get(url)
            is_valid = True if test_get.status_code < 400 else False

            if is_valid:
                short_link = short_link_service.create_link(url)
                return PutLink(link=_service_link_to_real(short_link))
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
    def get_link(link: str) -> Response:
        real_link = short_link_service.get_real_link(link)

        if real_link is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Short link not found:(")

        return Response(status_code=status.HTTP_301_MOVED_PERMANENTLY, headers={"Location": real_link})

    return app
