"""CRUD operations on packages."""

from typing import Annotated, Optional
from dataclasses import dataclass
import json
import math

from fastapi import (
    APIRouter,
    Depends,
    File,
    Form,
    HTTPException,
    Request,
    Response,
    status,
    UploadFile,
)
from fastapi.responses import HTMLResponse, RedirectResponse

from sqlmodel import func, select, Session, desc, asc

from jinet import auth
from jinet.templates import templates
from jinet.db import database_session
from jinet.models import Package, Tag, User
from jinet.filesize import valid_content_len, read_upload_file

router = APIRouter()

PAGINATION_LIMIT = 12


@dataclass
class PackageName:
    """A fully qualified package name needs all of these fields.

    Serialized, it looks like james.collier412/NetMUG@5
    This would result in:
      user: "james.collier412"
      package: "NetMUG"
      version:5
    """

    user: str
    package: str
    version: int


def parse_package_name(name: str) -> Optional[PackageName]:
    """Parse a package name in the format user/name@version."""
    try:
        (user, (package_version)) = name.split("/", 1)
        (package, version) = package_version.split("@", 1)
        return PackageName(user, package, int(version))
    except ValueError:
        return None


@dataclass(frozen=True)
class Page:
    """Describes a page of applications that is paginated."""

    page: int
    active: bool
    offset: int


@router.get("/list", response_class=HTMLResponse)
async def listing(
    request: Request,
    offset: int = 0,
    active: int = 1,
    tag: Optional[str] = None,
    term: Optional[str] = None,
    session: Session = Depends(database_session),
):
    """Retrieve a paginated listing of all packages."""
    if term == "":
        term = None

    match (tag, term):
        case (None, None):
            pkg_qry = (
                select(Package)
                .distinct(Package.name, Package.owner_id)
                .order_by(
                    Package.name,
                    Package.owner_id,
                    desc(Package.version),
                )
                .subquery()
            )

        case (tg, None):
            pkg_qry = (
                select(Package)
                .distinct(Package.name, Package.owner_id)
                .order_by(Package.name, Package.owner_id, desc(Package.version))
                .where(Package.tags.any(Tag.name == tg))
                .subquery()
            )

        case (None, query):
            pkg_qry = (
                select(Package)
                .distinct(Package.name, Package.owner_id)
                .order_by(Package.name, Package.owner_id, desc(Package.version))
                .where(
                    Package.name.icontains(query)
                    | Package.short_description.icontains(query)
                    | Package.description.icontains(query)
                )
                .subquery()
            )

        case (tg, query):
            pkg_qry = (
                select(Package)
                .distinct(Package.name, Package.owner_id)
                .filter(Package.tags.any(Tag.name == tg))
                .filter(Package.name.op("%")(query))
                .order_by(Package.name, Package.owner_id, desc(Package.version))
                .subquery()
            )
    total = (await session.exec(select(func.count()).select_from(pkg_qry))).one()

    packages = (
        await session.exec(
            select(Package)
            .join(pkg_qry, Package.id == pkg_qry.c.id)
            .order_by(asc(pkg_qry.c.id))
            .offset(offset)
            .limit(PAGINATION_LIMIT)
        )
    ).all()

    if tag is None:
        tags = (await session.exec(select(Tag.name).distinct())).all()
        filtered_by_tag = False
    else:
        tags = [tag]
        filtered_by_tag = True

    pages = [
        Page(page=p + 1, active=(p + 1) == active, offset=p * PAGINATION_LIMIT)
        for p in range(math.ceil(total / PAGINATION_LIMIT))
    ]

    term_options = {} if term is None else {"term": term}
    tag_options = {} if tag is None else {"tag": tag}
    return templates.TemplateResponse(
        request=request,
        name="package-list.html",
        context={
            "packages": packages,
            "tags": tags,
            "filtered_by_tag": filtered_by_tag,
            "pages": pages,
        }
        | term_options
        | tag_options,
    )


@router.get("/new", response_class=HTMLResponse)
async def new(request: Request, user: Annotated[User, Depends(auth.current_user)]):
    """Create a new package."""
    if user.can_upload:
        return templates.TemplateResponse(
            request=request, name="package-new.html", context={"user": user}
        )
    else:
        return RedirectResponse(request.url_for("packages"))


