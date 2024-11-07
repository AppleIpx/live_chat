FROM python:3.12.4-alpine3.20 as prod

RUN pip install poetry==1.8.4
RUN pip install gunicorn==23.0.0

# Configuring poetry
RUN poetry config virtualenvs.create false
RUN poetry config cache-dir /tmp/poetry_cache

# Copying requirements of a project
COPY pyproject.toml poetry.lock /app/src/
WORKDIR /app/src

# Installing requirements
RUN --mount=type=cache,target=/tmp/poetry_cache poetry install --only main

# Copying actuall application
COPY . /app/src/
RUN --mount=type=cache,target=/tmp/poetry_cache poetry install --only main

CMD ["/usr/local/bin/python", "-m", "live_chat"]

FROM prod as dev

RUN --mount=type=cache,target=/tmp/poetry_cache poetry install
