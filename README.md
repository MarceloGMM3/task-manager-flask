# Task Manager Flask

[![CI](https://github.com/MarceloGMM3/task-manager-flask/actions/workflows/ci.yml/badge.svg?branch=main)](https://github.com/MarceloGMM3/task-manager-flask/actions/workflows/ci.yml)

Aplicación web de gestión de tareas desarrollada como proyecto de portafolio con
una arquitectura Flask modular, persistencia SQLite explícita y un flujo de calidad
automatizado. El proyecto prioriza código auditable, pruebas aisladas, seguridad
básica y una interfaz accesible sin ampliar innecesariamente el stack.

**Python · Flask · SQLite · Pytest · GitHub Actions**

- **45 pruebas automatizadas** y **97 % de cobertura**.
- Integración continua para pruebas, cobertura, lint y formato.
- Protección CSRF en todas las operaciones mutativas.
- Migraciones SQLite versionadas, transaccionales e idempotentes.
- Interfaz responsive con criterios de accesibilidad y navegación por teclado.

## Vista de la aplicación

La captura principal del flujo de tareas se incorporará cuando esté disponible. El
README está preparado para alojarla en `docs/images/task-manager-preview.png` sin
mantener mientras tanto un recurso visual roto.

## Características

- Listado de tareas pendientes y completadas, con estados visuales y textuales.
- Creación y edición con normalización y validación de título obligatorio.
- Cambio de estado entre pendiente y completada.
- Eliminación mediante `POST` con confirmación previa en el navegador.
- Estado vacío, mensajes de confirmación y páginas personalizadas 404 y 500.
- Diseño adaptable a escritorio, tablet y móvil.
- Formularios con labels asociados, mensajes accesibles, foco visible y skip link.

## Arquitectura

La aplicación utiliza **Application Factory** y un **Blueprint** para el dominio de
tareas. La separación principal es:

```text
HTTP → routes.py → repository.py → SQLite
```

- `routes.py` procesa solicitudes, validación de formularios y respuestas HTTP.
- `repository.py` concentra las operaciones de persistencia y el SQL parametrizado.
- `db.py` administra una conexión SQLite por contexto mediante `flask.g`, activa
  claves foráneas y cierra automáticamente la conexión.
- `migrations.py` descubre y ejecuta evoluciones versionadas del esquema.

Esta división mantiene la lógica HTTP separada del acceso a datos sin incorporar
un ORM para el alcance actual.

## Tecnologías

| Área | Tecnología |
| --- | --- |
| Backend | Python 3.11+, Flask 3, Jinja |
| Persistencia | SQLite y `sqlite3` nativo |
| Seguridad de formularios | Flask-WTF / CSRFProtect |
| Frontend | HTML semántico y CSS nativo |
| Pruebas | pytest y pytest-cov |
| Calidad | Ruff |
| Automatización | GitHub Actions |

## Seguridad

- Flask-WTF aplica protección CSRF global y los formularios `POST` incluyen tokens.
- Todas las consultas que reciben valores dinámicos usan placeholders `?`.
- Las escrituras realizan `commit` explícito y `rollback` ante errores SQLite.
- En una configuración marcada como producción, la aplicación exige una
  `SECRET_KEY` explícita y rechaza el valor local `dev`.
- Las bases locales, `.env` y entornos virtuales están excluidos de Git.

Son controles acordes con una aplicación de portafolio; no representan por sí
solos una estrategia completa de seguridad o despliegue en producción.

## Migraciones de base de datos

Las migraciones son archivos SQL con nombres `NNNN_descripcion.sql`. La tabla
`schema_migrations` registra las versiones aplicadas y permite que `upgrade-db`
ejecute únicamente las pendientes, en orden y una sola vez.

Cada migración usa una transacción explícita: el DDL y el registro de versión se
confirman juntos, o se revierten ante un error. La estrategia es **forward-only** y
preserva los registros existentes.

```bash
python -m flask --app wsgi upgrade-db
```

- `init-db` crea o reinicia de forma destructiva una base de desarrollo con el
  esquema actual.
- `upgrade-db` actualiza una base existente sin reinicializar sus datos.

No debe utilizarse `init-db` para actualizar una base cuyos datos deban conservarse.

## Pruebas y calidad

La suite contiene **45 pruebas automatizadas** y mantiene **97 % de cobertura**.
Incluye casos de rutas, repositorio, CSRF, configuración, errores HTTP, conexión a
SQLite y migraciones, incluidos orden, idempotencia y rollback ante fallos.

GitHub Actions se ejecuta en cada push y Pull Request hacia `main` con Python 3.11.
La CI instala las dependencias de desarrollo, exige al menos 85 % de cobertura y
ejecuta las verificaciones de Ruff.

## Instalación

Requisitos:

- Python 3.11 o superior.
- Git.

Clona el repositorio y entra al directorio:

```bash
git clone https://github.com/MarceloGMM3/task-manager-flask.git
cd task-manager-flask
python -m venv .venv
```

En Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
python -m pip install -e ".[dev]"
$env:SECRET_KEY = "reemplazar-por-un-valor-aleatorio"
```

En macOS o Linux:

```bash
source .venv/bin/activate
python -m pip install -e ".[dev]"
export SECRET_KEY="reemplazar-por-un-valor-aleatorio"
```

Inicializa una base local nueva:

```bash
python -m flask --app wsgi init-db
```

La base se almacena bajo `instance/` y no se versiona.

## Ejecución

Inicia el servidor de desarrollo:

```bash
python -m flask --app wsgi run --debug
```

Flask mostrará en la terminal la dirección local de la aplicación.

## Pruebas

Ejecuta la suite completa:

```bash
python -m pytest
```

Mide cobertura y aplica el mismo umbral mínimo de CI:

```bash
python -m pytest --cov=task_manager --cov-fail-under=85
```

Comprueba lint y formato:

```bash
ruff check .
ruff format --check .
```

## Estructura del proyecto

```text
task-manager-flask/
├── .github/workflows/ci.yml
├── task_manager/
│   ├── __init__.py
│   ├── config.py
│   ├── db.py
│   ├── errors.py
│   ├── migrations.py
│   ├── migrations/
│   │   └── 0001_optimize_task_listing.sql
│   ├── schema.sql
│   ├── static/css/styles.css
│   ├── tasks/
│   │   ├── repository.py
│   │   └── routes.py
│   └── templates/
│       ├── base.html
│       ├── errors/
│       └── tasks/
├── tests/
│   ├── tasks/
│   ├── conftest.py
│   ├── test_app.py
│   ├── test_db.py
│   ├── test_errors.py
│   └── test_migrations.py
├── pyproject.toml
└── wsgi.py
```

## Decisiones técnicas

- **Flask modular:** Application Factory y Blueprints permiten separar arranque,
  configuración y dominio sin añadir capas innecesarias.
- **SQLite sin ORM:** conserva SQL explícito y facilita evaluar consultas,
  transacciones y ciclo de conexión en un proyecto de esta escala.
- **Migraciones ligeras propias:** mantienen el historial SQL visible y evitan
  introducir una herramienta mayor para un esquema pequeño.
- **Pruebas y CI:** verifican comportamiento, seguridad básica y calidad en cada
  cambio dirigido a `main`.
- **CSS nativo y accesibilidad:** ofrecen una interfaz ligera, responsive y usable
  por teclado sin depender de frameworks frontend.

Estas decisiones responden al alcance educativo y de portafolio del proyecto; no
se plantean como una solución universal para aplicaciones de cualquier tamaño.

## Limitaciones actuales

- No incluye autenticación ni separación de tareas por usuario.
- No expone una API pública.
- No dispone todavía de Docker ni despliegue público.
- Las migraciones son forward-only y no almacenan checksums.
- La accesibilidad se prueba mediante aserciones HTML, sin auditoría WCAG automática.
- Los errores CSRF utilizan la respuesta estándar de Flask-WTF.

## Posibles mejoras futuras

- Publicar una instancia demostrativa con configuración de despliegue documentada.
- Evaluar autenticación si el alcance requiere tareas por usuario.
- Diseñar una API pública manteniendo separada la persistencia.
- Incorporar Docker para un entorno reproducible de ejecución.
- Automatizar auditorías de accesibilidad y ampliar la estrategia de migraciones.

## Autor

**Marcelo Molina**

Ingeniero en Informática

[GitHub](https://github.com/MarceloGMM3)

## Licencia

Este proyecto se distribuye bajo la [Licencia MIT](LICENSE).
