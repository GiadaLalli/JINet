""" Share results. """

from typing import Annotated, Optional

from fastapi import APIRouter, Depends, Form, HTTPException, Request, status
from fastapi.responses import RedirectResponse
from sqlmodel import Session, select

from jinet import auth
from jinet.db import database_session
from jinet.models import User, Package, ShareData
from jinet.packages import parse_package_name
from jinet.templates import templates

router = APIRouter()


@router.post("/share")
async def create_share(
    request: Request,
    application: str,
    output_type: Annotated[str, Form(alias="output-type")],
    data: Annotated[str, Form(alias="output-data")],
    checksum: Annotated[str, Form()],
    filename: Annotated[Optional[str], Form()] = None,
    session: Session = Depends(database_session),
):
    """Create a share data entry in the database and generate a link in the response."""
    user = auth.user(request)
    if not user.get("can_upload", False):
        return RedirectResponse(request.url_for("index"))

    pkgdef = parse_package_name(application)
    if (
        owner := (
            await session.exec(select(User).where(User.username == pkgdef.user))
        ).first()
    ) is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not a user")

    package_query = (
        select(Package)
        .where(Package.name == pkgdef.package)
        .where(Package.owner_id == owner.id)
        .where(Package.version == pkgdef.version)
    )
    if (package := (await session.exec(package_query)).first()) is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Not a package"
        )

    share = ShareData(
        filename=filename,
        checksum=checksum,
        data=data,
        owner_id=owner.id,
        package_id=package.id,
        output=output_type,
    )
    session.add(share)
    await session.commit()
    await session.refresh(share)

    return templates.TemplateResponse(
        request=request,
        name="share-response.html",
        context={"url": "/shared/" + str(share.reference)},
    )


@router.get("/shared/{reference}")
async def retrieve_results(
    request: Request,
    reference: str,
    session: Session = Depends(database_session),
):
    """Display shared results."""
    if (
        shared := (
            await session.exec(
                select(ShareData).where(ShareData.reference == reference)
            )
        ).first()
    ) is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Unknown share."
        )

    return templates.TemplateResponse(
        request=request, name="shared-result.html", context={"share": shared}
    )
