"""Access information for a user."""

from typing import Annotated

from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse

from sqlmodel import Session, select, desc

from jinet import auth
from jinet.db import database_session
from jinet.models import User, Package
from jinet.templates import templates

router = APIRouter()


@router.get("/me", response_class=HTMLResponse)
async def user_me(
    request: Request,
    session: Annotated[Session, Depends(database_session)],
    user: Annotated[User, Depends(auth.current_user)],
):
    """Logged-in users data page."""
    apps = (
        await session.exec(
            select(Package)
            .where(Package.owner_id == user.id)
            .distinct(Package.name)
            .order_by(Package.name, desc(Package.version))
        )
    ).all()
    return templates.TemplateResponse(
        request=request, name="me.html", context={"user": user, "apps": apps}
    )
