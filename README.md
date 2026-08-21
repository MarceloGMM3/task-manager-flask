# task-manager-flask

Aplicación web de gestión de tareas desarrollada con Python, Flask y SQLite,
con enfoque en buenas prácticas, pruebas y documentación.

## Estado

El proyecto se encuentra en su etapa inicial. Por ahora incluye la fábrica de la
aplicación, configuración básica, conexión SQLite, esquema inicial y pruebas de
infraestructura. El CRUD de tareas todavía no está implementado.

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
