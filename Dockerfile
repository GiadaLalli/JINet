FROM python:3.12-slim-bookworm

WORKDIR /jinet
COPY ./pyproject.toml ./
COPY ./poetry.lock ./

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV VENV_PATH=/opt/venv

RUN apt-get update && apt-get install -y --no-install-recommends \
  build-essential \
  libpq-dev \
  curl \
  && pip install poetry \
  && python -m venv $VENV_PATH \
  && poetry config virtualenvs.create false \
  && rm -rf /var/lib/apt/lists/* \
  && poetry install --no-interaction --no-ansi --no-root -vvv

COPY . ./
RUN pip install uvicorn
CMD ["uvicorn", "jinet.main:app", "--host", "0.0.0.0", "--port", "5000"]