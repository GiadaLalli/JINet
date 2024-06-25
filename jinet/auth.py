"""Authorisation / login."""

from typing import Annotated, Any, Callable
import json
import secrets

from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import HTMLResponse, RedirectResponse

from authlib.integrations.starlette_client import OAuth

from sqlmodel import select, Session

from jinet.config import settings
from jinet.db import database_session
from jinet.models import User, UserToken


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


async def user_in_context(request: Request, session: Session):
    """Place an authenticated user in a Jinja2 context."""

    try:
        user = await current_user(request, session)
        return {"user": user}
    except HTTPException:
        return {}


async def current_user(
    request: Request, session: Annotated[Session, Depends(database_session)]
) -> User:
    """Get the user based on the token. To be used with Depends()."""
    if (token := request.session.get("token", None)) is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized"
        )

    user = (
        await session.exec(select(User).join(UserToken).where(UserToken.token == token))
    ).one_or_none()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized"
        )

    return user


async def current_admin(
    request: Request, user: Annotated[User, Depends(current_user)]
) -> User:
    """Get the admin user based on the token."""
    if user.role == "admin":
        return user

    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized")


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
        await session.refresh(user)
        db_user = user

    token = UserToken(token=secrets.token_urlsafe(32), user_id=db_user.id)
    session.add(token)
    await session.commit()
    await session.refresh(token)

    request.session["token"] = token.token
    return RedirectResponse(request.url_for(request.session.get("from", "index")))


@router.get("/me")
async def me(request: Request):
    user = request.session.get("user", None)
    request.session["from"] = "/me"
    if user:
        return HTMLResponse(f"<pre>{json.dumps(user)}</pre>")
    return RedirectResponse(request.url_for("login"))
