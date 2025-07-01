from logging.config import fileConfig
from sqlalchemy import engine_from_config
from sqlalchemy import pool
from alembic import context

# Import your app's settings and Base model
import os
import sys

# Add the app directory to the Python path
# This assumes 'alembic' directory is at the same level as 'app' directory
# For example, if project structure is:
# myproject/
#   alembic/
#   app/
# then `../../` would point to `myproject`
# If backend/
#       alembic/
#       app/
# then `../` would point to `backend`
# Since the bash session runs in backend/, and alembic is run from backend/,
# app is a sibling directory.
sys.path.insert(0, os.path.realpath(os.path.join(os.path.dirname(__file__), "..")))

from app.core.config import settings # noqa
from app.models.base import Base # noqa
# Import all models here so Base knows about them for 'autogenerate'
from app.models.user import User # noqa
# Other models will be imported as they are created:
# from app.models.question import Question # noqa
# from app.models.subject import Subject # noqa
# from app.models.practice import PracticeSession, UserAnswer # noqa
# from app.models.analytics import UserAnalytics # noqa

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
# Commented out to avoid logging config issues
# if config.config_file_name is not None:
#     fileConfig(config.config_file_name)

# Set the sqlalchemy.url from your application settings
# This overrides the sqlalchemy.url in alembic.ini
# For Alembic, we use a synchronous version of the DB URI
if not settings.SQLALCHEMY_DATABASE_URI:
    raise ValueError("SQLALCHEMY_DATABASE_URI is not set in the application settings.")

sync_db_url = settings.SQLALCHEMY_DATABASE_URI.replace("+asyncpg", "")
config.set_main_option("sqlalchemy.url", sync_db_url.replace('%', '%%')) # Escape % for ini file if any

# add your model's MetaData object here
# for 'autogenerate' support
# from myapp import mymodel
# target_metadata = mymodel.Base.metadata
target_metadata = Base.metadata

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True, # Detect column type changes
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True, # Detect column type changes
            # Include object hooks for custom DDL for enums, etc. if needed in future
            # process_revision_directives=process_revision_directives,
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
