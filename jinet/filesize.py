"""Define limits on upload file size."""

from io import BytesIO
from fastapi import Header, UploadFile, HTTPException, status

# 2mb
MAX_CONTENT_LEN = 2 * 1024 * 1024


async def valid_content_len(content_length: int = Header(..., lt=MAX_CONTENT_LEN)):
    """Limit the Content-Length header to be < 100k."""
    return content_length


def read_upload_file(thefile: UploadFile) -> bytes:
    """Extract data from an UploadFile but throw if too large."""
    buf = BytesIO()
    actual_size = 0
    for chunk in thefile.file:
        actual_size += len(chunk)
        if actual_size > MAX_CONTENT_LEN:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail="File too large.",
            )

        buf.write(chunk)
    buf.seek(0)
    return buf.read()
