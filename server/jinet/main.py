"""Main entry point."""

from fastapi import FastAPI, APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles

from jinet import packages
from jinet.templates import templates

app = FastAPI(title="JINet")
app.mount("/static", StaticFiles(directory="static"), name="static")

api_router = APIRouter()
api_router.include_router(packages.router, prefix="/packages")
app.include_router(api_router)


@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    """Home page."""
    return templates.TemplateResponse(request=request, name="index.html")


@app.get("/packages", response_class=HTMLResponse)
async def packages(
    request: Request,
):
    """List of packages."""
    return templates.TemplateResponse(request=request, name="packages.html")
