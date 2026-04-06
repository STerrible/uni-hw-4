from pathlib import Path

from sqlalchemy.orm import Session

from app.crud import DatabaseManager
from app.database import SessionLocal

CSV_PATH = Path(__file__).resolve().parent / "students.csv"


def main() -> None:
    session: Session = SessionLocal()

    try:
        manager = DatabaseManager(session)
        result = manager.load_from_csv(CSV_PATH)
        print(f"Данные успешно загружены: {result}")

    except Exception as exc:  # noqa: BLE001
        session.rollback()
        print(f"Ошибка при загрузке данных: {exc}")
        raise
    finally:
        session.close()


if __name__ == "__main__":
    main()
