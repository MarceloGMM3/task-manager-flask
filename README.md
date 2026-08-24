# task-manager-flask

Aplicación web de gestión de tareas desarrollada con Python, Flask y SQLite,
con enfoque en buenas prácticas, pruebas y documentación.

## Estado

El proyecto incluye la fábrica de la aplicación, configuración básica, conexión
SQLite, esquema inicial y las operaciones CRUD de tareas con pruebas automatizadas.

## Desarrollo local

Requiere Python 3.11 o superior.

```bash
python -m venv .venv
python -m pip install -e ".[dev]"
python -m flask --app wsgi init-db
python -m flask --app wsgi run --debug
```

## Calidad

```bash
python -m pytest
ruff check .
ruff format --check .
```

## Limitaciones actuales

- Todavía no hay protección CSRF.
- Todas las operaciones mutativas utilizan solicitudes `POST`.
- La protección CSRF se abordará antes de considerar un despliegue de producción.
