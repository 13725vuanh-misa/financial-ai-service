from sqlalchemy import URL, create_engine, text
from sqlalchemy.engine import Engine

from app.config import settings


def create_database_engine() -> Engine:
    """Tạo engine kết nối tới PostgreSQL."""

    database_url = URL.create(
        drivername="postgresql+psycopg",
        username=settings.db_user,
        password=settings.db_password,
        host=settings.db_host,
        port=settings.db_port,
        database=settings.db_name,
    )

    return create_engine(
        database_url,
        pool_pre_ping=True,
        pool_size=5,
        max_overflow=5,
        echo=False,
    )


engine = create_database_engine()


def check_database_connection() -> bool:
    """Kiểm tra DB có kết nối được hay không."""

    with engine.connect() as connection:
        connection.execute(text("SELECT 1"))

    return True
