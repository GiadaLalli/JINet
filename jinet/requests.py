"""Permission requests."""

from typing import Annotated

from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse, PlainTextResponse

from sqlmodel import select, Session

from jinet import auth
from jinet.db import database_session
from jinet.models import PermissionRequest, User

router = APIRouter()


@router.get("/upload", response_class=HTMLResponse)
async def upload(
    request: Request,
    session: Annotated[Session, Depends(database_session)],
    user: Annotated[User, Depends(auth.current_user)],
):
    perm_request = PermissionRequest(
        permission="upload",
        user_id=user.id,
    )
    session.add(perm_request)
    await session.commit()

    return f"""<div class="uk-alert-success" uk-alert><p>Successfully requested upload permission.</p></div>"""


@router.post("/grant/{user_id}", response_class=PlainTextResponse)
async def grant(
    request: Request,
    session: Annotated[Session, Depends(database_session)],
    admin: Annotated[User, Depends(auth.current_admin)],
    user_id: int,
):
    # Remove the permission request
    perm_request = (
        await session.exec(
            select(PermissionRequest).where(PermissionRequest.user_id == user_id)
        )
    ).one_or_none()
    if perm_request is None:
        return "ERROR: No permission request"

    session.delete(perm_request)

    # Make user an uploader
    user = (await session.exec(select(User).where(User.id == user_id))).one_or_none()
    if user is None:
        return "Error: No user"

    user.can_upload = True
    session.add(user)

    await session.commit()
    return "granted"


@router.post("/deny/{user_id}", response_class=PlainTextResponse)
async def deny(
    request: Request,
    session: Annotated[Session, Depends(database_session)],
    admin: Annotated[User, Depends(auth.current_admin)],
    user_id: int,
):
    # Change the permission request to denied
    perm_request = (
        await session.exec(
            select(PermissionRequest).where(PermissionRequest.user_id == user_id)
        )
    ).one_or_none()

    if perm_request is None:
        return "ERROR: No permission request"

    perm_request.status = "denied"
    session.add(perm_request)
    await session.commit()

    return "denied"
