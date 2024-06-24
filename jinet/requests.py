"""Permission requests."""

from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse

from sqlmodel import select, Session

from jinet import auth
from jinet.db import database_session
from jinet.models import PermissionRequest, User

router = APIRouter()


@router.get("/upload", response_class=HTMLResponse)
async def upload(
    request: Request,
    session: Session = Depends(database_session),
):
    userdata = auth.user(request)

    user = (
        await session.exec(select(User).where(User.sub == userdata.get("sub")))
    ).first()

    perm_request = PermissionRequest(
        permission="upload",
        user_id=user.id,
    )
    session.add(perm_request)
    await session.commit()

    return f"""<div class="uk-alert-success" uk-alert><p>Successfully requested upload permission</p></div>"""
