"""Main entry point."""

from fastapi import FastAPI, APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from jinet import analyses

app = FastAPI(title="JINet")
app.mount("/static", StaticFiles(directory="static"), name="static")

api_router = APIRouter()
api_router.include_router(analyses.router, prefix="/analyses")

templates = Jinja2Templates(directory="templates")


@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    """Home page."""
    return templates.TemplateResponse(request=request, name="index.html")
