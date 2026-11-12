
from sqlalchemy import bindparam, text

from app.database.connection import engine


def validate_tickers(tickers: list[str]) -> None:
    """Kiểm tra các mã cổ phiếu có tồn tại trong DB."""

    if not tickers:
        raise ValueError("Danh sách tickers không được để trống")

    query = text("""
        SELECT symbol
        FROM securities
        WHERE symbol IN :tickers
    """).bindparams(
        bindparam("tickers", expanding=True)
    )

    with engine.connect() as connection:
        result = connection.execute(
            query,
            {"tickers": tickers},
        )

        existing_tickers = {
            row.symbol for row in result
        }

    missing_tickers = set(tickers) - existing_tickers

    if missing_tickers:
        raise ValueError(
            f"Các mã cổ phiếu không tồn tại: "
            f"{', '.join(sorted(missing_tickers))}"
        )
