from app.database.connection import check_database_connection


if __name__ == "__main__":
    try:
        check_database_connection()
        print("Kết nối PostgreSQL thành công!")
    except Exception as exc:
        print("Không thể kết nối PostgreSQL.")
        print(f"Chi tiết lỗi: {exc}")
