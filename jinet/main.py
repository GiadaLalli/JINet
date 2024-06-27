"""Main entry point."""

from typing import Annotated, Optional

from fastapi import FastAPI, APIRouter, Depends, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles

from sqlmodel import select, Session, asc, desc

from starlette.exceptions import HTTPException as StarletteHTTPException
from starlette.middleware.sessions import SessionMiddleware

from Secweb.CrossOriginEmbedderPolicy import CrossOriginEmbedderPolicy
from Secweb.CrossOriginOpenerPolicy import CrossOriginOpenerPolicy
from Secweb.CrossOriginResourcePolicy import CrossOriginResourcePolicy
from Secweb.ContentSecurityPolicy import ContentSecurityPolicy

from jinet import auth, data, js, packages, requests, share
from jinet.config import settings
from jinet.db import database_session
from jinet.models import SampleData, User, PermissionRequest, Package
from jinet.templates import templates

app = FastAPI(title="JINet")
app.add_middleware(SessionMiddleware, secret_key=settings.secret_key)
app.add_middleware(
    ContentSecurityPolicy,
    Option={
        "default-src": ["'none'"],
        "script-src": [
            "'self'",
            "'unsafe-eval'",  # For Webassembly on Chromium
            "'unsafe-inline'",  # For Plotly.js (even the strict bundle)
            "https://cdn.jsdelivr.net",
            "https://unpkg.com",
            "https://webr.r-wasm.org",
        ],
        "style-src": [
            "'self'",
            "'unsafe-inline'",  # For Plotly.js (even the strict bundle)
            "https://cdn.jsdelivr.net",
        ],
        "img-src": [
            "'self'",
            "data: w3.org/svg/2000",
            "https://*.googleusercontent.com",
        ],
        "connect-src": [
            "'self'",
            "https://*.r-wasm.org",
            "https://cdn.jsdelivr.net",
            "https://pypi.org",
            "https://files.pythonhosted.org",
            "https://raw.githubusercontent.com",
        ],
        "child-src": ["'self'"],
        "worker-src": ["'self'", "blob:"],
    },
)
app.add_middleware(
    CrossOriginEmbedderPolicy, Option={"Cross-Origin-Embedder-Policy": "require-corp"}
)
app.add_middleware(
    CrossOriginOpenerPolicy, Option={"Cross-Origin-Opener-Policy": "same-origin"}
)
app.add_middleware(
    CrossOriginResourcePolicy, Option={"Cross-Origin-Resource-Policy": "same-origin"}
)
app.mount("/static", StaticFiles(directory="static"), name="static")

api_router = APIRouter()
api_router.include_router(auth.router)
api_router.include_router(packages.router, prefix="/packages")
api_router.include_router(data.router, prefix="/data")
api_router.include_router(requests.router, prefix="/requests")
api_router.include_router(js.router)
api_router.include_router(share.router)
app.include_router(api_router)


@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request, exception):
    return HTMLResponse(
        content=f"""<div class="uk-alert-danger" uk-alert>
          <p>{exception.detail}</p>
        </div>""",
        status_code=status.HTTP_200_OK,
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exception):
    return HTMLResponse(
        content=f"""<div class="uk-alert-danger" uk-alert>
          <p>{str(exception)}</p>
        </div>""",
        status_code=status.HTTP_200_OK,
    )


@app.get("/", response_class=HTMLResponse)
async def index(
    request: Request, session: Annotated[Session, Depends(database_session)]
):
    """Home page."""
    request.session["from"] = "index"
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context=await auth.user_in_context(request, session),
    )


@app.get("/packages", response_class=HTMLResponse)
async def packages(
    request: Request, session: Annotated[Session, Depends(database_session)]
):
    """List of packages."""
    request.session["from"] = "packages"
    return templates.TemplateResponse(
        request=request,
        name="packages.html",
        context=await auth.user_in_context(request, session),
    )


@app.get("/contribute", response_class=HTMLResponse)
async def contribute(
    request: Request, session: Annotated[Session, Depends(database_session)]
):
    """Documentation for createing a package."""
    request.session["from"] = "contribute"
    select
    return templates.TemplateResponse(
        request=request,
        name="contribute.html",
        context=await auth.user_in_context(request, session),
    )


@app.get("/data", response_class=HTMLResponse)
async def data(
    request: Request,
    since: Optional[int] = 0,
    session: Session = Depends(database_session),
):
    """Upload example data formats."""
    request.session["from"] = "data"
    query = (
        select(SampleData)
        .order_by(asc(SampleData.id))
        .where(SampleData.id >= since)
        .limit(10)
    )
    data = await session.exec(query)
    return templates.TemplateResponse(
        request=request,
        name="data.html",
        context=await auth.user_in_context(request, session) | {"data": data.all()},
    )


@app.get("/admin", response_class=HTMLResponse)
async def admin(
    request: Request,
    session: Annotated[Session, Depends(database_session)],
    admin: Annotated[User, Depends(auth.current_admin)],
):
    perm_requests = (await session.exec(select(PermissionRequest))).all()
    users = (await session.exec(select(User))).all()
    apps = (
        await session.exec(
            select(Package)
            .distinct(Package.name, Package.owner_id)
            .order_by(
                Package.name,
                Package.owner_id,
                desc(Package.version),
            )
        )
    ).all()
    sampledata = (await session.exec(select(SampleData))).all()

    return templates.TemplateResponse(
        request=request,
        name="admin.html",
        context={
            "user": admin,
            "requests": perm_requests,
            "users": users,
            "apps": apps,
            "sampledata": sampledata,
        },
    )
