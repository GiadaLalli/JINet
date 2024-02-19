"""CRUD operations on packages."""

from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse

from sqlmodel import select, Session

from jinet.templates import templates
from jinet.db import database_session
from jinet.models import Package

router = APIRouter()


@router.get("/list", response_class=HTMLResponse)
async def listing(
    request: Request, since: int = 0, session: Session = Depends(database_session)
):
    """Retrieve a paginated listing of all packages."""
    query = select(Package).where(Package.id >= since).limit(10)
    results = await session.exec(query)
    return templates.TemplateResponse(
        request=request, name="package-list.html", context={"packages": results}
    )
