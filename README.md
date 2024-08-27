![JINet logo](static/banner.png)

# JINet

Easily run analysis scripts where you are.

## Development

Use `docker` to run an instance of the analysis distribution server.

```bash
docker compose up -d
```

### Build database migrations

```bash
DATABASE_URI="postgresql+asyncpg://postgres:postgres@localhost:5432/jinet" poetry run alembic revision --autogenerate -m "Your message here"
```

## Running scripts

Analysis scripts may be written in Python, R, Julia, or Javascript and output either a file for local storage or HTML (e.g. to display a plot).

## Contributing

Pull requests are welcome. For major changes, please open an issue first
to discuss what you would like to change.

Please make sure to update tests as appropriate.

## License

[Apache 2.0](https://www.apache.org/licenses/LICENSE-2.0)
