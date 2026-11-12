import numpy as np
import pandas as pd

from app.components.validators.base import ValidationReport


def validate_not_empty(df: pd.DataFrame, report: ValidationReport):
    """Kiểm tra dataset có dữ liệu hay không."""

    if df.empty:
        report.add_issue(
            name="empty_dataset",
            message="Dataset không có dữ liệu."
        )


def validate_required_columns(
    df: pd.DataFrame,
    required_columns: list[str],
    report: ValidationReport,
):
    """Kiểm tra các cột bắt buộc."""

    missing_columns = [
        column for column in required_columns
        if column not in df.columns
    ]

    if missing_columns:
        report.add_issue(
            name="missing_columns",
            message="Dataset thiếu các cột bắt buộc.",
            details={"columns": missing_columns}
        )


def validate_missing_values(
    df: pd.DataFrame,
    report: ValidationReport,
):
    """Thống kê các giá trị bị thiếu."""

    missing_counts = df.isna().sum()
    missing_counts = missing_counts[missing_counts > 0]

    if not missing_counts.empty:
        report.add_issue(
            name="missing_values",
            message="Dataset có giá trị bị thiếu.",
            severity="warning",
            details={
                "columns": missing_counts.to_dict(),
                "total": int(missing_counts.sum())
            }
        )


def validate_duplicates(
    df: pd.DataFrame,
    report: ValidationReport,
    subset: list[str] | None = None,
):
    """Kiểm tra các dòng dữ liệu trùng lặp."""

    duplicate_count = int(df.duplicated(subset=subset).sum())

    if duplicate_count > 0:
        report.add_issue(
            name="duplicate_rows",
            message="Dataset có các dòng dữ liệu trùng lặp.",
            details={"count": duplicate_count}
        )


def validate_numeric_values(
    df: pd.DataFrame,
    report: ValidationReport,
):
    """Kiểm tra giá trị vô cực trong các cột số."""

    numeric_df = df.select_dtypes(include="number")

    invalid_counts = {}

    for column in numeric_df.columns:
        count = int(
            (~np.isfinite(numeric_df[column])).sum()
        )

        if count > 0:
            invalid_counts[column] = count

    if invalid_counts:
        report.add_issue(
            name="invalid_numeric_values",
            message="Dataset có giá trị vô cực hoặc không hợp lệ.",
            details={"columns": invalid_counts}
        )


def validate_dataset(
    df: pd.DataFrame,
    required_columns: list[str] | None = None,
    duplicate_subset: list[str] | None = None,
) -> ValidationReport:
    """
    Thực hiện các bước kiểm tra cơ bản cho dataset.
    """

    report = ValidationReport()

    validate_not_empty(df, report)

    if df.empty:
        return report

    if required_columns:
        validate_required_columns(
            df, required_columns, report
        )

    validate_missing_values(df, report)

    validate_duplicates(
        df, report, subset=duplicate_subset
    )

    validate_numeric_values(df, report)

    return report