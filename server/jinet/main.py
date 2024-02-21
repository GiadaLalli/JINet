"""Main entry point."""

from fastapi import FastAPI, APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles

from starlette.middleware.sessions import SessionMiddleware

from jinet import auth, packages
from jinet.config import settings
from jinet.templates import templates

app = FastAPI(title="JINet")
app.add_middleware(SessionMiddleware, secret_key=settings.secret_key)
app.mount("/static", StaticFiles(directory="static"), name="static")

api_router = APIRouter()
api_router.include_router(auth.router)
api_router.include_router(packages.router, prefix="/packages")
app.include_router(api_router)


@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    """Home page."""
    request.session["from"] = "/"
    return templates.TemplateResponse(
        request=request, name="index.html", context=auth.user_in_context(request)
    )


@app.get("/packages", response_class=HTMLResponse)
async def packages(
    request: Request,
):
    """List of packages."""
    request.session["from"] = "/packages"
    return templates.TemplateResponse(
        request=request, name="packages.html", context=auth.user_in_context(request)
    )
