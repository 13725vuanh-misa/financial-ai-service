import pandas as pd
from sqlalchemy import bindparam, text

from app.database.connection import engine
from app.repositories.security_repository import validate_tickers


def get_fundamental_data(
    tickers: list[str],
    start_date,
    end_date,
    lookback_periods: int = 0,
) -> pd.DataFrame:
    """
    Lấy dữ liệu chỉ tiêu tài chính theo quý từ PostgreSQL.

    Bao gồm:
    - Dữ liệu trong khoảng ngày yêu cầu.
    - Một số quý trước start_date để tính Feature.
    """

    if not tickers:
        raise ValueError("Danh sách tickers không được để trống")
    
    validate_tickers(tickers)

    if start_date >= end_date:
        raise ValueError("start_date phải nhỏ hơn end_date")

    if lookback_periods < 0:
        raise ValueError("lookback_periods không được âm")

    query = text("""
        WITH selected_securities AS (
            SELECT
                id AS security_id,
                symbol
            FROM securities
            WHERE symbol IN :tickers
        ),

        previous_periods AS (
            SELECT
                id AS financial_period_id,
                end_date
            FROM financial_periods
            WHERE end_date < :start_date
            ORDER BY end_date DESC
            LIMIT :lookback_periods
        ),

        previous_metrics AS (
            SELECT
                fm.security_id,
                s.symbol,
                fp.fiscal_year,
                fp.period_type,
                fp.end_date,
                fm.as_of_date,
                md.code AS metric_code,
                fm.value

            FROM financial_metrics fm

            JOIN selected_securities s
                ON fm.security_id = s.security_id

            JOIN financial_periods fp
                ON fm.financial_period_id = fp.id

            JOIN metric_definitions md
                ON fm.metric_definition_id = md.id

            JOIN previous_periods pp
                ON fp.id = pp.financial_period_id

            WHERE fm.is_canonical = TRUE
            AND fm.as_of_date < :start_date
        ),

        range_metrics AS (
            SELECT
                fm.security_id,
                s.symbol,
                fp.fiscal_year,
                fp.period_type,
                fp.end_date,
                fm.as_of_date,
                md.code AS metric_code,
                fm.value

            FROM financial_metrics fm

            JOIN selected_securities s
                ON fm.security_id = s.security_id

            JOIN financial_periods fp
                ON fm.financial_period_id = fp.id

            JOIN metric_definitions md
                ON fm.metric_definition_id = md.id

            WHERE fm.is_canonical = TRUE
            AND fm.as_of_date >= :start_date
            AND fm.as_of_date < :end_date
        )

        SELECT *
        FROM previous_metrics

        UNION ALL

        SELECT *
        FROM range_metrics

        ORDER BY symbol, as_of_date, metric_code
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
                "start_date": start_date,
                "end_date": end_date,
                "lookback_periods": lookback_periods,
            },
        )

    return result
