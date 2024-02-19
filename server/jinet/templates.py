"""HTML Templating."""

from base64 import b64encode

from fastapi.templating import Jinja2Templates

templates = Jinja2Templates(directory="templates")
templates.env.filters["b64encode"] = b64encode
