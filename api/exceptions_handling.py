from typing import Callable, NoReturn

from litestar import Request
from litestar.datastructures import URL
from litestar.plugins.problem_details import ProblemDetailsException
from litestar.status_codes import HTTP_400_BAD_REQUEST
from sqlalchemy.exc import IntegrityError

from logic.exceptions import AssetNotFoundError, BaseLedgerApiException


def _url_from_request(request: Request) -> URL:
    return URL.from_components(
                    'https',
                    request.url.netloc,
                    request.url.path,
                    request.url.fragment,
                    request.url.query,
                )

def _make_error_description_url(url: URL, error_html: str) -> str:
    return f"https://{url.netloc}/error-descriptions/{error_html}"

def integrity_error_handler_factory(
        title: str,
        detail: str,
        pg_error_code: str,
        error_html: str,
) -> Callable[[Request, IntegrityError], NoReturn]:
    def _handler(request: Request, exc: IntegrityError) -> NoReturn:
            if exc.orig is not None and exc.orig.pgcode == pg_error_code:
                url = _url_from_request(request)
                raise ProblemDetailsException(
                    type_=_make_error_description_url(url, error_html),
                    title=title,
                    detail=detail,
                    instance=str(url),
                    extra={},
                    status_code=HTTP_400_BAD_REQUEST,
                )
            else:
                raise exc
    return _handler


def base_error_handler_factory(
        title: str,
        detail: str,
        error_html: str,
) -> Callable[[Request, BaseLedgerApiException], NoReturn]:
    def _handler(request: Request, exc: BaseLedgerApiException) -> NoReturn:
            url = _url_from_request(request)
            raise ProblemDetailsException(
                    type_=_make_error_description_url(url, error_html),
                    title=title,
                    detail=detail,
                    instance=str(url),
                    extra=exc.extra,
                    status_code=HTTP_400_BAD_REQUEST,
                )

    return _handler
