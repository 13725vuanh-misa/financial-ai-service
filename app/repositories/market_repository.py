from datetime import date, datetime, time, timedelta

import pandas as pd
from sqlalchemy import bindparam, text

from app.database.connection import engine
from app.repositories.security_repository import validate_tickers

    
def get_market_prices(
    tickers: list[str],
    start_date: date,
    end_date: date,
    interval_code: str,
    lookback_periods: int = 0,
) -> pd.DataFrame:
    """
    Lấy dữ liệu giá cổ phiếu từ PostgreSQL.

    Bao gồm:
    - Dữ liệu trong khoảng ngày được yêu cầu.
    - Một số phiên giao dịch trước start_date để tính Feature.
    """

    if not tickers:
        raise ValueError("Danh sách tickers không được để trống")

    validate_tickers(tickers)

    if start_date >= end_date:
        raise ValueError("start_date phải nhỏ hơn end_date")

    if lookback_periods < 0:
        raise ValueError("lookback_periods không được âm")

    start_timestamp = datetime.combine(start_date, time.min)
    end_timestamp = datetime.combine(
        end_date + timedelta(days=1),
        time.min,
    )

    query = text("""
        WITH selected_securities AS (
            SELECT
                id AS security_id,
                symbol
            FROM securities
            WHERE symbol IN :tickers
        ),

        previous_prices AS (
            SELECT
                mp.security_id,
                s.symbol,
                mp.price_timestamp,
                mp.interval_code,
                mp.open_price,
                mp.high_price,
                mp.low_price,
                mp.close_price,
                mp.adjusted_close,
                mp.volume,
                mp.trading_value,

                ROW_NUMBER() OVER (
                    PARTITION BY mp.security_id
                    ORDER BY mp.price_timestamp DESC
                ) AS row_number

            FROM market_prices mp

            JOIN selected_securities s
                ON mp.security_id = s.security_id

            WHERE mp.interval_code = :interval_code
              AND mp.is_canonical = TRUE
              AND mp.price_timestamp < :start_timestamp
        ),

        range_prices AS (
            SELECT
                mp.security_id,
                s.symbol,
                mp.price_timestamp,
                mp.interval_code,
                mp.open_price,
                mp.high_price,
                mp.low_price,
                mp.close_price,
                mp.adjusted_close,
                mp.volume,
                mp.trading_value

            FROM market_prices mp

            JOIN selected_securities s
                ON mp.security_id = s.security_id

            WHERE mp.interval_code = :interval_code
              AND mp.is_canonical = TRUE
              AND mp.price_timestamp >= :start_timestamp
              AND mp.price_timestamp < :end_timestamp
        ),

        lookback_prices AS (
            SELECT
                security_id,
                symbol,
                price_timestamp,
                interval_code,
                open_price,
                high_price,
                low_price,
                close_price,
                adjusted_close,
                volume,
                trading_value

            FROM previous_prices

            WHERE row_number <= :lookback_periods
        )

        SELECT *
        FROM lookback_prices

        UNION ALL

        SELECT *
        FROM range_prices

        ORDER BY symbol, price_timestamp
    """)

    query = query.bindparams(
        bindparam("tickers", expanding=True)
    )

    with engine.connect() as connection:
        result = pd.read_sql_query(
            query,
            connection,
            params={
                "tickers": tickers,
                "interval_code": interval_code,
                "start_timestamp": start_timestamp,
                "end_timestamp": end_timestamp,
                "lookback_periods": lookback_periods,
            },
        )

    return result