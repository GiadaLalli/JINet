"""CRUD operations on packages."""

from typing import Annotated
from statistics import mean
from io import BytesIO
import json

from fastapi import (
    APIRouter,
    Depends,
    File,
    Form,
    Header,
    HTTPException,
    Request,
    Response,
    status,
    UploadFile,
)
from fastapi.responses import HTMLResponse, RedirectResponse

from sqlmodel import select, Session, desc

from jinet import auth
from jinet.templates import templates
from jinet.db import database_session
from jinet.models import Package, Tag, User

router = APIRouter()


# 100k
MAX_CONTENT_LEN = 100_000


async def valid_content_len(content_length: int = Header(..., lt=MAX_CONTENT_LEN)):
    """Limit the Content-Length header to be < 100k."""
    return content_length


@router.get("/list", response_class=HTMLResponse)
async def listing(
    request: Request, since: int = 0, session: Session = Depends(database_session)
):
    """Retrieve a paginated listing of all packages."""
    query = (
        select(Package)
        .distinct(Package.name, Package.owner_id)
        .order_by(Package.name, Package.owner_id, desc(Package.version))
        .where(Package.id >= since)
        .limit(10)
    )
    results = await session.exec(query)
    return templates.TemplateResponse(
        request=request,
        name="package-list.html",
        context={"packages": results.all()},
    )


@router.get("/new", response_class=HTMLResponse)
async def new(request: Request):
    """Create a new package."""
    user = auth.user(request)
    return templates.TemplateResponse(
        request=request, name="package-new.html", context={"user": user}
    )


@router.post("/validate", response_class=HTMLResponse)
async def validate(
    request: Request,
    runtime: Annotated[str, Form()],
    package_name: Annotated[str, Form(alias="package-name")],
    package_description: Annotated[str, Form(alias="package-description")],
    package_tags: Annotated[str, Form(alias="package-tags")],
    package_file: Annotated[UploadFile, File(alias="package-file")],
    entrypoint: Annotated[str, Form()],
    parameters: Annotated[str, Form()],
    output: Annotated[str, Form()],
    content_size: int = Depends(valid_content_len),
    session: Session = Depends(database_session),
):
    """Validate a submitted package."""
    user = auth.user(request)

    # Validate the parameters
    try:
        package_parameters = json.loads(parameters)
    except ValueError as err:
        return templates.TemplateResponse(
            request=request,
            name="package-validate.html",
            context={"user": user, "error": str(err)},
        )

    owner = (
        await session.exec(select(User).where(User.sub == user.get("sub")))
    ).first()

    # Check file size by actually reading it.
    buf = BytesIO()
    actual_size = 0
    for chunk in package_file.file:
        actual_size += len(chunk)
        if actual_size > MAX_CONTENT_LEN:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail="File too large.",
            )

        buf.write(chunk)
    buf.seek(0)

    # Does this user already have a package by this name
    query = (
        select(Package)
        .where(Package.name == package_name)
        .where(Package.owner_id == owner.id)
        .order_by(desc(Package.version))
    )
    results = await session.exec(query)
    previous_version = results.first()

    # Get ready to insert into the database
    package = Package(
        name=package_name,
        data=buf.read(),
        description=package_description,
        version=previous_version.version + 1 if previous_version is not None else 1,
        runtime=runtime,
        interface={
            "entrypoint": entrypoint,
            "parameters": package_parameters,
            "output": output,
        },
        owner=owner,
        tags=[Tag(name=tag.strip()) for tag in package_tags.split(",")],
    )
    session.add(package)
    await session.commit()
    await session.refresh(package)
    return templates.TemplateResponse(
        request=request,
        name="package-validate.html",
        context={"user": user, "package": package},
    )


@router.get("/run", response_class=HTMLResponse)
async def run(
    request: Request,
    package: str,
    runtime: str,
):
    """Run a package in the users browser."""
    match runtime:
        case "python-runtime":
            return templates.TemplateResponse(
                request=request,
                name="package-run-python.html",
                context=auth.user_in_context(request) | {"package": package},
            )
        case _:
            return RedirectResponse(request.url_for("packages"))


@router.get("/file")
async def file(
    request: Request, package: str, session: Session = Depends(database_session)
):
    """Get the package data file from the database."""
    (user, (package_version)) = package.split("/", 1)
    (package, version) = package_version.split("@", 1)
    owner = (await session.exec(select(User).where(User.username == user))).first()
    if owner is None:
        return RedirectResponse(request.url_for("packages"))

    query = (
        select(Package)
        .where(Package.name == package)
        .where(Package.owner_id == owner.id)
        .where(Package.version == int(version))
    )
    result = await session.exec(query)
    db_package = result.first()
    if db_package is None:
        return RedirectResponse(request.url_for("packages"))

    return Response(content=db_package.data, media_type="text/x-python")
