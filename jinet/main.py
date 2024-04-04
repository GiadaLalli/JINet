"""Main entry point."""

from typing import Optional

from fastapi import FastAPI, APIRouter, Depends, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles

from sqlmodel import select, Session, asc

from starlette.middleware.sessions import SessionMiddleware
from Secweb.CrossOriginEmbedderPolicy import CrossOriginEmbedderPolicy
from Secweb.CrossOriginOpenerPolicy import CrossOriginOpenerPolicy

from jinet import auth, data, js, packages
from jinet.config import settings
from jinet.db import database_session
from jinet.models import SampleData
from jinet.templates import templates

app = FastAPI(title="JINet")
app.add_middleware(SessionMiddleware, secret_key=settings.secret_key)
app.add_middleware(
    CrossOriginEmbedderPolicy, Option={"Cross-Origin-Embedder-Policy": "credentialless"}
)
app.add_middleware(
    CrossOriginOpenerPolicy, Option={"Cross-Origin-Opener-Policy": "same-origin"}
)
app.mount("/static", StaticFiles(directory="static"), name="static")

api_router = APIRouter()
api_router.include_router(auth.router)
api_router.include_router(packages.router, prefix="/packages")
api_router.include_router(data.router, prefix="/data")
api_router.include_router(js.router)
app.include_router(api_router)


@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    """Home page."""
    request.session["from"] = "index"
    return templates.TemplateResponse(
        request=request, name="index.html", context=auth.user_in_context(request)
    )


@app.get("/packages", response_class=HTMLResponse)
async def packages(request: Request):
    """List of packages."""
    request.session["from"] = "packages"
    return templates.TemplateResponse(
        request=request,
        name="packages.html",
        context=auth.user_in_context(request),
    )


@app.get("/contribute", response_class=HTMLResponse)
async def contribute(request: Request):
    """Documentation for createing a package."""
    request.session["from"] = "contribute"
    return templates.TemplateResponse(
        request=request,
        name="contribute.html",
        context=auth.user_in_context(request),
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
        context=auth.user_in_context(request) | {"data": data.all()},
    )
