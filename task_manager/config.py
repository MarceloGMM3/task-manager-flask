"""Default application configuration."""

import os


class Config:
    """Configuration shared by local and production environments."""

    APP_ENV = os.environ.get("APP_ENV", "development")
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev")
    DATABASE = os.environ.get("DATABASE")
