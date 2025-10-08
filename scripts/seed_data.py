from sqlmodel import select

from db import get_session
from models import Channel, Salesperson


def seed_channels():
    with get_session() as session:
        existing = session.exec(select(Channel)).all()
        existing_names = {c.channel_name for c in existing}

        to_add = []
        for name in ["Airbnb", "Offline", "Facebook", "Tiktok", "Sale"]:
            if name not in existing_names:
                to_add.append(Channel(channel_name=name))

        if to_add:
            session.add_all(to_add)
            session.commit()
            print(f"✅ Đã thêm {len(to_add)} kênh mới.")
        else:
            print("✅ Danh sách kênh đã đầy đủ.")


def seed_salespeople():
    with get_session() as session:
        existing = session.exec(select(Salesperson)).all()
        if not existing:
            session.add_all(
                [
                    Salesperson(name="Dược", commission_rate=0.03, is_active=True),
                    Salesperson(name="Hồng", commission_rate=0.04, is_active=True),
                ]
            )
            session.commit()
            print("✅ Đã thêm nhân viên sale.")
        else:
            print("✅ Nhân viên sale đã có.")


if __name__ == "__main__":
    seed_channels()
    seed_salespeople()