@router.post("/validate", response_class=HTMLResponse)
async def validate(
    request: Request,
    runtime: Annotated[str, Form()],
    package_name: Annotated[str, Form(alias="package-name")],
    package_file: Annotated[UploadFile, File(alias="package-file")],
    parameters: Annotated[str, Form()],
    output: Annotated[str, Form()],
    content_size: Annotated[int, Depends(valid_content_len)],
    session: Annotated[Session, Depends(database_session)],
    owner: Annotated[User, Depends(auth.current_user)],
    package_headline: Annotated[Optional[str], Form(alias="package-headline")] = None,
    package_description: Annotated[
        Optional[str], Form(alias="package-description")
    ] = None,
    package_logo: Annotated[Optional[UploadFile], File(alias="package-logo")] = None,
    package_tags: Annotated[Optional[str], Form(alias="package-tags")] = None,
    entrypoint: Annotated[Optional[str], Form()] = None,
):
    """Validate a submitted package."""
    if not owner.can_upload:
        return RedirectResponse(request.url_for("packages"))

    # Validate the parameters
    try:
        package_parameters = json.loads(parameters)
    except ValueError as err:
        return templates.TemplateResponse(
            request=request,
            name="package-validate.html",
            context={"user": owner, "error": str(err)},
        )

    # Check file size by actually reading it.
    file_buffer = read_upload_file(package_file)
    if package_logo is not None:
        logo_buffer = read_upload_file(package_logo)
        logo_mime = package_logo.content_type
    else:
        logo_buffer = None
        logo_mime = None

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
    interface = {
        "entrypoint": entrypoint or "main",
        "parameters": package_parameters,
        "output": output,
    }

    tags = (
        [Tag(name=tag.strip()) for tag in package_tags.split(",")]
        if package_tags is not None
        else []
    )

    package = Package(
        name=package_name,
        data=file_buffer,
        short_description=package_headline,
        description=package_description,
        version=previous_version.version + 1 if previous_version is not None else 1,
        runtime=runtime,
        interface=interface,
        logo=logo_buffer,
        logo_mime=logo_mime,
        owner=owner,
        tags=tags,
    )
    session.add(package)
    await session.commit()
    await session.refresh(package)
    return templates.TemplateResponse(
        request=request,
        name="package-validate.html",
        context={"user": owner, "package": package},
    )


@router.get("/run", response_class=HTMLResponse)
async def run(
    request: Request,
    package: str,
    session: Session = Depends(database_session),
):
    """Run a package in the users browser."""
    pkgdef = parse_package_name(package)
    owner = (
        await session.exec(select(User).where(User.username == pkgdef.user))
    ).first()
    if owner is None:
        return RedirectResponse(request.url_for("packages"))

    query = (
        select(Package)
        .where(Package.name == pkgdef.package)
        .where(Package.owner_id == owner.id)
        .where(Package.version == pkgdef.version)
    )
    result = await session.exec(query)
    db_package = result.first()

    match db_package.runtime:
        case "python-runtime":
            return templates.TemplateResponse(
                request=request,
                name="package-run-python.html",
                context=(await auth.user_in_context(request, session))
                | {"application": package, "package": db_package},
            )
        case "R-runtime":
            return templates.TemplateResponse(
                request=request,
                name="package-run-R.html",
                context=(await auth.user_in_context(request, session))
                | {"application": package, "package": db_package},
            )
        case _:
            return RedirectResponse(request.url_for("packages"))


@router.get("/file")
async def file(
    request: Request, package: str, session: Session = Depends(database_session)
):
    """Get the package data file from the database."""
    pkgdef = parse_package_name(package)
    owner = (
        await session.exec(select(User).where(User.username == pkgdef.user))
    ).first()
    if owner is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not a user")

    query = (
        select(Package)
        .where(Package.name == pkgdef.package)
        .where(Package.owner_id == owner.id)
        .where(Package.version == pkgdef.version)
    )
    result = await session.exec(query)
    db_package = result.first()
    if db_package is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Not a package"
        )

    return Response(content=db_package.data, media_type="text/x-python")


@router.get("/logo")
async def logo(request: Request, package: str, session=Depends(database_session)):
    """Get a package logo if one exists."""
    pkgdef = parse_package_name(package)
    if (
        owner := (
            await session.exec(select(User).where(User.username == pkgdef.user))
        ).first()
    ) is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not a user")

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

    if db_package.logo is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="No logo for this package"
        )

    return Response(content=db_package.logo, media_type=db_package.logo_mime)
