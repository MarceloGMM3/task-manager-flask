# task-manager-flask

[![CI](https://github.com/MarceloGMM3/task-manager-flask/actions/workflows/ci.yml/badge.svg)](https://github.com/MarceloGMM3/task-manager-flask/actions/workflows/ci.yml)

Aplicación web de gestión de tareas construida con Python, Flask y SQLite. El
proyecto prioriza una arquitectura clara, persistencia explícita, seguridad básica,
pruebas automatizadas y automatización de calidad mediante GitHub Actions.

## Funcionalidades

- Listar tareas pendientes y completadas.
- Crear y editar tareas con validación de título obligatorio.
- Marcar tareas como completadas o pendientes.
- Eliminar tareas mediante formularios `POST`.
- Proteger todas las operaciones mutativas mediante tokens CSRF.
- Mostrar páginas personalizadas para errores HTTP 404 y 500.
- Ofrecer una interfaz responsive con navegación por teclado y estados accesibles.

## Stack tecnológico

- Python 3.11 o superior.
- Flask y Flask-WTF.
- SQLite mediante el módulo `sqlite3` de la biblioteca estándar.
- Jinja, HTML y CSS sin frameworks JavaScript.
- pytest, pytest-cov y Ruff.
- GitHub Actions para integración continua.

## Arquitectura

La aplicación utiliza Application Factory y Blueprints. El flujo del módulo de
tareas es:

```text
HTTP → routes.py → repository.py → SQLite
```

Las rutas gestionan solicitudes, validación y respuestas HTTP. El repositorio
concentra las consultas SQL parametrizadas y controla `commit` y `rollback`. La
conexión SQLite se almacena en `flask.g`, utiliza `sqlite3.Row`, activa claves
foráneas y se cierra automáticamente al terminar el contexto de aplicación.

## Estructura principal

```text
task_manager/
├── __init__.py
├── config.py
├── db.py
├── errors.py
├── schema.sql
├── static/css/styles.css
├── tasks/
│   ├── __init__.py
│   ├── repository.py
│   └── routes.py
└── templates/
    ├── base.html
    ├── errors/
    └── tasks/
tests/
├── tasks/
├── conftest.py
├── test_app.py
├── test_db.py
└── test_errors.py
```

## Instalación

Clona el repositorio, crea un entorno virtual e instala el proyecto con sus
dependencias de desarrollo:

```bash
python -m venv .venv
```

En Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
python -m pip install -e ".[dev]"
```

En macOS o Linux:

```bash
source .venv/bin/activate
python -m pip install -e ".[dev]"
```

Usa `.env.example` como referencia y define `SECRET_KEY` con un valor aleatorio y
privado directamente en el entorno. Por ejemplo, en PowerShell:

```powershell
$env:SECRET_KEY = "reemplazar-por-un-valor-seguro"
```

En macOS o Linux:

```bash
export SECRET_KEY="reemplazar-por-un-valor-seguro"
```

Para una ejecución de producción también debes seleccionar el entorno explícito:

```bash
export APP_ENV="production"
```

Cuando `APP_ENV=production`, la aplicación falla al iniciar si `SECRET_KEY` está
ausente, vacía o conserva el valor local inseguro `dev`.

## Inicialización y ejecución

Inicializa la base SQLite local:

```bash
python -m flask --app wsgi init-db
```

Inicia el servidor de desarrollo:

```bash
python -m flask --app wsgi run --debug
```

La base se crea dentro de `instance/` y no se versiona.

## Pruebas y calidad

Ejecuta la suite:

```bash
python -m pytest
```

Mide cobertura y exige localmente el mismo mínimo de CI:

```bash
python -m pytest --cov --cov-fail-under=85
```

Ejecuta lint y verificación de formato:

```bash
ruff check .
ruff format --check .
```

## Integración continua

El workflow `.github/workflows/ci.yml` se ejecuta en cada push y Pull Request
hacia `main`. Instala Python 3.11 y las dependencias de desarrollo, ejecuta pytest,
exige una cobertura mínima del 85% y valida lint y formato con Ruff.

## Seguridad CSRF

`Flask-WTF` registra protección CSRF global. Cada formulario mutativo incluye un
token asociado a la sesión y las solicitudes sin token o con un token inválido se
rechazan antes de llegar a las rutas. Desarrollo conserva una configuración local
sencilla; una ejecución marcada explícitamente como producción exige una
`SECRET_KEY` segura y falla durante el arranque si no la recibe.

## Decisiones técnicas

- Se mantiene `sqlite3` nativo para hacer explícito el ciclo de conexión y las
  transacciones.
- El SQL vive exclusivamente en la capa de repositorio y usa placeholders `?`.
- `schema.sql` inicializa la versión actual; aún no existe un sistema de migraciones.
- Las operaciones mutativas usan `POST` y HTML tradicional, sin JavaScript complejo.
- Los errores 404 y 500 comparten la presentación base de la aplicación.

## Limitaciones actuales

- No hay autenticación ni separación de tareas por usuario.
- No existe API REST.
- `init-db` recrea el esquema y debe utilizarse solo para inicialización local.
- No hay migraciones, contenedores ni despliegue cloud configurado.
- La interfaz se mantiene ligera y sin framework CSS ni JavaScript complejo.

## Roadmap

- Incorporar migraciones cuando el esquema necesite evolucionar.
- Mejorar accesibilidad y experiencia visual sin alterar la arquitectura.
- Definir una estrategia de despliegue y configuración de producción.
- Evaluar autenticación únicamente si el alcance futuro lo requiere.
