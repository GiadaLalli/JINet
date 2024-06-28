"""Authorisation / login."""

from typing import Annotated, Any, Callable
import json
import secrets

from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import HTMLResponse, RedirectResponse

from authlib.integrations.starlette_client import OAuth

from sqlmodel import delete, select, Session

from jinet.config import settings
from jinet.db import database_session
from jinet.models import User, UserToken


class RequiresLoginException(Exception):
    """Thrown when an endpoint requires login but the user is not authenticated."""

    pass


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
    except RequiresLoginException:
        return {}


async def current_user(
    request: Request, session: Annotated[Session, Depends(database_session)]
) -> User:
    """Get the user based on the token. To be used with Depends()."""
    request.session["from"] = request.url.path

    if (token := request.session.get("token", None)) is None:
        raise RequiresLoginException()

    user = (
        await session.exec(select(User).join(UserToken).where(UserToken.token == token))
    ).one_or_none()
    if user is None:
        raise RequiresLoginException()

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
    """Endpoint to begin user login."""
    redirect_uri = request.url_for("auth")
    return await oauth.auth0.authorize_redirect(request, redirect_uri)


@router.get("/logout")
async def logout(
    request: Request,
    session: Annotated[Session, Depends(database_session)],
    user: Annotated[User, Depends(current_user)],
):
    """Logout the current user."""
    token = request.session.pop("token")
    await session.exec(delete(UserToken).where(UserToken.token == token))
    await session.commit()
    return RedirectResponse(request.url_for("index"))


@router.get("/callback")
async def auth(
    request: Request, session: Annotated[Session, Depends(database_session)]
):
    """Authenticate a user."""
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
    return RedirectResponse(request.session.get("from", "/"))
