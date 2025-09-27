"""
Create default admin user for authentication system
"""
from auth.security import get_password_hash
from sqlmodel import Session, select, create_engine
from models import User
from datetime import datetime

# Create engine - use SQLite database
DATABASE_URL = "sqlite:///./app.db"
engine = create_engine(DATABASE_URL)

def create_admin_user():
    """Create default admin user"""
    
    # Get database session
    with Session(engine) as session:
        try:
            # Check if admin exists
            statement = select(User).where(User.email == "admin@airbnb.local")
            existing_admin = session.exec(statement).first()
            
            if existing_admin:
                print("✅ Admin user already exists!")
                return
            
            # Create admin user
            admin_password = "admin123"
            hashed_password = get_password_hash(admin_password)
            
            admin_user = User(
                email="admin@airbnb.local",
                username="admin",
                full_name="System Administrator",
                hashed_password=hashed_password,
                role="admin",
                is_active=True,
                is_verified=True,
                accessible_properties="[]"
            )
            
            session.add(admin_user)
            session.commit()
            session.refresh(admin_user)
            
            print("✅ Admin user created successfully!")
            print(f"📧 Email: {admin_user.email}")
            print(f"👤 Username: {admin_user.username}")
            print(f"🔐 Password: admin123")
            print(f"🎭 Role: {admin_user.role}")
            
            # Create demo user
            user_password = "user123"
            hashed_password = get_password_hash(user_password)
            
            demo_user = User(
                email="user@airbnb.local", 
                username="user",
                full_name="Demo User",
                hashed_password=hashed_password,
                role="user",
                is_active=True,
                is_verified=True,
                accessible_properties='[1, 2, 3]'
            )
            
            session.add(demo_user)
            session.commit()
            session.refresh(demo_user)
            
            print("✅ Demo user created successfully!")
            print(f"📧 Email: {demo_user.email}")
            print(f"👤 Username: {demo_user.username}")
            print(f"🔐 Password: user123")
            print(f"🎭 Role: {demo_user.role}")
            
        except Exception as e:
            print(f"❌ Error creating users: {e}")
            session.rollback()

if __name__ == "__main__":
    create_admin_user()