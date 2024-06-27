"""Sample data interface."""

from typing import Annotated

from fastapi import APIRouter, Depends, File, Request, Response, UploadFile
from fastapi.responses import HTMLResponse, RedirectResponse

from sqlmodel import select, Session, delete

from jinet import auth
from jinet.db import database_session
from jinet.models import SampleData, User
from jinet.filesize import valid_content_len, read_upload_file

router = APIRouter()


@router.post("/new", response_class=HTMLResponse)
async def new(
    request: Request,
    filedata: Annotated[UploadFile, File(alias="file-data")],
    content_size: Annotated[int, Depends(valid_content_len)],
    session: Annotated[Session, Depends(database_session)],
    owner: Annotated[User, Depends(auth.current_user)],
):
    if not owner.can_upload:
        return RedirectResponse(request.url_for(request.session.get("from", "data")))

    sample_data = SampleData(
        name=filedata.filename,
        data=read_upload_file(filedata),
        mime=filedata.content_type,
        owner=owner,
    )
    session.add(sample_data)
    await session.commit()

    return f"""<div class="uk-alert-success" uk-alert><p>Successfully added {filedata.filename}</p></div>"""


@router.get("/file")
async def datafile(
    request: Request, name: str, session: Session = Depends(database_session)
):
    """Get the sample data file from the database."""
    query = select(SampleData).where(SampleData.name == name)
    result = (await session.exec(query)).first()
    if result is None:
        return RedirectResponse(request.url_for(request.session.get("from", "data")))

    return Response(content=result.data, media_type=result.mime)


@router.delete("/delete/{identifier}", response_class=HTMLResponse)
async def delete_data(
    request: Request,
    identifier: int,
    session: Annotated[Session, Depends(database_session)],
    admin: Annotated[User, Depends(auth.current_admin)],
):
    await session.exec(delete(SampleData).where(SampleData.id == identifier))
    await session.commit()
    return "<p>Deleted</p>"
