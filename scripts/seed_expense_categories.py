from sqlmodel import Session, SQLModel, create_engine, select

from models import ExpenseCategory

# Kết nối đến cơ sở dữ liệu
engine = create_engine("sqlite:///app.db")


# Thêm dữ liệu mẫu vào bảng ExpenseCategory
def seed_expense_categories():
    with Session(engine) as session:
        categories = [
            {"name": "Utilities", "is_fixed": 1},
            {"name": "Maintenance", "is_fixed": 0},
            {"name": "Marketing", "is_fixed": 0},
            {"name": "Salaries", "is_fixed": 1},
            {"name": "Miscellaneous", "is_fixed": 0},
        ]

        for category in categories:
            existing_category = session.exec(
                select(ExpenseCategory).where(ExpenseCategory.name == category["name"])
            ).first()

            if not existing_category:
                session.add(ExpenseCategory(**category))

        session.commit()
        print("Seeded expense categories successfully.")


if __name__ == "__main__":
    SQLModel.metadata.create_all(engine)
    seed_expense_categories()
