"""Access information for a user."""

from typing import Annotated

from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse

from sqlmodel import Session

from jinet import auth
from jinet.db import database_session
from jinet.models import User
from jinet.templates import templates

router = APIRouter()


@router.get("/me", response_class=HTMLResponse)
async def user_me(
    request: Request,
    session: Annotated[Session, Depends(database_session)],
    user: Annotated[User, Depends(auth.current_user)],
):
    """Logged-in users data page."""
    return templates.TemplateResponse(
        request=request, name="me.html", context={"user": user}
    )
