from alembic import context
from sqlalchemy import create_engine

from settings import get_settings

settings = get_settings()
target_metadata = ()
config = context.config


def run_migrations() -> None:
    url = config.get_main_option("sqlalchemy.url") or settings.DB_URI
    connectable = create_engine(url)
    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
        )
        with context.begin_transaction() as transaction:
            context.run_migrations()
            if "dry-run" in context.get_x_argument():
                print("Dry-run succeeded; now rolling back transaction...")
                transaction.rollback()
    connectable.dispose()


run_migrations()
