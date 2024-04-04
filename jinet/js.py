"""Javascript source templating."""

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlmodel import Session, select

from jinet.db import database_session
from jinet.models import User, Package
from jinet.packages import parse_package_name
from jinet.templates import templates

router = APIRouter()


@router.get("/js/{script}")
async def javascript_template(
    request: Request,
    script: str,
    application: Optional[str] = None,
    session: Session = Depends(database_session),
):
    """Template generator for Javascript."""
    if application is not None:
        pkgdef = parse_package_name(application)
        if (
            owner := (
                await session.exec(select(User).where(User.username == pkgdef.user))
            ).first()
        ) is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Not a user"
            )

        query = (
            select(Package)
            .where(Package.name == pkgdef.package)
            .where(Package.owner_id == owner.id)
            .where(Package.version == pkgdef.version)
        )
        result = await session.exec(query)
        if (db_package := result.first()) is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Not a package"
            )
        context = {"application": application, "package": db_package}
    else:
        context = {}

    return templates.TemplateResponse(
        request=request,
        name=script,
        context=context,
        media_type="text/javascript",
    )
