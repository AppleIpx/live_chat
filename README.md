# live_chat

**This project is an online chat using FastApi, SQLAlchemy, and SSE connection to send messages**

## Poetry

This project uses poetry. It's a modern dependency management
tool.

To run the project use this set of commands:

```bash
poetry install
poetry run python -m live_chat
```

This will start the server on the configured host.

You can find swagger documentation at `/api/docs`.

You can read more about poetry here: https://python-poetry.org/

## Docker

You can start the project with docker using this command:

```bash
docker-compose -f docker-compose.local.yml up --build
```


## Project structure

```bash
$ tree "live_chat"
live_chat
├── db  # module contains db configurations
│   └── migrations  # The folder in which the migrations are located.
│   └── models  # Package contains different models for ORMs.
├── __main__.py  # Startup script. Starts uvicorn.
├── services  # Package for different external services such as rabbit or redis etc.
├── settings.py  # Main configuration settings for project.
├── static  # Static content.
└── web  # Package contains web server. Handlers, startup config.
    ├── api  # Package with all handlers.
    │   └── chat  # Chat view. This includes schemas, routers, and other utils
    │   └── messages  # Message view. This includes schemas, SSE connection and operations with Redis, as well as utils for message operation
    │   └── monitoring  # Simple view to monitor the correct operation of the server
    │   └── users  # User view. This includes schemas, routers, auth logic and other utils
    │   └── router.py  # Main router.
    ├── application.py  # FastAPI application configuration.
    └── lifespan.py  # Contains actions to perform on startup and shutdown.
    └── s3_client.py  # Configuring the S3 client to communicate with MInIO.
    
```

## Configuration

This application can be configured with environment variables.

You can create `.env` file in the directory _.envs/.local/_ and place all
environment variables here.

An example of .env file for work with docker:
```bash
# General
IS_RELOAD=True
USERS_SECRET= <your secret key>
WORKERS_COUNT=1
HOST=0.0.0.0
PORT=8000

#Database
POSTGRES_USER=postgres-live-chat
POSTGRES_PASSWORD=postgres-live-chat
POSTGRES_HOST=postgres-live-chat-local
POSTGRES_PORT=5432
POSTGRES_DB=postgres_live_chat_local

# Redis
REDIS_HOST=redis-live-chat-local
REDIS_PORT=6379

# AWS
# ------------------------------------------------------------------------------
USE_S3=True
AWS_ACCESS_KEY_ID=live_chat_local
AWS_SECRET_ACCESS_KEY=live_chat_local
AWS_S3_MAX_MEMORY_SIZE=100_000_000_000_000
AWS_S3_REGION_NAME=us-east-1
AWS_BUCKET_NAME=live-chat-bucket
AWS_S3_ENDPOINT_URL=http://minio-live-chat-local:9000
AWS_S3_URL_PROTOCOL=http:


# MinIO
# ------------------------------------------------------------------------------
MINIO_ROOT_USER=admin_docker
MINIO_ROOT_PASSWORD=12345678
MINIO_URL=http://localhost:9000/live-chat-bucket/
```

You can read more about BaseSettings class here: https://pydantic-docs.helpmanual.io/usage/settings/

## Pre-commit

To install pre-commit simply run inside the shell:
```bash
pre-commit install
```

pre-commit is very useful to check your code before publishing it.
It's configured using .pre-commit-config.yaml file.

By default it runs:
* black (formats your code);
* mypy (validates types);
* ruff (spots possible bugs);


You can read more about pre-commit here: https://pre-commit.com/

## Migrations

If you want to migrate your database, you should run following commands:
```bash
# To run all migrations until the migration with revision_id.
alembic upgrade "<revision_id>"

# To perform all pending migrations.
alembic upgrade "head"
```

### Reverting migrations

If you want to revert migrations, you should run:
```bash
# revert all migrations up to: revision_id.
alembic downgrade <revision_id>

# Revert everything.
 alembic downgrade base
```

### Migration generation

To generate migrations you should run:
```bash
# For automatic change detection.
alembic revision --autogenerate

# For empty file generation.
alembic revision
```


## Running tests

If you want to run it in docker, simply run:

```bash
docker-compose -f docker-compose.test.yml build  
docker compose -f docker-compose.test.yml run fastapi-live-chat-test pytest
```

For running tests on your local machine.
1. you need to start a database.

2. Run the pytest.
```bash
pytest -vv .
```
