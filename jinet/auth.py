"""Authorisation / login."""

from typing import Any, Callable
import json

from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import HTMLResponse, RedirectResponse

from authlib.integrations.starlette_client import OAuth

from sqlmodel import select, Session

from jinet.config import settings
from jinet.db import database_session
from jinet.models import User


router = APIRouter()
oauth = OAuth()
oauth.register(
    "auth0",
    client_id=settings.client_id,
    client_secret=settings.client_secret,
    client_kwargs={
        "scope": "openid profile",
    },
    server_metadata_url=f"https://{settings.auth0_domain}/.well-known/openid-configuration",
)


def unauthorized():
    """Return unauthorized to the user."""
    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")


def user_in_context(request: Request):
    """Place an authenticated user in a Jinja2 context."""

    def ok(user: dict) -> dict:
        return {"user": user}

    return user(request, ok=ok, err=dict)


def user(
    request: Request,
    ok: Callable[[dict], dict] = lambda x: x,
    err: Callable[[], Any] = unauthorized,
) -> dict:
    """Extract user session."""
    user = request.session.get("user", None)
    return ok(user) if user is not None else err()


@router.get("/login")
async def login(request: Request) -> RedirectResponse:
    redirect_uri = request.url_for("auth")
    return await oauth.auth0.authorize_redirect(request, redirect_uri)


@router.get("/callback")
async def auth(request: Request, session: Session = Depends(database_session)):
    token = await oauth.auth0.authorize_access_token(request)
    info = token["userinfo"]
    db_user = (
        await session.exec(select(User).where(User.sub == info["sub"]))
    ).one_or_none()
    role = "user"
    name = info.get("nickname", None)
    can_upload = False

    if db_user is None:
        # Create the user in the database
        user = User(
            username=info["nickname"],
            role="user",
            picture=info["picture"],
            sub=info["sub"],
        )
        session.add(user)
        await session.commit()
    else:
        role = db_user.role
        name = db_user.username
        can_upload = db_user.can_upload

    request.session["user"] = {
        "sub": info.get("sub", None),
        "sid": info.get("sid", None),
        "picture": info.get("picture", None),
        "role": role,
        "name": name,
        "can_upload": can_upload,
    }
    return RedirectResponse(request.url_for(request.session.get("from", "index")))


@router.get("/me")
async def me(request: Request):
    user = request.session.get("user", None)
    request.session["from"] = "/me"
    if user:
        return HTMLResponse(f"<pre>{json.dumps(user)}</pre>")
    return RedirectResponse(request.url_for("login"))
