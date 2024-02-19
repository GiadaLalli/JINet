# Server

## Build database migrations

```bash
DATABASE_URI="postgresql+asyncpg://postgres:postgres@localhost:5432/jinet" poetry run alembic revision --autogenerate -m "init"
```
