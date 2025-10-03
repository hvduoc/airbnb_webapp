"""
Script khởi tạo dữ liệu và tạo user admin
"""


from auth_service import ROLES, create_user
from database import SessionLocal, create_tables


def init_database():
    """Khởi tạo database và tạo dữ liệu mẫu"""
    print("🔧 Đang khởi tạo database...")
    create_tables()
    
    db = SessionLocal()
    
    try:
        # Tạo các user mẫu
        sample_users = [
            {
                "username": "admin",
                "password": "admin123",
                "full_name": "Quản trị viên",
                "role": "owner",
                "phone": "0900000000",
                "email": "admin@airbnb.vn"
            },
            {
                "username": "manager1",
                "password": "manager123",
                "full_name": "Nguyễn Văn Quản Lý",
                "role": "manager",
                "phone": "0901234567",
                "email": "manager@airbnb.vn"
            },
            {
                "username": "assistant1",
                "password": "assistant123",
                "full_name": "Trần Thị Trợ Lý",
                "role": "assistant",
                "phone": "0902345678",
                "email": "assistant@airbnb.vn"
            },
            {
                "username": "assistant2",
                "password": "assistant123",
                "full_name": "Lê Văn Hỗ Trợ",
                "role": "assistant",
                "phone": "0903456789",
                "email": "assistant2@airbnb.vn"
            },
            {
                "username": "accountant",
                "password": "account123",
                "full_name": "Phạm Thị Kế Toán",
                "role": "manager",
                "phone": "0904567890",
                "email": "accountant@airbnb.vn"
            }
        ]
        
        created_users = []
        for user_data in sample_users:
            try:
                user = create_user(db, **user_data)
                created_users.append(user)
                print(f"✅ Đã tạo user: {user.username} - {user.full_name} ({ROLES[user.role]})")
            except ValueError as e:
                print(f"⚠️ {e}")
        
        print(f"\n🎉 Đã khởi tạo database thành công với {len(created_users)} người dùng!")
        print("\n📋 Danh sách tài khoản:")
        print("=" * 60)
        
        for user in created_users:
            print(f"👤 {user.full_name}")
            print(f"   Username: {user.username}")
            print(f"   Role: {ROLES[user.role]}")
            print(f"   Phone: {user.phone}")
            print(f"   Email: {user.email}")
            print("-" * 40)
        
        print("\n🔑 Tài khoản quản trị:")
        print("Username: admin")
        print("Password: admin123")
        print("Role: Chủ sở hữu (toàn quyền)")
        
    except Exception as e:
        print(f"❌ Lỗi khởi tạo: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    init_database()